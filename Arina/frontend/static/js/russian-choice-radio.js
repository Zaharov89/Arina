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

function getOrCreateRussianChoiceContainer() {
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

function clearRussianChoiceOptions() {
    const container = getOrCreateRussianChoiceContainer();
    container.innerHTML = '';
    container.style.display = 'none';
}

function renderRussianChoiceOptions(choices) {
    const container = getOrCreateRussianChoiceContainer();
    container.innerHTML = '';

    choices.forEach((choice, index) => {
        const id = `russianChoice_${index}`;
        const label = document.createElement('label');
        label.className = 'choice-option';
        label.setAttribute('for', id);

        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'russianChoice';
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

function getSelectedRussianChoice() {
    const selected = document.querySelector('input[name="russianChoice"]:checked');
    return selected ? selected.value : '';
}

function setRussianChoiceOptionsDisabled(disabled) {
    document.querySelectorAll('input[name="russianChoice"]').forEach(input => {
        input.disabled = disabled;
        const label = input.closest('.choice-option');
        if (label) label.classList.toggle('disabled-choice', disabled);
    });
}

function setRussianAnswerMode(task) {
    const answerInput = document.getElementById('answerInput');
    if (!answerInput) return;

    if (task?.answer_type === 'choice' && Array.isArray(task.choices) && task.choices.length > 0) {
        answerInput.value = '';
        answerInput.style.display = 'none';
        renderRussianChoiceOptions(task.choices);
        return;
    }

    clearRussianChoiceOptions();
    answerInput.style.display = 'block';
    answerInput.placeholder = 'Введите ответ';
    answerInput.disabled = false;
    answerInput.focus();
}

function getCurrentRussianTopicAnswer() {
    if (currentRussianTask?.answer_type === 'choice') {
        return getSelectedRussianChoice();
    }

    const answerInput = document.getElementById('answerInput');
    return answerInput ? answerInput.value.trim() : '';
}

generateRussianTopicQuestion = function() {
    const answerInput = document.getElementById('answerInput');
    const resultMessage = document.getElementById('resultMessage');
    if (!answerInput || !resultMessage) return;

    if (currentQuestion > totalWords) {
        finishRussianTopicTest();
        return;
    }

    answerInput.value = '';
    answerInput.style.display = 'block';
    clearRussianChoiceOptions();
    resultMessage.textContent = '';
    resultMessage.className = 'result-message';
    document.getElementById('checkBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    answerInput.disabled = false;

    const counter = document.getElementById('questionCounter');
    if (counter) counter.textContent = `Задание №${currentQuestion} из ${totalWords}`;

    fetch('/russian/generate_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            class: window.russianTopicTestSettings?.classNum || '1',
            topic: window.russianTopicTestSettings?.topicId || 'sounds_and_letters',
            used_questions: usedRussianQuestionTexts,
        })
    })
    .then(response => response.json())
    .then(task => {
        currentRussianTask = task;
        rememberRussianTaskQuestion(task);

        const topicEl = document.getElementById('questionTopic');
        if (topicEl && task.topic_title) {
            topicEl.style.display = 'block';
            topicEl.textContent = task.topic_title;
        }

        const display = document.getElementById('questionDisplay');
        if (display) display.textContent = String(task.question || '').trim() || 'Задание недоступно';

        setRussianAnswerMode(task);
    })
    .catch(error => {
        console.error('Ошибка загрузки задания:', error);
        const display = document.getElementById('questionDisplay');
        if (display) display.textContent = 'Ошибка загрузки задания';
    });
};

checkRussianTopicAnswer = function() {
    const userAnswer = getCurrentRussianTopicAnswer();
    const resultMessage = document.getElementById('resultMessage');
    if (!resultMessage) return;

    fetch('/russian/check_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            answer: userAnswer,
            correct: currentRussianTask?.correct,
            answer_type: currentRussianTask?.answer_type,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.result === 'correct') {
            resultMessage.textContent = '✓ Правильно!';
            resultMessage.className = 'result-message correct';
            correctAnswers++;
        } else if (data.result === 'empty') {
            resultMessage.textContent = `Вы ничего не выбрали или не ввели. Правильный ответ: ${data.correct_answer}`;
            resultMessage.className = 'result-message empty-answer';
            emptyAnswers++;
            wrongAnswersList.push({...currentRussianTask, userAnswer: '(пусто)', correctAnswer: data.correct_answer});
        } else {
            resultMessage.textContent = `✗ Неправильно. Правильный ответ: ${data.correct_answer}`;
            resultMessage.className = 'result-message incorrect';
            wrongAnswers++;
            wrongAnswersList.push({...currentRussianTask, userAnswer: userAnswer, correctAnswer: data.correct_answer});
        }

        document.getElementById('checkBtn').disabled = true;
        document.getElementById('nextBtn').disabled = false;
        document.getElementById('answerInput').disabled = true;
        setRussianChoiceOptionsDisabled(true);
    })
    .catch(error => {
        console.error('Ошибка проверки:', error);
        resultMessage.textContent = 'Ошибка проверки ответа';
        resultMessage.className = 'result-message incorrect';
    });
};
