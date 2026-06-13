function injectWorldChoiceStyles() {
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

injectWorldChoiceStyles();

function getOrCreateWorldChoiceContainer() {
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

function clearWorldChoiceOptions() {
    const container = getOrCreateWorldChoiceContainer();
    container.innerHTML = '';
    container.style.display = 'none';
}

function renderWorldChoiceOptions(choices) {
    const container = getOrCreateWorldChoiceContainer();
    container.innerHTML = '';

    choices.forEach((choice, index) => {
        const id = `worldChoice_${index}`;
        const label = document.createElement('label');
        label.className = 'choice-option';
        label.setAttribute('for', id);

        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'worldChoice';
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

function getSelectedWorldChoice() {
    const selected = document.querySelector('input[name="worldChoice"]:checked');
    return selected ? selected.value : '';
}

function setWorldChoiceOptionsDisabled(disabled) {
    document.querySelectorAll('input[name="worldChoice"]').forEach(input => {
        input.disabled = disabled;
        const label = input.closest('.choice-option');
        if (label) label.classList.toggle('disabled-choice', disabled);
    });
}

function setWorldAnswerMode(task) {
    const answerInput = document.getElementById('answerInput');
    if (!answerInput) return;

    if (task?.answer_type === 'choice' && Array.isArray(task.choices) && task.choices.length > 0) {
        answerInput.value = '';
        answerInput.style.display = 'none';
        renderWorldChoiceOptions(task.choices);
        return;
    }

    clearWorldChoiceOptions();
    answerInput.style.display = 'block';
    answerInput.placeholder = 'Введите ответ';
    answerInput.disabled = false;
    answerInput.focus();
}

function getCurrentWorldTopicAnswer() {
    if (currentWorldTask?.answer_type === 'choice') {
        return getSelectedWorldChoice();
    }

    const answerInput = document.getElementById('answerInput');
    return answerInput ? answerInput.value.trim() : '';
}
