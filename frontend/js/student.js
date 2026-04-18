const API_URL = 'http://localhost:8000/api';
let currentTab = 'available';

// Check authentication
const user = JSON.parse(localStorage.getItem('user'));
if (!user || user.role !== 'student') {
    window.location.href = 'index.html';
}

document.getElementById('studentName').textContent = user.full_name;

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

function showTab(tab) {
    // Hide all tabs
    document.getElementById('availableTab').classList.add('hidden');
    document.getElementById('applicationsTab').classList.add('hidden');
    document.getElementById('resultsTab').classList.add('hidden');
    document.getElementById('notificationsTab').classList.add('hidden');
    
    // Show selected tab
    currentTab = tab;
    switch(tab) {
        case 'available':
            document.getElementById('availableTab').classList.remove('hidden');
            loadAvailableExams();
            break;
        case 'applications':
            document.getElementById('applicationsTab').classList.remove('hidden');
            loadMyApplications();
            break;
        case 'results':
            document.getElementById('resultsTab').classList.remove('hidden');
            loadResults();
            break;
        case 'notifications':
            document.getElementById('notificationsTab').classList.remove('hidden');
            loadNotifications();
            break;
    }
}

async function loadAvailableExams() {
    try {
        const response = await fetch(`${API_URL}/student/exams`, {
            headers: getAuthHeaders()
        });
        
        const exams = await response.json();
        const container = document.getElementById('examsList');
        
        if (exams.length === 0) {
            container.innerHTML = '<p>No exams available</p>';
            return;
        }
        
        container.innerHTML = exams.map(exam => `
            <div class="card">
                <h3>${exam.title}</h3>
                <p>${exam.description}</p>
                <p><strong>Fee:</strong> ₹${exam.fee}</p>
                <p><strong>Duration:</strong> ${exam.duration_minutes} minutes</p>
                <p><strong>Total Marks:</strong> ${exam.total_marks}</p>
                <p><strong>Exam Date:</strong> ${new Date(exam.exam_date).toLocaleString()}</p>
                <button class="btn btn-primary mt-2" onclick="applyForExam(${exam.id})">
                    Apply Now
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function applyForExam(examId) {
    if (!confirm('Are you sure you want to apply for this exam?')) return;
    
    try {
        const response = await fetch(`${API_URL}/student/apply`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ exam_id: examId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Application submitted successfully!');
            showTab('applications');
        } else {
            alert(data.detail || 'Application failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Application failed');
    }
}

async function loadMyApplications() {
    try {
        const response = await fetch(`${API_URL}/student/applications`, {
            headers: getAuthHeaders()
        });
        
        const applications = await response.json();
        const container = document.getElementById('applicationsList');
        
        if (applications.length === 0) {
            container.innerHTML = '<p class="card">No applications found</p>';
            return;
        }
        
        container.innerHTML = applications.map(app => `
            <div class="card">
                <h3>${app.title}</h3>
                <p><strong>Fee:</strong> ₹${app.fee}</p>
                <p><strong>Exam Date:</strong> ${new Date(app.exam_date).toLocaleString()}</p>
                <p><strong>Applied On:</strong> ${new Date(app.application_date).toLocaleString()}</p>
                <p>
                    <strong>Payment Status:</strong> 
                    <span class="badge badge-${app.payment_status}">${app.payment_status.toUpperCase()}</span>
                </p>
                <p>
                    <strong>Approval Status:</strong> 
                    <span class="badge badge-${app.admin_approval}">${app.admin_approval.toUpperCase()}</span>
                </p>
                
                ${app.payment_status === 'pending' ? 
                    `<button class="btn btn-success mt-2" onclick="openPaymentModal(${app.id})">Pay Now</button>` : ''}
                
                ${app.admin_approval === 'approved' ? 
                    `<button class="btn btn-primary mt-2" onclick="startExam(${app.exam_id})">Start Exam</button>` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

function openPaymentModal(appId) {
    document.getElementById('payment_app_id').value = appId;
    document.getElementById('paymentModal').style.display = 'block';
}

function closePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
}

async function submitPayment(event) {
    event.preventDefault();
    
    const appId = document.getElementById('payment_app_id').value;
    const transactionId = document.getElementById('transaction_id').value;
    
    try {
        const response = await fetch(`${API_URL}/student/payment/${appId}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({ transaction_id: transactionId })
        });
        
        if (response.ok) {
            alert('Payment submitted successfully! Waiting for admin approval.');
            closePaymentModal();
            loadMyApplications();
        } else {
            alert('Payment submission failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Payment submission failed');
    }
}

function startExam(examId) {
    window.location.href = `exam.html?exam_id=${examId}`;
}

async function loadResults() {
    try {
        const response = await fetch(`${API_URL}/student/results`, {
            headers: getAuthHeaders()
        });
        
        const results = await response.json();
        const container = document.getElementById('resultsList');
        
        if (results.length === 0) {
            container.innerHTML = '<p class="card">No results found</p>';
            return;
        }
        
        container.innerHTML = results.map(result => `
            <div class="card">
                <h3>${result.exam_title}</h3>
                <p><strong>Obtained Marks:</strong> ${result.obtained_marks}/${result.total_marks}</p>
                <p><strong>Percentage:</strong> ${result.percentage}%</p>
                <p>
                    <strong>Status:</strong> 
                    <span class="badge badge-${result.status === 'pass' ? 'approved' : 'rejected'}">
                        ${result.status.toUpperCase()}
                    </span>
                </p>
                <p><strong>Exam Date:</strong> ${new Date(result.exam_date).toLocaleString()}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadNotifications() {
    try {
        const response = await fetch(`${API_URL}/notifications`, {
            headers: getAuthHeaders()
        });
        
        const notifications = await response.json();
        const container = document.getElementById('notificationsList');
        
        if (notifications.length === 0) {
            container.innerHTML = '<p class="card">No notifications</p>';
            return;
        }
        
        container.innerHTML = notifications.map(notif => `
            <div class="notification-item ${!notif.is_read ? 'unread' : ''}">
                <p>${notif.message}</p>
                <small>${new Date(notif.created_at).toLocaleString()}</small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

// Load initial data
loadAvailableExams();