const API_URL = 'http://localhost:8000/api';
let examId;
let questions = [];
let answers = {};
let timer;
let timeLeft;

// Get exam ID from URL
const urlParams = new URLSearchParams(window.location.search);
examId = urlParams.get('exam_id');

if (!examId) {
    alert('Invalid exam');
    window.location.href = 'student_dashboard.html';
}

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function loadExam() {
    try {
        const response = await fetch(`${API_URL}/student/exam/${examId}/questions`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            alert('You are not approved for this exam');
            window.location.href = 'student_dashboard.html';
            return;
        }
        
        questions = await response.json();
        
        if (questions.length === 0) {
            alert('No questions available');
            window.location.href = 'student_dashboard.html';
            return;
        }
        
        displayQuestions();
        startTimer();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load exam');
        window.location.href = 'student_dashboard.html';
    }
}

function displayQuestions() {
    const container = document.getElementById('questionsContainer');
    
    container.innerHTML = questions.map((q, index) => `
        <div class="question">
            <h3>Question ${index + 1} (${q.marks} marks)</h3>
            <p>${q.question_text}</p>
            <div class="options">
                <label class="option">
                    <input type="radio" name="q${q.id}" value="A" onchange="saveAnswer(${q.id}, 'A')">
                    <span>A) ${q.option_a}</span>
                </label>
                <label class="option">
                    <input type="radio" name="q${q.id}" value="B" onchange="saveAnswer(${q.id}, 'B')">
                    <span>B) ${q.option_b}</span>
                </label>
                <label class="option">
                    <input type="radio" name="q${q.id}" value="C" onchange="saveAnswer(${q.id}, 'C')">
                    <span>C) ${q.option_c}</span>
                </label>
                <label class="option">
                    <input type="radio" name="q${q.id}" value="D" onchange="saveAnswer(${q.id}, 'D')">
                    <span>D) ${q.option_d}</span>
                </label>
            </div>
        </div>
    `).join('');
}

function saveAnswer(questionId, answer) {
    answers[questionId] = answer;
}

function startTimer() {
    // Set timer to 60 minutes (you can get this from exam data)
    timeLeft = 60 * 60; // 60 minutes in seconds
    
    timer = setInterval(() => {
        timeLeft--;
        
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        document.getElementById('timer').textContent = 
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(timer);
            submitExam();
        }
    }, 1000);
}

async function submitExam() {
    if (!confirm('Are you sure you want to submit the exam?')) {
        return;
    }
    
    clearInterval(timer);
    
    // Convert answers object to array format
    const answerArray = Object.keys(answers).map(questionId => ({
        question_id: parseInt(questionId),
        answer: answers[questionId]
    }));
    
    try {
        const response = await fetch(`${API_URL}/student/submit-exam`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                exam_id: parseInt(examId),
                answers: answerArray
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`Exam submitted successfully!\n\nScore: ${result.obtained_marks}/${result.total_marks}\nPercentage: ${result.percentage}%\nStatus: ${result.status.toUpperCase()}`);
            window.location.href = 'student_dashboard.html';
        } else {
            alert('Failed to submit exam');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to submit exam');
    }
}

// Prevent page reload
window.addEventListener('beforeunload', (e) => {
    if (timeLeft > 0) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Load exam on page load
loadExam();