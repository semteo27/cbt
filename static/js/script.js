// Created: 2026-01-03 15:30

document.addEventListener('DOMContentLoaded', function() {
    const examForm = document.getElementById('exam-form');

    if (examForm) {
        examForm.addEventListener('submit', handleExamSubmit);
    }
});

async function handleExamSubmit(event) {
    event.preventDefault();

    // 답안 수집
    const formData = new FormData(event.target);
    const answers = {};

    for (let [key, value] of formData.entries()) {
        const questionId = key.replace('question_', '');
        answers[questionId] = value;
    }

    // 모든 문제에 답했는지 확인
    const allQuestions = document.querySelectorAll('.question-card');
    if (Object.keys(answers).length < allQuestions.length) {
        alert('모든 문제에 답해주세요!');
        return;
    }

    try {
        // 서버에 답안 제출
        const response = await fetch('/submit_exam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answers: answers })
        });

        if (!response.ok) {
            throw new Error('채점 중 오류가 발생했습니다.');
        }

        const result = await response.json();
        displayResults(result);

    } catch (error) {
        console.error('Error:', error);
        alert('채점 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
}

function displayResults(result) {
    // 시험 섹션 숨기기
    document.getElementById('exam-section').style.display = 'none';

    // 결과 섹션 표시
    const resultSection = document.getElementById('result-section');
    resultSection.style.display = 'block';

    // 점수 표시
    document.getElementById('score-percentage').textContent = Math.round(result.score);
    document.getElementById('correct-count').textContent = result.correct_count;
    document.getElementById('total-count').textContent = result.total_questions;

    // 결과 목록 생성
    const resultsList = document.getElementById('results-list');
    resultsList.innerHTML = '';

    result.results.forEach((item, index) => {
        const resultCard = createResultCard(item, index + 1);
        resultsList.appendChild(resultCard);
    });

    // 페이지 상단으로 스크롤
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function createResultCard(item, questionNumber) {
    const card = document.createElement('div');
    card.className = `result-card ${item.is_correct ? 'correct' : 'incorrect'}`;

    const statusBadge = document.createElement('div');
    statusBadge.className = `result-status ${item.is_correct ? 'correct' : 'incorrect'}`;
    statusBadge.textContent = item.is_correct ? '✓ 정답' : '✗ 오답';

    const questionNumberDiv = document.createElement('div');
    questionNumberDiv.className = 'question-number';
    questionNumberDiv.textContent = `문제 ${questionNumber}`;

    const questionText = document.createElement('div');
    questionText.className = 'question-text';
    questionText.textContent = item.question_text;

    const answerComparison = document.createElement('div');
    answerComparison.className = 'answer-comparison';

    const userAnswerBox = document.createElement('div');
    userAnswerBox.className = 'answer-box user-answer';
    userAnswerBox.innerHTML = `
        <h4>선택한 답</h4>
        <div class="answer-value">${item.user_answer || '미선택'}: ${item.options[item.user_answer] || ''}</div>
    `;

    const correctAnswerBox = document.createElement('div');
    correctAnswerBox.className = 'answer-box correct-answer';
    correctAnswerBox.innerHTML = `
        <h4>정답</h4>
        <div class="answer-value">${item.correct_answer}: ${item.options[item.correct_answer]}</div>
    `;

    answerComparison.appendChild(userAnswerBox);
    answerComparison.appendChild(correctAnswerBox);

    card.appendChild(statusBadge);
    card.appendChild(questionNumberDiv);
    card.appendChild(questionText);
    card.appendChild(answerComparison);

    // 해설 섹션 추가
    if (item.explanation || item.explanation_image) {
        const explanationSection = createExplanationSection(item);
        card.appendChild(explanationSection);
    }

    return card;
}

function createExplanationSection(item) {
    const section = document.createElement('div');
    section.className = 'explanation-section';

    const toggleButton = document.createElement('button');
    toggleButton.className = 'explanation-toggle';
    toggleButton.textContent = '해설 보기';
    toggleButton.onclick = function() {
        const content = this.nextElementSibling;
        if (content.classList.contains('show')) {
            content.classList.remove('show');
            this.textContent = '해설 보기';
        } else {
            content.classList.add('show');
            this.textContent = '해설 숨기기';
        }
    };

    const content = document.createElement('div');
    content.className = 'explanation-content';

    if (item.explanation) {
        const explanationText = document.createElement('div');
        explanationText.className = 'explanation-text';
        explanationText.textContent = item.explanation;
        content.appendChild(explanationText);
    }

    if (item.explanation_image) {
        const explanationImage = document.createElement('img');
        explanationImage.className = 'explanation-image';
        explanationImage.src = '/static/' + item.explanation_image;
        explanationImage.alt = '해설 이미지';
        content.appendChild(explanationImage);
    }

    section.appendChild(toggleButton);
    section.appendChild(content);

    return section;
}

// 알림 메시지 자동 숨김
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
