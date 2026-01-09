# Created: 2026-01-03 15:30
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
import os
import database as db

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 세션 및 flash 메시지용

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB 제한 (동영상 지원)

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    """허용된 이미지 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_video(filename):
    """허용된 동영상 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

@app.route('/')
def index():
    """메인 페이지"""
    question_count = db.get_question_count()
    subjects = db.get_all_subjects()

    # 각 과목별 회차 정보
    subject_info = []
    for subject in subjects:
        exam_sets = db.get_exam_sets_by_subject(subject['id'])
        exam_set_list = []
        for exam_set in exam_sets:
            questions = db.get_questions_by_subject_and_exam_set(subject['id'], exam_set)
            exam_set_list.append({'set_number': exam_set, 'count': len(questions)})

        subject_info.append({
            'id': subject['id'],
            'name': subject['name'],
            'description': subject['description'],
            'exam_sets': exam_set_list
        })

    return render_template('index.html',
                         question_count=question_count,
                         subject_info=subject_info)

@app.route('/admin')
def admin():
    """관리자 페이지 - 문제 목록"""
    subject_id = request.args.get('subject_id', type=int)
    subjects = db.get_all_subjects()

    if subject_id:
        # 특정 과목의 문제만 조회
        exam_sets = db.get_exam_sets_by_subject(subject_id)
        questions_by_set = {}
        for exam_set in exam_sets:
            questions_by_set[exam_set] = db.get_questions_by_subject_and_exam_set(subject_id, exam_set)
        questions = []
        for q_list in questions_by_set.values():
            questions.extend(q_list)
        current_subject = db.get_subject_by_id(subject_id)
    else:
        # 모든 문제 조회
        questions = db.get_all_questions()
        exam_sets = db.get_exam_sets()
        questions_by_set = {}
        for exam_set in exam_sets:
            questions_by_set[exam_set] = db.get_questions_by_exam_set(exam_set)
        current_subject = None

    return render_template('admin.html',
                         questions=questions,
                         questions_by_set=questions_by_set,
                         exam_sets=exam_sets,
                         subjects=subjects,
                         current_subject=current_subject,
                         current_subject_id=subject_id)

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
        subject_id = request.form.get('subject_id', None)
        if subject_id:
            subject_id = int(subject_id)

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

        # 해설 동영상 처리 (여러 개 지원, 최대 5개)
        explanation_video = ''
        explanation_videos_list = []

        if 'explanation_videos' in request.files:
            files = request.files.getlist('explanation_videos')

            # 최대 5개 제한 검증
            if len(files) > 5:
                flash('해설 동영상은 최대 5개까지만 업로드할 수 있습니다.', 'error')
                return redirect(url_for('add_question'))

            for file in files:
                if file and file.filename and allowed_video(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    explanation_videos_list.append(f'uploads/{filename}')

        # 여러 동영상을 파이프(|)로 구분하여 저장
        explanation_videos = '|'.join(explanation_videos_list) if explanation_videos_list else ''

        # 하위 호환성: 첫 번째 동영상을 explanation_video로도 저장
        if explanation_videos_list:
            explanation_video = explanation_videos_list[0]

        db.add_question(question_text, option_a, option_b, option_c, option_d,
                       correct_answer, explanation, explanation_image, exam_set,
                       question_image, option_a_image, option_b_image,
                       option_c_image, option_d_image, explanation_images, subject_id,
                       explanation_video, explanation_videos)
        flash('문제가 성공적으로 추가되었습니다!', 'success')
        # 추가 후 해당 과목 페이지로 돌아가기
        if subject_id:
            return redirect(url_for('admin', subject_id=subject_id))
        return redirect(url_for('admin'))

    subjects = db.get_all_subjects()
    default_subject_id = request.args.get('subject_id', type=int)
    return render_template('add_question.html', subjects=subjects, default_subject_id=default_subject_id)

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
        subject_id = request.form.get('subject_id', None)
        if subject_id:
            subject_id = int(subject_id)

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

        # 해설 동영상 업데이트 (여러 개 지원, 최대 5개)
        explanation_video = existing_question['explanation_video'] or ''
        explanation_videos = existing_question['explanation_videos'] or ''
        explanation_videos_list = explanation_videos.split('|') if explanation_videos else []
        # 빈 문자열 제거
        explanation_videos_list = [v for v in explanation_videos_list if v]

        if 'explanation_videos' in request.files:
            files = request.files.getlist('explanation_videos')
            new_videos = []

            # 최대 5개 제한 검증 (기존 동영상 + 새 동영상)
            total_count = len(explanation_videos_list) + len([f for f in files if f and f.filename])
            if total_count > 5:
                flash(f'해설 동영상은 최대 5개까지만 추가할 수 있습니다. (현재: {len(explanation_videos_list)}개)', 'error')
                return redirect(url_for('edit_question', question_id=question_id))

            for file in files:
                if file and file.filename and allowed_video(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    new_videos.append(f'uploads/{filename}')

            # 새 동영상이 있으면 기존 동영상에 추가
            if new_videos:
                explanation_videos_list.extend(new_videos)

        # 여러 동영상을 파이프(|)로 구분하여 저장
        explanation_videos = '|'.join(explanation_videos_list) if explanation_videos_list else ''

        # 하위 호환성: 첫 번째 동영상을 explanation_video로도 저장
        if explanation_videos_list:
            explanation_video = explanation_videos_list[0]
        else:
            explanation_video = ''

        db.update_question(question_id, question_text, option_a, option_b, option_c,
                          option_d, correct_answer, explanation, explanation_image, exam_set,
                          question_image, option_a_image, option_b_image,
                          option_c_image, option_d_image, explanation_images, subject_id,
                          explanation_video, explanation_videos)
        flash('문제가 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('admin'))

    question = db.get_question_by_id(question_id)
    subjects = db.get_all_subjects()
    return render_template('edit_question.html', question=question, subjects=subjects)

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

        # 이미지/동영상 타입별 처리
        image_field_map = {
            'question': 'question_image',
            'option_a': 'option_a_image',
            'option_b': 'option_b_image',
            'option_c': 'option_c_image',
            'option_d': 'option_d_image',
            'explanation': 'explanation_image',
            'explanation_video': 'explanation_video'
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

@app.route('/admin/delete_explanation_video/<int:question_id>/<int:video_index>', methods=['POST'])
def delete_explanation_video(question_id, video_index):
    """해설 동영상 삭제 (특정 인덱스)"""
    try:
        # 문제 정보 가져오기
        question = db.get_question_by_id(question_id)
        if not question:
            return jsonify({'success': False, 'message': '문제를 찾을 수 없습니다.'}), 404

        # 현재 해설 동영상들 가져오기
        explanation_videos = question['explanation_videos'] or ''
        if not explanation_videos:
            return jsonify({'success': False, 'message': '삭제할 동영상이 없습니다.'}), 404

        videos_list = [v for v in explanation_videos.split('|') if v]

        # 인덱스 유효성 검사
        if video_index < 0 or video_index >= len(videos_list):
            return jsonify({'success': False, 'message': '잘못된 동영상 인덱스입니다.'}), 400

        # 삭제할 동영상 경로
        video_to_delete = videos_list[video_index]

        # 파일 삭제
        file_path = os.path.join('static', video_to_delete)
        if os.path.exists(file_path):
            os.remove(file_path)

        # 리스트에서 제거
        videos_list.pop(video_index)

        # 업데이트된 동영상 목록을 파이프로 구분하여 저장
        new_explanation_videos = '|'.join(videos_list) if videos_list else ''

        # DB 업데이트
        conn = db.sqlite3.connect(db.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE questions SET explanation_videos = ?, explanation_video = ? WHERE id = ?',
                      (new_explanation_videos, videos_list[0] if videos_list else '', question_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '해설 동영상이 삭제되었습니다.'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500

@app.route('/exam')
def exam():
    """시험 페이지"""
    subject_id = request.args.get('subject_id', type=int)
    exam_set = request.args.get('exam_set', type=int)

    if subject_id and exam_set:
        # 특정 과목의 특정 회차 문제 가져오기
        subject = db.get_subject_by_id(subject_id)
        if not subject:
            flash('과목을 찾을 수 없습니다.', 'warning')
            return redirect(url_for('index'))

        questions = db.get_questions_by_subject_and_exam_set(subject_id, exam_set)
        if not questions:
            flash(f'{subject["name"]} {exam_set}회 모의고사에 등록된 문제가 없습니다.', 'warning')
            return redirect(url_for('index'))
        exam_title = f'{subject["name"]} 모의고사 {exam_set}회'
    elif exam_set:
        # 회차만 지정된 경우 (하위 호환성)
        questions = db.get_questions_by_exam_set(exam_set)
        if not questions:
            flash(f'{exam_set}회 모의고사에 등록된 문제가 없습니다.', 'warning')
            return redirect(url_for('index'))
        exam_title = f'모의고사 {exam_set}회'
    else:
        # 지정되지 않은 경우 모든 문제
        questions = db.get_all_questions()
        if not questions:
            flash('등록된 문제가 없습니다. 관리자 페이지에서 문제를 추가해주세요.', 'warning')
            return redirect(url_for('index'))
        exam_title = 'CBT 모의고사'

    return render_template('exam.html',
                         questions=questions,
                         exam_title=exam_title,
                         exam_set=exam_set,
                         subject_id=subject_id)

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

@app.route('/admin/subjects')
def subjects():
    """과목 관리 페이지"""
    subjects = db.get_all_subjects()

    # 각 과목별 문제 수 계산
    subject_stats = []
    for subject in subjects:
        exam_sets = db.get_exam_sets_by_subject(subject['id'])
        question_count = 0
        for exam_set in exam_sets:
            questions = db.get_questions_by_subject_and_exam_set(subject['id'], exam_set)
            question_count += len(questions)
        subject_stats.append({
            'id': subject['id'],
            'name': subject['name'],
            'description': subject['description'],
            'exam_set_count': len(exam_sets),
            'question_count': question_count
        })

    return render_template('subjects.html', subjects=subject_stats)

@app.route('/admin/subjects/add', methods=['GET', 'POST'])
def add_subject():
    """과목 추가"""
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('과목명을 입력해주세요.', 'error')
            return redirect(url_for('add_subject'))

        subject_id = db.add_subject(name, description)
        if subject_id:
            flash(f'"{name}" 과목이 추가되었습니다.', 'success')
            return redirect(url_for('subjects'))
        else:
            flash('이미 존재하는 과목명입니다.', 'error')
            return redirect(url_for('add_subject'))

    return render_template('add_subject.html')

@app.route('/admin/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    """과목 수정"""
    subject = db.get_subject_by_id(subject_id)
    if not subject:
        flash('과목을 찾을 수 없습니다.', 'error')
        return redirect(url_for('subjects'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('과목명을 입력해주세요.', 'error')
            return redirect(url_for('edit_subject', subject_id=subject_id))

        # 중복 체크 (자기 자신 제외)
        existing = db.get_subject_by_name(name)
        if existing and existing['id'] != subject_id:
            flash('이미 존재하는 과목명입니다.', 'error')
            return redirect(url_for('edit_subject', subject_id=subject_id))

        db.update_subject(subject_id, name, description)
        flash(f'"{name}" 과목이 수정되었습니다.', 'success')
        return redirect(url_for('subjects'))

    return render_template('edit_subject.html', subject=subject)

@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    """과목 삭제"""
    subject = db.get_subject_by_id(subject_id)
    if not subject:
        flash('과목을 찾을 수 없습니다.', 'error')
        return redirect(url_for('subjects'))

    # 해당 과목에 문제가 있는지 확인
    exam_sets = db.get_exam_sets_by_subject(subject_id)
    has_questions = any(db.get_questions_by_subject_and_exam_set(subject_id, es) for es in exam_sets)

    if has_questions:
        flash(f'"{subject["name"]}" 과목에 문제가 있어 삭제할 수 없습니다. 먼저 문제를 삭제하거나 다른 과목으로 이동해주세요.', 'error')
        return redirect(url_for('subjects'))

    db.delete_subject(subject_id)
    flash(f'"{subject["name"]}" 과목이 삭제되었습니다.', 'success')
    return redirect(url_for('subjects'))

if __name__ == '__main__':
    # 업로드 폴더 생성
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # 데이터베이스 초기화 및 마이그레이션
    db.init_db()
    db.migrate_add_exam_set()
    db.migrate_add_image_columns()
    db.migrate_add_explanation_images()
    db.migrate_add_subject_id()
    db.migrate_add_explanation_video()
    db.migrate_add_explanation_videos()
    print("CBT 시스템을 시작합니다...")
    print("브라우저에서 http://127.0.0.1:5000 을 열어주세요.")
    print("같은 네트워크의 다른 컴퓨터에서는 http://[이 컴퓨터의 IP]:5000 으로 접속하세요.")
    app.run(debug=True, host='0.0.0.0')
