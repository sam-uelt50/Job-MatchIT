// Professional JavaScript for AI Recruitment Platform

// ============ GLOBAL UTILITIES ============

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.createContainer();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        this.container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(this.container);
    }

    show(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${icons[type] || icons.success}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        toast.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 12px 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            min-width: 280px;
            animation: slideInRight 0.3s ease;
            border-left: 4px solid ${type === 'success' ? '#06d6a0' : type === 'error' ? '#ef476f' : type === 'warning' ? '#ffd166' : '#4361ee'};
        `;
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            color: #999;
        `;
        
        closeBtn.onclick = () => {
            toast.remove();
        };
        
        this.container.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, duration);
    }
}

// Loading Overlay
class LoadingOverlay {
    constructor() {
        this.overlay = null;
    }

    show(message = 'Loading...') {
        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
        `;
        
        this.overlay.innerHTML = `
            <div class="spinner"></div>
            <p style="margin-top: 20px;">${message}</p>
        `;
        
        document.body.appendChild(this.overlay);
    }

    hide() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }
}

// Confetti Effect
function showConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#4361ee', '#7209b7', '#06d6a0', '#ffd166', '#ef476f']
        });
    }
}

// Format Date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
}

// Format Match Score
function formatMatchScore(score) {
    const num = parseFloat(score);
    if (num >= 90) return { class: 'match-excellent', icon: '🏆', text: 'Excellent Match' };
    if (num >= 75) return { class: 'match-great', icon: '⭐', text: 'Great Match' };
    if (num >= 60) return { class: 'match-good', icon: '👍', text: 'Good Match' };
    if (num >= 45) return { class: 'match-potential', icon: '📌', text: 'Potential Match' };
    return { class: 'match-low', icon: '⚠️', text: 'Low Match' };
}

// Escape HTML
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Get greeting based on time of day
function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
}

// Animate number counter
function animateNumber(element, target, suffix = '') {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.innerText = target + suffix;
            clearInterval(timer);
        } else {
            element.innerText = Math.floor(current) + suffix;
        }
    }, 20);
}

// ============ ANIMATION EFFECTS ============

// Scroll animations
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-up, .zoom-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => observer.observe(el));
}

// Particle background effect
function initParticleBackground() {
    const bg = document.getElementById('animatedBg');
    if (!bg) return;
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('span');
        const size = Math.random() * 30 + 5;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 20 + 's';
        particle.style.animationDuration = Math.random() * 10 + 10 + 's';
        bg.appendChild(particle);
    }
}

// ============ FORM VALIDATION ============

class FormValidator {
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    static validatePhone(phone) {
        const re = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,5}[-\s\.]?[0-9]{1,5}$/;
        return re.test(phone);
    }
    
    static validatePassword(password) {
        return password.length >= 6;
    }
    
    static validateRequired(value) {
        return value && value.trim().length > 0;
    }
}

// ============ STORAGE MANAGER ============

class StorageManager {
    static set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }
    
    static get(key, defaultValue = null) {
        const value = localStorage.getItem(key);
        if (value) {
            try {
                return JSON.parse(value);
            } catch {
                return value;
            }
        }
        return defaultValue;
    }
    
    static remove(key) {
        localStorage.removeItem(key);
    }
    
    static clear() {
        localStorage.clear();
    }
}

// ============ API CLIENT ============

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }
        
        return response.json();
    }
    
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
    
    upload(endpoint, formData) {
        return fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            body: formData
        }).then(res => res.json());
    }
}

// ============ CHART UTILITIES ============

class ChartManager {
    static createDoughnutChart(ctx, data, labels, colors) {
        if (window.myChart) window.myChart.destroy();
        
        window.myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    static createLineChart(ctx, labels, data, label) {
        if (window.lineChart) window.lineChart.destroy();
        
        window.lineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }
    
    static createBarChart(ctx, labels, data, label, colors) {
        if (window.barChart) window.barChart.destroy();
        
        window.barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: colors || '#4361ee',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }
}

// ============ EXPORT FUNCTIONS ============

function exportToCSV(data, filename) {
    const headers = Object.keys(data[0]);
    const csvRows = [];
    
    csvRows.push(headers.join(','));
    
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header] || '';
            return `"${String(value).replace(/"/g, '""')}"`;
        });
        csvRows.push(values.join(','));
    }
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// ============ KEYBOARD SHORTCUTS ============

class KeyboardShortcuts {
    constructor() {
        this.shortcuts = {};
        this.init();
    }
    
    init() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch(e.key) {
                    case 'u':
                        e.preventDefault();
                        document.getElementById('uploadArea')?.click();
                        break;
                    case 'j':
                        e.preventDefault();
                        document.querySelector('[data-tab="jobs"]')?.click();
                        break;
                    case 'a':
                        e.preventDefault();
                        document.querySelector('[data-tab="applications"]')?.click();
                        break;
                }
            }
        });
    }
}

// ============ INITIALIZATION ============

const toast = new ToastManager();
const loading = new LoadingOverlay();
const api = new APIClient('https://job-matchit.onrender.com);
const keyboard = new KeyboardShortcuts();

// Export for use in other files
window.toast = toast;
window.loading = loading;
window.api = api;
window.showConfetti = showConfetti;
window.formatDate = formatDate;
window.formatMatchScore = formatMatchScore;
window.escapeHtml = escapeHtml;
window.getGreeting = getGreeting;
window.animateNumber = animateNumber;
window.exportToCSV = exportToCSV;
window.StorageManager = StorageManager;
window.FormValidator = FormValidator;
window.ChartManager = ChartManager;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initParticleBackground();
    initScrollAnimations();
    
    // Add animation classes to elements
    document.querySelectorAll('.card, .job-card, .feature-item').forEach(el => {
        el.classList.add('fade-in');
    });
});