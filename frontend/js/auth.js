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

    if (password.length < 8 || password.length > 50) {
        showAlert('Пароль должен быть от 8 до 50 символов');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
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
                showLoginForm();
                document.getElementById('login-email').value = email;
            }, 2000);
        } else {
            const error = await response.json();
            if (error.detail) {
                if (Array.isArray(error.detail)) {
                    showAlert(error.detail.map(err => err.msg).join(', '));
                } else {
                    showAlert(error.detail);
                }
            } else {
                showAlert('Ошибка регистрации');
            }
        }
    } catch (error) {
        showAlert('Ошибка соединения с сервером');
    }
});

if (localStorage.getItem('isAuthenticated') === 'true') {
    window.location.href = 'dashboard.html';
}

function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Пароль должен содержать минимум 8 символов' };
    }
    if (password.length > 50) {
        return { valid: false, message: 'Пароль должен содержать не более 50 символов' };
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: 'Пароль должен содержать хотя бы одну заглавную букву' };
    }
    if (!/[0-9]/.test(password)) {
        return { valid: false, message: 'Пароль должен содержать хотя бы одну цифру' };
    }
    return { valid: true, message: '' };
}

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('register-name').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;

    // Валидация
    if (!name || name.length < 2) {
        showAlert('Имя должно содержать минимум 2 символа', 'warning');
        return;
    }

    if (!email.includes('@')) {
        showAlert('Введите корректный email', 'warning');
        return;
    }

    if (password !== passwordConfirm) {
        showAlert('Пароли не совпадают', 'warning');
        return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        showAlert(passwordValidation.message, 'warning');
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
            showAlert('Регистрация успешна! Перенаправление...', 'success');
            
            setTimeout(async () => {
                const loginResponse = await fetch(`${API_BASE}/auth/login`, {
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

                if (loginResponse.ok) {
                    localStorage.setItem('isAuthenticated', 'true');
                    window.location.href = 'dashboard.html';
                } else {
                    showAlert('Регистрация успешна, но вход не удался. Пожалуйста, войдите вручную.', 'info');
                    showLoginForm();
                }
            }, 1500);
            
        } else {
            const error = await response.json();
            if (error.detail) {
                if (Array.isArray(error.detail)) {
                    showAlert(error.detail.map(err => err.msg).join(', '));
                } else {
                    showAlert(error.detail);
                }
            } else {
                showAlert('Ошибка регистрации. Пользователь с таким email уже существует.');
            }
        }
    } catch (error) {
        showAlert('Ошибка соединения с сервером', 'danger');
    }
});

window.addEventListener('load', () => {
    if (localStorage.getItem('isAuthenticated') === 'true') {
        fetch(`${API_BASE}/auth/me`, {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                localStorage.removeItem('isAuthenticated');
            } else {
                window.location.href = 'dashboard.html';
            }
        })
        .catch(() => {
            localStorage.removeItem('isAuthenticated');
        });
    }
});