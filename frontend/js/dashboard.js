const API_BASE = 'http://localhost:8000';
let currentUser = null;
let filesData = null;
let currentFileTab = 'owned';

document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    await loadFiles();
});

async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/auth/refresh`, {
            method: 'POST',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Not authenticated');
        }

        await loadUserProfile();
    } catch (error) {
        localStorage.removeItem('isAuthenticated');
        window.location.href = 'index.html';
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-name').textContent = currentUser.name;
            document.getElementById('user-email').textContent = currentUser.email;
            document.getElementById('user-initials').textContent =
                currentUser.name.charAt(0).toUpperCase();
        }
    } catch (error) {
        console.error('Failed to load user profile:', error);
    }
}

async function loadFiles() {
    try {
        const response = await fetch(`${API_BASE}/files/`, {
            credentials: 'include'
        });

        if (response.ok) {
            filesData = await response.json();
            updateStats();
            renderFiles();
        }
    } catch (error) {
        showToast('Ошибка загрузки файлов', 'danger');
    }
}

function updateStats() {
    if (filesData) {
        document.getElementById('total-files').textContent =
            filesData.counts?.total || 0;
        document.getElementById('owned-files').textContent =
            filesData.counts?.owned || 0;
        document.getElementById('shared-files').textContent =
            filesData.counts?.shared || 0;
    }
}

function renderFiles() {
    const filesList = document.getElementById('files-list');

    // Проверяем структуру данных
    let files = [];
    if (filesData) {
        if (currentFileTab === 'owned' && filesData.files?.owned) {
            files = filesData.files.owned;
        } else if (currentFileTab === 'shared' && filesData.files?.shared) {
            files = filesData.files.shared;
        } else if (filesData.files) {
            files = filesData.files; // Если структура отличается
        }
    }

    if (files.length === 0) {
        filesList.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-folder-x" style="font-size: 4rem; color: #dee2e6;"></i>
                <h5 class="mt-3 text-muted">Файлы не найдены</h5>
            </div>
        `;
        return;
    }

    filesList.innerHTML = files.map(file => `
        <div class="card file-card mb-3" onclick="openFileActions(${file.id})">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-auto">
                        <i class="bi bi-file-earmark file-icon"></i>
                    </div>
                    <div class="col">
                        <h5 class="mb-1">${file.original_filename || file.filename || file.name}</h5>
                        <p class="text-muted mb-1">
                            ${formatFileSize(file.size)} • 
                            ${new Date(file.created_at || file.uploaded_at).toLocaleDateString()}
                        </p>
                        ${file.shared_file || file.is_shared ?
            '<span class="badge bg-primary">Доступ</span>' :
            '<span class="badge bg-success">Владелец</span>'
        }
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="event.stopPropagation(); downloadFile(${file.id})">
                            <i class="bi bi-download"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function showFilesTab(tab, event = null) {
    if (event) {
        currentFileTab = tab;
        document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        event.target.classList.add('active');
        renderFiles();
    }
}

function showSection(sectionId, event = null) {
    const targetElement = event ? event.target : null;
    document.querySelectorAll('.main-content > div[id$="section"]').forEach(div => {
        div.classList.add('d-none');
    });
    document.getElementById(`${sectionId}-section`).classList.remove('d-none');
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    if (targetElement) {
        targetElement.classList.add('active');
    }
    if (sectionId === 'files') {
        loadFiles();
    } else if (sectionId === 'upload') {
        // Reset upload form
        document.getElementById('file-input').value = '';
        document.getElementById('upload-progress').style.width = '0%';
        document.getElementById('upload-results').innerHTML = '';
    } else if (sectionId === 'links') {
        loadLinksData();
    } else if (sectionId === 'profile') {
        loadUserProfile();
    } else if (sectionId === 'shared') {
        loadShareData();
    }
}

async function loadShareData() {
    const select = document.getElementById('share-file-select');
    if (!select) return; // Если секция sharing не существует

    select.innerHTML = '<option value="">Загрузка файлов...</option>';

    try {
        const response = await fetch(`${API_BASE}/files/`, {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            const ownedFiles = data.files?.owned || data.files || [];
            select.innerHTML = ownedFiles.map(file =>
                `<option value="${file.id}">${file.original_filename || file.filename}</option>`
            ).join('');
            if (ownedFiles.length > 0) {
                await loadSharedUsers(ownedFiles[0].id);
            } else {
                document.getElementById('shared-users-list').innerHTML = `
                    <div class="text-center text-muted py-3">
                        У вас нет файлов для предоставления доступа
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Failed to load files for sharing:', error);
    }
}

