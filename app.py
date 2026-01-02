# Created: 2026-01-03 15:30
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
import os
import database as db

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 세션 및 flash 메시지용

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """메인 페이지"""
    question_count = db.get_question_count()
    return render_template('index.html', question_count=question_count)

@app.route('/admin')
def admin():
    """관리자 페이지 - 문제 목록"""
    questions = db.get_all_questions()
    return render_template('admin.html', questions=questions)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_question():
    """문제 추가"""
    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        explanation = request.form.get('explanation', '')

        # 이미지 파일 처리
        explanation_image = ''
        if 'explanation_image' in request.files:
            file = request.files['explanation_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                explanation_image = f'uploads/{filename}'

        db.add_question(question_text, option_a, option_b, option_c, option_d,
                       correct_answer, explanation, explanation_image)
        flash('문제가 성공적으로 추가되었습니다!', 'success')
        return redirect(url_for('admin'))

    return render_template('add_question.html')

@app.route('/admin/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    """문제 수정"""
    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        explanation = request.form.get('explanation', '')

        # 기존 이미지 정보 가져오기
        existing_question = db.get_question_by_id(question_id)
        explanation_image = existing_question['explanation_image']

        # 새 이미지가 업로드되었는지 확인
        if 'explanation_image' in request.files:
            file = request.files['explanation_image']
            if file and file.filename and allowed_file(file.filename):
                # 기존 이미지 삭제
                if explanation_image:
                    old_image_path = os.path.join('static', explanation_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # 새 이미지 저장
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                explanation_image = f'uploads/{filename}'

        db.update_question(question_id, question_text, option_a, option_b, option_c,
                          option_d, correct_answer, explanation, explanation_image)
        flash('문제가 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('admin'))

    question = db.get_question_by_id(question_id)
    return render_template('edit_question.html', question=question)

@app.route('/admin/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    """문제 삭제"""
    db.delete_question(question_id)
    flash('문제가 성공적으로 삭제되었습니다!', 'success')
    return redirect(url_for('admin'))

@app.route('/exam')
def exam():
    """시험 페이지"""
    questions = db.get_all_questions()
    if not questions:
        flash('등록된 문제가 없습니다. 관리자 페이지에서 문제를 추가해주세요.', 'warning')
        return redirect(url_for('index'))
    return render_template('exam.html', questions=questions)

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    """시험 제출 및 채점"""
    data = request.get_json()
    answers = data.get('answers', {})

    questions = db.get_all_questions()
    results = []
    correct_count = 0

    for question in questions:
        question_id = str(question['id'])
        user_answer = answers.get(question_id, '')
        is_correct = user_answer == question['correct_answer']

        if is_correct:
            correct_count += 1

        results.append({
            'id': question['id'],
            'question_text': question['question_text'],
            'user_answer': user_answer,
            'correct_answer': question['correct_answer'],
            'is_correct': is_correct,
            'explanation': question['explanation'],
            'explanation_image': question['explanation_image'],
            'options': {
                'A': question['option_a'],
                'B': question['option_b'],
                'C': question['option_c'],
                'D': question['option_d']
            }
        })

    total_questions = len(questions)
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0

    return jsonify({
        'score': score,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'results': results
    })

if __name__ == '__main__':
    # 업로드 폴더 생성
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # 데이터베이스 초기화
    db.init_db()
    print("CBT 시스템을 시작합니다...")
    print("브라우저에서 http://127.0.0.1:5000 을 열어주세요.")
    app.run(debug=True)
