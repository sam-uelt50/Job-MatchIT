
// frontend/js/api.js - Complete API Integration for AI Recruitment Platform

// API Base URL - Change this if your backend is on a different port
const API_BASE = "https://job-matchit.onrender.com/api";

// Helper function to handle API responses
async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

// API Service Object
const api = {
    // ============================================
    // AUTHENTICATION ENDPOINTS
    // ============================================
    auth: {
        // Register a new job seeker (candidate)
        registerUser: async (userData) => {
            const response = await fetch(`${API_BASE}/auth/register/user`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });
            return handleResponse(response);
        },
        
        // Register a new company (employer)
        registerCompany: async (companyData) => {
            const response = await fetch(`${API_BASE}/auth/register/company`, {
                method: 'POST',
                headers: {
                    'Content-Type':application/json'
                },
                body: JSON.stringify(companyData)
            });
            return handleResponse(response);
        },
        
        // Login (both user and company)
        login: async (email, password) => {
            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            return handleResponse(response);
        },
        
        // Refresh access token
        refreshToken: async (refreshToken) => {
            const response = await fetch(`${API_BASE}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            return handleResponse(response);
        }
    },
    
    // ============================================
    // USER (CANDIDATE) ENDPOINTS
    // ============================================
    user: {
        // Upload and parse resume (supports PDF, DOCX, TXT, Images)
        uploadResume: async (userId, file) => {
            const formData = new FormData();
            formData.append('resume_file', file);
            
            const response = await fetch(`${API_BASE}/user/upload-resume?user_id=${userId}`, {
                method: 'POST',
                body: formData
                // Do NOT set Content-Type header - let browser set it with boundary
            });
            return handleResponse(response);
        },
        
        // Get personalized job recommendations
        getRecommendations: async (userId, limit = 10) => {
            const response = await fetch(`${API_BASE}/user/recommendations?user_id=${userId}&limit=${limit}`);
            return handleResponse(response);
        },
        
        // Apply for a specific job
        applyForJob: async (userId, jobId, coverLetter = '') => {
            const response = await fetch(`${API_BASE}/user/apply/${jobId}?user_id=${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cover_letter: coverLetter })
            });
            return handleResponse(response);
        },
        
        // Get user's job applications
        getApplications: async (userId) => {
            const response = await fetch(`${API_BASE}/user/applications?user_id=${userId}`);
            return handleResponse(response);
        },
        
        // Get user profile
        getProfile: async (userId) => {
            const response = await fetch(`${API_BASE}/user/profile?user_id=${userId}`);
            return handleResponse(response);
        },
        
        // Update user profile
        updateProfile: async (userId, profileData) => {
            const response = await fetch(`${API_BASE}/user/profile?user_id=${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });
            return handleResponse(response);
        }
    },
    
    // ============================================
    // COMPANY (EMPLOYER) ENDPOINTS
    // ============================================
    company: {
        // Create a new job posting
        createJob: async (companyId, jobData) => {
            const response = await fetch(`${API_BASE}/company/jobs?company_id=${companyId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jobData)
            });
            return handleResponse(response);
        },
        
        // Get all jobs for a company
        getJobs: async (companyId) => {
            const response = await fetch(`${API_BASE}/company/jobs?company_id=${companyId}`);
            return handleResponse(response);
        },
        
        // Get a specific job by ID
        getJobById: async (jobId) => {
            const response = await fetch(`${API_BASE}/company/jobs/${jobId}`);
            return handleResponse(response);
        },
        
        // Update a job posting
        updateJob: async (jobId, companyId, jobData) => {
            const response = await fetch(`${API_BASE}/company/jobs/${jobId}?company_id=${companyId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jobData)
            });
            return handleResponse(response);
        },
        
        // Delete a job posting
        deleteJob: async (jobId, companyId) => {
            const response = await fetch(`${API_BASE}/company/jobs/${jobId}?company_id=${companyId}`, {
                method: 'DELETE'
            });
            return handleResponse(response);
        },
        
        // Get candidates ranked for a specific job
        getCandidates: async (jobId) => {
            const response = await fetch(`${API_BASE}/company/jobs/${jobId}/candidates`);
            return handleResponse(response);
        },
        
        // Shortlist a candidate for a job
        shortlistCandidate: async (jobId, userId) => {
            const response = await fetch(`${API_BASE}/company/jobs/${jobId}/shortlist/${userId}`, {
                method: 'POST'
            });
            return handleResponse(response);
        },
        
        // Get company profile
        getProfile: async (companyId) => {
            const response = await fetch(`${API_BASE}/company/profile?company_id=${companyId}`);
            return handleResponse(response);
        },
        
        // Update company profile
        updateProfile: async (companyId, profileData) => {
            const response = await fetch(`${API_BASE}/company/profile?company_id=${companyId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });
            return handleResponse(response);
        }
    },
    
    // ============================================
    // PUBLIC ENDPOINTS
    // ============================================
    public: {
        // Get all active jobs (no authentication required)
        getAllJobs: async (skip = 0, limit = 50) => {
            const response = await fetch(`${API_BASE}/jobs?skip=${skip}&limit=${limit}`);
            return handleResponse(response);
        },
        
        // Get a specific job by ID
        getJobById: async (jobId) => {
            const response = await fetch(`${API_BASE}/jobs/${jobId}`);
            return handleResponse(response);
        },
        
        // Search jobs by keyword
        searchJobs: async (keyword) => {
            const response = await fetch(`${API_BASE}/jobs/search?q=${encodeURIComponent(keyword)}`);
            return handleResponse(response);
        },
        
        // Health check
        health: async () => {
            const response = await fetch(`https://job-matchit.onrender.com`);
            return response.json();
        }
    }
};

// ============================================
// STORAGE HELPER FUNCTIONS
// ============================================

// Save authentication data to localStorage
function saveAuthData(token, user) {
    localStorage.setItem('authToken', token);
    localStorage.setItem('currentUser', JSON.stringify(user));
}

// Get authentication token from localStorage
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Get current user from localStorage
function getCurrentUser() {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
}

// Clear authentication data (logout)
function clearAuthData() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Get user type (user or company)
function getUserType() {
    const user = getCurrentUser();
    return user ? user.user_type : null;
}

// Get user ID
function getUserId() {
    const user = getCurrentUser();
    return user ? user.user_id : null;
}

// ============================================
// EXPORT FOR USE IN OTHER FILES
// ============================================

// Make api available globally
window.api = api;
window.saveAuthData = saveAuthData;
window.getAuthToken = getAuthToken;
window.getCurrentUser = getCurrentUser;
window.clearAuthData = clearAuthData;
window.isAuthenticated = isAuthenticated;
window.getUserType = getUserType;
window.getUserId = getUserId;

console.log('✅ API module loaded. Backend URL:', API_BASE);