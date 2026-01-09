# Created: 2026-01-03 15:30
import sqlite3
import os

DATABASE_PATH = 'cbt_questions.db'

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 과목 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 문제 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            question_image TEXT,
            option_a TEXT NOT NULL,
            option_a_image TEXT,
            option_b TEXT NOT NULL,
            option_b_image TEXT,
            option_c TEXT NOT NULL,
            option_c_image TEXT,
            option_d TEXT NOT NULL,
            option_d_image TEXT,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            explanation_image TEXT,
            exam_set INTEGER DEFAULT 1,
            subject_id INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    ''')

    conn.commit()
    conn.close()

def migrate_add_exam_set():
    """기존 테이블에 exam_set 컬럼 추가 (마이그레이션)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # exam_set 컬럼이 없으면 추가
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'exam_set' not in columns:
            cursor.execute('ALTER TABLE questions ADD COLUMN exam_set INTEGER DEFAULT 1')
            conn.commit()
            print("exam_set 컬럼이 추가되었습니다.")
        else:
            print("exam_set 컬럼이 이미 존재합니다.")
    except Exception as e:
        print(f"마이그레이션 오류: {e}")
    finally:
        conn.close()

def migrate_add_image_columns():
    """기존 테이블에 이미지 컬럼들 추가 (마이그레이션)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # 현재 컬럼 목록 확인
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]

        # 추가할 컬럼들
        new_columns = {
            'question_image': 'TEXT',
            'option_a_image': 'TEXT',
            'option_b_image': 'TEXT',
            'option_c_image': 'TEXT',
            'option_d_image': 'TEXT'
        }

        # 없는 컬럼만 추가
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                cursor.execute(f'ALTER TABLE questions ADD COLUMN {col_name} {col_type}')
                print(f"{col_name} 컬럼이 추가되었습니다.")
            else:
                print(f"{col_name} 컬럼이 이미 존재합니다.")

        conn.commit()
    except Exception as e:
        print(f"이미지 컬럼 마이그레이션 오류: {e}")
    finally:
        conn.close()

def migrate_add_explanation_images():
    """기존 테이블에 explanation_images 컬럼 추가 (여러 해설 이미지 지원)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # 현재 컬럼 목록 확인
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]

        # explanation_images 컬럼이 없으면 추가
        if 'explanation_images' not in columns:
            cursor.execute('ALTER TABLE questions ADD COLUMN explanation_images TEXT')
            conn.commit()
            print("explanation_images 컬럼이 추가되었습니다.")

            # 기존 explanation_image 데이터를 explanation_images로 마이그레이션
            cursor.execute("UPDATE questions SET explanation_images = explanation_image WHERE explanation_image IS NOT NULL AND explanation_image != ''")
            conn.commit()
            print("기존 해설 이미지 데이터를 마이그레이션했습니다.")
        else:
            print("explanation_images 컬럼이 이미 존재합니다.")
    except Exception as e:
        print(f"해설 이미지 마이그레이션 오류: {e}")
    finally:
        conn.close()

def migrate_add_subject_id():
    """기존 테이블에 subject_id 컬럼 추가 (마이그레이션)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # 현재 컬럼 목록 확인
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]

        # subject_id 컬럼이 없으면 추가
        if 'subject_id' not in columns:
            cursor.execute('ALTER TABLE questions ADD COLUMN subject_id INTEGER')
            conn.commit()
            print("subject_id 컬럼이 추가되었습니다.")
        else:
            print("subject_id 컬럼이 이미 존재합니다.")
    except Exception as e:
        print(f"subject_id 마이그레이션 오류: {e}")
    finally:
        conn.close()

def migrate_add_explanation_video():
    """기존 테이블에 explanation_video 컬럼 추가 (해설 동영상 지원)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # 현재 컬럼 목록 확인
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]

        # explanation_video 컬럼이 없으면 추가
        if 'explanation_video' not in columns:
            cursor.execute('ALTER TABLE questions ADD COLUMN explanation_video TEXT')
            conn.commit()
            print("explanation_video 컬럼이 추가되었습니다.")
        else:
            print("explanation_video 컬럼이 이미 존재합니다.")
    except Exception as e:
        print(f"해설 동영상 마이그레이션 오류: {e}")
    finally:
        conn.close()

def get_max_question_id():
    """현재 최대 문제 ID 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT MAX(id) FROM questions')
    max_id = cursor.fetchone()[0]

    conn.close()
    return max_id if max_id is not None else 0

def add_question(question_text, option_a, option_b, option_c, option_d,
                 correct_answer, explanation='', explanation_image='', exam_set=1,
                 question_image='', option_a_image='', option_b_image='',
                 option_c_image='', option_d_image='', explanation_images='', subject_id=None,
                 explanation_video=''):
    """새 문제 추가"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # explanation_images가 제공되지 않았고 explanation_image가 있으면 사용
    if not explanation_images and explanation_image:
        explanation_images = explanation_image

    # 마지막 문제 번호 다음 번호를 새 ID로 사용
    new_id = get_max_question_id() + 1

    cursor.execute('''
        INSERT INTO questions (id, question_text, question_image, option_a, option_a_image,
                              option_b, option_b_image, option_c, option_c_image,
                              option_d, option_d_image, correct_answer, explanation,
                              explanation_image, explanation_images, exam_set, subject_id,
                              explanation_video)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (new_id, question_text, question_image, option_a, option_a_image,
          option_b, option_b_image, option_c, option_c_image,
          option_d, option_d_image, correct_answer, explanation,
          explanation_image, explanation_images, exam_set, subject_id,
          explanation_video))

    conn.commit()
    conn.close()
    return new_id

