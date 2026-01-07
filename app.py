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
    exam_sets = db.get_exam_sets()

    # 각 회차별 문제 수 조회
    exam_set_info = []
    for exam_set in exam_sets:
        count = db.get_question_count_by_exam_set(exam_set)
        exam_set_info.append({'set_number': exam_set, 'count': count})

    return render_template('index.html',
                         question_count=question_count,
                         exam_set_info=exam_set_info)

@app.route('/admin')
def admin():
    """관리자 페이지 - 문제 목록"""
    questions = db.get_all_questions()
    exam_sets = db.get_exam_sets()

    # 회차별로 문제 그룹화
    questions_by_set = {}
    for exam_set in exam_sets:
        questions_by_set[exam_set] = db.get_questions_by_exam_set(exam_set)

    return render_template('admin.html',
                         questions=questions,
                         questions_by_set=questions_by_set,
                         exam_sets=exam_sets)

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
        exam_set = int(request.form.get('exam_set', 1))

        # 문제 이미지 처리
        question_image = ''
        if 'question_image' in request.files:
            file = request.files['question_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                question_image = f'uploads/{filename}'

        # 보기 A 이미지 처리
        option_a_image = ''
        if 'option_a_image' in request.files:
            file = request.files['option_a_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_a_image = f'uploads/{filename}'

        # 보기 B 이미지 처리
        option_b_image = ''
        if 'option_b_image' in request.files:
            file = request.files['option_b_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_b_image = f'uploads/{filename}'

        # 보기 C 이미지 처리
        option_c_image = ''
        if 'option_c_image' in request.files:
            file = request.files['option_c_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_c_image = f'uploads/{filename}'

        # 보기 D 이미지 처리
        option_d_image = ''
        if 'option_d_image' in request.files:
            file = request.files['option_d_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_d_image = f'uploads/{filename}'

        # 해설 이미지 처리 (여러 개 지원, 최대 5개)
        explanation_image = ''
        explanation_images_list = []

        if 'explanation_images' in request.files:
            files = request.files.getlist('explanation_images')

            # 최대 5개 제한 검증
            if len(files) > 5:
                flash('해설 이미지는 최대 5개까지만 업로드할 수 있습니다.', 'error')
                return redirect(url_for('add_question'))

            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    explanation_images_list.append(f'uploads/{filename}')

        # 여러 이미지를 파이프(|)로 구분하여 저장
        explanation_images = '|'.join(explanation_images_list) if explanation_images_list else ''

        # 하위 호환성: 첫 번째 이미지를 explanation_image로도 저장
        if explanation_images_list:
            explanation_image = explanation_images_list[0]

        db.add_question(question_text, option_a, option_b, option_c, option_d,
                       correct_answer, explanation, explanation_image, exam_set,
                       question_image, option_a_image, option_b_image,
                       option_c_image, option_d_image, explanation_images)
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
        exam_set = int(request.form.get('exam_set', 1))

        # 기존 이미지 정보 가져오기
        existing_question = db.get_question_by_id(question_id)
        question_image = existing_question['question_image'] or ''
        option_a_image = existing_question['option_a_image'] or ''
        option_b_image = existing_question['option_b_image'] or ''
        option_c_image = existing_question['option_c_image'] or ''
        option_d_image = existing_question['option_d_image'] or ''
        explanation_image = existing_question['explanation_image'] or ''

        # 문제 이미지 업데이트
        if 'question_image' in request.files:
            file = request.files['question_image']
            if file and file.filename and allowed_file(file.filename):
                if question_image:
                    old_path = os.path.join('static', question_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                question_image = f'uploads/{filename}'

        # 보기 A 이미지 업데이트
        if 'option_a_image' in request.files:
            file = request.files['option_a_image']
            if file and file.filename and allowed_file(file.filename):
                if option_a_image:
                    old_path = os.path.join('static', option_a_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_a_image = f'uploads/{filename}'

        # 보기 B 이미지 업데이트
        if 'option_b_image' in request.files:
            file = request.files['option_b_image']
            if file and file.filename and allowed_file(file.filename):
                if option_b_image:
                    old_path = os.path.join('static', option_b_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_b_image = f'uploads/{filename}'

        # 보기 C 이미지 업데이트
        if 'option_c_image' in request.files:
            file = request.files['option_c_image']
            if file and file.filename and allowed_file(file.filename):
                if option_c_image:
                    old_path = os.path.join('static', option_c_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_c_image = f'uploads/{filename}'

        # 보기 D 이미지 업데이트
        if 'option_d_image' in request.files:
            file = request.files['option_d_image']
            if file and file.filename and allowed_file(file.filename):
                if option_d_image:
                    old_path = os.path.join('static', option_d_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                option_d_image = f'uploads/{filename}'

        # 해설 이미지 업데이트 (여러 개 지원, 최대 5개)
        explanation_images = existing_question['explanation_images'] or ''
        explanation_images_list = explanation_images.split('|') if explanation_images else []

        if 'explanation_images' in request.files:
            files = request.files.getlist('explanation_images')
            new_images = []

            # 최대 5개 제한 검증 (기존 이미지 + 새 이미지)
            total_count = len(explanation_images_list) + len(files)
            if total_count > 5:
                flash(f'해설 이미지는 최대 5개까지만 추가할 수 있습니다. (현재: {len(explanation_images_list)}개, 선택: {len(files)}개)', 'error')
                return redirect(url_for('edit_question', question_id=question_id))

            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    new_images.append(f'uploads/{filename}')

            # 새 이미지가 있으면 기존 이미지에 추가
            if new_images:
                explanation_images_list.extend(new_images)

        # 여러 이미지를 파이프(|)로 구분하여 저장
        explanation_images = '|'.join(explanation_images_list) if explanation_images_list else ''

        # 하위 호환성: 첫 번째 이미지를 explanation_image로도 저장
        if explanation_images_list:
            explanation_image = explanation_images_list[0]
        else:
            explanation_image = ''

        db.update_question(question_id, question_text, option_a, option_b, option_c,
                          option_d, correct_answer, explanation, explanation_image, exam_set,
                          question_image, option_a_image, option_b_image,
                          option_c_image, option_d_image, explanation_images)
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

@app.route('/admin/delete_image/<int:question_id>/<image_type>', methods=['POST'])
def delete_image(question_id, image_type):
    """이미지 삭제"""
    try:
        # 문제 정보 가져오기
        question = db.get_question_by_id(question_id)
        if not question:
            return jsonify({'success': False, 'message': '문제를 찾을 수 없습니다.'}), 404

        # 이미지 타입별 처리
        image_field_map = {
            'question': 'question_image',
            'option_a': 'option_a_image',
            'option_b': 'option_b_image',
            'option_c': 'option_c_image',
            'option_d': 'option_d_image',
            'explanation': 'explanation_image'
        }

        if image_type not in image_field_map:
            return jsonify({'success': False, 'message': '잘못된 이미지 타입입니다.'}), 400

        image_path = question[image_field_map[image_type]]

        if not image_path:
            return jsonify({'success': False, 'message': '삭제할 이미지가 없습니다.'}), 404

        # 파일 삭제
        file_path = os.path.join('static', image_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        # DB 업데이트 - 해당 이미지 필드를 빈 문자열로 설정
        conn = db.sqlite3.connect(db.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE questions SET {image_field_map[image_type]} = "" WHERE id = ?', (question_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '이미지가 삭제되었습니다.'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500

@app.route('/admin/delete_explanation_image/<int:question_id>/<int:image_index>', methods=['POST'])
def delete_explanation_image(question_id, image_index):
    """해설 이미지 삭제 (특정 인덱스)"""
    try:
        # 문제 정보 가져오기
        question = db.get_question_by_id(question_id)
        if not question:
            return jsonify({'success': False, 'message': '문제를 찾을 수 없습니다.'}), 404

        # 현재 해설 이미지들 가져오기
        explanation_images = question['explanation_images'] or ''
        if not explanation_images:
            return jsonify({'success': False, 'message': '삭제할 이미지가 없습니다.'}), 404

        images_list = explanation_images.split('|')

        # 인덱스 유효성 검사
        if image_index < 0 or image_index >= len(images_list):
            return jsonify({'success': False, 'message': '잘못된 이미지 인덱스입니다.'}), 400

        # 삭제할 이미지 경로
        image_to_delete = images_list[image_index]

        # 파일 삭제
        file_path = os.path.join('static', image_to_delete)
        if os.path.exists(file_path):
            os.remove(file_path)

        # 리스트에서 제거
        images_list.pop(image_index)

        # 업데이트된 이미지 목록을 파이프로 구분하여 저장
        new_explanation_images = '|'.join(images_list) if images_list else ''

        # DB 업데이트
        conn = db.sqlite3.connect(db.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE questions SET explanation_images = ?, explanation_image = ? WHERE id = ?',
                      (new_explanation_images, images_list[0] if images_list else '', question_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '해설 이미지가 삭제되었습니다.'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500

@app.route('/exam')
def exam():
    """시험 페이지"""
    exam_set = request.args.get('exam_set', type=int)

    if exam_set:
        # 특정 회차의 문제만 가져오기
        questions = db.get_questions_by_exam_set(exam_set)
        if not questions:
            flash(f'{exam_set}회 모의고사에 등록된 문제가 없습니다.', 'warning')
            return redirect(url_for('index'))
        exam_title = f'모의고사 {exam_set}회'
    else:
        # 회차가 지정되지 않은 경우 모든 문제
        questions = db.get_all_questions()
        if not questions:
            flash('등록된 문제가 없습니다. 관리자 페이지에서 문제를 추가해주세요.', 'warning')
            return redirect(url_for('index'))
        exam_title = 'CBT 모의고사'

    return render_template('exam.html',
                         questions=questions,
                         exam_title=exam_title,
                         exam_set=exam_set)

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

    # 데이터베이스 초기화 및 마이그레이션
    db.init_db()
    db.migrate_add_exam_set()
    db.migrate_add_image_columns()
    db.migrate_add_explanation_images()
    print("CBT 시스템을 시작합니다...")
    print("브라우저에서 http://127.0.0.1:5000 을 열어주세요.")
    print("같은 네트워크의 다른 컴퓨터에서는 http://[이 컴퓨터의 IP]:5000 으로 접속하세요.")
    app.run(debug=True, host='0.0.0.0')
