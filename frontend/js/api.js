// API Configuration
const api = axios.create({
    baseURL: "http://localhost:8000",
    withCredentials: true,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

// Request interceptor for adding auth token if needed
api.interceptors.request.use(
    config => {
        // You can add token here if using JWT
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// Response interceptor for handling errors globally
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response) {
            // Handle specific status codes
            switch (error.response.status) {
                case 401:
                    // Unauthorized - redirect to login
                    showLogin();
                    showToast('Session expired. Please login again.', 'error');
                    break;
                case 403:
                    showToast('Access forbidden', 'error');
                    break;
                case 404:
                    showToast('Resource not found', 'error');
                    break;
                case 500:
                    showToast('Server error occurred', 'error');
                    break;
            }
        } else if (error.request) {
            showToast('Network error. Please check your connection.', 'error');
        }
        return Promise.reject(error);
    }
);