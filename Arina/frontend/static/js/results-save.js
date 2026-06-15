function getAuthStorageForResults() {
    if (localStorage.getItem('arinaAccessToken')) return localStorage;
    if (sessionStorage.getItem('arinaAccessToken')) return sessionStorage;
    return null;
}

function getAccessTokenForResults() {
    const storage = getAuthStorageForResults();
    return storage ? storage.getItem('arinaAccessToken') : '';
}

function calculateGradeFromPercent(scorePercent) {
    const errorPercent = 100 - Number(scorePercent || 0);
    if (errorPercent <= 5) return 5;
    if (errorPercent <= 15) return 4;
    if (errorPercent <= 30) return 3;
    return 2;
}

function getResultMeta(defaultSubjectCode, defaultClassNumber, defaultTopicCode) {
    return {
        subject_code: localStorage.getItem('resultSubjectCode') || defaultSubjectCode,
        class_number: parseInt(localStorage.getItem('resultClassNumber') || defaultClassNumber || '1'),
        topic_code: localStorage.getItem('resultTopicCode') || defaultTopicCode || '',
    };
}

function buildTestAttemptPayload(defaultSubjectCode, defaultClassNumber, defaultTopicCode) {
    const totalQuestions = parseInt(localStorage.getItem('totalQuestions')) || 0;
    const correctAnswers = parseInt(localStorage.getItem('correctAnswers')) || 0;
    const wrongAnswers = parseInt(localStorage.getItem('wrongAnswers')) || 0;
    const emptyAnswers = parseInt(localStorage.getItem('emptyAnswers')) || 0;
    const timeSpent = parseInt(localStorage.getItem('timeSpent')) || 0;
    const averageTime = parseFloat(localStorage.getItem('averageTime')) || 0;
    const scorePercent = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
    const meta = getResultMeta(defaultSubjectCode, defaultClassNumber, defaultTopicCode);
    const wrongAnswersList = JSON.parse(localStorage.getItem('wrongAnswersList') || '[]');

    return {
        ...meta,
        total_questions: totalQuestions,
        correct_answers: correctAnswers,
        wrong_answers: wrongAnswers,
        empty_answers: emptyAnswers,
        score_percent: scorePercent,
        grade: calculateGradeFromPercent(scorePercent),
        time_spent_seconds: timeSpent,
        average_time_seconds: averageTime,
        answers: wrongAnswersList,
    };
}

function renderGradeSaveMessage(message, type) {
    const element = document.getElementById('gradeSaveMessage');
    if (!element) return;
    element.textContent = message || '';
    element.className = `grade-save-message ${type || ''}`;
    element.style.display = message ? 'block' : 'none';
}

async function saveTestAttemptResult(defaultSubjectCode, defaultClassNumber, defaultTopicCode) {
    const payload = buildTestAttemptPayload(defaultSubjectCode, defaultClassNumber, defaultTopicCode);
    if (!payload.total_questions) return;

    const token = getAccessTokenForResults();
    if (!token) {
        renderGradeSaveMessage('Не удалось сохранить оценку: пользователь не авторизован.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/test-attempts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json();

        if (!response.ok) {
            renderGradeSaveMessage(data.message || data.error || 'Не удалось сохранить оценку.', 'error');
            return;
        }

        renderGradeSaveMessage(data.message || 'Оценка сохранена.', 'success');
    } catch (error) {
        renderGradeSaveMessage(`Не удалось сохранить оценку: ${error}`, 'error');
    }
}
