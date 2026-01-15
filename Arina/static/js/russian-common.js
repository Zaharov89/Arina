// ==== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====
let class1Words = [];
let class2Words = [];
let class3Words = [];
let allWords = [];

let currentQuestion = 1;
let totalWords = 25;
let correctAnswers = 0;
let wrongAnswers = 0;
let emptyAnswers = 0;
let wrongAnswersList = [];
let currentWord = null;
let testStartTime = null;
let questionStartTime = null;
let testTimerInterval = null;
let testWords = [];

// ==== НАВИГАЦИЯ ====
function goBackToMain() {
    window.location.href = '/';
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
    window.location.href = `/russian/rules?student=${encodeURIComponent(student)}`;
}

// ==== ТЕСТИРОВАНИЕ ====
function goToStep1() {
    document.getElementById('testStep1').style.display = 'block';
    document.getElementById('testStep2').style.display = 'none';
}

function goToStep2() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'block';
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
    // 🔥 Слово НЕ отображается — только звук по кнопке
}

function speakCurrentWord() {
    if (currentWord) {
        speakWord(currentWord);
    } else {
        console.error("Нет слова для воспроизведения");
    }
}

function speakWord(word) {
    if (!('speechSynthesis' in window)) {
        alert("Ваш браузер не поддерживает озвучку текста");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = 'ru-RU';
    utterance.rate = 0.8;
    const voices = speechSynthesis.getVoices();
    let selectedVoice = voices.find(voice => voice.lang.startsWith('ru'));
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }

    window.speechSynthesis.speak(utterance);
}

function normalizeYo(text) {
    return text.toLowerCase().replace(/ё/g, 'е');
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
            document.getElementById('resultMessage').textContent = "✓ Правильно!";
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

    const classNum = classSelect.value;
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';

    window.location.href = `/russian/test?class=${encodeURIComponent(classNum)}&words=${totalWords}&student=${encodeURIComponent(student)}`;
}

// ==== УНИВЕРСАЛЬНЫЕ ФУНКЦИИ ====
function renderDateBar() {
    const dateTimeBar = document.getElementById("dateTimeBar");
    if (!dateTimeBar) return;

    const now = new Date();
    const monthsRu = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];
    dateTimeBar.textContent =
        `${now.getDate()} ${monthsRu[now.getMonth()]} ${now.getFullYear()} года ` +
        `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;
}

// ==== ИНИЦИАЛИЗАЦИЯ ====
document.addEventListener('DOMContentLoaded', function () {
    renderDateBar();

    // Загружаем данные из Flask (для меню и словарика, но не для теста)
    if (typeof window.CLASS1_WORDS !== 'undefined') {
        class1Words = window.CLASS1_WORDS;
        class2Words = window.CLASS2_WORDS;
        class3Words = window.CLASS3_WORDS;
        allWords = [...class1Words, ...class2Words, ...class3Words];
    }

    // Обработчик кнопки "Начать тест"
    const startTestBtn = document.getElementById('startTestBtn');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', startRussianTest);
    }

    // Если мы на странице теста — инициализируем тест
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

    // Enter для ответа
    const answerInput = document.getElementById('answerInput');
    if (answerInput) {
        answerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (!document.getElementById('checkBtn').disabled) {
                    checkAnswer();
                } else if (!document.getElementById('nextBtn').disabled) {
                    nextQuestion();
                }
            }
        });
    }

    // Загрузка голосов
    if ('speechSynthesis' in window) {
        speechSynthesis.onvoiceschanged = () => {};
    }
});