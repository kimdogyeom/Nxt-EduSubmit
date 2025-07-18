import sqlite3
import os
import sys

def backup_database():
    """데이터베이스 백업"""
    if os.path.exists('database.db'):
        backup_file = 'database.db.backup'
        i = 1
        while os.path.exists(backup_file):
            backup_file = f'database.db.backup{i}'
            i += 1
        
        os.system(f'cp database.db {backup_file}')
        print(f"데이터베이스가 {backup_file}으로 백업되었습니다.")
    else:
        print("데이터베이스 파일이 존재하지 않습니다.")
        sys.exit(1)

def update_schema():
    """데이터베이스 스키마 업데이트"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 기존 테이블 정보 확인
    cursor.execute("PRAGMA table_info(evaluations)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # 필요한 열 추가
    if 'is_auto_evaluated' not in column_names:
        print("is_auto_evaluated 열 추가 중...")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN is_auto_evaluated BOOLEAN DEFAULT 0")
    
    if 'auto_grade' not in column_names:
        print("auto_grade 열 추가 중...")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN auto_grade TEXT CHECK(auto_grade IN ('A', 'B', 'C', 'D', 'F', NULL))")
    
    if 'auto_comments' not in column_names:
        print("auto_comments 열 추가 중...")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN auto_comments TEXT")
    
    if 'auto_evaluation_time' not in column_names:
        print("auto_evaluation_time 열 추가 중...")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN auto_evaluation_time DATETIME")
    
    conn.commit()
    conn.close()
    print("데이터베이스 스키마 업데이트가 완료되었습니다.")

if __name__ == "__main__":
    backup_database()
    update_schema()
