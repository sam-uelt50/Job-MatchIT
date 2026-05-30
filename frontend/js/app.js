// frontend/js/app.js - Shared API Functions
const API_BASE = 'http://localhost:8000/api';

// ============ AUTH FUNCTIONS ============
async function registerUser(userData) {
    const response = await fetch(`${API_BASE}/auth/register/user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    });
    return response.json();
}

async function registerCompany(companyData) {
    const response = await fetch(`${API_BASE}/auth/register/company`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(companyData)
    });
    return response.json();
}

async function login(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    return response.json();
}

// ============ USER FUNCTIONS ============
async function uploadResume(userId, file) {
    const formData = new FormData();
    formData.append('resume_file', file);
    
    const response = await fetch(`${API_BASE}/user/upload-resume?user_id=${userId}`, {
        method: 'POST',
        body: formData
    });
    return response.json();
}

async function getJobRecommendations(userId, limit = 10) {
    const response = await fetch(`${API_BASE}/user/recommendations?user_id=${userId}&limit=${limit}`);
    return response.json();
}

async function applyForJob(userId, jobId) {
    const response = await fetch(`${API_BASE}/user/apply/${jobId}?user_id=${userId}`, {
        method: 'POST'
    });
    return response.json();
}

async function getUserApplications(userId) {
    const response = await fetch(`${API_BASE}/user/applications?user_id=${userId}`);
    return response.json();
}

async function getUserNotifications(userId) {
    const response = await fetch(`${API_BASE}/user/notifications?user_id=${userId}`);
    return response.json();
}

async function markNotificationRead(notificationId, userId) {
    const response = await fetch(`${API_BASE}/user/notifications/${notificationId}/read?user_id=${userId}`, {
        method: 'PUT'
    });
    return response.json();
}

// ============ COMPANY FUNCTIONS ============
async function createJob(companyId, jobData) {
    const response = await fetch(`${API_BASE}/company/jobs?company_id=${companyId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jobData)
    });
    return response.json();
}

async function getCompanyJobs(companyId) {
    const response = await fetch(`${API_BASE}/company/jobs?company_id=${companyId}`);
    return response.json();
}

async function getJobApplications(jobId, companyId) {
    const response = await fetch(`${API_BASE}/company/jobs/${jobId}/applications?company_id=${companyId}`);
    return response.json();
}

async function updateApplicationStatus(jobId, applicationId, status, companyId) {
    const response = await fetch(`${API_BASE}/company/jobs/${jobId}/applications/${applicationId}/status?status=${status}&company_id=${companyId}`, {
        method: 'POST'
    });
    return response.json();
}

// ============ HELPER FUNCTIONS ============
function saveAuthData(token, userId, userType, name) {
    localStorage.setItem('token', token);
    localStorage.setItem('userId', userId);
    localStorage.setItem('userType', userType);
    localStorage.setItem('userName', name);
}

function clearAuthData() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('userType');
    localStorage.removeItem('userName');
}

function isAuthenticated() {
    return !!localStorage.getItem('token');
}

function getCurrentUser() {
    return {
        userId: localStorage.getItem('userId'),
        userType: localStorage.getItem('userType'),
        name: localStorage.getItem('userName')
    };
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification alert-${type}`;
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
        border-left: 4px solid ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getMatchScoreClass(score) {
    if (score >= 70) return 'match-high';
    if (score >= 50) return 'match-medium';
    return 'match-low';
}