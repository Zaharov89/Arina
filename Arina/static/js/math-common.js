// ==== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====
let currentQuestion = 1;
let totalQuestions = 25;
let correctAnswers = 0;
let wrongAnswers = 0;
let emptyAnswers = 0;
let wrongAnswersList = [];
let currentExample = null;
let testStartTime = null;
let questionStartTime = null;
let testTimerInterval = null;
let currentSpeedTimerInterval = null;
let currentSpeedTimerExpired = false;

// ==== НАВИГАЦИЯ ====
function goBackToMain() {
    window.location.href = '/';
}

function goBackToMenu() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/math?student=${encodeURIComponent(student)}`;
}

function showTesting() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/math/test_setup?student=${encodeURIComponent(student)}`;
}

// ==== НАСТРОЙКИ ТЕСТА ====
function selectQuestionCount(count) {
    totalQuestions = count;
    activateQuestionButton(count);
}

function activateQuestionButton(count) {
    document.querySelectorAll('.question-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const btn = Array.from(document.querySelectorAll('.question-btn')).find(b => b.textContent == count);
    if (btn) btn.classList.add('active');
}

// ==== ШАГИ НАСТРОЙКИ ====
function goToStep1() {
    document.getElementById('testStep1').style.display = 'block';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'none';
    document.getElementById('testStep4').style.display = 'none';
}

function goToStep2() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'block';
    document.getElementById('testStep3').style.display = 'none';
    document.getElementById('testStep4').style.display = 'none';

    const classNum = document.getElementById('classSelect').value;
    const tableRow = document.getElementById('tableRow');
    const advancedOptions = document.getElementById('advancedOptions');

    if (classNum === '3') {
        tableRow.style.display = 'flex';
        advancedOptions.style.display = 'flex';
        const typeSelect = document.getElementById('typeSelect');
        typeSelect.innerHTML = `
            <option value="all">Все операции</option>
            <option value="addsub">Сложение и вычитание</option>
            <option value="muldiv">Умножение и деление</option>
            <option value="+">Только сложение</option>
            <option value="-">Только вычитание</option>
            <option value="*">Только умножение</option>
            <option value="/">Только деление</option>
        `;
    } else {
        tableRow.style.display = 'none';
        advancedOptions.style.display = 'none';
        if (document.getElementById('includeEquations'))
            document.getElementById('includeEquations').checked = false;
        if (document.getElementById('includeParentheses'))
            document.getElementById('includeParentheses').checked = false;
        const typeSelect = document.getElementById('typeSelect');
        typeSelect.innerHTML = `
            <option value="all">Все операции</option>
            <option value="addsub">Сложение и вычитание</option>
            <option value="+">Только сложение</option>
            <option value="-">Только вычитание</option>
        `;
    }
    document.getElementById('typeSelect').selectedIndex = 0;
}

function goToStep3() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'block';
    document.getElementById('testStep4').style.display = 'none';
}

function goToStep4() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'none';
    document.getElementById('testStep4').style.display = 'block';
}

// ==== ЗАПУСК ТЕСТА ====
function startMathTest(isSpeedMode = false) {
    const classNum = document.getElementById('classSelect').value;
    const exampleType = document.getElementById('typeSelect').value;
    const tableSelect = document.getElementById('tableSelect');
    const tableNum = tableSelect ? tableSelect.value : 'all';
    const includeEquations = document.getElementById('includeEquations') ?
        document.getElementById('includeEquations').checked : false;
    const includeParentheses = document.getElementById('includeParentheses') ?
        document.getElementById('includeParentheses').checked : false;
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';

    const params = new URLSearchParams({
        class: classNum,
        type: exampleType,
        table: tableNum,
        equations: includeEquations,
        parentheses: includeParentheses,
        speed: isSpeedMode,
        questions: totalQuestions,
        student: student
    });

    window.location.href = `/math/test?${params.toString()}`;
}

