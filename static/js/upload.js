// User ID management
function getUserId() {
    let userId = localStorage.getItem('webquiz_user_id');
    if (!userId) {
        userId = generateUUID();
        localStorage.setItem('webquiz_user_id', userId);
    }
    return userId;
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// DOM elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadPrompt = document.getElementById('uploadPrompt');
const processingIndicator = document.getElementById('processingIndicator');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const quizSetup = document.getElementById('quizSetup');
const startQuizBtn = document.getElementById('startQuizBtn');
const numQuestionsSelect = document.getElementById('numQuestions');

// State
let processedData = null;

// Event listeners
uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', handleDragOver);
uploadZone.addEventListener('dragleave', handleDragLeave);
uploadZone.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
startQuizBtn.addEventListener('click', handleStartQuiz);

function handleDragOver(e) {
    e.preventDefault();
    uploadZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validate file
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];

    if (file.size > maxSize) {
        showError('File is too large. Maximum size is 10MB.');
        return;
    }

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|xlsx|xls)$/i)) {
        showError('Invalid file type. Please upload a PDF or Excel file.');
        return;
    }

    // Upload and process
    uploadDocument(file);
}

async function uploadDocument(file) {
    // Show processing indicator
    uploadPrompt.classList.add('hidden');
    processingIndicator.classList.remove('hidden');
    errorMessage.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        // Store processed data
        processedData = {
            fileId: data.file_id,
            filename: data.filename,
            knowledge: data.knowledge,
            documentType: data.document_type
        };

        // Show quiz setup
        processingIndicator.classList.add('hidden');
        quizSetup.classList.remove('hidden');

    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message);
        resetUploadZone();
    }
}

async function handleStartQuiz() {
    if (!processedData) return;

    const numQuestions = parseInt(numQuestionsSelect.value);
    const userId = getUserId();

    // Disable button
    startQuizBtn.disabled = true;
    startQuizBtn.textContent = 'Creating quiz...';

    try {
        const response = await fetch('/generate-quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                knowledge: processedData.knowledge,
                num_questions: numQuestions,
                user_id: userId,
                document_name: processedData.filename,
                file_id: processedData.fileId
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Quiz generation failed');
        }

        // Redirect to quiz page
        window.location.href = `/quiz?session_id=${data.session_id}`;

    } catch (error) {
        console.error('Quiz generation error:', error);
        showError(error.message);
        startQuizBtn.disabled = false;
        startQuizBtn.textContent = 'Start Quiz!';
    }
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

function resetUploadZone() {
    uploadPrompt.classList.remove('hidden');
    processingIndicator.classList.add('hidden');
    fileInput.value = '';
}
