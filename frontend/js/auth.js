// Login function
async function login(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Basic validation
    if (!email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    try {
        const response = await api.post("/auth/login", {
            email,
            password
        });

        showToast('Login successful!', 'success');
        await showFiles();

    } catch (err) {
        const errorMsg = err.response?.data?.message || "Invalid email or password";
        showToast(errorMsg, 'error');
        console.error('Login error:', err);
    }
}

// Register function
async function register(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const password_confirm = document.getElementById('password_confirm').value;

    // Validation
    if (!name || !email || !password || !password_confirm) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    if (password !== password_confirm) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    try {
        const response = await api.post("/auth/register", {
            name,
            email,
            password,
            password_confirm
        });

        showToast('Registration successful! Please login.', 'success');
        showLogin();

    } catch (err) {
        const errorMsg = err.response?.data?.message || "Registration failed";
        showToast(errorMsg, 'error');
        console.error('Registration error:', err);
    }
}

// Logout function
async function logout() {
    if (!confirm('Are you sure you want to logout?')) return;

    try {
        await api.post("/auth/logout");
        showToast('Logged out successfully', 'success');
        showLogin();
    } catch (err) {
        showToast('Error logging out', 'error');
        console.error('Logout error:', err);
    }
}