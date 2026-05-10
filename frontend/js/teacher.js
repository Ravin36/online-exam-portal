const API_URL = '/api';

// Check authentication
const user = JSON.parse(localStorage.getItem('user'));
if (!user || user.role !== 'teacher') {
    window.location.href = 'index.html';
}

document.getElementById('teacherName').textContent = user.full_name;

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
    document.getElementById('unpaidTab').classList.add('hidden');
    document.getElementById('notificationsTab').classList.add('hidden');
    
    switch(tab) {
        case 'unpaid':
            document.getElementById('unpaidTab').classList.remove('hidden');
            loadUnpaidStudents();
            break;
        case 'notifications':
            document.getElementById('notificationsTab').classList.remove('hidden');
            loadNotifications();
            break;
    }
}

async function loadUnpaidStudents() {
    try {
        const response = await fetch(`${API_URL}/teacher/unpaid-students`, {
            headers: getAuthHeaders()
        });
        
        const unpaid = await response.json();
        const tbody = document.getElementById('unpaidTable');
        
        document.getElementById('unpaidCount').textContent = unpaid.length;
        
        if (unpaid.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No unpaid students</td></tr>';
            return;
        }
        
        tbody.innerHTML = unpaid.map(student => `
            <tr>
                <td>${student.full_name}</td>
                <td>${student.email}</td>
                <td>${student.exam_title}</td>
                <td>₹${student.fee}</td>
                <td>${new Date(student.application_date).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-primary btn-sm" 
                            onclick="openReminderModal(${student.student_id}, '${student.full_name}')">
                        Send Reminder
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

function openReminderModal(studentId, studentName) {
    document.getElementById('reminder_student_id').value = studentId;
    document.getElementById('reminder_student_name').value = studentName;
    document.getElementById('reminderModal').style.display = 'block';
}

function closeReminderModal() {
    document.getElementById('reminderModal').style.display = 'none';
}

async function sendReminder(event) {
    event.preventDefault();
    
    const studentId = parseInt(document.getElementById('reminder_student_id').value);
    const message = document.getElementById('reminder_message').value;
    
    try {
        const response = await fetch(`${API_URL}/teacher/send-reminder`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ student_id: studentId, message })
        });
        
        if (response.ok) {
            alert('Reminder sent successfully!');
            closeReminderModal();
        } else {
            alert('Failed to send reminder');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to send reminder');
    }
}

async function loadNotifications() {
    try {
        const response = await fetch(`${API_URL}/teacher/notifications`, {
            headers: getAuthHeaders()
        });
        
        const notifications = await response.json();
        const container = document.getElementById('notificationsList');
        
        const unreadCount = notifications.filter(n => !n.is_read).length;
        document.getElementById('notificationsCount').textContent = unreadCount;
        
        if (notifications.length === 0) {
            container.innerHTML = '<p class="card">No notifications</p>';
            return;
        }
        
        container.innerHTML = notifications.map(notif => `
            <div class="notification-item ${!notif.is_read ? 'unread' : ''}">
                <p><strong>${notif.sender_name || 'System'}:</strong> ${notif.message}</p>
                <small>${new Date(notif.created_at).toLocaleString()}</small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

// Load initial data
loadUnpaidStudents();
loadNotifications();