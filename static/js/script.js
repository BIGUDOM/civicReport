const API_BASE_URL = "/api";
const SOCKET_URL = "/";

const state = { user: null, token: localStorage.getItem('civicreport_token'), categories: [], incidents: [], notifications: [], socket: null };

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}

function showLoading(buttonId, isLoading, originalText = '') {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    if (isLoading) { btn.dataset.originalText = btn.textContent; btn.textContent = 'Loading...'; btn.disabled = true; } 
    else { btn.textContent = btn.dataset.originalText || originalText; btn.disabled = false; }
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

async function apiRequest(endpoint, options = {}) {
    const headers = { ...options.headers };
    if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'An error occurred');
        return data;
    } catch (error) { console.error('API Error:', error); throw error; }
}

function navigateTo(pageId) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    const targetPage = document.getElementById(pageId);
    if (targetPage) targetPage.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageId) item.classList.add('active');
    });
    const bottomNav = document.getElementById('bottom-nav');
    if (['welcome-page', 'signup-page', 'login-page'].includes(pageId)) bottomNav.classList.add('hidden');
    else bottomNav.classList.remove('hidden');
    
    if (pageId === 'dashboard-page') loadDashboard();
    if (pageId === 'my-reports-page') loadMyReports();
    if (pageId === 'notifications-page') loadNotifications();
    if (pageId === 'profile-page') loadProfile();
    if (pageId === 'report-page') loadReportCategories();
}

async function handleSignup(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    if (data.password !== data.confirm_password) { document.getElementById('error-signup-confirm').textContent = 'Passwords do not match'; return; }
    showLoading('btn-signup-submit', true);
    try {
        await apiRequest('/auth/register', { method: 'POST', body: JSON.stringify({ full_name: data.full_name, email: data.email, phone: data.phone, password: data.password }) });
        showToast('Account created successfully!', 'success');
        navigateTo('login-page');
        form.reset();
    } catch (error) { showToast(error.message, 'error'); } 
    finally { showLoading('btn-signup-submit', false); }
}

async function handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    showLoading('btn-login-submit', true);
    try {
        const response = await apiRequest('/auth/login', { method: 'POST', body: JSON.stringify({ email: data.email, password: data.password }) });
        state.token = response.token;
        state.user = response.user;
        localStorage.setItem('civicreport_token', response.token);
        showToast('Login successful!', 'success');
        navigateTo('dashboard-page');
        form.reset();
        initSocket();
    } catch (error) { showToast(error.message, 'error'); } 
    finally { showLoading('btn-login-submit', false); }
}

async function handleLogout() {
    try { await apiRequest('/auth/logout', { method: 'POST' }); } catch (e) {}
    state.token = null; state.user = null; localStorage.removeItem('civicreport_token');
    if (state.socket) { state.socket.disconnect(); state.socket = null; }
    showToast('Logged out successfully', 'info');
    navigateTo('welcome-page');
}

async function checkAuth() {
    if (!state.token) return false;
    try { const response = await apiRequest('/auth/me'); state.user = response.user; return true; } 
    catch (error) { state.token = null; localStorage.removeItem('civicreport_token'); return false; }
}

async function loadDashboard() {
    if (state.user) document.getElementById('user-greeting').textContent = `Welcome, ${state.user.full_name.split(' ')[0]}`;
    const listContainer = document.getElementById('incidents-list');
    listContainer.innerHTML = '<div class="loading-state">Loading incidents...</div>';
    try {
        const response = await apiRequest('/incidents');
        state.incidents = response.incidents || [];
        renderIncidents(state.incidents, listContainer);
    } catch (error) { listContainer.innerHTML = '<div class="empty-state">Unable to connect to CivicReport server. Please check your internet connection.</div>'; }
}

