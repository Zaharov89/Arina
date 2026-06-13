function injectChoiceRadioStyles() {
    if (document.getElementById('choiceRadioStyles')) return;

    const style = document.createElement('style');
    style.id = 'choiceRadioStyles';
    style.textContent = `
        .choice-options { display: none; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; max-width: 760px; margin: 25px auto 15px auto; }
        .choice-option { display: flex; align-items: center; justify-content: flex-start; gap: 12px; padding: 16px 18px; background: #fff; border: 2px solid #cfe0f6; border-radius: 14px; color: #27407a; font-size: 22px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }
        .choice-option:hover { border-color: #5d92e0; background: #f8fafd; transform: translateY(-2px); }
        .choice-option input[type="radio"] { width: 22px; height: 22px; cursor: pointer; accent-color: #5d92e0; }
        .choice-option.selected-choice { border-color: #2fd072; background: #d5f4e6; }
        .choice-option.disabled-choice { cursor: default; opacity: 0.8; }
        @media (max-width: 768px) { .choice-options { grid-template-columns: 1fr; } .choice-option { font-size: 20px; } }
    `;
    document.head.appendChild(style);
}

injectChoiceRadioStyles();

function getOrCreateMathChoiceContainer() {
    let container = document.getElementById('choiceOptions');
    if (container) return container;

    const answerInput = document.getElementById('answerInput');
    container = document.createElement('div');
    container.id = 'choiceOptions';
    container.className = 'choice-options';

    if (answerInput && answerInput.parentNode) {
        answerInput.parentNode.insertBefore(container, answerInput.nextSibling);
    }

    return container;
}

function clearMathChoiceOptions() {
    const container = getOrCreateMathChoiceContainer();
    container.innerHTML = '';
    container.style.display = 'none';
}

function renderMathChoiceOptions(choices) {
    const container = getOrCreateMathChoiceContainer();
    container.innerHTML = '';

    choices.forEach((choice, index) => {
        const id = `mathChoice_${index}`;
        const label = document.createElement('label');
        label.className = 'choice-option';
        label.setAttribute('for', id);

        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'mathChoice';
        radio.id = id;
        radio.value = String(choice);
        radio.addEventListener('change', () => {
            document.querySelectorAll('.choice-option').forEach(item => item.classList.remove('selected-choice'));
            label.classList.add('selected-choice');
        });

        const text = document.createElement('span');
        text.textContent = String(choice);

        label.appendChild(radio);
        label.appendChild(text);
        container.appendChild(label);
    });

    container.style.display = 'grid';
}

function getSelectedMathChoice() {
    const selected = document.querySelector('input[name="mathChoice"]:checked');
    return selected ? selected.value : '';
}

function setMathChoiceOptionsDisabled(disabled) {
    document.querySelectorAll('input[name="mathChoice"]').forEach(input => {
        input.disabled = disabled;
        const label = input.closest('.choice-option');
        if (label) label.classList.toggle('disabled-choice', disabled);
    });
}

function setMathAnswerMode(example) {
    const answerInput = document.getElementById('answerInput');
    if (!answerInput) return;

    if (example?.answer_type === 'choice' && Array.isArray(example.choices) && example.choices.length > 0) {
        answerInput.value = '';
        answerInput.style.display = 'none';
        renderMathChoiceOptions(example.choices);
        return;
    }

    clearMathChoiceOptions();
    answerInput.style.display = 'block';
    answerInput.placeholder = 'Введите ответ';
    answerInput.disabled = false;
    answerInput.focus();
}

function getCurrentMathUserAnswer() {
    if (currentExample?.answer_type === 'choice') {
        return getSelectedMathChoice();
    }

    const answerInput = document.getElementById('answerInput');
    return answerInput ? answerInput.value.trim() : '';
}

const originalMathDisableAnswer = disableAnswer;
disableAnswer = function() {
    originalMathDisableAnswer();
    setMathChoiceOptionsDisabled(true);
};

generateQuestion = function() {
    const answerInput = document.getElementById('answerInput');
    const resultMessage = document.getElementById('resultMessage');
    if (!answerInput || !resultMessage) return;

    answerInput.value = '';
    answerInput.style.display = 'block';
    clearMathChoiceOptions();
    resultMessage.textContent = '';
    resultMessage.className = 'result-message';
    document.getElementById('checkBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    answerInput.disabled = false;
    questionStartTime = Date.now();

    const counter = document.getElementById('questionCounter');
    if (counter) counter.textContent = `Задание №${currentQuestion} из ${totalQuestions}`;

    const topicEl = document.getElementById('questionTopic');
    if (topicEl) {
        topicEl.style.display = 'none';
        topicEl.textContent = '';
    }

    if (currentSpeedTimerInterval) clearInterval(currentSpeedTimerInterval);

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
                if (!document.getElementById('checkBtn').disabled) checkAnswer();
                return;
            }
            if (progressBar) progressBar.style.width = `${(timeLeft / 30) * 100}%`;
        }, 1000);
    }

    fetch('/generate_example', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class: window.testSettings?.classNum || '1',
            type: window.testSettings?.exampleType || 'add_sub_to_20',
            table_num: window.testSettings?.tableNum || 'all',
            include_equation: window.testSettings?.includeEquations || false,
            include_parentheses: window.testSettings?.includeParentheses || false,
            used_questions: usedQuestionTexts
        })
    })
    .then(response => response.json())
    .then(data => {
        currentExample = data;
        rememberQuestion(data);
        const display = document.getElementById('exampleDisplay');
        if (!display) return;

        if (topicEl && data.topic_title) {
            topicEl.style.display = 'block';
            topicEl.textContent = data.topic_title;
        }

        setMathAnswerMode(data);

        if (data.question !== undefined) {
            display.textContent = String(data.question).trim();
        } else if (data.expr !== undefined && data.expr !== null) {
            display.textContent = `${data.expr} = ?`;
        } else if (data.a !== undefined && data.op !== undefined && data.b !== undefined) {
            display.textContent = `${data.a} ${data.op} ${data.b} = ?`;
        } else {
            display.textContent = 'Пример недоступен';
        }
    })
    .catch(error => {
        console.error('Ошибка загрузки примера:', error);
        const display = document.getElementById('exampleDisplay');
        if (display) display.textContent = 'Ошибка загрузки примера';
    });
};

checkAnswer = function() {
    if (currentSpeedTimerInterval) clearInterval(currentSpeedTimerInterval);

    const userAnswer = getCurrentMathUserAnswer();
    const resultMessage = document.getElementById('resultMessage');
    if (!resultMessage) return;

    if (!userAnswer) {
        resultMessage.textContent = `Вы ничего не выбрали или не ввели. Правильный ответ: ${currentExample?.correct ?? 'неизвестен'}`;
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
        const correct = currentExample?.correct ?? 'неизвестен';
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
            answer_type: currentExample?.answer_type,
            correct: currentExample?.correct,
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
            resultMessage.textContent = '✓ Правильно!';
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
        resultMessage.textContent = 'Ошибка проверки ответа';
        resultMessage.className = 'result-message incorrect';
        disableAnswer();
    });
};