// ==== ТЕСТОВАЯ СТРАНИЦА ====
function startTestTimer() {
    clearInterval(testTimerInterval);
    testStartTime = Date.now();
    testTimerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - testStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        const timerEl = document.getElementById('testTimer');
        if (timerEl) {
            timerEl.textContent = `Время: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

function generateQuestion() {
    const answerInput = document.getElementById('answerInput');
    const resultMessage = document.getElementById('resultMessage');
    if (!answerInput || !resultMessage) return;

    answerInput.value = '';
    resultMessage.textContent = '';
    resultMessage.className = 'result-message';
    document.getElementById('checkBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    answerInput.disabled = false;
    answerInput.focus();
    questionStartTime = Date.now();

    const counter = document.getElementById('questionCounter');
    if (counter) {
        counter.textContent = `Пример №${currentQuestion} из ${totalQuestions}`;
    }

    // Останавливаем предыдущий таймер
    if (currentSpeedTimerInterval) {
        clearInterval(currentSpeedTimerInterval);
    }

    // Запускаем таймер на скорость (если включен)
    if (window.testSettings?.isSpeedMode) {
        const speedBar = document.getElementById('speedTimerBar');
        const progressBar = document.querySelector('.speed-timer-progress');
        if (speedBar) speedBar.style.display = 'block';
        if (progressBar) progressBar.style.width = '100%';

        let timeLeft = 30;
        currentSpeedTimerExpired = false;
        currentSpeedTimerInterval = setInterval(() => {
            timeLeft--;
            if (timeLeft <= 0) {
                clearInterval(currentSpeedTimerInterval);
                currentSpeedTimerExpired = true;
                if (!document.getElementById('checkBtn').disabled) {
                    checkAnswer();
                }
                return;
            }
            if (progressBar) {
                progressBar.style.width = `${(timeLeft / 30) * 100}%`;
            }
        }, 1000);
    }

    // Запрашиваем пример с сервера
    fetch('/generate_example', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class: window.testSettings?.classNum || '1',
            type: window.testSettings?.exampleType || 'all',
            table_num: window.testSettings?.tableNum || 'all',
            include_equation: window.testSettings?.includeEquations || false,
            include_parentheses: window.testSettings?.includeParentheses || false
        })
    })
    .then(response => response.json())
    .then(data => {
        currentExample = data;
        const display = document.getElementById('exampleDisplay');
        if (!display) return;

        // Тип 1: выражение вида "15 + 27"
        if (data.expr !== undefined && data.expr !== null) {
            display.textContent = `${data.expr} = ?`;
        }
        // Тип 2: компоненты a, op, b
        else if (data.a !== undefined && data.op !== undefined && data.b !== undefined) {
            display.textContent = `${data.a} ${data.op} ${data.b} = ?`;
        }
        // Тип 3: готовое уравнение (например, "x + 42 = 75")
        else if (data.question !== undefined) {
            let questionStr = String(data.question).trim();

            // Удаляем всё, что похоже на " = ?", "=?", "= ?", " ?" в конце
            questionStr = questionStr
                .replace(/\s*=\s*\?\s*$/i, '')
                .replace(/\s*\?\s*$/, '')
                .trim();

            // Убираем лишнее " = " в конце (если осталось)
            if (questionStr.endsWith(' =')) {
                questionStr = questionStr.slice(0, -2).trim();
            }

            // Выводим ТОЛЬКО чистое уравнение
            display.textContent = questionStr;
        }
        // Резерв: если ничего не подошло
        else {
            display.textContent = "Пример недоступен";
        }
    })
    .catch(error => {
        console.error('Ошибка загрузки примера:', error);
        const display = document.getElementById('exampleDisplay');
        if (display) {
            display.textContent = "Ошибка загрузки примера";
        }
    });
}

function checkAnswer() {
    if (currentSpeedTimerInterval) {
        clearInterval(currentSpeedTimerInterval);
    }

    const userAnswer = document.getElementById('answerInput').value.trim();
    const resultMessage = document.getElementById('resultMessage');
    if (!resultMessage) return;

    if (!userAnswer) {
        resultMessage.textContent = `Вы ничего не ввели. Правильный ответ: ${currentExample?.correct || 'неизвестен'}`;
        resultMessage.className = 'result-message empty-answer';
        emptyAnswers++;
        wrongAnswersList.push({
            ...currentExample,
            example: document.getElementById('exampleDisplay')?.textContent || '',
            userAnswer: '(пусто)',
            correctAnswer: currentExample?.correct
        });
        disableAnswer();
        return;
    }

    if (window.testSettings?.isSpeedMode && currentSpeedTimerExpired) {
        const correct = currentExample?.correct || 'неизвестен';
        resultMessage.textContent = `Вы не успели дать ответ. Правильный ответ: ${correct}`;
        resultMessage.className = 'result-message incorrect';
        wrongAnswers++;
        wrongAnswersList.push({
            ...currentExample,
            example: document.getElementById('exampleDisplay')?.textContent || '',
            userAnswer: '(не успел)',
            correctAnswer: correct
        });
        disableAnswer();
        return;
    }

    fetch('/check_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class: window.testSettings?.classNum,
            type: window.testSettings?.exampleType,
            table_num: window.testSettings?.tableNum,
            answer: userAnswer,
            a: currentExample?.a,
            op: currentExample?.op,
            b: currentExample?.b,
            expr: currentExample?.expr,
            x: currentExample?.x
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.result === 'correct') {
            resultMessage.textContent = "✓ Правильно!";
            resultMessage.className = 'result-message correct';
            correctAnswers++;
        } else {
            resultMessage.textContent = `✗ Неправильно. Правильный ответ: ${data.correct_answer}`;
            resultMessage.className = 'result-message incorrect';
            wrongAnswers++;
            wrongAnswersList.push({
                ...currentExample,
                example: document.getElementById('exampleDisplay')?.textContent || '',
                userAnswer: userAnswer,
                correctAnswer: data.correct_answer
            });
        }
        disableAnswer();
    })
    .catch(error => {
        console.error('Ошибка проверки:', error);
        resultMessage.textContent = "Ошибка проверки ответа";
        resultMessage.className = 'result-message incorrect';
        disableAnswer();
    });
}

function disableAnswer() {
    const checkBtn = document.getElementById('checkBtn');
    const nextBtn = document.getElementById('nextBtn');
    const answerInput = document.getElementById('answerInput');
    if (checkBtn) checkBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = false;
    if (answerInput) answerInput.disabled = true;
}

function nextQuestion() {
    currentQuestion++;
    if (currentQuestion > totalQuestions) {
        finishTest();
    } else {
        generateQuestion();
    }
}

function finishTest() {
    if (currentSpeedTimerInterval) clearInterval(currentSpeedTimerInterval);
    if (testTimerInterval) clearInterval(testTimerInterval);
    const totalTime = Math.round((Date.now() - testStartTime) / 1000);

    localStorage.setItem('testSubject', 'Математика');
    localStorage.setItem('totalQuestions', totalQuestions);
    localStorage.setItem('correctAnswers', correctAnswers);
    localStorage.setItem('wrongAnswers', wrongAnswers);
    localStorage.setItem('emptyAnswers', emptyAnswers);
    localStorage.setItem('timeSpent', totalTime);
    localStorage.setItem('averageTime', totalQuestions > 0 ? (totalTime / totalQuestions).toFixed(1) : 0);
    localStorage.setItem('wrongAnswersList', JSON.stringify(wrongAnswersList));
    localStorage.setItem('isSpeedMode', window.testSettings?.isSpeedMode || false);

    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/results/math?student=${encodeURIComponent(student)}`;
}

// ==== ИНИЦИАЛИЗАЦИЯ ====
document.addEventListener('DOMContentLoaded', function () {
    // Кнопки настройки
    const speedYesBtn = document.getElementById('speedYesBtn');
    const speedNoBtn = document.getElementById('speedNoBtn');
    if (speedYesBtn) speedYesBtn.addEventListener('click', () => startMathTest(true));
    if (speedNoBtn) speedNoBtn.addEventListener('click', () => startMathTest(false));

    // Смена класса
    const classSelect = document.getElementById('classSelect');
    if (classSelect) {
        classSelect.addEventListener('change', function () {
            const classNum = this.value;
            const typeSelect = document.getElementById('typeSelect');
            const tableRow = document.getElementById('tableRow');
            const advancedOptions = document.getElementById('advancedOptions');

            if (classNum === '3') {
                typeSelect.innerHTML = `
                    <option value="all">Все операции</option>
                    <option value="addsub">Сложение и вычитание</option>
                    <option value="muldiv">Умножение и деление</option>
                    <option value="+">Только сложение</option>
                    <option value="-">Только вычитание</option>
                    <option value="*">Только умножение</option>
                    <option value="/">Только деление</option>
                `;
                if (tableRow) tableRow.style.display = 'flex';
                if (advancedOptions) advancedOptions.style.display = 'flex';
            } else {
                typeSelect.innerHTML = `
                    <option value="all">Все операции</option>
                    <option value="addsub">Сложение и вычитание</option>
                    <option value="+">Только сложение</option>
                    <option value="-">Только вычитание</option>
                `;
                if (tableRow) tableRow.style.display = 'none';
                if (advancedOptions) advancedOptions.style.display = 'none';
                if (document.getElementById('includeEquations'))
                    document.getElementById('includeEquations').checked = false;
                if (document.getElementById('includeParentheses'))
                    document.getElementById('includeParentheses').checked = false;
            }
            typeSelect.selectedIndex = 0;
        });
    }

    // Enter для ответа
    const answerInput = document.getElementById('answerInput');
    if (answerInput) {
        answerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const checkBtn = document.getElementById('checkBtn');
                const nextBtn = document.getElementById('nextBtn');
                if (checkBtn && !checkBtn.disabled) {
                    checkAnswer();
                } else if (nextBtn && !nextBtn.disabled) {
                    nextQuestion();
                }
            }
        });
    }

    // Инициализация теста
    if (document.getElementById('testBlock')) {
        if (typeof window.testSettings !== 'undefined') {
            totalQuestions = window.totalQuestions || 25;
            currentQuestion = 1;
            correctAnswers = 0;
            wrongAnswers = 0;
            emptyAnswers = 0;
            wrongAnswersList = [];
            startTestTimer();
            generateQuestion();
        }
    }

    // Дата и время
    renderDateBar();
});

function renderDateBar() {
    const dateTimeBar = document.getElementById("dateTimeBar");
    if (!dateTimeBar) return;

    const now = new Date();
    const monthsRu = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];
    dateTimeBar.textContent =
        `${now.getDate()} ${monthsRu[now.getMonth()]} ${now.getFullYear()} года ` +
        `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;
}