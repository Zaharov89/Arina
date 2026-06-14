function buildUniqueQuestionKey(task) {
    if (!task) return '';

    if (task.question_key) {
        return String(task.question_key).trim();
    }

    const question = String(task.question || task.expr || '').trim();
    const choices = Array.isArray(task.choices) ? task.choices.map(String).join(' | ') : '';

    if (question && choices) {
        return `${question} | ${choices}`;
    }

    if (question) return question;

    if (task.a !== undefined && task.op !== undefined && task.b !== undefined) {
        return `${task.a} ${task.op} ${task.b} = ?`;
    }

    return '';
}

if (typeof getQuestionKey === 'function') {
    getQuestionKey = buildUniqueQuestionKey;
}

if (typeof getRussianTaskQuestionKey === 'function') {
    getRussianTaskQuestionKey = buildUniqueQuestionKey;
}

if (typeof getWorldTaskQuestionKey === 'function') {
    getWorldTaskQuestionKey = buildUniqueQuestionKey;
}
