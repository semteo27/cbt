# Created: 2026-01-09 00:00
"""EXCEL 과목 등록"""

from database import add_subject, get_subject_by_name, get_all_subjects

def add_excel_subject():
    """EXCEL 과목을 등록"""

    # 현재 등록된 과목 확인
    print("현재 등록된 과목:")
    subjects = get_all_subjects()
    for subject in subjects:
        print(f"  ID: {subject['id']}, 이름: {subject['name']}, 설명: {subject['description']}")
    print()

    # EXCEL 과목이 이미 있는지 확인
    subject = get_subject_by_name('EXCEL')

    if subject:
        print(f"'EXCEL' 과목이 이미 등록되어 있습니다. (ID: {subject['id']})")
        return subject['id']
    else:
        # EXCEL 과목 추가
        subject_id = add_subject('EXCEL', 'EXCEL 과목 모의고사')
        if subject_id:
            print(f"'EXCEL' 과목이 등록되었습니다. (ID: {subject_id})")
        else:
            print("과목 등록에 실패했습니다.")
            return None

    return subject_id

if __name__ == '__main__':
    add_excel_subject()
    print("\n과목 추가가 완료되었습니다.")

    # 추가 후 전체 과목 목록 확인
    print("\n최종 과목 목록:")
    subjects = get_all_subjects()
    for subject in subjects:
        print(f"  ID: {subject['id']}, 이름: {subject['name']}, 설명: {subject['description']}")
