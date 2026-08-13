const levelsConfig = window.typingLevelsConfig;
const progressState = document.getElementById('typingProgressState');
const levelsGrid = document.getElementById('typingLevelsGrid');
const recentAttempts = document.getElementById('typingRecentAttempts');
const animalLink = document.getElementById('typingAnimalLink');

function getAuthStorage() {
    if (localStorage.getItem('arinaAccessToken')) return localStorage;
    if (sessionStorage.getItem('arinaAccessToken')) return sessionStorage;
    return null;
}

function getAccessToken() {
    const storage = getAuthStorage();
    return storage ? storage.getItem('arinaAccessToken') : '';
}

function animalTitle(code) {
    return levelsConfig.animals?.[code]?.title || 'Динозаврик';
}

function animalEmoji(code) {
    return levelsConfig.animals?.[code]?.emoji || '🦖';
}

function formatPercent(value) {
    return `${Math.round(Number(value || 0))}%`;
}

function formatSpeed(value) {
    return `${Math.round(Number(value || 0))} зн/мин`;
}

function renderUnauthorized() {
    progressState.innerHTML = `
        <h2>Нужно войти в аккаунт</h2>
        <p>Прогресс клавиатурного тренажёра сохраняется отдельно для каждого пользователя. Войди в аккаунт, чтобы открыть уровни.</p>
        <div class="typing-actions"><a class="typing-btn blue-btn" href="/auth/login">Войти</a></div>
    `;
    levelsGrid.innerHTML = '';
}

function renderProgress(data) {
    const progress = data.progress;
    const animalCode = progress.animal_code || 'dino';
    animalLink.href = `/typing-trainer/animal?layout=${levelsConfig.layoutCode}&student=${encodeURIComponent(levelsConfig.student)}`;
    progressState.innerHTML = `
        <h2>Мой прогресс</h2>
        <div class="typing-progress-grid">
            <div><strong>${animalEmoji(animalCode)} ${animalTitle(animalCode)}</strong><span>персонаж</span></div>
            <div><strong>${progress.max_unlocked_level}</strong><span>открытый уровень</span></div>
            <div><strong>${progress.total_attempts}</strong><span>попыток</span></div>
            <div><strong>${formatPercent(progress.best_accuracy)}</strong><span>лучшая точность</span></div>
            <div><strong>${formatSpeed(progress.best_speed_cpm)}</strong><span>лучшая скорость</span></div>
        </div>
    `;
}

function levelClass(level) {
    if (level.is_locked) return 'typing-level-card locked-level';
    if (level.is_completed) return 'typing-level-card completed-level';
    if (level.is_current) return 'typing-level-card current-level';
    return 'typing-level-card open-level';
}

function renderLevels(data) {
    const animalCode = data.progress.animal_code || 'dino';
    levelsGrid.innerHTML = data.levels.map(level => {
        const letters = level.letters.map(letter => `<span>${letter}</span>`).join('');
        const best = level.best_attempt ? `<p class="typing-level-best">Лучшее: ${formatPercent(level.best_attempt.accuracy_percent)}, ${formatSpeed(level.best_attempt.speed_cpm)}</p>` : '<p class="typing-level-best">Пока нет попыток</p>';
        const action = level.is_locked
            ? '<button class="typing-btn locked-btn" disabled>Закрыт</button>'
            : `<a class="typing-btn green-btn" href="/typing-trainer/game?layout=${levelsConfig.layoutCode}&animal=${animalCode}&level=${level.level}&student=${encodeURIComponent(levelsConfig.student)}">Играть</a>`;
        const hand = level.level === 1
            ? `<a class="typing-btn blue-btn" href="/typing-trainer/hand-position?layout=${levelsConfig.layoutCode}&animal=${animalCode}&student=${encodeURIComponent(levelsConfig.student)}">Постановка рук</a>`
            : '';
        return `
            <div class="${levelClass(level)}">
                <div class="typing-level-status">${level.status_title}</div>
                <h2>Уровень ${level.level}: ${level.title}</h2>
                <p>Точность для прохождения: ${level.required_accuracy}%</p>
                <div class="typing-level-letters">${letters}</div>
                ${best}
                <div class="typing-actions">${hand}${action}</div>
            </div>
        `;
    }).join('');
}

function renderRecent(data) {
    if (!data.recent_attempts || data.recent_attempts.length === 0) {
        recentAttempts.style.display = 'none';
        return;
    }
    recentAttempts.style.display = 'block';
    const rows = data.recent_attempts.map(attempt => `
        <tr>
            <td>${attempt.level_number}</td>
            <td>${attempt.is_passed ? 'Да' : 'Нет'}</td>
            <td>${formatPercent(attempt.accuracy_percent)}</td>
            <td>${formatSpeed(attempt.speed_cpm)}</td>
            <td>${attempt.correct_letters}/${attempt.total_letters}</td>
        </tr>
    `).join('');
    recentAttempts.innerHTML = `
        <h2>Последние попытки</h2>
        <div class="typing-table-wrap">
            <table class="typing-table">
                <thead><tr><th>Уровень</th><th>Пройден</th><th>Точность</th><th>Скорость</th><th>Верно</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
    `;
}

async function loadLevels() {
    const token = getAccessToken();
    if (!token) {
        renderUnauthorized();
        return;
    }
    try {
        const response = await fetch(`/api/typing-trainer/levels?layout=${levelsConfig.layoutCode}`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        if (response.status === 401) {
            renderUnauthorized();
            return;
        }
        const data = await response.json();
        if (data.status !== 'ok') {
            progressState.innerHTML = `<h2>Не удалось загрузить уровни</h2><p>${data.message || 'Ошибка загрузки прогресса.'}</p>`;
            return;
        }
        renderProgress(data);
        renderLevels(data);
        renderRecent(data);
    } catch (error) {
        console.error('typing trainer levels failed', error);
        progressState.innerHTML = '<h2>Ошибка загрузки</h2><p>Проверь, что приложение запущено и база данных доступна.</p>';
    }
}

loadLevels();