def get_all_questions():
    """모든 문제 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM questions ORDER BY id')
    questions = cursor.fetchall()

    conn.close()
    return questions

def get_question_by_id(question_id):
    """ID로 특정 문제 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
    question = cursor.fetchone()

    conn.close()
    return question

def update_question(question_id, question_text, option_a, option_b, option_c,
                   option_d, correct_answer, explanation='', explanation_image='', exam_set=1,
                   question_image='', option_a_image='', option_b_image='',
                   option_c_image='', option_d_image='', explanation_images='', subject_id=None,
                   explanation_video=''):
    """문제 수정"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # explanation_images가 제공되지 않았고 explanation_image가 있으면 사용
    if not explanation_images and explanation_image:
        explanation_images = explanation_image

    cursor.execute('''
        UPDATE questions
        SET question_text = ?, question_image = ?, option_a = ?, option_a_image = ?,
            option_b = ?, option_b_image = ?, option_c = ?, option_c_image = ?,
            option_d = ?, option_d_image = ?, correct_answer = ?, explanation = ?,
            explanation_image = ?, explanation_images = ?, exam_set = ?, subject_id = ?,
            explanation_video = ?
        WHERE id = ?
    ''', (question_text, question_image, option_a, option_a_image,
          option_b, option_b_image, option_c, option_c_image,
          option_d, option_d_image, correct_answer, explanation,
          explanation_image, explanation_images, exam_set, subject_id,
          explanation_video, question_id))

    conn.commit()
    conn.close()

def delete_question(question_id):
    """문제 삭제"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 이미지 파일이 있으면 삭제
    question = get_question_by_id(question_id)
    if question and question['explanation_image']:
        image_path = os.path.join('static', question['explanation_image'])
        if os.path.exists(image_path):
            os.remove(image_path)

    cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))

    conn.commit()
    conn.close()

def get_question_count():
    """전체 문제 수 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM questions')
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_questions_by_exam_set(exam_set):
    """특정 회차의 문제 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM questions WHERE exam_set = ? ORDER BY id', (exam_set,))
    questions = cursor.fetchall()

    conn.close()
    return questions

def get_exam_sets():
    """등록된 모든 회차 번호 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT exam_set FROM questions ORDER BY exam_set')
    exam_sets = [row[0] for row in cursor.fetchall()]

    conn.close()
    return exam_sets

def get_question_count_by_exam_set(exam_set):
    """특정 회차의 문제 수 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM questions WHERE exam_set = ?', (exam_set,))
    count = cursor.fetchone()[0]

    conn.close()
    return count

# ============== 과목 관련 함수 ==============

def add_subject(name, description=''):
    """새 과목 추가"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO subjects (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        subject_id = cursor.lastrowid
        conn.close()
        return subject_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # 중복된 과목명

def get_all_subjects():
    """모든 과목 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM subjects ORDER BY id')
    subjects = cursor.fetchall()

    conn.close()
    return subjects

def get_subject_by_id(subject_id):
    """ID로 특정 과목 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,))
    subject = cursor.fetchone()

    conn.close()
    return subject

def get_subject_by_name(name):
    """이름으로 과목 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM subjects WHERE name = ?', (name,))
    subject = cursor.fetchone()

    conn.close()
    return subject

def update_subject(subject_id, name, description=''):
    """과목 수정"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE subjects SET name = ?, description = ? WHERE id = ?',
                  (name, description, subject_id))
    conn.commit()
    conn.close()

def delete_subject(subject_id):
    """과목 삭제"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
    conn.commit()
    conn.close()

def get_exam_sets_by_subject(subject_id):
    """특정 과목의 모든 회차 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT exam_set FROM questions WHERE subject_id = ? ORDER BY exam_set',
                  (subject_id,))
    exam_sets = [row[0] for row in cursor.fetchall()]

    conn.close()
    return exam_sets

def get_questions_by_subject_and_exam_set(subject_id, exam_set):
    """특정 과목의 특정 회차 문제들 조회"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM questions WHERE subject_id = ? AND exam_set = ? ORDER BY id',
                  (subject_id, exam_set))
    questions = cursor.fetchall()

    conn.close()
    return questions

def update_question_subject(question_id, subject_id):
    """문제의 과목 변경"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE questions SET subject_id = ? WHERE id = ?', (subject_id, question_id))
    conn.commit()
    conn.close()

def update_all_questions_subject(subject_id):
    """모든 문제를 특정 과목으로 할당"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE questions SET subject_id = ?', (subject_id,))
    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()
    return affected_rows

if __name__ == '__main__':
    # 데이터베이스 초기화
    init_db()
    migrate_add_exam_set()
    migrate_add_image_columns()
    migrate_add_explanation_images()
    migrate_add_subject_id()
    migrate_add_explanation_video()
    print("데이터베이스가 초기화되었습니다.")
