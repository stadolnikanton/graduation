const API_BASE = 'http://localhost:8000';

function showRegisterForm() {
    document.getElementById('login-form').classList.add('d-none');
    document.getElementById('register-form').classList.remove('d-none');
    hideAlert();
}

function showLoginForm() {
    document.getElementById('register-form').classList.add('d-none');
    document.getElementById('login-form').classList.remove('d-none');
    hideAlert();
}

function showAlert(message, type = 'danger') {
    const alertDiv = document.getElementById('auth-alert');
    alertDiv.textContent = message;
    alertDiv.className = `alert alert-${type}`;
    alertDiv.classList.remove('d-none');
}

function hideAlert() {
    document.getElementById('auth-alert').classList.add('d-none');
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        if (response.ok) {
            localStorage.setItem('isAuthenticated', 'true');
            window.location.href = 'dashboard.html';
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Ошибка входа');
        }
    } catch (error) {
        showAlert('Ошибка соединения с сервером');
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;

    if (password !== passwordConfirm) {
        showAlert('Пароли не совпадают');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                password_confirm: passwordConfirm
            })
        });

        if (response.ok) {
            showAlert('Регистрация успешна! Теперь вы можете войти.', 'success');
            setTimeout(() => {
                localStorage.setItem('isAuthenticated', 'true'); // После успешной регистрации переходит в приложение
                window.location.href = 'dashboard.html'; // После успешной регистрации переходит в приложение
                // showLoginForm(); После успешной регистрации показывает формлу логина
                // document.getElementById('login-email').value = email;
            }, 2000);
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Ошибка регистрации');
        }
    } catch (error) {
        showAlert('Ошибка соединения с сервером');
    }
});

if (localStorage.getItem('isAuthenticated') === 'true') {
    window.location.href = 'dashboard.html';
}