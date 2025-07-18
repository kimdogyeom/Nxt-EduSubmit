# Nxt-EduSubmit

## 학생 과제 제출 및 관리 시스템

Nxt-EduSubmit은 학생들이 과제를 온라인으로 제출하고, 교수가 제출 현황을 관리하며 평가할 수 있는 웹 애플리케이션입니다. Version 2.0부터는 AWS Bedrock을 활용한 자동 평가 기능이 추가되어 교수의 업무 효율성을 높였습니다.

## 주요 기능

### 학생 기능
- 📤 **과제 제출**: 다양한 형식의 파일 업로드
- 📋 **제출 내역 관리**: 제출한 과제 목록 확인 및 삭제
- 📊 **평가 결과 확인**: 교수 평가 및 AI 자동 평가 결과 확인

### 교수 기능
- 📊 **제출 현황 대시보드**: 전체 학생 제출 현황 및 통계 확인
- 📝 **평가 시스템**: A, B, C, D, F 성적 부여 및 코멘트 작성
- 🤖 **자동 평가 시스템**: AWS Bedrock을 활용한 학생 과제 자동 평가
- 📤 **참고자료 업로드**: 평가기준 및 모범답안 파일 업로드

## 기술 스택

- **Frontend/Backend**: Streamlit
- **데이터베이스**: SQLite
- **언어**: Python
- **파일 처리**: PyPDF2, python-docx
- **AI 서비스**: AWS Bedrock (Claude 모델)

## 시작하기

### 요구사항
- Python 3.11+
- 필요한 패키지: streamlit, pandas, PyPDF2, python-docx, boto3
- AWS 계정 및 Bedrock 서비스 접근 권한

### 설치
```bash
# 필요한 패키지 설치
pip install streamlit pandas PyPDF2 python-docx boto3
```

### 실행
```bash
streamlit run app.py --server.port 5000
```

## 초기 계정 정보

**학생 계정:**
- 학번: 20251111, 20252222, 20253333
- 비밀번호: 1234 (모든 계정 공통)

**교수 계정:**
- 아이디: admin1, admin2, admin3
- 비밀번호: 1234 (모든 계정 공통)

## 버전 정보

### Version 2.0 (2025-07-18)
- AWS Bedrock 기반 자동 평가 기능 추가
- 자동 평가 결과 관리 및 교수 평가 연동 기능 추가
- 데이터베이스 스키마 확장
- UI 개선

### Version 1.0 (2025-07-18)
- 초기 버전 출시
- 학생 과제 제출 기능
- 교수 평가 기능
- 파일 업로드 및 관리 기능

## 문서

자세한 정보는 다음 문서를 참조하세요:
- [프로젝트 개요](docs/README.md)
- [Version 1.0 기능 상세](docs/version1.0-features.md)
- [Version 2.0 기능 상세](docs/version2.0-features.md)

## 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.
