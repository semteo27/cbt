# Created: 2026-01-03 15:30
import sqlite3
import os

DATABASE_PATH = 'cbt_questions.db'

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 문제 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            explanation_image TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_question(question_text, option_a, option_b, option_c, option_d,
                 correct_answer, explanation='', explanation_image=''):
    """새 문제 추가"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO questions (question_text, option_a, option_b, option_c,
                              option_d, correct_answer, explanation, explanation_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (question_text, option_a, option_b, option_c, option_d,
          correct_answer, explanation, explanation_image))

    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return question_id

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
                   option_d, correct_answer, explanation='', explanation_image=''):
    """문제 수정"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE questions
        SET question_text = ?, option_a = ?, option_b = ?, option_c = ?,
            option_d = ?, correct_answer = ?, explanation = ?, explanation_image = ?
        WHERE id = ?
    ''', (question_text, option_a, option_b, option_c, option_d,
          correct_answer, explanation, explanation_image, question_id))

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

if __name__ == '__main__':
    # 데이터베이스 초기화
    init_db()
    print("데이터베이스가 초기화되었습니다.")
