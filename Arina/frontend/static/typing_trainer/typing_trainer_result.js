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

function renderResult() {
    const result = getSavedResult();
    if (!result || !result.level_number) {
        resultPage.innerHTML = '<p>Результат не найден. Пройди уровень ещё раз.</p>';
        actions.innerHTML = `<a class="typing-btn blue-btn" href="/typing-trainer/levels?layout=${encodeURIComponent(resultConfig.layoutCode)}&student=${encodeURIComponent(resultConfig.student)}">К уровням</a>`;
        return;
    }

    resultPage.innerHTML = `
        <div class="typing-result-animal">${resultConfig.animal.emoji}</div>
        <h2>${resultTitle(result)}</h2>
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
