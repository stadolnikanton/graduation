// DOM Elements
const loginView = document.getElementById("login-view");
const registerView = document.getElementById("register-view");
const filesView = document.getElementById("files-view");
const loader = document.getElementById("loader");
const pageTitle = document.getElementById("page-title");
const pageSubtitle = document.getElementById("page-subtitle");
const authButtons = document.getElementById("auth-buttons");
const userMenu = document.getElementById("user-menu");
const welcomeText = document.getElementById("welcome-text");

// Toast system
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toastId = 'toast-' + Date.now();

    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${type === 'success' ? 'bi-check-circle' : type === 'error' ? 'bi-exclamation-circle' : 'bi-info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl, {
        delay: 3000
    });
    toast.show();

    // Remove toast after it's hidden
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

// View Management
function showLogin() {
    hideAllViews();
    loginView.classList.remove("d-none");
    authButtons.classList.remove("d-none");
    userMenu.classList.add("d-none");
    pageTitle.innerText = "Sign In";
    pageSubtitle.innerText = "Access your FileCloud account";
}

function showRegister() {
    hideAllViews();
    registerView.classList.remove("d-none");
    authButtons.classList.remove("d-none");
    userMenu.classList.add("d-none");
    pageTitle.innerText = "Create Account";
    pageSubtitle.innerText = "Join FileCloud today";
}

async function showFiles() {
    hideAllViews();
    loader.classList.remove("d-none");
    pageTitle.innerText = "My Files";
    pageSubtitle.innerText = "Manage and share your uploaded files";

    try {
        await loadFiles();
        filesView.classList.remove("d-none");
        authButtons.classList.add("d-none");
        userMenu.classList.remove("d-none");
        // You might want to fetch user data to show name here
        welcomeText.innerText = "Welcome back!";
    } catch (error) {
        showLogin();
    } finally {
        loader.classList.add("d-none");
    }
}

function hideAllViews() {
    loader.classList.add("d-none");
    loginView.classList.add("d-none");
    registerView.classList.add("d-none");
    filesView.classList.add("d-none");
}

// Check authentication status on page load
document.addEventListener("DOMContentLoaded", async () => {
    try {
        await api.get("/files/");
        await showFiles();
    } catch (error) {
        showLogin();
    }
});