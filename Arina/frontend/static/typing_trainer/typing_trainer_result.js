const resultConfig = window.typingResultConfig;
const resultCard = document.getElementById('typingResultCard');
const repeatLink = document.getElementById('typingRepeatLink');
const nextLink = document.getElementById('typingNextLink');

function formatPercent(value) {
    return `${Math.round(Number(value || 0))}%`;
}

function formatSpeed(value) {
    return `${Math.round(Number(value || 0))} зн/мин`;
}

function renderNoResult() {
    resultCard.innerHTML = `
        <h2>Результат не найден</h2>
        <p>Похоже, страница открыта напрямую. Вернись к уровням и запусти тренировку.</p>
    `;
}

function renderResult() {
    const raw = sessionStorage.getItem('typingTrainerLastResult');
    if (!raw) {
        renderNoResult();
        return;
    }
    let result;
    try {
        result = JSON.parse(raw);
    } catch (error) {
        renderNoResult();
        return;
    }
    const attempt = result.attempt || result;
    const levelNumber = Number(attempt.level_number || result.level_number || 1);
    const isPassed = Boolean(result.is_passed ?? attempt.is_passed);
    repeatLink.href = `/typing-trainer/game?layout=${resultConfig.layoutCode}&animal=${resultConfig.animalCode}&level=${levelNumber}&student=${encodeURIComponent(resultConfig.student)}`;
    if (isPassed) {
        nextLink.href = `/typing-trainer/game?layout=${resultConfig.layoutCode}&animal=${resultConfig.animalCode}&level=${levelNumber + 1}&student=${encodeURIComponent(resultConfig.student)}`;
        nextLink.style.display = 'inline-flex';
    }
    const title = isPassed ? 'Уровень пройден!' : 'Пока не получилось';
    const hint = isPassed ? 'Следующий уровень открыт. Можно продолжать.' : 'Ничего страшного: повтори уровень и поймай кубики точнее.';
    resultCard.innerHTML = `
        <div class="typing-result-hero">${resultConfig.animal?.emoji || '🦖'}</div>
        <h2>${title}</h2>
        <p>${hint}</p>
        <div class="typing-progress-grid">
            <div><strong>${levelNumber}</strong><span>уровень</span></div>
            <div><strong>${formatPercent(attempt.accuracy_percent)}</strong><span>точность</span></div>
            <div><strong>${formatSpeed(attempt.speed_cpm)}</strong><span>скорость</span></div>
            <div><strong>${attempt.correct_letters || 0}/${attempt.total_letters || 0}</strong><span>правильно</span></div>
            <div><strong>${attempt.wrong_letters || 0}</strong><span>не та/рано</span></div>
            <div><strong>${attempt.missed_letters || 0}</strong><span>пропущено</span></div>
        </div>
    `;
}

renderResult();
