// Get user ID
function getUserId() {
    let userId = localStorage.getItem('webquiz_user_id');
    if (!userId) {
        showEmptyState();
        return null;
    }
    return userId;
}

const userId = getUserId();

// DOM elements
const emptyState = document.getElementById('emptyState');
const historyTable = document.getElementById('historyTable');
const historyBody = document.getElementById('historyBody');

// Load history
if (userId) {
    loadHistory();
}

async function loadHistory() {
    try {
        const response = await fetch(`/history/${userId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load history');
        }

        if (data.quizzes.length === 0) {
            showEmptyState();
        } else {
            displayHistory(data.quizzes);
        }

    } catch (error) {
        console.error('Load history error:', error);
        showEmptyState();
    }
}

function displayHistory(quizzes) {
    historyBody.innerHTML = '';
    historyTable.classList.remove('hidden');
    emptyState.classList.add('hidden');

    quizzes.forEach(quiz => {
        const row = document.createElement('tr');
        row.className = 'border-t border-gray-200 hover:bg-gray-50 cursor-pointer';

        const date = new Date(quiz.completed_at);
        const formattedDate = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const scoreClass = quiz.score_percentage >= 70 ? 'text-success' : 'text-error';

        row.innerHTML = `
            <td class="p-4">${formattedDate}</td>
            <td class="p-4 font-medium">${quiz.document_name}</td>
            <td class="p-4 text-center">${quiz.correct_answers}/${quiz.total_questions}</td>
            <td class="p-4 text-center ${scoreClass} font-bold">${quiz.score_percentage}%</td>
            <td class="p-4 text-center">${formatTime(quiz.time_taken_seconds)}</td>
            <td class="p-4 text-center">
                <button onclick="viewQuiz('${quiz.quiz_id}')"
                        class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-opacity-90 transition text-sm font-medium">
                    View Details
                </button>
            </td>
        `;

        historyBody.appendChild(row);
    });
}

function showEmptyState() {
    historyTable.classList.add('hidden');
    emptyState.classList.remove('hidden');
}

function viewQuiz(quizId) {
    window.location.href = `/results?session_id=${quizId}`;
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}
