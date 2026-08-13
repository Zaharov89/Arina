const resultConfig = window.typingResultPageConfig;
const resultPage = document.getElementById('typingResultPage');
const actions = document.getElementById('typingResultActions');

function getSavedResult() {
    try {
        return JSON.parse(sessionStorage.getItem('typingTrainerLastResult') || '{}');
    } catch (error) {
        return {};
    }
}

function resultTitle(result) {
    if (result.is_passed) return 'Уровень пройден!';
    return 'Попробуй ещё раз';
}

function calculateStars(result) {
    if (!result.is_passed) return 0;
    const accuracy = Number(result.accuracy_percent || 0);
    const speed = Number(result.speed_cpm || 0);
    if (accuracy >= 95 && speed >= 30) return 3;
    if (accuracy >= 90) return 2;
    return 1;
}

function renderStars(stars) {
    return '★'.repeat(stars) + '☆'.repeat(Math.max(3 - stars, 0));
}

function renderResult() {
    const result = getSavedResult();
    if (!result || !result.level_number) {
        resultPage.innerHTML = '<p>Результат не найден. Пройди уровень ещё раз.</p>';
        actions.innerHTML = `<a class="typing-btn blue-btn" href="/typing-trainer/levels?layout=${encodeURIComponent(resultConfig.layoutCode)}&student=${encodeURIComponent(resultConfig.student)}">К уровням</a>`;
        return;
    }

    const stars = Number.isFinite(Number(result.stars)) ? Number(result.stars) : calculateStars(result);
    resultPage.innerHTML = `
        <div class="typing-result-animal">${resultConfig.animal.emoji}</div>
        <h2>${resultTitle(result)}</h2>
        <p class="typing-stars">${renderStars(stars)}</p>
        <div class="typing-result-stats">
            <span>Уровень: <strong>${result.level_number}</strong></span>
            <span>Точность: <strong>${Math.round(result.accuracy_percent)}%</strong></span>
            <span>Скорость: <strong>${Math.round(result.speed_cpm)} зн/мин</strong></span>
            <span>Правильно: <strong>${result.correct_letters}</strong></span>
            <span>Ошибки: <strong>${result.wrong_letters}</strong></span>
            <span>Пропущено: <strong>${result.missed_letters}</strong></span>
        </div>
    `;

    const nextLevel = Number(result.level_number) + 1;
    const nextLink = result.is_passed
        ? `<a class="typing-btn green-btn" href="/typing-trainer/game?layout=${encodeURIComponent(result.layout_code)}&animal=${encodeURIComponent(result.animal_code)}&level=${nextLevel}&student=${encodeURIComponent(resultConfig.student)}">Следующий уровень</a>`
        : '';
    actions.innerHTML = `
        <a class="typing-btn red-btn" href="/typing-trainer/levels?layout=${encodeURIComponent(result.layout_code)}&student=${encodeURIComponent(resultConfig.student)}">К уровням</a>
        <a class="typing-btn blue-btn" href="/typing-trainer/game?layout=${encodeURIComponent(result.layout_code)}&animal=${encodeURIComponent(result.animal_code)}&level=${result.level_number}&student=${encodeURIComponent(resultConfig.student)}">Повторить</a>
        ${nextLink}
    `;
}

renderResult();
