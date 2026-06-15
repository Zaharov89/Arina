// ==== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====
let currentQuestion = 1;
let totalWords = 25;
let correctAnswers = 0;
let wrongAnswers = 0;
let emptyAnswers = 0;
let wrongAnswersList = [];
let currentWord = null;
let currentRussianTask = null;
let usedRussianQuestionTexts = [];
let testStartTime = null;
let questionStartTime = null;
let testTimerInterval = null;
let testWords = [];

// ==== НАВИГАЦИЯ ====
function goBackToMain() {
    window.location.href = '/subjects';
}

function goBackToMenu() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/russian?student=${encodeURIComponent(student)}`;
}

function showTesting() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/russian/test_setup?student=${encodeURIComponent(student)}`;
}

function showRules() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/russian/learning?class=1&student=${encodeURIComponent(student)}`;
}

// ==== НАСТРОЙКИ ТЕСТА ====
function getRussianClass1TopicOptionsHtml() {
    const topics = window.RUSSIAN_CLASS_1_TOPICS || [];
    return topics.map(topic => `<option value="${topic.id}">${topic.title}</option>`).join('');
}

function isRussianTopicClass(classNum) {
    return classNum === '1';
}

function isRussianVocabularyClass(classNum) {
    return classNum === 'vocab_1' || classNum === '2' || classNum === '3' || classNum === 'all';
}

function normalizeRussianVocabularyClass(classNum) {
    return classNum === 'vocab_1' ? '1' : classNum;
}

function setInitialRussianSetupValues() {
    const classSelect = document.getElementById('classSelect');
    if (!classSelect) return;

    if (window.INITIAL_RUSSIAN_CLASS) {
        classSelect.value = window.INITIAL_RUSSIAN_CLASS === '1' && !window.INITIAL_RUSSIAN_TOPIC ? 'vocab_1' : window.INITIAL_RUSSIAN_CLASS;
    }

    updateRussianSetupForClass(classSelect.value);

    const topicSelect = document.getElementById('topicSelect');
    if (topicSelect && window.INITIAL_RUSSIAN_TOPIC) {
        const optionExists = Array.from(topicSelect.options).some(option => option.value === window.INITIAL_RUSSIAN_TOPIC);
        if (optionExists) topicSelect.value = window.INITIAL_RUSSIAN_TOPIC;
    }

    if (window.DIRECT_RUSSIAN_TOPIC_TEST) {
        initDirectRussianTopicMode();
    }
}

function updateRussianSetupForClass(classNum) {
    const topicRow = document.getElementById('topicRow');
    const topicSelect = document.getElementById('topicSelect');
    const questionCountLabel = document.getElementById('questionCountLabel');

    if (isRussianTopicClass(classNum)) {
        if (topicRow) topicRow.style.display = 'flex';
        if (topicSelect) topicSelect.innerHTML = getRussianClass1TopicOptionsHtml();
        if (questionCountLabel) questionCountLabel.textContent = 'Количество заданий:';
    } else {
        if (topicRow) topicRow.style.display = 'none';
        if (questionCountLabel) questionCountLabel.textContent = 'Количество слов:';
    }
}

function goBackFromRussianQuestionCount() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';

    if (window.DIRECT_RUSSIAN_TOPIC_TEST && window.INITIAL_RUSSIAN_TOPIC) {
        window.location.href = `/russian/learning/topic/${window.INITIAL_RUSSIAN_TOPIC}?student=${encodeURIComponent(student)}`;
        return;
    }

    goToStep2();
}

function initDirectRussianTopicMode() {
    const note = document.getElementById('directTopicNote');
    const step1 = document.getElementById('testStep1');
    const step2 = document.getElementById('testStep2');
    const step3 = document.getElementById('testStep3');
    const title = document.getElementById('questionCountStepTitle');
    const classSelect = document.getElementById('classSelect');
    const topicSelect = document.getElementById('topicSelect');

    if (classSelect) classSelect.value = '1';
    updateRussianSetupForClass('1');
    if (topicSelect && window.INITIAL_RUSSIAN_TOPIC) topicSelect.value = window.INITIAL_RUSSIAN_TOPIC;

    if (note) note.style.display = 'block';
    if (step1) step1.style.display = 'none';
    if (step2) step2.style.display = 'none';
    if (step3) step3.style.display = 'block';
    if (title) title.textContent = 'Настройки теста — Шаг 1/1';
}

// ==== ТЕСТИРОВАНИЕ СЛОВАРНЫХ СЛОВ ====
function goToStep1() {
    document.getElementById('testStep1').style.display = 'block';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'none';
}

function goToStep2() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'block';
    document.getElementById('testStep3').style.display = 'none';

    const classSelect = document.getElementById('classSelect');
    if (classSelect) updateRussianSetupForClass(classSelect.value);
}

function goToStep3() {
    const classSelect = document.getElementById('classSelect');
    const classNum = classSelect ? classSelect.value : '1';

    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'block';

    const title = document.getElementById('questionCountStepTitle');
    if (title) title.textContent = isRussianVocabularyClass(classNum) ? 'Настройки теста — Шаг 2/2' : 'Настройки теста — Шаг 3/3';
}

function activateWordCountButton(count) {
    document.querySelectorAll('.question-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const btn = Array.from(document.querySelectorAll('.question-btn')).find(b =>
        parseInt(b.getAttribute('data-count')) === count
    );
    if (btn) btn.classList.add('active');
}

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

    if (currentQuestion > totalWords) {
        finishTest();
        return;
    }

    answerInput.value = '';
    resultMessage.textContent = '';
    resultMessage.className = 'result-message';
    document.getElementById('checkBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    answerInput.disabled = false;
    answerInput.focus();
    questionStartTime = Date.now();

    document.getElementById('questionCounter').textContent = `Слово №${currentQuestion} из ${totalWords}`;

    currentWord = testWords[currentQuestion - 1];
}

function speakCurrentWord() {
    if (currentWord) {
        speakWord(currentWord);
    } else {
        console.error('Нет слова для воспроизведения');
    }
}

function speakWord(word) {
    if (!('speechSynthesis' in window)) {
        alert('Ваш браузер не поддерживает озвучку текста');
        return;
    }

    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = 'ru-RU';
    utterance.rate = 0.8;
    const voices = speechSynthesis.getVoices();
    const selectedVoice = voices.find(voice => voice.lang.startsWith('ru'));
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }

    window.speechSynthesis.speak(utterance);
}

function normalizeYo(text) {
    return String(text).trim().toLowerCase().replace(/ё/g, 'е');
}

function checkAnswer() {
    const userAnswer = document.getElementById('answerInput').value.trim();
    const correctWord = currentWord;

    if (userAnswer === '') {
        document.getElementById('resultMessage').textContent = `Вы ничего не ввели. Правильный ответ: ${correctWord}`;
        document.getElementById('resultMessage').className = 'result-message empty-answer';
        emptyAnswers++;
        wrongAnswersList.push({word: correctWord, userAnswer: '(пусто)', correctAnswer: correctWord});
    } else {
        const normalizedUser = normalizeYo(userAnswer);
        const normalizedCorrect = normalizeYo(correctWord);

        if (normalizedUser === normalizedCorrect) {
            document.getElementById('resultMessage').textContent = '✓ Правильно!';
            document.getElementById('resultMessage').className = 'result-message correct';
            correctAnswers++;
        } else {
            document.getElementById('resultMessage').textContent = `✗ Неправильно. Правильный ответ: ${correctWord}`;
            document.getElementById('resultMessage').className = 'result-message incorrect';
            wrongAnswers++;
            wrongAnswersList.push({word: correctWord, userAnswer: userAnswer, correctAnswer: correctWord});
        }
    }

    document.getElementById('checkBtn').disabled = true;
    document.getElementById('nextBtn').disabled = false;
    document.getElementById('answerInput').disabled = true;
}

function nextQuestion() {
    currentQuestion++;
    generateQuestion();
}

function finishTest() {
    if (testTimerInterval) clearInterval(testTimerInterval);
    const totalTime = Math.round((Date.now() - testStartTime) / 1000);

    localStorage.setItem('testSubject', 'Русский язык');
    localStorage.setItem('totalQuestions', totalWords);
    localStorage.setItem('correctAnswers', correctAnswers);
    localStorage.setItem('wrongAnswers', wrongAnswers);
    localStorage.setItem('emptyAnswers', emptyAnswers);
    localStorage.setItem('timeSpent', totalTime);
    localStorage.setItem('averageTime', totalWords > 0 ? (totalTime / totalWords).toFixed(1) : 0);
    localStorage.setItem('wrongAnswersList', JSON.stringify(wrongAnswersList));

    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/results/russian?student=${encodeURIComponent(student)}`;
}

