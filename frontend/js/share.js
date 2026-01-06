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
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE}/share/${token}`, {
            credentials: 'include'
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // Получаем имя файла из заголовков или из ответа
            const filename = response.headers.get('Content-Disposition')?.match(/filename="(.+)"/)?.[1]
                || response.headers.get('X-Filename')
                || 'file';

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Обновляем информацию после скачивания
            setTimeout(() => loadShareInfo(), 1000);
        } else if (response.status === 410) {
            showExpired();
        } else if (response.status === 404) {
            showError('Ссылка не найдена');
        } else {
            showError('Ошибка скачивания файла');
        }
    } catch (error) {
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

document.addEventListener('DOMContentLoaded', loadShareInfo);