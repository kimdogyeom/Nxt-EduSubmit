import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import os
from datetime import datetime
import PyPDF2
from docx import Document

# 애플리케이션 설정
st.set_page_config(
    page_title="학생 과제 제출 및 관리 시스템",
    page_icon="📚",
    layout="wide"
)

# 데이터베이스 초기화 함수
def initialize_database():
    """데이터베이스와 테이블을 초기화하고 초기 데이터를 삽입합니다."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # students 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    
    # professors 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professors (
            admin_id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    
    # submissions 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            submission_time DATETIME NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    # professor_files 테이블 생성 (평가기준, 모범답안 등)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professor_files (
            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            upload_time DATETIME NOT NULL,
            FOREIGN KEY (admin_id) REFERENCES professors (admin_id)
        )
    ''')
    
    # 초기 데이터 확인 및 삽입
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        # 비밀번호 '1234'를 해싱
        hashed_password = hashlib.sha256('1234'.encode()).hexdigest()
        
        # 학생 초기 데이터 삽입
        students_data = [
            ('20251111', hashed_password, '이국민', 'leegukmin@email.com'),
            ('20252222', hashed_password, '김대학', 'kimdaehak@email.com'),
            ('20253333', hashed_password, '최학생', 'choihaksaeng@email.com')
        ]
        cursor.executemany('INSERT INTO students VALUES (?, ?, ?, ?)', students_data)
        
        # 교수 초기 데이터 삽입
        professors_data = [
            ('admin1', hashed_password, '이교수'),
            ('admin2', hashed_password, '김교수'),
            ('admin3', hashed_password, '최교수')
        ]
        cursor.executemany('INSERT INTO professors VALUES (?, ?, ?)', professors_data)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """비밀번호를 SHA256으로 해싱합니다."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_student(student_id, password):
    """학생 로그인 인증을 처리합니다."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    cursor.execute('SELECT student_id, name FROM students WHERE student_id = ? AND password = ?', 
                   (student_id, hashed_password))
    result = cursor.fetchone()
    conn.close()
    
    return result

def authenticate_admin(admin_id, password):
    """관리자 로그인 인증을 처리합니다."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    cursor.execute('SELECT admin_id, name FROM professors WHERE admin_id = ? AND password = ?', 
                   (admin_id, hashed_password))
    result = cursor.fetchone()
    conn.close()
    
    return result

