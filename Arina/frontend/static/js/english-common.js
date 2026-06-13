// ==== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====
let class2Words = [];
let class3Words = [];
let allWords = [];

let currentVocabPage = 1;
const WORDS_PER_PAGE = 50;

let currentQuestion = 1;
let totalWords = 25;
let correctAnswers = 0;
let wrongAnswers = 0;
let emptyAnswers = 0;
let wrongAnswersList = [];
let currentWord = null;
let currentDirection = null;
let isCurrentAnswerChecked = false;
let testWords = [];
let testStartTime = null;
let questionStartTime = null;
let testTimerInterval = null;
let questionDirections = []; // ← НОВОЕ: массив направлений для mixed-режима

// ==== НАВИГАЦИЯ ====
function goBackToMain() {
    window.location.href = '/';
}

function goBackToMenu() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/english/menu?student=${encodeURIComponent(student)}`;
}

function showVocabulary() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/english/vocabulary?student=${encodeURIComponent(student)}`;
}

function showRulesSelection() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/english/rules?student=${encodeURIComponent(student)}`;
}

function showTesting() {
    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/english/test_setup?student=${encodeURIComponent(student)}`;
}

// ==== СЛОВАРИК ====
function renderVocabulary() {
    const startIndex = (currentVocabPage - 1) * WORDS_PER_PAGE;
    const endIndex = startIndex + WORDS_PER_PAGE;
    const pageWords = allWords.slice(startIndex, endIndex);

    const tbody = document.getElementById('vocabularyTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (pageWords.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 20px;">Слова не найдены.</td></tr>`;
        return;
    }

    pageWords.forEach((entry) => {
        const en = entry.en[0];
        const transcription = entry.transcription[0] || '';
        const ru = Array.isArray(entry.ru) ? entry.ru.join(', ') : entry.ru;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${en}</strong></td>
            <td>${transcription}</td>
            <td>${ru}</td>
            <td><button class="sound-btn" onclick="speakWordWithLang('${en.replace(/'/g, "\\'")}', 'en-US')">🔊</button></td>
        `;
        tbody.appendChild(row);
    });

    renderPagination();
}

function renderPagination() {
    const pagination = document.getElementById('vocabularyPagination');
    if (!pagination) return;

    const totalPages = Math.ceil(allWords.length / WORDS_PER_PAGE);
    pagination.innerHTML = '';

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.classList.add('page-btn');
        if (i === currentVocabPage) btn.classList.add('active');
        btn.onclick = () => {
            currentVocabPage = i;
            renderVocabulary();
        };
        pagination.appendChild(btn);
    }
}

// ==== ПРАВИЛА ====
function showRuleImage(imageNames, title) {
    const rulesSelection = document.getElementById('rulesSelection');
    const ruleImageDisplay = document.getElementById('ruleImageDisplay');
    if (!rulesSelection || !ruleImageDisplay) return;

    rulesSelection.style.display = 'none';
    ruleImageDisplay.style.display = 'block';
    document.getElementById('ruleTitle').textContent = title;

    const container = document.getElementById('ruleImageContainer');
    container.innerHTML = '';

    if (typeof imageNames === 'string') {
        imageNames = [imageNames];
    }

    const imagesContainer = document.createElement('div');
    imagesContainer.style.display = 'flex';
    imagesContainer.style.flexWrap = 'wrap';
    imagesContainer.style.gap = '15px';
    imagesContainer.style.justifyContent = 'center';
    imagesContainer.style.alignItems = 'center';
    imagesContainer.style.padding = '20px';
    imagesContainer.style.backgroundColor = '#fff';
    imagesContainer.style.borderRadius = '12px';
    imagesContainer.style.boxShadow = '0 4px 16px rgba(0,0,0,0.1)';
    imagesContainer.style.maxWidth = '100%';

    imageNames.forEach((imageName) => {
        const img = document.createElement('img');
        img.src = `/static/img/${imageName}`;
        img.alt = title;
        img.style.maxWidth = '48%';
        img.style.maxHeight = '70vh';
        img.style.objectFit = 'contain';
        img.style.borderRadius = '8px';
        img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        img.style.transition = 'transform 0.3s';
        img.style.cursor = 'pointer';

        img.addEventListener('mouseenter', () => {
            img.style.transform = 'scale(1.05)';
        });

        img.addEventListener('mouseleave', () => {
            img.style.transform = 'scale(1)';
        });

        imagesContainer.appendChild(img);
    });

    container.appendChild(imagesContainer);
}

// ==== ТЕСТИРОВАНИЕ ====
function goToStep1() {
    document.getElementById('testStep1').style.display = 'block';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'none';
}

function goToStep2() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'block';
    document.getElementById('testStep3').style.display = 'none';
}

function goToStep3() {
    document.getElementById('testStep1').style.display = 'none';
    document.getElementById('testStep2').style.display = 'none';
    document.getElementById('testStep3').style.display = 'block';
}

function selectWordCount(count) {
    totalWords = count;
    activateWordCountButton(count);
}

function activateWordCountButton(count) {
    document.querySelectorAll('.question-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const btn = Array.from(document.querySelectorAll('.question-btn')).find(b => b.textContent == count);
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
    isCurrentAnswerChecked = false;
    document.getElementById('checkBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    answerInput.disabled = false;
    answerInput.focus();
    questionStartTime = Date.now();

    document.getElementById('questionCounter').textContent = `Слово №${currentQuestion} из ${totalWords}`;

    currentWord = testWords[currentQuestion - 1];

    // 🔥 ОПРЕДЕЛЯЕМ НАПРАВЛЕНИЕ ДЛЯ ЭТОГО ВОПРОСА
    if (window.testType === 'mixed') {
        // Используем предварительно сгенерированный сбалансированный массив
        currentDirection = questionDirections[currentQuestion - 1];
    } else {
        currentDirection = window.testType;
    }

    if (currentDirection === 'en_to_ru') {
        document.getElementById('questionDisplay').textContent = currentWord.en[0];
    } else {
        document.getElementById('questionDisplay').textContent = currentWord.ru[0];
    }
}

function speakCurrentQuestionWord() {
    const word = document.getElementById('questionDisplay').textContent;
    if (currentDirection === 'en_to_ru') {
        speakWordWithLang(word, 'en-US');
    } else {
        speakWordWithLang(word, 'ru-RU');
    }
}

function speakWordWithLang(word, lang) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = lang;
        utterance.rate = lang === 'en-US' ? 0.8 : 1.0;
        const voices = speechSynthesis.getVoices();
        const targetVoice = voices.find(voice => voice.lang.startsWith(lang));
        if (targetVoice) {
            utterance.voice = targetVoice;
        }
        window.speechSynthesis.speak(utterance);
    }
}

function checkAnswer() {
    if (!currentWord) return;

    const userAnswer = document.getElementById('answerInput').value.trim();
    const isAnswerEmpty = userAnswer === '';

    let correctAnswersList = [];
    let correctAnswerDisplay = '';
    let isCorrect = false;
    let message = '';

    if (currentDirection === 'en_to_ru') {
        correctAnswersList = currentWord.ru.map(r => r.toLowerCase());
        correctAnswerDisplay = currentWord.ru[0];
        isCorrect = correctAnswersList.includes(userAnswer.toLowerCase());
    } else {
        correctAnswersList = currentWord.en.map(e => e.toLowerCase());
        correctAnswerDisplay = currentWord.en[0];
        isCorrect = correctAnswersList.includes(userAnswer.toLowerCase());
    }

    if (isAnswerEmpty) {
        message = `Вы ничего не ввели. Правильный ответ: ${correctAnswerDisplay}`;
        document.getElementById('resultMessage').className = 'result-message empty-answer';
        emptyAnswers++;
        wrongAnswersList.push({
            ...currentWord,
            userAnswer: '(пусто)',
            correctAnswer: correctAnswerDisplay,
            direction: currentDirection
        });
    } else if (isCorrect) {
        message = "✓ Правильно!";
        document.getElementById('resultMessage').className = 'result-message correct';
        correctAnswers++;
    } else {
        message = `✗ Неправильно. Правильный ответ: ${correctAnswerDisplay}`;
        document.getElementById('resultMessage').className = 'result-message incorrect';
        wrongAnswers++;
        wrongAnswersList.push({
            ...currentWord,
            userAnswer,
            correctAnswer: correctAnswerDisplay,
            direction: currentDirection
        });
    }

    document.getElementById('resultMessage').textContent = message;
    document.getElementById('checkBtn').disabled = true;
    document.getElementById('nextBtn').disabled = false;
    document.getElementById('answerInput').disabled = true;
    isCurrentAnswerChecked = true;
}

function nextQuestion() {
    if (!isCurrentAnswerChecked) return;
    currentQuestion++;
    generateQuestion();
}

function finishTest() {
    if (testTimerInterval) clearInterval(testTimerInterval);
    const totalTime = Math.round((Date.now() - testStartTime) / 1000);

    localStorage.setItem('testSubject', 'Английский язык');
    localStorage.setItem('totalQuestions', totalWords);
    localStorage.setItem('correctAnswers', correctAnswers);
    localStorage.setItem('wrongAnswers', wrongAnswers);
    localStorage.setItem('emptyAnswers', emptyAnswers);
    localStorage.setItem('timeSpent', totalTime);
    localStorage.setItem('averageTime', totalWords > 0 ? (totalTime / totalWords).toFixed(1) : 0);
    localStorage.setItem('wrongAnswersList', JSON.stringify(wrongAnswersList));

    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';
    window.location.href = `/results/english?student=${encodeURIComponent(student)}`;
}

function startEnglishTest() {
    const classSelect = document.getElementById('classSelect');
    const testTypeSelect = document.getElementById('testTypeSelect');
    if (!classSelect || !testTypeSelect) return;

    const classNum = classSelect.value;
    const testType = testTypeSelect.value;

    const activeBtn = document.querySelector('.question-btn.active');
    const totalWords = activeBtn ? parseInt(activeBtn.getAttribute('data-count')) : 25;

    const student = new URLSearchParams(window.location.search).get('student') || 'Арина';

    const params = new URLSearchParams({
        class: classNum,
        words: totalWords,
        type: testType,
        student: student
    });

    window.location.href = `/english/test?${params.toString()}`;
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

    if (typeof window.CLASS2_WORDS !== 'undefined') {
        class2Words = window.CLASS2_WORDS;
        class3Words = window.CLASS3_WORDS;
        allWords = [...class2Words, ...class3Words];

        if (document.getElementById('vocabularyTableBody')) {
            renderVocabulary();
        }

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

            // 🔥 ГЕНЕРАЦИЯ СБАЛАНСИРОВАННЫХ НАПРАВЛЕНИЙ ДЛЯ MIXED
            if (window.testType === 'mixed') {
                questionDirections = [];
                const half = Math.ceil(totalWords / 2);
                for (let i = 0; i < half; i++) {
                    questionDirections.push('en_to_ru');
                }
                for (let i = half; i < totalWords; i++) {
                    questionDirections.push('ru_to_en');
                }
                // Перемешиваем
                for (let i = questionDirections.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [questionDirections[i], questionDirections[j]] = [questionDirections[j], questionDirections[i]];
                }
            }

            startTestTimer();
            generateQuestion();
        }
    }

    const startTestBtn = document.getElementById('startTestBtn');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', startEnglishTest);
    }

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

    if ('speechSynthesis' in window) {
        speechSynthesis.onvoiceschanged = () => {};
    }
});