function startRussianTest() {
    const classSelect = document.getElementById('classSelect');
    if (!classSelect) return;

    const activeBtn = document.querySelector('.question-btn.active');
    const totalWords = activeBtn ? parseInt(activeBtn.getAttribute('data-count')) : 25;
    const selectedClass = classSelect.value;
    const classNum = normalizeRussianVocabularyClass(selectedClass);
    const topicSelect = document.getElementById('topicSelect');
    const topicId = topicSelect ? topicSelect.value : '';
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';

    const params = new URLSearchParams({
        class: classNum,
        words: totalWords,
        student: student,
    });

    if (isRussianTopicClass(selectedClass) && topicId) {
        params.set('type', topicId);
    }

    window.location.href = `/russian/test?${params.toString()}`;
}

// ==== ТЕСТИРОВАНИЕ 1 КЛАССА ПО ТЕМАМ ====
function getRussianTaskQuestionKey(task) {
    if (!task || task.question === undefined || task.question === null) return '';
    return String(task.question).trim();
}

function rememberRussianTaskQuestion(task) {
    const key = getRussianTaskQuestionKey(task);
    if (!key) return;

    if (!usedRussianQuestionTexts.includes(key)) {
        usedRussianQuestionTexts.push(key);
    }

    if (usedRussianQuestionTexts.length > 300) {
        usedRussianQuestionTexts = usedRussianQuestionTexts.slice(-300);
    }
}

