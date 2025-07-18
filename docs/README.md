# 학생 과제 제출 및 관리 시스템

## 프로젝트 개요

이 프로젝트는 학생들이 과제를 온라인으로 제출하고, 교수가 제출 현황을 관리하며 평가할 수 있는 웹 애플리케이션입니다. Streamlit과 SQLite를 기반으로 구축되어 간단하고 직관적인 인터페이스를 제공합니다.

## 주요 기능

### 학생 기능
- 📤 **과제 제출**: 다양한 형식의 파일 업로드 (PDF, Word, 텍스트, 압축파일 등)
- 📋 **제출 내역 관리**: 제출한 과제 목록 확인 및 삭제
- 📊 **평가 결과 확인**: 교수의 성적 평가 및 피드백 확인
- 🔄 **실시간 업데이트**: 새로고침 기능으로 최신 정보 확인

### 교수 기능
- 📊 **제출 현황 대시보드**: 전체 학생 제출 현황 및 통계 확인
- 👁️ **파일 내용 보기**: 학생이 제출한 파일 내용 직접 확인
- 📝 **평가 시스템**: A, B, C, D, F 성적 부여 및 코멘트 작성
- 📤 **참고자료 업로드**: 평가기준 및 모범답안 파일 업로드
- 📁 **파일 관리**: 업로드된 참고자료 관리 및 내용 확인

## 기술 스택

- **Frontend/Backend**: Streamlit
- **데이터베이스**: SQLite
- **언어**: Python
- **파일 처리**: PyPDF2, python-docx
- **인증**: 세션 기반 로그인

## 설치 및 실행

### 요구사항
- Python 3.11+
- 필요한 패키지: streamlit, pandas, PyPDF2, python-docx

### 실행 방법
```bash
streamlit run app.py --server.port 5000
```

## 사용자 가이드

### 초기 계정 정보

**학생 계정:**
- 학번: 20251111, 20252222, 20253333
- 비밀번호: 1234 (모든 계정 공통)

**교수 계정:**
- 아이디: admin1, admin2, admin3
- 비밀번호: 1234 (모든 계정 공통)

### 로그인 방법
1. 사이드바에서 사용자 역할(학생/관리자) 선택
2. 해당 계정 정보 입력
3. 로그인 버튼 클릭

## 프로젝트 구조

```
project/
├── app.py                      # 메인 애플리케이션
├── database.db                 # SQLite 데이터베이스
├── storage/                    # 파일 저장 디렉토리
│   ├── {학번}_{파일명}         # 학생 제출 파일
│   └── professor_files/        # 교수 업로드 파일
├── docs/                       # 문서화
│   ├── README.md               # 프로젝트 개요
│   └── version1.0-features.md  # 버전 1.0 기능 상세
├── .streamlit/
│   └── config.toml             # Streamlit 설정
└── replit.md                   # 프로젝트 아키텍처 문서
```

## 데이터베이스 스키마

### students 테이블
- `student_id` (TEXT, Primary Key): 학번
- `password` (TEXT): 해싱된 비밀번호
- `name` (TEXT): 학생 이름
- `email` (TEXT): 이메일 주소

### professors 테이블
- `admin_id` (TEXT, Primary Key): 관리자 ID
- `password` (TEXT): 해싱된 비밀번호
- `name` (TEXT): 교수 이름

### submissions 테이블
- `submission_id` (INTEGER, Primary Key): 제출 ID
- `student_id` (TEXT): 학생 학번
- `file_path` (TEXT): 파일 저장 경로
- `original_filename` (TEXT): 원본 파일명
- `submission_time` (DATETIME): 제출 시간

### professor_files 테이블
- `file_id` (INTEGER, Primary Key): 파일 ID
- `admin_id` (TEXT): 교수 ID
- `file_type` (TEXT): 파일 유형 (평가기준/모범답안)
- `file_path` (TEXT): 파일 저장 경로
- `original_filename` (TEXT): 원본 파일명
- `upload_time` (DATETIME): 업로드 시간

### evaluations 테이블
- `evaluation_id` (INTEGER, Primary Key): 평가 ID
- `submission_id` (INTEGER): 제출물 ID
- `admin_id` (TEXT): 평가한 교수 ID
- `grade` (TEXT): 성적 (A, B, C, D, F)
- `comments` (TEXT): 평가 코멘트
- `evaluation_time` (DATETIME): 평가 시간

## 보안 기능

- **비밀번호 해싱**: SHA256을 사용한 비밀번호 암호화
- **세션 관리**: Streamlit 세션 상태를 통한 인증 관리
- **파일 격리**: 사용자별 파일 저장 경로 분리
- **SQL 인젝션 방지**: 매개변수화된 쿼리 사용

## 지원 파일 형식

### 학생 과제 제출
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- 텍스트 파일 (.txt)
- 압축 파일 (.zip, .rar)

### 교수 참고자료
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- 텍스트 파일 (.txt)
- 한글 파일 (.hwp)
- PowerPoint (.pptx)

## 향후 개발 계획

- 이메일 알림 시스템
- 파일 다운로드 기능
- 과제별 마감일 설정
- 대용량 파일 업로드 지원
- 사용자 관리 기능 확장
- 평가 통계 및 분석 기능

## 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

## 문의사항

프로젝트 관련 문의사항이나 버그 리포트는 개발팀에 연락주시기 바랍니다.