async function loadSharedUsers(fileId = null) {
    const fileSelect = document.getElementById('share-file-select');
    const fileIdToUse = fileId || fileSelect.value;

    if (!fileIdToUse) {
        document.getElementById('shared-users-list').innerHTML = `
            <div class="text-center text-muted py-3">
                Выберите файл для просмотра списка пользователей
            </div>
        `;
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/files/${fileIdToUse}/shared-users`, {
            credentials: 'include'
        });

        const sharedUsersList = document.getElementById('shared-users-list');

        if (response.ok) {
            const users = await response.json();

            if (users.length === 0) {
                sharedUsersList.innerHTML = `
                    <div class="text-center text-muted py-3">
                        Нет предоставленных доступов
                    </div>
                `;
                return;
            }

            sharedUsersList.innerHTML = users.map(user => `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
                    <div>
                        <strong>${user.name || user.username}</strong>
                        <div class="text-muted small">${user.email}</div>
                        <span class="badge bg-info">${getAccessLevelLabel(user.access_level)}</span>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="revokeAccess(${fileIdToUse}, ${user.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `).join('');
        } else {
            sharedUsersList.innerHTML = `
                <div class="text-center text-muted py-3">
                    Ошибка загрузки списка пользователей
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load shared users:', error);
    }
}

function getAccessLevelLabel(level) {
    const labels = {
        'read': 'Только чтение',
        'write': 'Чтение и запись',
        'manage': 'Полный доступ'
    };
    return labels[level] || level;
}

async function revokeAccess(fileId, userId) {
    if (!confirm('Вы уверены, что хотите отозвать доступ?')) return;

    try {
        const response = await fetch(`${API_BASE}/files/${fileId}/share/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            showToast('Доступ успешно отозван', 'success');
            await loadSharedUsers(fileId);
        } else {
            const error = await response.json();
            showToast(error.detail || 'Ошибка отзыва доступа', 'danger');
        }
    } catch (error) {
        showToast('Ошибка соединения', 'danger');
    }
}

