const API_URL = 'http://localhost:8000/api';

function setActiveTab(tabName) {
    document.querySelectorAll('.tab-item').forEach((item) => {
        const tab = item.dataset.tab;
        if (!tab) return;
        item.classList.toggle('active', tab === tabName);
    });
}

function showTab(eventOrTab, tabName) {
    if (typeof eventOrTab === 'string') {
        tabName = eventOrTab;
    } else if (eventOrTab && typeof eventOrTab.preventDefault === 'function') {
        eventOrTab.preventDefault();
    }

    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const resetForm = document.getElementById('resetForm');

    if (loginForm) loginForm.classList.toggle('hidden', tabName !== 'login');
    if (registerForm) registerForm.classList.toggle('hidden', tabName !== 'signup');
    if (resetForm) resetForm.classList.toggle('hidden', tabName !== 'reset');

    setActiveTab(tabName);
}

function showLoginForm() {
    showTab('login');
}

function showRegisterForm() {
    showTab('signup');
}

function showResetForm() {
    showTab('reset');
}

function togglePassword(fieldId, button) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    const isPassword = field.type === 'password';
    field.type = isPassword ? 'text' : 'password';
    button.textContent = isPassword ? 'Hide' : 'Show';
}

function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.password-toggle-btn');
    toggleButtons.forEach((button) => {
        const target = button.dataset.target;
        if (!target) return;
        button.addEventListener('click', () => togglePassword(target, button));
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordToggles);
} else {
    initPasswordToggles();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Redirect based on role
            switch(data.user.role) {
                case 'student':
                    window.location.href = 'student_dashboard.html';
                    break;
                case 'admin':
                    window.location.href = 'admin_dashboard.html';
                    break;
                case 'teacher':
                    window.location.href = 'teacher_dashboard.html';
                    break;
            }
        } else {
            alert(data.detail || 'Login failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Login failed. Please try again.');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const userData = {
        username: document.getElementById('reg_username').value,
        email: document.getElementById('reg_email').value,
        password: document.getElementById('reg_password').value,
        full_name: document.getElementById('reg_fullname').value,
        role: document.getElementById('reg_role').value
    };
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            showLoginForm();
        } else {
            alert(data.detail || 'Registration failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Registration failed. Please try again.');
    }
}

async function handleResetPassword(event) {
    event.preventDefault();
    const emailField = document.getElementById('reset_email');
    const email = emailField ? emailField.value.trim() : '';

    if (!email) {
        alert('Please enter your email address.');
        return;
    }

    // If a backend reset endpoint exists, replace this alert with a real request.
    alert(`If the email ${email} exists, reset instructions will be sent.`);
    showTab('login');
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}