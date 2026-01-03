async function loadFiles() {
    try {
        const res = await api.get("/files/");
        // Получаем файлы из разных возможных структур ответа
        const files = res.data.files || res.data.all_files || [];
        const filesList = document.getElementById("files-list");
        const noFiles = document.getElementById("no-files");

        filesList.innerHTML = "";

        if (files.length === 0) {
            if (!noFiles) {
                filesList.innerHTML = `
                    <div class="text-center py-5 text-muted" id="no-files">
                        <i class="bi bi-folder-x display-4 d-block mb-3"></i>
                        <p class="mb-0">No files uploaded yet</p>
                        <small>Upload your first file using the form above</small>
                    </div>
                `;
            }
            return;
        }

        // Remove no files message if exists
        if (noFiles) noFiles.remove();

        files.forEach(file => {
            // Используем file.size вместо file.file_size
            const fileSize = formatFileSize(file.size || file.file_size || 0);
            // Используем file.created_at вместо file.uploaded_at
            const uploadDate = formatDate(file.created_at || file.uploaded_at);

            const fileCard = document.createElement("div");
            fileCard.className = "file-card card p-3 mb-3";
            fileCard.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="file-icon me-3">
                        <i class="bi ${getFileIcon(file.original_filename || file.name)} text-primary fs-3"></i>
                    </div>
                    <div class="file-info">
                        <h6 class="mb-1 fw-bold text-truncate">${file.original_filename || file.name}</h6>
                        <div class="text-muted small">
                            <span class="me-3"><i class="bi bi-hdd me-1"></i>${fileSize}</span>
                            <span><i class="bi bi-calendar me-1"></i>${uploadDate}</span>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-sm btn-outline-primary me-2" 
                                onclick="downloadFile(${file.id}, '${escapeHtml(file.original_filename || file.name)}')"
                                title="Download">
                            <i class="bi bi-download"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary me-2" 
                                onclick="shareFile(${file.id})"
                                title="Share">
                            <i class="bi bi-share"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="deleteFile(${file.id})"
                                title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            filesList.appendChild(fileCard);
        });

    } catch (error) {
        console.error('Error loading files:', error);
        throw error; // Propagate to show login if unauthorized
    }
}

// Upload file
async function uploadFile(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        showToast('Please select a file to upload', 'error');
        return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showToast('File size must be less than 10MB', 'error');
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const uploadBtn = event.target.querySelector('button[type="submit"]');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Uploading...';
    uploadBtn.disabled = true;

    try {
        const response = await api.post("/files/upload/", formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        showToast(`File "${file.name}" uploaded successfully`, 'success');
        fileInput.value = '';
        await loadFiles();

    } catch (error) {
        const errorMsg = error.response?.data?.message || "Failed to upload file";
        showToast(errorMsg, 'error');
        console.error('Upload error:', error);
    } finally {
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
    }
}

// Delete file with confirmation
async function deleteFile(id) {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
        const response = await api.delete(`/files/${id}`);
        showToast('File deleted successfully', 'success');
        await loadFiles();
    } catch (error) {
        if (error.response?.status === 404) {
            showToast('File not found', 'error');
        } else if (error.response?.status === 401) {
            showToast('Please login again', 'error');
            showLogin();
        } else {
            showToast('Failed to delete file', 'error');
        }
        console.error('Delete error:', error);
    }
}

// Download file
async function downloadFile(id, filename) {
    try {
        const response = await api.get(`/files/${id}/download`, {
            responseType: "blob"
        });

        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement("a");
        a.href = url;
        a.download = decodeURIComponent(filename);
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        showToast('Download started', 'success');
    } catch (error) {
        showToast('Failed to download file', 'error');
        console.error('Download error:', error);
    }
}

// Share file
async function shareFile(id) {
    const hours = prompt("How many hours should the file be available?", "24");
    const maxDownloads = prompt("Maximum number of downloads?", "1");

    if (!hours || !maxDownloads) return;

    try {
        const response = await api.post(`/share/${id}/`, {
            expires_hours: parseInt(hours),
            max_downloads: parseInt(maxDownloads)
        });

        const shareUrl = response.data.share_url || response.data.url;
        const fullUrl = `http://localhost:8000${shareUrl}`;

        // Copy to clipboard
        await navigator.clipboard.writeText(fullUrl);
        showToast('Share link copied to clipboard!', 'success');

    } catch (error) {
        showToast('Failed to create share link', 'error');
        console.error('Share error:', error);
    }
}

// Helper functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown date';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return 'Invalid date';
    }
}

function getFileIcon(filename) {
    if (!filename) return 'bi-file-earmark';

    const name = filename.toLowerCase();
    const ext = name.split('.').pop();

    const icons = {
        'pdf': 'bi-file-pdf',
        'doc': 'bi-file-word',
        'docx': 'bi-file-word',
        'xls': 'bi-file-excel',
        'xlsx': 'bi-file-excel',
        'ppt': 'bi-file-ppt',
        'pptx': 'bi-file-ppt',
        'jpg': 'bi-file-image',
        'jpeg': 'bi-file-image',
        'png': 'bi-file-image',
        'gif': 'bi-file-image',
        'zip': 'bi-file-zip',
        'rar': 'bi-file-zip',
        'txt': 'bi-file-text',
        'mp3': 'bi-file-music',
        'mp4': 'bi-file-play',
        'avi': 'bi-file-play',
        'mov': 'bi-file-play'
    };

    return icons[ext] || 'bi-file-earmark';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}