async function shareFile() {
    const fileId = document.getElementById('share-file-select').value;
    const userId = document.getElementById('share-user-id').value;
    const accessLevel = document.getElementById('share-access-level').value;

    if (!fileId || !userId) {
        showToast('Заполните все поля', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/files/${fileId}/share`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                user_id: parseInt(userId),
                access_level: accessLevel
            })
        });

        if (response.ok) {
            showToast('Доступ успешно предоставлен', 'success');
            document.getElementById('share-user-id').value = '';
            await loadSharedUsers(fileId);
        } else {
            const error = await response.json();
            showToast(error.detail || 'Ошибка предоставления доступа', 'danger');
        }
    } catch (error) {
        showToast('Ошибка соединения', 'danger');
    }
}

async function loadLinksData() {
    const select = document.getElementById('link-file-select');
    select.innerHTML = '<option value="">Загрузка файлов...</option>';

    try {
        const response = await fetch(`${API_BASE}/files/`, {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            const ownedFiles = data.files?.owned || data.files || [];
            select.innerHTML = ownedFiles.map(file =>
                `<option value="${file.id}">${file.original_filename || file.filename}</option>`
            ).join('');
        }
    } catch (error) {
        console.error('Failed to load files for links:', error);
    }
}

async function createShareLink() {
    const fileId = document.getElementById('link-file-select').value;
    const expiresHours = document.getElementById('link-expires').value;
    const maxDownloads = document.getElementById('link-max-downloads').value;

    if (!fileId) {
        showToast('Выберите файл', 'warning');
        return;
    }

    const formData = new URLSearchParams();
    formData.append('expires_hours', expiresHours);
    formData.append('max_downloads', maxDownloads);

    try {
        const response = await fetch(`${API_BASE}/share/${fileId}`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            showToast('Ссылка создана успешно!', 'success');
            const activeLinks = document.getElementById('active-links');
            activeLinks.innerHTML = `
                <div class="alert alert-success">
                    <h6>Новая ссылка:</h6>
                    <p class="mb-2">
                        <a href="${window.location.origin}/share.html?token=${data.token}" target="_blank">
                            ${window.location.origin}/share.html?token=${data.token}
                        </a>
                    </p>
                    <small class="text-muted">
                        Действует до: ${new Date(data.expires_at).toLocaleString()}
                    </small>
                </div>
            `;
        } else {
            const error = await response.json();
            showToast(error.detail || 'Ошибка создания ссылки', 'danger');
        }
    } catch (error) {
        showToast('Ошибка соединения', 'danger');
    }
}

async function uploadFiles() {
    const fileInput = document.getElementById('file-input');
    const files = fileInput.files;

    if (files.length === 0) {
        showToast('Выберите файлы для загрузки', 'warning');
        return;
    }

    const progressBar = document.getElementById('upload-progress');
    const resultsDiv = document.getElementById('upload-results');
    progressBar.style.width = '0%';
    resultsDiv.innerHTML = '';

    // Проверка размера файлов
    for (let file of files) {
        if (file.size > 100 * 1024 * 1024) {
            showToast(`Файл ${file.name} превышает 100MB`, 'danger');
            return;
        }
    }

    if (files.length === 1) {
        const formData = new FormData();
        formData.append('file', files[0]);

        try {
            const response = await fetch(`${API_BASE}/files/upload`, {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            progressBar.style.width = '100%';

            if (response.ok) {
                const result = await response.json();
                showToast('Файл успешно загружен!', 'success');
                resultsDiv.innerHTML = `
                    <div class="alert alert-success">
                        <h6>${result.filename || result.name}</h6>
                        <p class="mb-0">Размер: ${formatFileSize(result.size)}</p>
                    </div>
                `;
                await loadFiles();
            } else {
                const error = await response.json();
                showToast(error.detail || 'Ошибка загрузки', 'danger');
            }
        } catch (error) {
            showToast('Ошибка соединения', 'danger');
        }
    } else {
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        try {
            const response = await fetch(`${API_BASE}/files/upload/multiple`, {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            progressBar.style.width = '100%';

            if (response.ok) {
                const result = await response.json();
                showToast(`Загружено ${result.successful || result.count} из ${result.total_files || files.length} файлов`, 'success');

                if (result.files) {
                    resultsDiv.innerHTML = result.files.map(file => `
                        <div class="alert alert-${file.status === 'success' ? 'success' : 'danger'}">
                            <h6>${file.filename || file.name}</h6>
                            ${file.status === 'success' ?
                            `<p class="mb-0">Размер: ${formatFileSize(file.size)}</p>` :
                            `<p class="mb-0">Ошибка: ${file.error || 'Неизвестная ошибка'}</p>`
                        }
                        </div>
                    `).join('');
                }

                await loadFiles();
            } else {
                const error = await response.json();
                showToast(error.detail || 'Ошибка загрузки', 'danger');
            }
        } catch (error) {
            showToast('Ошибка соединения', 'danger');
        }
    }
    fileInput.value = '';
}

function downloadFile(fileId) {
    window.open(`${API_BASE}/files/${fileId}/download`, '_blank');
}

function openFileActions(fileId) {
    const file = findFileById(fileId);
    if (!file) return;

    const modal = new bootstrap.Modal(document.getElementById('fileModal'));
    document.getElementById('fileModalTitle').textContent = file.original_filename || file.filename;

    const isOwner = !file.shared_file && !file.is_shared;

    let content = `
        <div class="mb-3">
            <p><strong>Имя файла:</strong> ${file.original_filename || file.filename}</p>
            <p><strong>Размер:</strong> ${formatFileSize(file.size)}</p>
            <p><strong>Дата создания:</strong> ${new Date(file.created_at || file.uploaded_at).toLocaleString()}</p>
            <p><strong>Статус:</strong> ${isOwner ? 'Владелец' : 'Доступ предоставлен'}</p>
        </div>
        
        <div class="d-grid gap-2">
            <button class="btn btn-primary" onclick="downloadFile(${fileId})">
                <i class="bi bi-download me-2"></i>Скачать файл
            </button>
    `;

    if (isOwner) {
        content += `
            <button class="btn btn-outline-danger" onclick="deleteFile(${fileId})">
                <i class="bi bi-trash me-2"></i>Удалить файл
            </button>
        `;
    }

    content += `</div>`;

    document.getElementById('fileModalContent').innerHTML = content;
    modal.show();
}

async function deleteFile(fileId) {
    if (!confirm('Вы уверены, что хотите удалить этот файл?')) return;

    try {
        const response = await fetch(`${API_BASE}/files/${fileId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            showToast('Файл успешно удален', 'success');
            await loadFiles();
            bootstrap.Modal.getInstance(document.getElementById('fileModal')).hide();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Ошибка удаления', 'danger');
        }
    } catch (error) {
        showToast('Ошибка соединения', 'danger');
    }
}

function findFileById(fileId) {
    if (!filesData) return null;

    // Ищем во всех файлах
    const allFiles = [
        ...(filesData.files?.owned || []),
        ...(filesData.files?.shared || []),
        ...(filesData.files || [])
    ];
    return allFiles.find(file => file.id === fileId);
}

async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });

        localStorage.removeItem('isAuthenticated');
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Logout error:', error);
    }
}

function showToast(message, type = 'info') {
    const container = document.querySelector('.toast-container');
    if (!container) return;

    const toastId = 'toast-' + Date.now();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('id', toastId);

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });

    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Auto-refresh token every 25 minutes
setInterval(async () => {
    try {
        await fetch(`${API_BASE}/auth/refresh`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.log('Token refresh failed');
    }
}, 25 * 60 * 1000);