def save_submission(student_id, uploaded_file):
    """과제 파일을 저장하고 데이터베이스에 기록합니다."""
    # storage 폴더가 없으면 생성
    if not os.path.exists('storage'):
        os.makedirs('storage')
    
    # 파일명 생성: {학번}_{원본파일명}
    filename = f"{student_id}_{uploaded_file.name}"
    file_path = os.path.join('storage', filename)
    
    try:
        # 파일 저장
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # 데이터베이스에 기록
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO submissions (student_id, file_path, original_filename, submission_time)
            VALUES (?, ?, ?, ?)
        ''', (student_id, file_path, uploaded_file.name, submission_time))
        
        conn.commit()
        conn.close()
        
        return True, "파일이 성공적으로 제출되었습니다!"
    except Exception as e:
        return False, f"파일 제출 중 오류가 발생했습니다: {str(e)}"

def get_student_submissions(student_id):
    """특정 학생의 제출 내역을 조회합니다."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT submission_id, original_filename, submission_time, file_path
        FROM submissions 
        WHERE student_id = ?
        ORDER BY submission_time DESC
    ''', (student_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def delete_submission(submission_id, file_path):
    """제출 기록과 파일을 삭제합니다."""
    try:
        # 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 데이터베이스에서 기록 삭제
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM submissions WHERE submission_id = ?', (submission_id,))
        conn.commit()
        conn.close()
        
        return True, "제출 내역이 성공적으로 삭제되었습니다."
    except Exception as e:
        return False, f"삭제 중 오류가 발생했습니다: {str(e)}"

def get_all_submissions():
    """모든 제출 내역을 학생 정보와 함께 조회합니다."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.student_id, st.name, s.original_filename, s.submission_time
        FROM submissions s
        JOIN students st ON s.student_id = st.student_id
        ORDER BY s.submission_time DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def save_professor_file(admin_id, uploaded_file, file_type):
    """교수 파일(평가기준, 모범답안)을 저장하고 데이터베이스에 기록합니다."""
    # storage 폴더가 없으면 생성
    if not os.path.exists('storage'):
        os.makedirs('storage')
    
    # professor_files 폴더 생성
    prof_storage = os.path.join('storage', 'professor_files')
    if not os.path.exists(prof_storage):
        os.makedirs(prof_storage)
    
    # 파일명 생성: {file_type}_{admin_id}_{원본파일명}
    filename = f"{file_type}_{admin_id}_{uploaded_file.name}"
    file_path = os.path.join(prof_storage, filename)
    
    try:
        # 파일 저장
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # 데이터베이스에 기록
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO professor_files (admin_id, file_type, file_path, original_filename, upload_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_id, file_type, file_path, uploaded_file.name, upload_time))
        
        conn.commit()
        conn.close()
        
        return True, "파일이 성공적으로 업로드되었습니다!"
    except Exception as e:
        return False, f"파일 업로드 중 오류가 발생했습니다: {str(e)}"

def get_professor_files(admin_id=None):
    """교수 파일 목록을 조회합니다."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if admin_id:
        cursor.execute('''
            SELECT file_id, file_type, original_filename, upload_time, file_path
            FROM professor_files 
            WHERE admin_id = ?
            ORDER BY upload_time DESC
        ''', (admin_id,))
    else:
        cursor.execute('''
            SELECT pf.file_id, pf.file_type, pf.original_filename, pf.upload_time, pf.file_path, p.name
            FROM professor_files pf
            JOIN professors p ON pf.admin_id = p.admin_id
            ORDER BY pf.upload_time DESC
        ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def delete_professor_file(file_id, file_path):
    """교수 파일을 삭제합니다."""
    try:
        # 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 데이터베이스에서 기록 삭제
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM professor_files WHERE file_id = ?', (file_id,))
        conn.commit()
        conn.close()
        
        return True, "파일이 성공적으로 삭제되었습니다."
    except Exception as e:
        return False, f"삭제 중 오류가 발생했습니다: {str(e)}"

def read_file_content(file_path):
    """파일 내용을 읽어서 반환합니다."""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return read_pdf_content(file_path)
        elif file_extension in ['.docx', '.doc']:
            return read_docx_content(file_path)
        elif file_extension == '.txt':
            return read_txt_content(file_path)
        else:
            return False, "지원하지 않는 파일 형식입니다. (PDF, Word, TXT 파일만 미리보기 가능)"
    
    except Exception as e:
        return False, f"파일을 읽는 중 오류가 발생했습니다: {str(e)}"

def read_pdf_content(file_path):
    """PDF 파일 내용을 읽습니다."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text() + "\n"
            
            if content.strip():
                return True, content
            else:
                return False, "PDF에서 텍스트를 추출할 수 없습니다."
    
    except Exception as e:
        return False, f"PDF 읽기 오류: {str(e)}"

def read_docx_content(file_path):
    """Word 문서 내용을 읽습니다."""
    try:
        doc = Document(file_path)
        content = ""
        
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        
        if content.strip():
            return True, content
        else:
            return False, "Word 문서에 텍스트가 없습니다."
    
    except Exception as e:
        return False, f"Word 문서 읽기 오류: {str(e)}"

def read_txt_content(file_path):
    """텍스트 파일 내용을 읽습니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if content.strip():
            return True, content
        else:
            return False, "텍스트 파일이 비어있습니다."
    
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp949') as file:
                content = file.read()
            return True, content
        except Exception as e:
            return False, f"텍스트 파일 인코딩 오류: {str(e)}"
    except Exception as e:
        return False, f"텍스트 파일 읽기 오류: {str(e)}"

def student_dashboard():
    """학생용 대시보드를 표시합니다."""
    st.header(f"환영합니다, {st.session_state.user_name}님! 👨‍🎓")
    st.subheader(f"학번: {st.session_state.user_id}")
    
    # 과제 제출 섹션
    st.markdown("---")
    st.subheader("📤 과제 제출")
    
    uploaded_file = st.file_uploader(
        "과제 파일을 선택하세요",
        type=['pdf', 'docx', 'doc', 'txt', 'zip', 'rar'],
        help="PDF, Word 문서, 텍스트 파일, 압축 파일을 업로드할 수 있습니다."
    )
    
    if uploaded_file is not None:
        st.info(f"선택된 파일: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        if st.button("📤 제출하기", type="primary"):
            with st.spinner("과제를 제출하는 중..."):
                success, message = save_submission(st.session_state.user_id, uploaded_file)
            
            if success:
                st.success(message)
                st.balloons()  # 제출 성공 시 풍선 효과
                st.info("과제가 성공적으로 제출되었습니다! 아래 제출 내역에서 확인하세요.")
                # 2초 후 자동으로 새로고침
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(message)
                st.warning("과제 제출에 실패했습니다. 다시 시도해주세요.")
    
    # 제출 내역 섹션
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📋 제출 내역")
    with col2:
        if st.button("🔄 새로고침", key="refresh_submissions"):
            st.rerun()
    
    submissions = get_student_submissions(st.session_state.user_id)
    
    if submissions:
        for idx, (submission_id, original_filename, submission_time, file_path) in enumerate(submissions):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{original_filename}**")
            
            with col2:
                st.write(f"제출시간: {submission_time}")
            
            with col3:
                if st.button("🗑️ 삭제", key=f"delete_{submission_id}"):
                    success, message = delete_submission(submission_id, file_path)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
    else:
        st.info("아직 제출한 과제가 없습니다.")

def admin_dashboard():
    """관리자용 대시보드를 표시합니다."""
    st.header(f"관리자 대시보드 👨‍🏫")
    st.subheader(f"환영합니다, {st.session_state.user_name}님!")
    
    # 탭으로 기능 구분
    tab1, tab2, tab3 = st.tabs(["📊 제출 현황", "📤 파일 업로드", "📁 업로드된 파일"])
    
    with tab1:
        # 제출 현황 대시보드
        st.subheader("📊 전체 제출 현황")
        
        submissions = get_all_submissions()
        
        if submissions:
            # DataFrame 생성
            df = pd.DataFrame(submissions, columns=['학번', '이름', '파일명', '제출시간'])
            
            # 통계 정보 표시
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 제출 건수", len(submissions))
            
            with col2:
                unique_students = df['학번'].nunique()
                st.metric("제출한 학생 수", unique_students)
            
            with col3:
                # 가장 최근 제출 시간
                latest_submission = df['제출시간'].iloc[0] if len(df) > 0 else "없음"
                st.metric("최근 제출", latest_submission)
            
            st.markdown("---")
            
            # 전체 제출 목록 표시
            st.subheader("📝 상세 제출 목록")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # 학생별 제출 현황
            st.markdown("---")
            st.subheader("👥 학생별 제출 현황")
            student_counts = df.groupby(['학번', '이름']).size().reset_index(name='제출 건수')
            st.dataframe(
                student_counts,
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("아직 제출된 과제가 없습니다.")
    
    with tab2:
        # 파일 업로드 섹션
        st.subheader("📤 파일 업로드")
        st.write("평가기준 및 모범답안 파일을 업로드하세요.")
        
        # 파일 타입 선택
        file_type = st.selectbox(
            "파일 유형 선택",
            ["평가기준", "모범답안"],
            help="업로드할 파일의 유형을 선택하세요."
        )
        
        # 파일 업로드
        uploaded_file = st.file_uploader(
            f"{file_type} 파일을 선택하세요",
            type=['pdf', 'docx', 'doc', 'txt', 'hwp', 'pptx'],
            help="PDF, Word 문서, 텍스트 파일, 한글 파일, PowerPoint를 업로드할 수 있습니다.",
            key=f"upload_{file_type}"
        )
        
        if uploaded_file is not None:
            st.info(f"선택된 파일: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("📤 업로드", type="primary", key=f"upload_btn_{file_type}"):
                    with st.spinner("파일을 업로드하는 중..."):
                        success, message = save_professor_file(st.session_state.user_id, uploaded_file, file_type)
                    
                    if success:
                        st.success(message)
                        st.balloons()  # 업로드 성공 시 풍선 효과
                        st.info("파일이 성공적으로 업로드되었습니다! '업로드된 파일' 탭에서 확인하세요.")
                        # 2초 후 자동으로 새로고침
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
                        st.warning("업로드에 실패했습니다. 다시 시도해주세요.")
    
    with tab3:
        # 업로드된 파일 목록
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📁 업로드된 파일 목록")
        with col2:
            if st.button("🔄 새로고침", key="refresh_professor_files"):
                st.rerun()
        
        professor_files = get_professor_files(st.session_state.user_id)
        
        if professor_files:
            st.write(f"총 {len(professor_files)}개의 파일이 업로드되어 있습니다.")
            
            # 파일 타입별로 그룹화
            evaluation_files = [f for f in professor_files if f[1] == '평가기준']
            answer_files = [f for f in professor_files if f[1] == '모범답안']
            
            # 평가기준 파일들
            if evaluation_files:
                st.markdown("### 📋 평가기준 파일")
                for file_id, file_type, original_filename, upload_time, file_path in evaluation_files:
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{original_filename}**")
                    
                    with col2:
                        st.write(f"업로드: {upload_time}")
                    
                    with col3:
                        if st.button("👁️ 내용보기", key=f"view_eval_{file_id}"):
                            success, content = read_file_content(file_path)
                            if success:
                                st.session_state[f"show_content_{file_id}"] = content
                            else:
                                st.error(content)
                    
                    with col4:
                        if st.button("🗑️ 삭제", key=f"delete_prof_{file_id}"):
                            success, message = delete_professor_file(file_id, file_path)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # 파일 내용 표시
                    if f"show_content_{file_id}" in st.session_state:
                        with st.expander(f"📄 {original_filename} 내용", expanded=True):
                            st.text_area(
                                "파일 내용:",
                                st.session_state[f"show_content_{file_id}"],
                                height=300,
                                key=f"content_area_{file_id}"
                            )
                            if st.button("❌ 닫기", key=f"close_{file_id}"):
                                del st.session_state[f"show_content_{file_id}"]
                                st.rerun()
                
                st.markdown("---")
            
            # 모범답안 파일들
            if answer_files:
                st.markdown("### 📝 모범답안 파일")
                for file_id, file_type, original_filename, upload_time, file_path in answer_files:
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{original_filename}**")
                    
                    with col2:
                        st.write(f"업로드: {upload_time}")
                    
                    with col3:
                        if st.button("👁️ 내용보기", key=f"view_answer_{file_id}"):
                            success, content = read_file_content(file_path)
                            if success:
                                st.session_state[f"show_content_{file_id}"] = content
                            else:
                                st.error(content)
                    
                    with col4:
                        if st.button("🗑️ 삭제", key=f"delete_prof_{file_id}"):
                            success, message = delete_professor_file(file_id, file_path)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # 파일 내용 표시
                    if f"show_content_{file_id}" in st.session_state:
                        with st.expander(f"📄 {original_filename} 내용", expanded=True):
                            st.text_area(
                                "파일 내용:",
                                st.session_state[f"show_content_{file_id}"],
                                height=300,
                                key=f"content_area_answer_{file_id}"
                            )
                            if st.button("❌ 닫기", key=f"close_answer_{file_id}"):
                                del st.session_state[f"show_content_{file_id}"]
                                st.rerun()
            
            if not evaluation_files and not answer_files:
                st.info("업로드된 파일이 없습니다.")
        
        else:
            st.info("아직 업로드된 파일이 없습니다.")

def main():
    """메인 애플리케이션 함수"""
    # 데이터베이스 초기화
    initialize_database()
    
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    
    # 애플리케이션 제목
    st.title("📚 학생 과제 제출 및 관리 시스템")
    
    # 로그인 상태에 따른 화면 분기
    if not st.session_state.logged_in:
        # 로그인 화면
        st.markdown("---")
        
        # 사이드바에서 역할 선택
        with st.sidebar:
            st.header("🔐 로그인")
            role = st.selectbox(
                "사용자 역할 선택",
                ["학생", "관리자"],
                help="학생 또는 관리자(교수) 중 선택하세요."
            )
            
            if role == "학생":
                st.subheader("학생 로그인")
                student_id = st.text_input("학번", placeholder="예: 20251111")
                password = st.text_input("비밀번호", type="password")
                
                if st.button("로그인", type="primary", use_container_width=True):
                    if student_id and password:
                        result = authenticate_student(student_id, password)
                        if result:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.user_id = result[0]
                            st.session_state.user_name = result[1]
                            st.success("로그인 성공!")
                            st.rerun()
                        else:
                            st.error("학번 또는 비밀번호가 일치하지 않습니다.")
                    else:
                        st.warning("학번과 비밀번호를 모두 입력해주세요.")
            
            else:  # 관리자
                st.subheader("관리자 로그인")
                admin_id = st.text_input("아이디", placeholder="예: admin1")
                password = st.text_input("비밀번호", type="password")
                
                if st.button("로그인", type="primary", use_container_width=True):
                    if admin_id and password:
                        result = authenticate_admin(admin_id, password)
                        if result:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "admin"
                            st.session_state.user_id = result[0]
                            st.session_state.user_name = result[1]
                            st.success("로그인 성공!")
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                    else:
                        st.warning("아이디와 비밀번호를 모두 입력해주세요.")
        
        # 메인 영역에 안내 메시지
        st.markdown("""
        ### 시스템 안내
        
        **학생용 기능:**
        - 과제 파일 업로드 및 제출
        - 제출 내역 확인 및 삭제
        
        **관리자용 기능:**
        - 전체 학생 제출 현황 조회
        - 제출 통계 및 상세 정보 확인
        
        ---
        
        **초기 계정 정보:**
        
        **학생 계정:**
        - 학번: 20251111, 20252222, 20253333
        - 비밀번호: 1234 (모든 계정 공통)
        
        **관리자 계정:**
        - 아이디: admin1, admin2, admin3
        - 비밀번호: 1234 (모든 계정 공통)
        """)
    
    else:
        # 로그인된 상태
        # 상단에 로그아웃 버튼
        with st.sidebar:
            st.success(f"로그인됨: {st.session_state.user_name}")
            if st.button("🚪 로그아웃", use_container_width=True):
                # 세션 상태 초기화
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.rerun()
        
        # 역할에 따른 대시보드 표시
        if st.session_state.user_role == "student":
            student_dashboard()
        elif st.session_state.user_role == "admin":
            admin_dashboard()

if __name__ == "__main__":
    main()