function renderIncidents(incidents, container) {
    if (!incidents || incidents.length === 0) { container.innerHTML = '<div class="empty-state">No incidents reported yet.</div>'; return; }
    container.innerHTML = incidents.map(inc => `
        <div class="incident-card" data-id="${inc.id}">
            <div class="incident-card-header"><h3>${escapeHtml(inc.title)}</h3><span class="badge ${inc.status === 'urgent' ? 'urgent' : ''}">${escapeHtml(inc.category_name || 'Unknown')}</span></div>
            <div class="incident-card-meta">📍 ${escapeHtml(inc.location)} • 🕒 ${formatDateTime(inc.created_at)}</div>
            <div class="incident-card-desc">${escapeHtml(inc.description)}</div>
            ${inc.image_url ? `<img src="${inc.image_url}" class="incident-card-image" alt="Incident image" onerror="this.style.display='none'">` : ''}
        </div>`).join('');
    container.querySelectorAll('.incident-card').forEach(card => {
        card.addEventListener('click', () => {
            const incident = state.incidents.find(i => i.id == card.dataset.id);
            if (incident) showIncidentModal(incident);
        });
    });
}

async function loadCategories() {
    try {
        const response = await apiRequest('/categories');
        state.categories = response.categories || [];
        const filterSelect = document.getElementById('category-filter');
        filterSelect.innerHTML = '<option value="all">All Categories</option>';
        state.categories.forEach(cat => { filterSelect.innerHTML += `<option value="${cat.id}">${escapeHtml(cat.name)}</option>`; });
        const reportSelect = document.getElementById('report-category');
        reportSelect.innerHTML = '<option value="">Select a category</option>';
        state.categories.forEach(cat => { reportSelect.innerHTML += `<option value="${cat.id}">${escapeHtml(cat.name)}</option>`; });
    } catch (error) { console.error('Failed to load categories', error); }
}

function loadReportCategories() { if (state.categories.length === 0) loadCategories(); }

document.getElementById('btn-use-location').addEventListener('click', () => {
    const statusEl = document.getElementById('location-status');
    statusEl.textContent = 'Getting location...';
    if (!navigator.geolocation) { statusEl.textContent = 'Geolocation is not supported.'; return; }
    navigator.geolocation.getCurrentPosition(
        (position) => {
            document.getElementById('report-lat').value = position.coords.latitude;
            document.getElementById('report-lng').value = position.coords.longitude;
            document.getElementById('report-location-text').value = `Lat: ${position.coords.latitude.toFixed(4)}, Lng: ${position.coords.longitude.toFixed(4)}`;
            statusEl.textContent = 'Location acquired successfully.';
            statusEl.style.color = 'var(--success-color)';
        },
        (error) => { statusEl.textContent = 'Unable to retrieve location. Please enter manually.'; statusEl.style.color = 'var(--danger-color)'; },
        { enableHighAccuracy: true, timeout: 10000 }
    );
});

const imageInput = document.getElementById('report-image');
const imagePreview = document.getElementById('image-preview');
const uploadPlaceholder = document.querySelector('.upload-placeholder');
const btnRemoveImage = document.getElementById('btn-remove-image');

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        if (file.size > 5 * 1024 * 1024) { showToast('Image must be less than 5MB', 'error'); imageInput.value = ''; return; }
        const reader = new FileReader();
        reader.onload = (e) => { imagePreview.src = e.target.result; imagePreview.classList.add('visible'); uploadPlaceholder.classList.add('hidden'); btnRemoveImage.classList.remove('hidden'); };
        reader.readAsDataURL(file);
    }
});

btnRemoveImage.addEventListener('click', () => {
    imageInput.value = ''; imagePreview.src = ''; imagePreview.classList.remove('visible'); uploadPlaceholder.classList.remove('hidden'); btnRemoveImage.classList.add('hidden');
});

async function handleReportSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const lat = document.getElementById('report-lat').value;
    const lng = document.getElementById('report-lng').value;
    if (!lat || !lng) { showToast('Please use "Use My Location" or enter coordinates', 'error'); return; }
    showLoading('btn-submit-report', true, 'Submit Report');
    try {
        await apiRequest('/incidents', { method: 'POST', body: formData });
        showToast('Incident reported successfully!', 'success');
        form.reset(); imagePreview.classList.remove('visible'); uploadPlaceholder.classList.remove('hidden'); btnRemoveImage.classList.add('hidden');
        document.getElementById('location-status').textContent = '';
        navigateTo('dashboard-page');
    } catch (error) { showToast(error.message, 'error'); } 
    finally { showLoading('btn-submit-report', false, 'Submit Report'); }
}

