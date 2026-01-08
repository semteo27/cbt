# Created: 2026-01-08 00:00
"""컴퓨터일반 과목 등록 및 기존 문제 할당"""

from database import add_subject, get_subject_by_name, update_all_questions_subject

def setup_computer_general_subject():
    """컴퓨터일반 과목을 등록하고 모든 문제를 할당"""

    # 컴퓨터일반 과목이 이미 있는지 확인
    subject = get_subject_by_name('컴퓨터일반')

    if subject:
        print(f"'컴퓨터일반' 과목이 이미 등록되어 있습니다. (ID: {subject['id']})")
        subject_id = subject['id']
    else:
        # 컴퓨터일반 과목 추가
        subject_id = add_subject('컴퓨터일반', '컴퓨터일반 과목 모의고사')
        if subject_id:
            print(f"'컴퓨터일반' 과목이 등록되었습니다. (ID: {subject_id})")
        else:
            print("과목 등록에 실패했습니다.")
            return None

    # 모든 문제를 컴퓨터일반 과목에 할당
    affected_rows = update_all_questions_subject(subject_id)
    print(f"{affected_rows}개의 문제가 '컴퓨터일반' 과목에 할당되었습니다.")

    return subject_id

if __name__ == '__main__':
    setup_computer_general_subject()
    print("\n과목 설정이 완료되었습니다.")
