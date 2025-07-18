import boto3
import json
import os
import logging
from botocore.exceptions import ClientError

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BedrockEvaluator:
    """AWS Bedrock을 사용하여 학생 과제를 자동으로 평가하는 클래스"""
    
    def __init__(self, region_name="us-east-1", model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
        """
        BedrockEvaluator 초기화
        
        Args:
            region_name (str): AWS 리전 이름
            model_id (str): Bedrock 모델 ID
        """
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        self.model_id = model_id
        logger.info(f"BedrockEvaluator initialized with model: {model_id}")
    
    def read_file_content(self, file_path):
        """
        파일 내용을 읽어서 반환
        
        Args:
            file_path (str): 파일 경로
            
        Returns:
            str: 파일 내용 또는 오류 메시지
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # 텍스트 파일
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            
            # PDF 파일
            elif file_extension == '.pdf':
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        content += page.extract_text() + "\n"
                    return content
            
            # Word 문서
            elif file_extension in ['.docx', '.doc']:
                from docx import Document
                doc = Document(file_path)
                content = ""
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
                return content
            
            else:
                return f"지원하지 않는 파일 형식입니다: {file_extension}"
                
        except Exception as e:
            logger.error(f"파일 읽기 오류: {str(e)}")
            return f"파일 읽기 오류: {str(e)}"
    
    def evaluate_submission(self, student_submission_path, evaluation_criteria_path, model_answer_path=None):
        """
        학생 과제를 평가 기준과 모범 답안을 기반으로 평가
        
        Args:
            student_submission_path (str): 학생 제출물 파일 경로
            evaluation_criteria_path (str): 평가 기준 파일 경로
            model_answer_path (str, optional): 모범 답안 파일 경로
            
        Returns:
            dict: 평가 결과 (grade, comments)
        """
        try:
            # 파일 내용 읽기
            student_content = self.read_file_content(student_submission_path)
            criteria_content = self.read_file_content(evaluation_criteria_path)
            
            model_answer_content = ""
            if model_answer_path:
                model_answer_content = self.read_file_content(model_answer_path)
            
            # 프롬프트 구성
            prompt = self._create_evaluation_prompt(
                student_content, 
                criteria_content, 
                model_answer_content
            )
            
            # Bedrock API 호출
            response = self._invoke_bedrock_model(prompt)
            
            # 응답 파싱
            evaluation_result = self._parse_evaluation_response(response)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"평가 중 오류 발생: {str(e)}")
            return {
                "grade": None,
                "comments": f"자동 평가 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _create_evaluation_prompt(self, student_content, criteria_content, model_answer_content=""):
        """
        평가를 위한 프롬프트 생성
        
        Args:
            student_content (str): 학생 제출물 내용
            criteria_content (str): 평가 기준 내용
            model_answer_content (str): 모범 답안 내용
            
        Returns:
            str: 평가 프롬프트
        """
        prompt = f"""
        당신은 학생 과제를 평가하는 교육 전문가입니다. 주어진 평가 기준과 모범 답안을 바탕으로 학생의 제출물을 공정하게 평가해주세요.
        
        # 평가 기준
        {criteria_content}
        
        # 학생 제출물
        {student_content}
        """
        
        if model_answer_content:
            prompt += f"""
            # 모범 답안
            {model_answer_content}
            """
        
        prompt += """
        # 평가 지침
        1. 평가 기준에 따라 학생의 제출물을 객관적으로 평가해주세요.
        2. 학생의 제출물과 모범 답안을 비교하여 유사점과 차이점을 분석해주세요.
        3. 학생의 이해도, 창의성, 논리적 구성을 고려해주세요.
        4. 최종 평가는 A, B, C, D, F 중 하나의 등급으로 제시해주세요.
        5. 개선을 위한 구체적인 피드백을 제공해주세요.
        
        # 응답 형식
        다음 JSON 형식으로 응답해주세요:
        ```json
        {
            "grade": "등급(A/B/C/D/F)",
            "comments": "상세한 피드백과 개선점"
        }
        ```
        
        JSON 형식만 응답하고 다른 설명은 포함하지 마세요.
        """
        
        return prompt
    
    def _invoke_bedrock_model(self, prompt):
        """
        Bedrock 모델 호출
        
        Args:
            prompt (str): 모델에 전달할 프롬프트
            
        Returns:
            str: 모델 응답
        """
        try:
            # Anthropic Claude 모델용 요청 본문
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Bedrock 모델 호출
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # 응답 파싱
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
            
        except ClientError as e:
            logger.error(f"Bedrock API 호출 오류: {str(e)}")
            raise Exception(f"Bedrock API 호출 오류: {str(e)}")
    
    def _parse_evaluation_response(self, response):
        """
        모델 응답에서 평가 결과 추출
        
        Args:
            response (str): 모델 응답
            
        Returns:
            dict: 평가 결과 (grade, comments)
        """
        try:
            # JSON 부분 추출
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # 필수 필드 확인
                if 'grade' not in result or 'comments' not in result:
                    raise ValueError("응답에 필수 필드(grade, comments)가 없습니다")
                
                # 등급 유효성 검사
                valid_grades = ['A', 'B', 'C', 'D', 'F']
                if result['grade'] not in valid_grades:
                    raise ValueError(f"유효하지 않은 등급입니다: {result['grade']}")
                
                return result
            else:
                raise ValueError("응답에서 JSON 형식을 찾을 수 없습니다")
                
        except Exception as e:
            logger.error(f"응답 파싱 오류: {str(e)}")
            return {
                "grade": None,
                "comments": f"자동 평가 결과를 처리하는 중 오류가 발생했습니다: {str(e)}"
            }