async function loadMyReports() {
    const container = document.getElementById('my-reports-list');
    container.innerHTML = '<div class="loading-state">Loading your reports...</div>';
    try {
        const response = await apiRequest('/reports/my');
        const reports = response.reports || [];
        if (reports.length === 0) { container.innerHTML = '<div class="empty-state">You have not reported any incidents yet.</div>'; return; }
        container.innerHTML = reports.map(inc => `
            <div class="incident-card" data-id="${inc.id}">
                <div class="incident-card-header"><h3>${escapeHtml(inc.title)}</h3><span class="badge">${escapeHtml(inc.category_name || 'Unknown')}</span></div>
                <div class="incident-card-meta">📍 ${escapeHtml(inc.location)} • 🕒 ${formatDateTime(inc.created_at)}</div>
                <div class="incident-card-desc">Status: ${inc.status}</div>
            </div>`).join('');
    } catch (error) { container.innerHTML = '<div class="empty-state">Unable to load reports.</div>'; }
}

async function loadNotifications() {
    const container = document.getElementById('notifications-list');
    container.innerHTML = '<div class="loading-state">Loading notifications...</div>';
    try {
        const response = await apiRequest('/notifications');
        state.notifications = response.notifications || [];
        renderNotifications();
        updateNotificationBadge();
    } catch (error) { container.innerHTML = '<div class="empty-state">Unable to load notifications.</div>'; }
}

function renderNotifications() {
    const container = document.getElementById('notifications-list');
    if (state.notifications.length === 0) { container.innerHTML = '<div class="empty-state">No notifications.</div>'; return; }
    container.innerHTML = state.notifications.map(notif => `
        <div class="notification-item ${notif.is_read ? '' : 'unread'}" data-id="${notif.id}">
            <h4>${escapeHtml(notif.title)}</h4><p>${escapeHtml(notif.description)}</p><time>${formatDateTime(notif.created_at)}</time>
        </div>`).join('');
    container.querySelectorAll('.notification-item.unread').forEach(item => {
        item.addEventListener('click', async () => {
            const id = item.dataset.id;
            try {
                await apiRequest(`/notifications/${id}/read`, { method: 'PATCH' });
                item.classList.remove('unread');
                const notif = state.notifications.find(n => n.id == id);
                if (notif) notif.is_read = 1;
                updateNotificationBadge();
            } catch (error) { console.error('Failed to mark as read', error); }
        });
    });
}

function updateNotificationBadge() {
    const unreadCount = state.notifications.filter(n => !n.is_read).length;
    const badge = document.getElementById('nav-notification-badge');
    if (unreadCount > 0) { badge.textContent = unreadCount; badge.classList.remove('hidden'); } 
    else { badge.classList.add('hidden'); }
}

document.getElementById('btn-mark-all-read').addEventListener('click', async () => {
    try {
        await apiRequest('/notifications/read-all', { method: 'PATCH' });
        state.notifications.forEach(n => n.is_read = 1);
        renderNotifications(); updateNotificationBadge();
        showToast('All notifications marked as read', 'success');
    } catch (error) { showToast('Failed to mark all as read', 'error'); }
});

async function loadProfile() {
    if (!state.user) return;
    document.getElementById('profile-name').value = state.user.full_name;
    document.getElementById('profile-email').value = state.user.email;
    document.getElementById('profile-phone').value = state.user.phone;
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    showLoading('btn-update-profile', true, 'Save Changes');
    try {
        const response = await apiRequest('/users/me', { method: 'PUT', body: JSON.stringify({ full_name: data.full_name, phone: data.phone }) });
        state.user = response.user;
        showToast('Profile updated successfully', 'success');
    } catch (error) { showToast(error.message, 'error'); } 
    finally { showLoading('btn-update-profile', false, 'Save Changes'); }
}

