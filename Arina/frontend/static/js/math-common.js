let currentQuestion = 1;
let totalQuestions = 25;
let selectedQuestionCount = 25;
let correctAnswers = 0;
let wrongAnswers = 0;
let emptyAnswers = 0;
let wrongAnswersList = [];
let currentExample = null;
let usedQuestionTexts = [];
let testStartTime = null;
let questionStartTime = null;
let testTimerInterval = null;
let currentSpeedTimerInterval = null;
let currentSpeedTimerExpired = false;

function goBackToMenu() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/math?student=${encodeURIComponent(student)}`;
}

function selectQuestionCount(count) {
    selectedQuestionCount = count;
    document.querySelectorAll('.question-btn').forEach(btn => btn.classList.remove('active'));
    const selected = Array.from(document.querySelectorAll('.question-btn')).find(btn => btn.textContent.trim() === String(count));
    if (selected) selected.classList.add('active');
}

function updateTypeOptionsForClass(classNum) {
    const typeSelect = document.getElementById('typeSelect');
    const tableRow = document.getElementById('tableRow');
    const advancedOptions = document.getElementById('advancedOptions');
    const typeSelectLabel = document.getElementById('typeSelectLabel');
    if (!typeSelect) return;
    if (classNum === '1' || classNum === '2') {
        const topics = classNum === '2' ? (window.CLASS_2_MATH_TOPICS || window.CLASS_1_MATH_TOPICS || []) : (window.CLASS_1_MATH_TOPICS || []);
        typeSelect.innerHTML = topics.map(topic => `<option value="${topic.id}">${topic.title}</option>`).join('');
        if (typeSelectLabel) typeSelectLabel.textContent = 'Раздел:';
        if (tableRow) tableRow.style.display = 'none';
        if (advancedOptions) advancedOptions.style.display = 'none';
        return;
    }
    typeSelect.innerHTML = `<option value="all">Все примеры</option><option value="addsub">Сложение и вычитание</option><option value="+">Только сложение</option><option value="-">Только вычитание</option>`;
    if (classNum === '3') typeSelect.innerHTML += `<option value="muldiv">Умножение и деление</option><option value="*">Только умножение</option><option value="/">Только деление</option>`;
    if (typeSelectLabel) typeSelectLabel.textContent = 'Тип примеров:';
    if (tableRow) tableRow.style.display = classNum === '3' ? 'flex' : 'none';
    if (advancedOptions) advancedOptions.style.display = classNum === '3' ? 'flex' : 'none';
}

function setInitialMathSetupValues() {
    const classSelect = document.getElementById('classSelect');
    const typeSelect = document.getElementById('typeSelect');
    if (classSelect && window.INITIAL_MATH_CLASS) classSelect.value = window.INITIAL_MATH_CLASS;
    updateTypeOptionsForClass(classSelect ? classSelect.value : '1');
    if (typeSelect && window.INITIAL_MATH_TYPE) {
        const optionExists = Array.from(typeSelect.options).some(option => option.value === window.INITIAL_MATH_TYPE);
        if (optionExists) typeSelect.value = window.INITIAL_MATH_TYPE;
    }
}

function goToStep1() { document.getElementById('testStep1').style.display = 'block'; document.getElementById('testStep2').style.display = 'none'; document.getElementById('testStep3').style.display = 'none'; document.getElementById('testStep4').style.display = 'none'; }
function goToStep2() { document.getElementById('testStep1').style.display = 'none'; document.getElementById('testStep2').style.display = 'block'; document.getElementById('testStep3').style.display = 'none'; document.getElementById('testStep4').style.display = 'none'; const classSelect = document.getElementById('classSelect'); if (classSelect) updateTypeOptionsForClass(classSelect.value); }
function goToStep3() { document.getElementById('testStep1').style.display = 'none'; document.getElementById('testStep2').style.display = 'none'; document.getElementById('testStep3').style.display = 'block'; document.getElementById('testStep4').style.display = 'none'; }
function goToStep4() { document.getElementById('testStep1').style.display = 'none'; document.getElementById('testStep2').style.display = 'none'; document.getElementById('testStep3').style.display = 'none'; document.getElementById('testStep4').style.display = 'block'; }

function startMathTest(isSpeedMode) {
    const classSelect = document.getElementById('classSelect');
    const typeSelect = document.getElementById('typeSelect');
    const tableSelect = document.getElementById('tableSelect');
    const includeEquations = document.getElementById('includeEquations');
    const includeParentheses = document.getElementById('includeParentheses');
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    const params = new URLSearchParams({ class: classSelect ? classSelect.value : '1', type: typeSelect ? typeSelect.value : 'add_sub_to_20', table: tableSelect ? tableSelect.value : 'all', equations: includeEquations ? includeEquations.checked : false, parentheses: includeParentheses ? includeParentheses.checked : false, speed: isSpeedMode, questions: selectedQuestionCount, student: student });
    window.location.href = `/math/test?${params.toString()}`;
}

function startTestTimer() { clearInterval(testTimerInterval); testStartTime = Date.now(); testTimerInterval = setInterval(() => { const elapsed = Math.floor((Date.now() - testStartTime) / 1000); const minutes = Math.floor(elapsed / 60); const seconds = elapsed % 60; const timerEl = document.getElementById('testTimer'); if (timerEl) timerEl.textContent = `Время: ${minutes}:${seconds.toString().padStart(2, '0')}`; }, 1000); }
function getQuestionKey(example) { if (!example) return ''; if (example.question !== undefined && example.question !== null) return String(example.question).trim(); if (example.expr !== undefined && example.expr !== null) return String(example.expr).trim(); if (example.a !== undefined && example.op !== undefined && example.b !== undefined) return `${example.a} ${example.op} ${example.b} = ?`; return ''; }
function rememberQuestion(example) { const questionKey = getQuestionKey(example); if (!questionKey) return; if (!usedQuestionTexts.includes(questionKey)) usedQuestionTexts.push(questionKey); if (usedQuestionTexts.length > 300) usedQuestionTexts = usedQuestionTexts.slice(-300); }

function generateQuestion() {
    const answerInput = document.getElementById('answerInput');
    const resultMessage = document.getElementById('resultMessage');
    if (!answerInput || !resultMessage) return;
    answerInput.value = ''; resultMessage.textContent = ''; resultMessage.className = 'result-message'; document.getElementById('checkBtn').disabled = false; document.getElementById('nextBtn').disabled = true; answerInput.disabled = false; answerInput.focus(); questionStartTime = Date.now();
    const counter = document.getElementById('questionCounter'); if (counter) counter.textContent = `Задание №${currentQuestion} из ${totalQuestions}`;
    const topicEl = document.getElementById('questionTopic'); if (topicEl) { topicEl.style.display = 'none'; topicEl.textContent = ''; }
    if (currentSpeedTimerInterval) clearInterval(currentSpeedTimerInterval);
    if (window.testSettings?.isSpeedMode) {
        const speedBar = document.getElementById('speedTimerBar'); const progressBar = document.querySelector('.speed-timer-progress'); if (speedBar) speedBar.style.display = 'block'; if (progressBar) progressBar.style.width = '100%'; let timeLeft = 30; currentSpeedTimerExpired = false;
        currentSpeedTimerInterval = setInterval(() => { timeLeft--; if (timeLeft <= 0) { clearInterval(currentSpeedTimerInterval); currentSpeedTimerExpired = true; if (!document.getElementById('checkBtn').disabled) checkAnswer(); return; } if (progressBar) progressBar.style.width = `${(timeLeft / 30) * 100}%`; }, 1000);
    }
    fetch('/generate_example', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ class: window.testSettings?.classNum || '1', type: window.testSettings?.exampleType || 'add_sub_to_20', table_num: window.testSettings?.tableNum || 'all', include_equation: window.testSettings?.includeEquations || false, include_parentheses: window.testSettings?.includeParentheses || false, used_questions: usedQuestionTexts, question_number: currentQuestion }) })
    .then(response => response.json()).then(data => { currentExample = data; rememberQuestion(data); const display = document.getElementById('exampleDisplay'); if (!display) return; if (topicEl && data.topic_title) { topicEl.style.display = 'block'; topicEl.textContent = data.topic_title; } answerInput.placeholder = data.answer_type === 'choice' ? 'Введите вариант ответа' : 'Введите ответ'; if (data.question !== undefined) { let questionText = String(data.question).trim(); if (Array.isArray(data.choices) && data.choices.length > 0) questionText += `\nВарианты: ${data.choices.join('   ')}`; display.textContent = questionText; } else if (data.expr !== undefined && data.expr !== null) display.textContent = `${data.expr} = ?`; else if (data.a !== undefined && data.op !== undefined && data.b !== undefined) display.textContent = `${data.a} ${data.op} ${data.b} = ?`; else display.textContent = 'Пример недоступен'; })
    .catch(error => { console.error('Ошибка загрузки примера:', error); const display = document.getElementById('exampleDisplay'); if (display) display.textContent = 'Ошибка загрузки примера'; });
}

function checkAnswer() {
    if (currentSpeedTimerInterval) clearInterval(currentSpeedTimerInterval);
    const userAnswer = document.getElementById('answerInput').value.trim();
    const resultMessage = document.getElementById('resultMessage'); if (!resultMessage) return;
    if (!userAnswer) { resultMessage.textContent = `Вы ничего не ввели. Правильный ответ: ${currentExample?.correct ?? 'неизвестен'}`; resultMessage.className = 'result-message empty-answer'; emptyAnswers++; wrongAnswersList.push({...currentExample, example: document.getElementById('exampleDisplay')?.textContent || '', userAnswer: '(пусто)', correctAnswer: currentExample?.correct}); disableAnswer(); return; }
    if (window.testSettings?.isSpeedMode && currentSpeedTimerExpired) { const correct = currentExample?.correct ?? 'неизвестен'; resultMessage.textContent = `Вы не успели дать ответ. Правильный ответ: ${correct}`; resultMessage.className = 'result-message incorrect'; wrongAnswers++; wrongAnswersList.push({...currentExample, example: document.getElementById('exampleDisplay')?.textContent || '', userAnswer: '(не успел)', correctAnswer: correct}); disableAnswer(); return; }
    fetch('/check_answer', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ class: window.testSettings?.classNum, type: window.testSettings?.exampleType, table_num: window.testSettings?.tableNum, answer: userAnswer, answer_type: currentExample?.answer_type, correct: currentExample?.correct, a: currentExample?.a, op: currentExample?.op, b: currentExample?.b, expr: currentExample?.expr, x: currentExample?.x }) })
    .then(response => response.json()).then(data => { if (data.result === 'correct') { resultMessage.textContent = '✓ Правильно!'; resultMessage.className = 'result-message correct'; correctAnswers++; } else { resultMessage.textContent = `✗ Неправильно. Правильный ответ: ${data.correct_answer}`; resultMessage.className = 'result-message incorrect'; wrongAnswers++; wrongAnswersList.push({...currentExample, example: document.getElementById('exampleDisplay')?.textContent || '', userAnswer: userAnswer, correctAnswer: data.correct_answer}); } disableAnswer(); })
    .catch(error => { console.error('Ошибка проверки:', error); resultMessage.textContent = 'Ошибка проверки ответа'; resultMessage.className = 'result-message incorrect'; disableAnswer(); });
}
function disableAnswer() { const checkBtn = document.getElementById('checkBtn'); const nextBtn = document.getElementById('nextBtn'); const answerInput = document.getElementById('answerInput'); if (checkBtn) checkBtn.disabled = true; if (nextBtn) nextBtn.disabled = false; if (answerInput) answerInput.disabled = true; }
function nextQuestion() { currentQuestion++; if (currentQuestion > totalQuestions) finishTest(); else generateQuestion(); }
function finishTest() { if (currentSpeedTimerInterval) clearInterval(currentSpeedTimerInterval); if (testTimerInterval) clearInterval(testTimerInterval); const totalTime = Math.round((Date.now() - testStartTime) / 1000); localStorage.setItem('testSubject', 'Математика'); localStorage.setItem('resultSubjectCode', 'math'); localStorage.setItem('resultClassNumber', window.testSettings?.classNum || '1'); localStorage.setItem('resultTopicCode', window.testSettings?.exampleType || ''); localStorage.setItem('totalQuestions', totalQuestions); localStorage.setItem('correctAnswers', correctAnswers); localStorage.setItem('wrongAnswers', wrongAnswers); localStorage.setItem('emptyAnswers', emptyAnswers); localStorage.setItem('timeSpent', totalTime); localStorage.setItem('averageTime', totalQuestions > 0 ? (totalTime / totalQuestions).toFixed(1) : 0); localStorage.setItem('wrongAnswersList', JSON.stringify(wrongAnswersList)); localStorage.setItem('isSpeedMode', window.testSettings?.isSpeedMode || false); const student = new URLSearchParams(window.location.search).get('student') || 'Арина'; window.location.href = `/results/math?student=${encodeURIComponent(student)}`; }

document.addEventListener('DOMContentLoaded', function () { const speedYesBtn = document.getElementById('speedYesBtn'); const speedNoBtn = document.getElementById('speedNoBtn'); if (speedYesBtn) speedYesBtn.addEventListener('click', () => startMathTest(true)); if (speedNoBtn) speedNoBtn.addEventListener('click', () => startMathTest(false)); const classSelect = document.getElementById('classSelect'); if (classSelect) { setInitialMathSetupValues(); classSelect.addEventListener('change', function () { updateTypeOptionsForClass(this.value); }); } const answerInput = document.getElementById('answerInput'); if (answerInput) { answerInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') { const checkBtn = document.getElementById('checkBtn'); const nextBtn = document.getElementById('nextBtn'); if (checkBtn && !checkBtn.disabled) checkAnswer(); else if (nextBtn && !nextBtn.disabled) nextQuestion(); } }); } if (document.getElementById('testBlock')) { if (typeof window.testSettings !== 'undefined') { totalQuestions = window.totalQuestions || 25; currentQuestion = 1; correctAnswers = 0; wrongAnswers = 0; emptyAnswers = 0; wrongAnswersList = []; usedQuestionTexts = []; startTestTimer(); generateQuestion(); } } renderDateBar(); });
function renderDateBar() { const dateTimeBar = document.getElementById('dateTimeBar'); if (!dateTimeBar) return; const now = new Date(); const monthsRu = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']; dateTimeBar.textContent = `${now.getDate()} ${monthsRu[now.getMonth()]} ${now.getFullYear()} года ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`; }
