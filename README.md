# CBT 모의고사 시스템

웹 기반 4지선다 모의고사 시스템입니다.

## 주요 기능

- 4지선다 문제 출제 및 응시
- 문제 및 보기 추가, 삭제, 수정
- 해설 보기/숨김 기능
- 해설 이미지 등록 및 표시
- SQLite 데이터베이스로 문제 관리
- 자동 채점 및 결과 확인

## 설치 방법

### 1. 의존성 패키지 설치

```bash
cd CBT
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
python app.py
```

실행 후 브라우저에서 `http://127.0.0.1:5000` 을 열어주세요.

## 사용 방법

### 문제 관리하기

1. 메인 페이지에서 **"문제 관리"** 버튼 클릭
2. **"새 문제 추가"** 버튼을 눌러 문제 등록
3. 문제, 4개의 보기, 정답, 해설 입력
4. 해설 이미지가 필요하면 이미지 파일 업로드 (선택사항)
5. **"문제 추가"** 버튼 클릭

### 문제 수정/삭제

- 문제 관리 페이지에서 각 문제 옆의 **"수정"** 또는 **"삭제"** 버튼 사용

### 시험 보기

1. 메인 페이지에서 **"시험 시작"** 버튼 클릭
2. 각 문제의 보기 중 하나를 선택
3. 모든 문제에 답한 후 **"답안 제출"** 버튼 클릭
4. 자동 채점 결과 확인

### 해설 확인

- 채점 결과 화면에서 각 문제의 **"해설 보기"** 버튼 클릭
- 해설 텍스트와 이미지 확인
- **"해설 숨기기"** 버튼으로 해설 숨김

## 프로젝트 구조

```
CBT/
├── app.py                 # Flask 메인 애플리케이션
├── database.py            # SQLite 데이터베이스 관리
├── requirements.txt       # 필요한 패키지 목록
├── cbt_questions.db       # SQLite 데이터베이스 파일 (자동 생성)
├── templates/             # HTML 템플릿
│   ├── index.html        # 메인 페이지
│   ├── admin.html        # 문제 관리 페이지
│   ├── add_question.html # 문제 추가 페이지
│   ├── edit_question.html# 문제 수정 페이지
│   └── exam.html         # 시험 페이지
└── static/               # 정적 파일
    ├── css/
    │   └── style.css     # 스타일시트
    ├── js/
    │   └── script.js     # JavaScript 기능
    └── uploads/          # 업로드된 이미지 저장 폴더
```

## 기술 스택

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **File Upload**: Werkzeug

## 지원 이미지 형식

PNG, JPG, JPEG, GIF (최대 16MB)

## 라이선스

바이브코딩 &copy; 2026