function showIncidentModal(incident) {
    document.getElementById('modal-title').textContent = incident.title;
    document.getElementById('modal-category').textContent = incident.category_name || 'Unknown';
    document.getElementById('modal-date').textContent = formatDateTime(incident.created_at);
    document.getElementById('modal-location').textContent = incident.location;
    document.getElementById('modal-lat').textContent = incident.latitude;
    document.getElementById('modal-lng').textContent = incident.longitude;
    document.getElementById('modal-description').textContent = incident.description;
    document.getElementById('modal-status').textContent = incident.status;
    document.getElementById('modal-reporter').textContent = incident.reporter_name || 'Anonymous';
    const imgEl = document.getElementById('modal-image');
    if (incident.image_url) { imgEl.src = incident.image_url; imgEl.style.display = 'block'; } 
    else { imgEl.style.display = 'none'; }
    document.getElementById('incident-modal').classList.add('active');
}

document.querySelector('.modal-close').addEventListener('click', () => { document.getElementById('incident-modal').classList.remove('active'); });
document.getElementById('incident-modal').addEventListener('click', (e) => { if (e.target.id === 'incident-modal') document.getElementById('incident-modal').classList.remove('active'); });

function initSocket() {
    if (!state.token || state.socket) return;
    state.socket = io(SOCKET_URL, { auth: { token: state.token } });
    state.socket.on('connect', () => console.log('Socket connected'));
    state.socket.on('new_incident', (data) => {
        showToast(`New incident reported: ${data.title}`, 'info');
        if (document.getElementById('dashboard-page').classList.contains('active')) {
            state.incidents.unshift(data);
            renderIncidents(state.incidents, document.getElementById('incidents-list'));
        }
        state.notifications.unshift({ id: Date.now(), title: 'New Incident Reported', description: `A new ${data.category_name} has been reported in your area.`, created_at: new Date().toISOString(), is_read: 0 });
        updateNotificationBadge();
    });
}

function escapeHtml(text) { if (!text) return ''; const div = document.createElement('div'); div.textContent = text; return div.innerHTML; }

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-get-started').addEventListener('click', () => navigateTo('signup-page'));
    document.getElementById('btn-login-nav').addEventListener('click', () => navigateTo('login-page'));
    document.getElementById('btn-signup-nav').addEventListener('click', () => navigateTo('signup-page'));
    document.getElementById('link-to-login').addEventListener('click', (e) => { e.preventDefault(); navigateTo('login-page'); });
    document.getElementById('link-to-signup').addEventListener('click', (e) => { e.preventDefault(); navigateTo('signup-page'); });
    document.querySelectorAll('.btn-back').forEach(btn => { btn.addEventListener('click', () => navigateTo('dashboard-page')); });
    document.querySelectorAll('.nav-item').forEach(item => { item.addEventListener('click', (e) => { e.preventDefault(); navigateTo(item.dataset.page); }); });
    document.getElementById('signup-form').addEventListener('submit', handleSignup);
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('report-form').addEventListener('submit', handleReportSubmit);
    document.getElementById('profile-form').addEventListener('submit', handleProfileUpdate);
    document.getElementById('btn-logout').addEventListener('click', handleLogout);
    document.querySelectorAll('.toggle-password').forEach(btn => { btn.addEventListener('click', () => { const input = btn.previousElementSibling; input.type = input.type === 'password' ? 'text' : 'password'; }); });
    document.getElementById('category-filter').addEventListener('change', (e) => {
        const categoryId = e.target.value;
        if (categoryId === 'all') renderIncidents(state.incidents, document.getElementById('incidents-list'));
        else renderIncidents(state.incidents.filter(inc => inc.category_id == categoryId), document.getElementById('incidents-list'));
    });
    loadCategories().then(() => {
        checkAuth().then(isAuth => {
            if (isAuth) { navigateTo('dashboard-page'); initSocket(); } 
            else { navigateTo('welcome-page'); }
        });
    });
});