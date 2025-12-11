// Get session ID from URL
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');

if (!sessionId) {
    window.location.href = '/';
}

// DOM elements
const scoreTitle = document.getElementById('scoreTitle');
const congratsMessage = document.getElementById('congratsMessage');
const scorePercentage = document.getElementById('scorePercentage');
const correctCount = document.getElementById('correctCount');
const incorrectCount = document.getElementById('incorrectCount');
const documentName = document.getElementById('documentName');
const timeSpent = document.getElementById('timeSpent');
const questionsList = document.getElementById('questionsList');

// Load results
loadResults();

async function loadResults() {
    try {
        const response = await fetch(`/results/${sessionId}`);
        const data = await response.json();

        if (!response.ok) {
            const userId = getUserId();
            const historyResponse = await fetch(`/history/${userId}`);
            const historyData = await historyResponse.json();

            const quiz = historyData.quizzes.find(q => q.quiz_id === sessionId);
            if (quiz) {
                displayHistoryResults(quiz);
                return;
            }

            throw new Error(data.error || 'Failed to load results');
        }

        displayResults(data);

    } catch (error) {
        console.error('Load results error:', error);
        alert('Failed to load results: ' + error.message);
        window.location.href = '/';
    }
}

function getUserId() {
    return localStorage.getItem('webquiz_user_id');
}

function displayResults(data) {
    const total = data.total_questions;
    const correct = data.correct_answers;
    const percentage = data.score_percentage;

    scoreTitle.textContent = `You scored ${correct} out of ${total}! ${getScoreEmoji(percentage)}`;
    congratsMessage.textContent = getCongratsMessage(percentage);
    scorePercentage.textContent = `${percentage}%`;
    correctCount.textContent = correct;
    incorrectCount.textContent = total - correct;
    documentName.textContent = `Document: ${data.document_name}`;

    displayQuestionsList(data.questions_review);
}

function displayHistoryResults(quiz) {
    const total = quiz.total_questions;
    const correct = quiz.correct_answers;
    const percentage = quiz.score_percentage;

    scoreTitle.textContent = `You scored ${correct} out of ${total}! ${getScoreEmoji(percentage)}`;
    congratsMessage.textContent = getCongratsMessage(percentage);
    scorePercentage.textContent = `${percentage}%`;
    correctCount.textContent = correct;
    incorrectCount.textContent = total - correct;
    documentName.textContent = `Document: ${quiz.document_name}`;
    timeSpent.textContent = `Time: ${formatTime(quiz.time_taken_seconds)}`;

    displayQuestionsList(quiz.questions_review);
}

function displayQuestionsList(questions) {
    questionsList.innerHTML = '';

    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = `p-4 rounded-lg border-2 ${q.is_correct ? 'border-success bg-success bg-opacity-5' : 'border-error bg-error bg-opacity-5'}`;

        questionDiv.innerHTML = `
            <div class="flex items-start gap-3">
                <span class="text-2xl">${q.is_correct ? '✓' : '✗'}</span>
                <div class="flex-1">
                    <p class="font-semibold mb-2">${index + 1}. ${q.question}</p>
                    <div class="text-sm space-y-1">
                        <p><span class="text-gray-500">Your answer:</span>
                           <span class="${q.is_correct ? 'text-success font-medium' : 'text-error'}">${q.user_answer}</span>
                        </p>
                        ${!q.is_correct ? `
                        <p><span class="text-gray-500">Correct answer:</span>
                           <span class="text-success font-medium">${q.correct_answer}</span>
                        </p>
                        ` : ''}
                        ${q.explanation ? `
                        <p class="mt-2 text-gray-600 italic">${q.explanation}</p>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        questionsList.appendChild(questionDiv);
    });
}

function getScoreEmoji(percentage) {
    if (percentage >= 90) return '🌟';
    if (percentage >= 70) return '🎉';
    if (percentage >= 50) return '💪';
    return '📚';
}

function getCongratsMessage(percentage) {
    if (percentage >= 90) return 'Outstanding!';
    if (percentage >= 70) return 'Great job!';
    if (percentage >= 50) return 'Good effort!';
    return 'Keep practicing!';
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ${remainingSeconds} second${remainingSeconds !== 1 ? 's' : ''}`;
}
