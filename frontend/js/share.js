const API_BASE = 'http://localhost:8000';

function getTokenFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('token') || null;
}

async function loadShareInfo() {
    const token = getTokenFromUrl();
    if (!token) {
        showError('Неверная ссылка');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/share/${token}/info`);

        if (response.ok) {
            const data = await response.json();
            displayFileInfo(data);
        } else if (response.status === 404) {
            showError('Ссылка не найдена');
        } else if (response.status === 410) {
            showExpired();
        } else {
            showError('Ошибка загрузки информации');
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
    }
}

function displayFileInfo(data) {
    document.getElementById('share-info').classList.add('d-none');
    document.getElementById('share-content').classList.remove('d-none');

    document.getElementById('file-name').textContent = data.file.original_filename || data.file.filename;
    document.getElementById('file-size').textContent = formatFileSize(data.file.size);

    if (data.expires_at) {
        document.getElementById('file-expires').textContent =
            `Действует до: ${new Date(data.expires_at).toLocaleString()}`;
    }

    if (data.max_downloads > 0) {
        const downloadsLeft = data.max_downloads - (data.downloads_count || 0);
        document.getElementById('downloads-left').textContent =
            `Осталось скачиваний: ${downloadsLeft}`;

        if (downloadsLeft <= 0) {
            showMaxDownloadsReached();
        }
    }
}

async function downloadSharedFile() {
    const token = getTokenFromUrl();
    if (!token) {
        showError('Неверная ссылка');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/share/${token}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'file';
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                    filename = decodeURIComponent(filename);
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            setTimeout(() => {
                loadShareInfo();
                showToast('Файл успешно скачан', 'success');
            }, 1000);
            
        } else if (response.status === 404) {
            showError('Ссылка не найдена');
        } else if (response.status === 410) {
            const data = await response.json().catch(() => ({}));
            if (data.detail === 'Link expired') {
                showExpired();
            } else if (data.detail === 'Download limit reached') {
                showMaxDownloadsReached();
            } else {
                showError('Ссылка больше не действительна');
            }
        } else {
            showError('Ошибка скачивания файла');
        }
    } catch (error) {
        console.error('Download error:', error);
        showError('Ошибка соединения с сервером');
    }
}

function showExpired() {
    document.getElementById('share-info').classList.add('d-none');
    document.getElementById('share-content').classList.remove('d-none');
    document.getElementById('download-section').classList.add('d-none');
    document.getElementById('expired-message').classList.remove('d-none');
}

function showMaxDownloadsReached() {
    document.getElementById('download-section').classList.add('d-none');
    document.getElementById('max-downloads-message').classList.remove('d-none');
}

function showError(message) {
    document.getElementById('share-info').classList.add('d-none');
    document.getElementById('share-content').classList.remove('d-none');
    document.getElementById('download-section').classList.add('d-none');
    document.getElementById('error-message').classList.remove('d-none');
    document.getElementById('error-text').textContent = message;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `position-fixed bottom-0 end-0 m-3 toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

document.addEventListener('DOMContentLoaded', loadShareInfo);
