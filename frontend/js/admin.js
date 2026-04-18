const API_URL = 'http://localhost:8000/api';

// Check authentication
const user = JSON.parse(localStorage.getItem('user'));
if (!user || user.role !== 'admin') {
    window.location.href = 'index.html';
}

document.getElementById('adminName').textContent = user.full_name;

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
    document.getElementById('applicationsTab').classList.add('hidden');
    document.getElementById('unpaidTab').classList.add('hidden');
    document.getElementById('examsTab').classList.add('hidden');
    
    switch(tab) {
        case 'applications':
            document.getElementById('applicationsTab').classList.remove('hidden');
            loadApplications();
            break;
        case 'unpaid':
            document.getElementById('unpaidTab').classList.remove('hidden');
            loadUnpaidStudents();
            break;
        case 'exams':
            document.getElementById('examsTab').classList.remove('hidden');
            break;
    }
}

async function loadApplications() {
    try {
        const response = await fetch(`${API_URL}/admin/applications`, {
            headers: getAuthHeaders()
        });
        
        const applications = await response.json();
        const tbody = document.getElementById('applicationsTable');
        
        // Update stats
        document.getElementById('totalApplications').textContent = applications.length;
        document.getElementById('pendingPayments').textContent = 
            applications.filter(a => a.payment_status === 'pending').length;
        document.getElementById('approvedCount').textContent = 
            applications.filter(a => a.admin_approval === 'approved').length;
        
        if (applications.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No applications found</td></tr>';
            return;
        }
        
        tbody.innerHTML = applications.map(app => `
            <tr>
                <td>${app.full_name}</td>
                <td>${app.email}</td>
                <td>${app.exam_title}</td>
                <td><span class="badge badge-${app.payment_status}">${app.payment_status.toUpperCase()}</span></td>
                <td><span class="badge badge-${app.admin_approval}">${app.admin_approval.toUpperCase()}</span></td>
                <td>
                    ${app.payment_status === 'paid' && app.admin_approval === 'pending' ? `
                        <button class="btn btn-success btn-sm" onclick="approveApplication(${app.id}, 'approved')">Approve</button>
                        <button class="btn btn-danger btn-sm" onclick="approveApplication(${app.id}, 'rejected')">Reject</button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function approveApplication(appId, status) {
    try {
        const response = await fetch(`${API_URL}/admin/approve`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({ application_id: appId, status })
        });
        
        if (response.ok) {
            alert(`Application ${status} successfully!`);
            loadApplications();
        } else {
            const data = await response.json();
            alert(data.detail || 'Action failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Action failed');
    }
}

async function loadUnpaidStudents() {
    try {
        const response = await fetch(`${API_URL}/admin/unpaid-students`, {
            headers: getAuthHeaders()
        });
        
        const unpaid = await response.json();
        const tbody = document.getElementById('unpaidTable');
        
        if (unpaid.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No unpaid students</td></tr>';
            return;
        }
        
        tbody.innerHTML = unpaid.map(student => `
            <tr>
                <td>${student.full_name}</td>
                <td>${student.email}</td>
                <td>${student.exam_title}</td>
                <td>${new Date(student.application_date).toLocaleDateString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function notifyTeacher() {
    const message = "Please follow up with students who have not completed their exam fee payment.";
    
    try {
        const response = await fetch(`${API_URL}/admin/notify-teacher`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            alert('Teacher notified successfully!');
        } else {
            alert('Notification failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Notification failed');
    }
}

function showCreateExamForm() {
    document.getElementById('createExamForm').classList.remove('hidden');
}

function hideCreateExamForm() {
    document.getElementById('createExamForm').classList.add('hidden');
}

async function createExam(event) {
    event.preventDefault();
    
    const examData = {
        title: document.getElementById('exam_title').value,
        description: document.getElementById('exam_desc').value,
        fee: parseFloat(document.getElementById('exam_fee').value),
        duration_minutes: parseInt(document.getElementById('exam_duration').value),
        total_marks: parseInt(document.getElementById('exam_marks').value),
        passing_marks: parseInt(document.getElementById('exam_passing').value),
        exam_date: document.getElementById('exam_date').value
    };
    
    try {
        const response = await fetch(`${API_URL}/admin/create-exam`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(examData)
        });
        
        if (response.ok) {
            alert('Exam created successfully!');
            hideCreateExamForm();
            event.target.reset();
        } else {
            alert('Exam creation failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Exam creation failed');
    }
}

// Load initial data
loadApplications();