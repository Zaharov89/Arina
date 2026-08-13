const levelsConfig = window.typingLevelsPageConfig;
const progressCard = document.getElementById('typingProgressCard');
const levelGrid = document.getElementById('typingLevelGrid');
const attemptsContainer = document.getElementById('typingRecentAttempts');
const authWarning = document.getElementById('typingAuthWarning');

function getAuthStorage() {
    if (localStorage.getItem('arinaAccessToken')) return localStorage;
    if (sessionStorage.getItem('arinaAccessToken')) return sessionStorage;
    return null;
}

function getToken() {
    const storage = getAuthStorage();
    return storage ? storage.getItem('arinaAccessToken') : '';
}

function fmt(value, suffix = '') {
    const number = Number(value || 0);
    return `${Math.round(number)}${suffix}`;
}

function renderProgress(progress) {
    const animal = levelsConfig.animals[progress.animal_code] || levelsConfig.animals.dino;
    progressCard.innerHTML = `
        <div class="typing-progress-main">
            <div class="typing-progress-animal">${animal.emoji}</div>
            <div>
                <h2>${animal.title}</h2>
                <p>Открыто до уровня: <strong>${progress.max_unlocked_level}</strong></p>
                <p>Всего попыток: <strong>${progress.total_attempts}</strong></p>
            </div>
        </div>
        <div class="typing-progress-stats">
            <span>Лучшая точность: <strong>${fmt(progress.best_accuracy, '%')}</strong></span>
            <span>Лучшая скорость: <strong>${fmt(progress.best_speed_cpm, ' зн/мин')}</strong></span>
        </div>
    `;
}

function levelStatusTitle(status) {
    if (status === 'passed') return 'Пройден';
    if (status === 'current') return 'Текущий';
    if (status === 'unlocked') return 'Открыт';
    return 'Закрыт';
}

function renderLevels(levels, progress) {
    levelGrid.innerHTML = '';
    levels.forEach(level => {
        const card = document.createElement('div');
        card.className = `typing-level-card ${level.status}`;
        const letters = (level.letters || []).map(letter => `<span>${letter}</span>`).join('');
        const best = level.best || {};
        const action = level.is_unlocked
            ? `<a class="typing-btn green-btn" href="/typing-trainer/game?layout=${encodeURIComponent(levelsConfig.layoutCode)}&animal=${encodeURIComponent(progress.animal_code)}&level=${level.level}&student=${encodeURIComponent(levelsConfig.student)}">Играть</a>`
            : `<button class="typing-btn locked-btn" disabled>Закрыт</button>`;
        card.innerHTML = `
            <div class="typing-level-top">
                <strong>Уровень ${level.level}</strong>
                <span>${levelStatusTitle(level.status)}</span>
            </div>
            <h3>${level.title}</h3>
            <div class="typing-level-letters small">${letters}</div>
            <p>Нужно: ${level.required_accuracy}% точности</p>
            ${best.best_accuracy ? `<p>Лучшее: ${fmt(best.best_accuracy, '%')} / ${fmt(best.best_speed_cpm, ' зн/мин')}</p>` : '<p>Попыток ещё нет</p>'}
            ${action}
        `;
        levelGrid.appendChild(card);
    });
}

function renderAttempts(attempts) {
    if (!attempts || attempts.length === 0) {
        attemptsContainer.textContent = 'Пока нет сохранённых попыток.';
        return;
    }
    attemptsContainer.innerHTML = `
        <div class="typing-attempt-table">
            ${attempts.map(attempt => `
                <div class="typing-attempt-row">
                    <span>Ур. ${attempt.level_number}</span>
                    <span>${attempt.is_passed ? 'Пройден' : 'Не пройден'}</span>
                    <span>${fmt(attempt.accuracy_percent, '%')}</span>
                    <span>${fmt(attempt.speed_cpm, ' зн/мин')}</span>
                </div>
            `).join('')}
        </div>
    `;
}

async function loadLevels() {
    const token = getToken();
    if (!token) {
        authWarning.style.display = 'block';
        progressCard.textContent = 'Войди в аккаунт, чтобы открыть уровни и сохранять прогресс.';
        return;
    }
    const response = await fetch(`/api/typing-trainer/levels?layout=${encodeURIComponent(levelsConfig.layoutCode)}`, {
        headers: {Authorization: `Bearer ${token}`}
    });
    const data = await response.json();
    if (data.status !== 'ok') {
        progressCard.textContent = data.message || 'Не удалось загрузить прогресс.';
        return;
    }
    renderProgress(data.progress);
    renderLevels(data.levels, data.progress);
    renderAttempts(data.recent_attempts);
}

loadLevels().catch(error => {
    console.error('typing levels failed', error);
    progressCard.textContent = 'Ошибка загрузки уровней.';
});
