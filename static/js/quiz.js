// Get session ID from URL
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');

if (!sessionId) {
    window.location.href = '/';
}

// DOM elements
const progress = document.getElementById('progress');
const scoreBadge = document.getElementById('scoreBadge');
const score = document.getElementById('score');
const questionText = document.getElementById('questionText');
const multipleChoiceOptions = document.getElementById('multipleChoiceOptions');
const fillBlankInput = document.getElementById('fillBlankInput');
const fillBlankAnswer = document.getElementById('fillBlankAnswer');
const submitBtn = document.getElementById('submitBtn');
const feedbackPanel = document.getElementById('feedbackPanel');
const correctFeedback = document.getElementById('correctFeedback');
const incorrectFeedback = document.getElementById('incorrectFeedback');
const correctAnswer = document.getElementById('correctAnswer');
const explanation = document.getElementById('explanation');
const nextBtn = document.getElementById('nextBtn');
const loadingIndicator = document.getElementById('loadingIndicator');

// State
let currentQuestionNum = 0;
let currentQuestion = null;
let totalQuestions = 0;
let currentScore = 0;

// Event listeners
submitBtn.addEventListener('click', handleSubmit);
nextBtn.addEventListener('click', loadNextQuestion);
fillBlankAnswer.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSubmit();
});

// Initialize
loadQuestion(0);

async function loadQuestion(questionNum) {
    showLoading(true);
    hideFeedback();

    try {
        const response = await fetch(`/question/${sessionId}/${questionNum}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load question');
        }

        currentQuestion = data;
        currentQuestionNum = questionNum;
        totalQuestions = data.total_questions;
        currentScore = data.current_score;

        displayQuestion(data);
        updateHeader();
        showLoading(false);

    } catch (error) {
        console.error('Load question error:', error);
        alert('Failed to load question: ' + error.message);
        window.location.href = '/';
    }
}

function displayQuestion(data) {
    questionText.textContent = data.question;

    if (data.type === 'multiple_choice') {
        multipleChoiceOptions.innerHTML = '';
        multipleChoiceOptions.classList.remove('hidden');
        fillBlankInput.classList.add('hidden');

        data.options.forEach((option, index) => {
            const button = document.createElement('button');
            button.className = 'answer-option w-full p-4 border-2 border-gray-300 rounded-lg text-left font-medium';
            button.textContent = option;
            button.dataset.answer = option;

            button.addEventListener('click', () => {
                document.querySelectorAll('.answer-option').forEach(btn => {
                    btn.classList.remove('selected');
                });
                button.classList.add('selected');
            });

            multipleChoiceOptions.appendChild(button);
        });

    } else if (data.type === 'fill_blank') {
        multipleChoiceOptions.classList.add('hidden');
        fillBlankInput.classList.remove('hidden');
        fillBlankAnswer.value = '';
        fillBlankAnswer.focus();
    }
}

async function handleSubmit() {
    let userAnswer = null;

    if (currentQuestion.type === 'multiple_choice') {
        const selected = document.querySelector('.answer-option.selected');
        if (!selected) {
            alert('Please select an answer');
            return;
        }
        userAnswer = selected.dataset.answer;

    } else if (currentQuestion.type === 'fill_blank') {
        userAnswer = fillBlankAnswer.value.trim();
        if (!userAnswer) {
            alert('Please enter an answer');
            return;
        }
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Checking...';

    try {
        const response = await fetch('/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                question_num: currentQuestionNum,
                answer: userAnswer
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to submit answer');
        }

        currentScore = data.current_score;
        showFeedback(data);
        updateHeader();

    } catch (error) {
        console.error('Submit error:', error);
        alert('Failed to submit answer: ' + error.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Answer';
    }
}

function showFeedback(data) {
    feedbackPanel.classList.remove('hidden');

    if (data.is_correct) {
        correctFeedback.classList.remove('hidden');
        incorrectFeedback.classList.add('hidden');
    } else {
        correctFeedback.classList.add('hidden');
        incorrectFeedback.classList.remove('hidden');
        correctAnswer.textContent = data.correct_answer;
    }

    explanation.textContent = data.explanation;
    submitBtn.classList.add('hidden');

    if (currentQuestionNum + 1 < totalQuestions) {
        nextBtn.textContent = 'Next Question';
    } else {
        nextBtn.textContent = 'View Results';
    }
}

function hideFeedback() {
    feedbackPanel.classList.add('hidden');
    submitBtn.classList.remove('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Answer';
}

function loadNextQuestion() {
    if (currentQuestionNum + 1 < totalQuestions) {
        loadQuestion(currentQuestionNum + 1);
    } else {
        completeQuiz();
    }
}

async function completeQuiz() {
    try {
        await fetch(`/complete-quiz/${sessionId}`, {
            method: 'POST'
        });
        window.location.href = `/results?session_id=${sessionId}`;
    } catch (error) {
        console.error('Complete quiz error:', error);
        window.location.href = `/results?session_id=${sessionId}`;
    }
}

function updateHeader() {
    progress.textContent = `Question ${currentQuestionNum + 1} of ${totalQuestions}`;
    score.textContent = `${currentScore}/${totalQuestions}`;

    const percentage = (currentScore / (currentQuestionNum + 1)) * 100;
    let emoji = '';
    if (percentage >= 90) emoji = '🌟';
    else if (percentage >= 70) emoji = '😊';
    else if (percentage >= 50) emoji = '🤔';
    else emoji = '📚';

    scoreBadge.innerHTML = `${emoji} <span id="score">${currentScore}/${totalQuestions}</span>`;
}

function showLoading(show) {
    if (show) {
        loadingIndicator.classList.remove('hidden');
        questionText.parentElement.classList.add('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
        questionText.parentElement.classList.remove('hidden');
    }
}
