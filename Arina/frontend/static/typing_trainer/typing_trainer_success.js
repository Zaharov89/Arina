const successConfig = window.typingSuccessConfig || {};
const statusBox = document.getElementById('typingSuccessStatus');
const dashboard = document.getElementById('typingSuccessDashboard');

function getAuthStorage() {
    if (localStorage.getItem('arinaAccessToken')) return localStorage;
    if (sessionStorage.getItem('arinaAccessToken')) return sessionStorage;
    return null;
}

function getAccessToken() {
    const storage = getAuthStorage();
    return storage ? storage.getItem('arinaAccessToken') : '';
}

function roundValue(value) {
    return Math.round(Number(value || 0));
}

async function loadLayout(layoutCode) {
    const token = getAccessToken();
    if (!token) throw new Error('Для просмотра успехов нужно войти в аккаунт.');
    const response = await fetch(`/api/typing-trainer/levels?layout=${layoutCode}`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    if (!response.ok) throw new Error('Не удалось загрузить статистику тренажёра.');
    return response.json();
}

function passedCount(payload) {
    return (payload.levels || []).filter(level => level.is_passed).length;
}

function bestAccuracy(payload) {
    return Math.max(0, ...((payload.levels || []).map(level => Number(level.best && level.best.best_accuracy || 0))));
}

function bestSpeed(payload) {
    return Math.max(0, ...((payload.levels || []).map(level => Number(level.best && level.best.best_speed_cpm || 0))));
}

function nextLevel(payload) {
    const progress = payload.progress || {};
    return Number(progress.current_level || progress.max_unlocked_level || 1);
}

function layoutCard(payload, icon) {
    const total = (payload.levels || []).length;
    const passed = passedCount(payload);
    const opened = Number(payload.progress && payload.progress.max_unlocked_level || 1);
    const current = nextLevel(payload);
    const layout = payload.layout_code || 'ru';
    const animal = payload.progress && payload.progress.animal_code || 'dino';
    return `
        <div class="typing-progress-card typing-success-card">
            <div class="typing-success-head">
                <span class="typing-success-icon">${icon}</span>
                <div>
                    <h2>${payload.layout_title}</h2>
                    <p>${passed} из ${total} уровней пройдено</p>
                </div>
            </div>
            <div class="typing-result-stats">
                <span>Открыто: <strong>${opened}</strong></span>
                <span>Текущий: <strong>${current}</strong></span>
                <span>Лучшая точность: <strong>${roundValue(bestAccuracy(payload))}%</strong></span>
                <span>Лучшая скорость: <strong>${roundValue(bestSpeed(payload))} зн/мин</strong></span>
                <span>Попыток: <strong>${Number(payload.progress && payload.progress.total_attempts || 0)}</strong></span>
                <span>Прогресс: <strong>${total ? Math.round((passed / total) * 100) : 0}%</strong></span>
            </div>
            <div class="typing-success-progress"><span style="width:${total ? Math.round((passed / total) * 100) : 0}%"></span></div>
            <div class="typing-actions">
                <a class="typing-btn blue-btn" href="/typing-trainer/levels?layout=${layout}&student=${encodeURIComponent(successConfig.student || '')}">К уровням</a>
                <a class="typing-btn green-btn" href="/typing-trainer/game?layout=${layout}&animal=${animal}&level=${current}&student=${encodeURIComponent(successConfig.student || '')}">Продолжить</a>
            </div>
        </div>
    `;
}

function recentAttempts(payload) {
    const rows = (payload.recent_attempts || []).slice(0, 5);
    if (!rows.length) return '<p>Попыток пока нет.</p>';
    return rows.map(attempt => `
        <div class="typing-attempt-row">
            <span>${payload.layout_title}</span>
            <span>Ур. ${attempt.level_number}</span>
            <span>${roundValue(attempt.accuracy_percent)}%</span>
            <span>${roundValue(attempt.speed_cpm)} зн/мин</span>
        </div>
    `).join('');
}

function renderDashboard(ru, en) {
    const totalPassed = passedCount(ru) + passedCount(en);
    const totalLevels = (ru.levels || []).length + (en.levels || []).length;
    statusBox.style.display = 'none';
    dashboard.innerHTML = `
        <div class="typing-info-card typing-success-summary">
            <h2>Общий прогресс</h2>
            <div class="typing-result-stats">
                <span>Пройдено уровней: <strong>${totalPassed} из ${totalLevels}</strong></span>
                <span>Кириллица: <strong>${passedCount(ru)} уров.</strong></span>
                <span>Латиница: <strong>${passedCount(en)} уров.</strong></span>
                <span>Лучшее: <strong>${roundValue(Math.max(bestAccuracy(ru), bestAccuracy(en)))}%</strong></span>
            </div>
        </div>
        <div class="typing-card-grid">
            ${layoutCard(ru, 'ФЫВА')}
            ${layoutCard(en, 'ASDF')}
        </div>
        <div class="typing-info-card">
            <h2>Последние тренировки</h2>
            <div class="typing-attempt-table">
                ${recentAttempts(ru)}
                ${recentAttempts(en)}
            </div>
        </div>
    `;
}

async function initSuccessDashboard() {
    try {
        const [ru, en] = await Promise.all([loadLayout('ru'), loadLayout('en')]);
        renderDashboard(ru, en);
    } catch (error) {
        statusBox.textContent = error.message;
    }
}

initSuccessDashboard();