function generateRussianTopicQuestion() {
    const answerInput = document.getElementById('answerInput');
    const resultMessage = document.getElementById('resultMessage');
    if (!answerInput || !resultMessage) return;

    if (currentQuestion > totalWords) {
        finishRussianTopicTest();
        return;
    }

    answerInput.value = '';
    resultMessage.textContent = '';
    resultMessage.className = 'result-message';
    document.getElementById('checkBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    answerInput.disabled = false;
    answerInput.focus();

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
        let questionText = String(task.question || '').trim();
        if (Array.isArray(task.choices) && task.choices.length > 0) {
            questionText += `\nВарианты: ${task.choices.join('   ')}`;
        }
        if (display) display.textContent = questionText || 'Задание недоступно';

        answerInput.placeholder = task.answer_type === 'choice' ? 'Введите вариант ответа' : 'Введите ответ';
    })
    .catch(error => {
        console.error('Ошибка загрузки задания:', error);
        const display = document.getElementById('questionDisplay');
        if (display) display.textContent = 'Ошибка загрузки задания';
    });
}

function checkRussianTopicAnswer() {
    const userAnswer = document.getElementById('answerInput').value.trim();
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
            resultMessage.textContent = `Вы ничего не ввели. Правильный ответ: ${data.correct_answer}`;
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
    })
    .catch(error => {
        console.error('Ошибка проверки:', error);
        resultMessage.textContent = 'Ошибка проверки ответа';
        resultMessage.className = 'result-message incorrect';
    });
}

function nextRussianTopicQuestion() {
    currentQuestion++;
    generateRussianTopicQuestion();
}

function finishRussianTopicTest() {
    if (testTimerInterval) clearInterval(testTimerInterval);
    const totalTime = Math.round((Date.now() - testStartTime) / 1000);

    localStorage.setItem('testSubject', 'Русский язык');
    localStorage.setItem('totalQuestions', totalWords);
    localStorage.setItem('correctAnswers', correctAnswers);
    localStorage.setItem('wrongAnswers', wrongAnswers);
    localStorage.setItem('emptyAnswers', emptyAnswers);
    localStorage.setItem('timeSpent', totalTime);
    localStorage.setItem('averageTime', totalWords > 0 ? (totalTime / totalWords).toFixed(1) : 0);
    localStorage.setItem('wrongAnswersList', JSON.stringify(wrongAnswersList));

    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/results/russian?student=${encodeURIComponent(student)}`;
}

// ==== УНИВЕРСАЛЬНЫЕ ФУНКЦИИ ====
function renderDateBar() {
    const dateTimeBar = document.getElementById('dateTimeBar');
    if (!dateTimeBar) return;

    const now = new Date();
    const monthsRu = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    dateTimeBar.textContent =
        `${now.getDate()} ${monthsRu[now.getMonth()]} ${now.getFullYear()} года ` +
        `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
}

// ==== ИНИЦИАЛИЗАЦИЯ ====
document.addEventListener('DOMContentLoaded', function () {
    renderDateBar();

    const classSelect = document.getElementById('classSelect');
    if (classSelect) {
        setInitialRussianSetupValues();
        classSelect.addEventListener('change', function () {
            updateRussianSetupForClass(this.value);
        });
    }

    const startTestBtn = document.getElementById('startTestBtn');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', startRussianTest);
    }

    if (document.getElementById('testBlock')) {
        if (typeof window.testWords !== 'undefined') {
            testWords = window.testWords;
            totalWords = window.totalWords || testWords.length;
            currentQuestion = 1;
            correctAnswers = 0;
            wrongAnswers = 0;
            emptyAnswers = 0;
            wrongAnswersList = [];
            testStartTime = null;
            questionStartTime = null;
            testTimerInterval = null;

            startTestTimer();
            generateQuestion();
        }
    }

    if (document.getElementById('topicTestBlock')) {
        if (typeof window.russianTopicTestSettings !== 'undefined') {
            totalWords = window.totalRussianTopicQuestions || 25;
            currentQuestion = 1;
            correctAnswers = 0;
            wrongAnswers = 0;
            emptyAnswers = 0;
            wrongAnswersList = [];
            usedRussianQuestionTexts = [];
            currentRussianTask = null;
            startTestTimer();
            generateRussianTopicQuestion();
        }
    }

    const answerInput = document.getElementById('answerInput');
    if (answerInput) {
        answerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const checkBtn = document.getElementById('checkBtn');
                const nextBtn = document.getElementById('nextBtn');
                if (checkBtn && !checkBtn.disabled) {
                    if (document.getElementById('topicTestBlock')) {
                        checkRussianTopicAnswer();
                    } else {
                        checkAnswer();
                    }
                } else if (nextBtn && !nextBtn.disabled) {
                    if (document.getElementById('topicTestBlock')) {
                        nextRussianTopicQuestion();
                    } else {
                        nextQuestion();
                    }
                }
            }
        });
    }
});
