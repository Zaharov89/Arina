const config = window.typingTrainerConfig;
const scene = document.getElementById('gameScene');
const message = document.getElementById('typingMessage');
const livesValue = document.getElementById('livesValue');
const correctValue = document.getElementById('correctValue');
const accuracyValue = document.getElementById('accuracyValue');
const speedValue = document.getElementById('speedValue');

let lives = 3;
let correct = 0;
let wrong = 0;
let missed = 0;
let earlyHits = 0;
let lateHits = 0;
let spawned = 0;
let finished = false;
let currentBlock = null;
let startTime = Date.now();
let blockTimer = null;
let missTimer = null;
const hitZoneLeft = 180;
const hitZoneRight = 282;
const startX = 1050;
const speedPx = 8;
const frameMs = 24;

function getAuthStorage() {
    if (localStorage.getItem('arinaAccessToken')) return localStorage;
    if (sessionStorage.getItem('arinaAccessToken')) return sessionStorage;
    return null;
}

function randomLetter() {
    const letters = config.level.letters;
    return letters[Math.floor(Math.random() * letters.length)];
}

function updateStats() {
    const totalAnswered = correct + wrong + missed;
    const accuracy = totalAnswered ? Math.round((correct / totalAnswered) * 100) : 0;
    const durationMinutes = Math.max((Date.now() - startTime) / 60000, 0.01);
    const speed = Math.round(correct / durationMinutes);
    livesValue.textContent = String(lives);
    correctValue.textContent = String(correct);
    accuracyValue.textContent = `${accuracy}%`;
    speedValue.textContent = `${speed} зн/мин`;
}

function createBlock() {
    if (finished || spawned >= config.level.total_letters) {
        if (!currentBlock) finishGame();
        return;
    }
    const block = document.createElement('div');
    block.className = 'letter-block';
    block.textContent = randomLetter();
    block.dataset.letter = block.textContent;
    block.dataset.x = String(startX);
    block.style.left = `${startX}px`;
    scene.appendChild(block);
    currentBlock = block;
    spawned += 1;
    message.textContent = `Нажми: ${block.dataset.letter}`;
    animateBlock(block);
}

function animateBlock(block) {
    clearInterval(blockTimer);
    clearTimeout(missTimer);
    blockTimer = setInterval(() => {
        if (finished || block !== currentBlock) {
            clearInterval(blockTimer);
            return;
        }
        const x = Number(block.dataset.x) - speedPx;
        block.dataset.x = String(x);
        block.style.left = `${x}px`;
        if (x < 95) {
            missBlock(block, true);
        }
    }, frameMs);
}

function removeBlock(block) {
    clearInterval(blockTimer);
    clearTimeout(missTimer);
    setTimeout(() => {
        if (block && block.parentElement) block.remove();
        currentBlock = null;
        if (!finished) setTimeout(createBlock, 260);
    }, 180);
}

function hitBlock(block) {
    block.classList.add('success');
    correct += 1;
    message.textContent = 'Отлично!';
    updateStats();
    removeBlock(block);
}

function failBlock(block, reason) {
    block.classList.add('fail');
    wrong += 1;
    lives -= 1;
    if (reason === 'early') earlyHits += 1;
    if (reason === 'late') lateHits += 1;
    message.textContent = reason === 'wrong' ? 'Не та клавиша!' : reason === 'early' ? 'Рано!' : 'Поздно!';
    updateStats();
    removeBlock(block);
    if (lives <= 0) setTimeout(finishGame, 300);
}

function missBlock(block) {
    missed += 1;
    lives -= 1;
    message.textContent = 'Поздно! Кубик убежал.';
    updateStats();
    removeBlock(block);
    if (lives <= 0) setTimeout(finishGame, 300);
}

function handleKey(event) {
    if (finished || !currentBlock) return;
    const pressed = event.key.length === 1 ? event.key.toUpperCase() : event.key;
    const expected = currentBlock.dataset.letter.toUpperCase();
    const x = Number(currentBlock.dataset.x);
    if (pressed !== expected) {
        failBlock(currentBlock, 'wrong');
        return;
    }
    if (x > hitZoneRight) {
        failBlock(currentBlock, 'early');
        return;
    }
    if (x < hitZoneLeft) {
        failBlock(currentBlock, 'late');
        return;
    }
    hitBlock(currentBlock);
}

async function saveAttempt(result) {
    const storage = getAuthStorage();
    const token = storage ? storage.getItem('arinaAccessToken') : '';
    if (!token) return null;
    const response = await fetch('/api/typing-trainer/attempts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
        body: JSON.stringify(result)
    });
    return response.json();
}

async function finishGame() {
    if (finished) return;
    finished = true;
    clearInterval(blockTimer);
    clearTimeout(missTimer);
    const total = correct + wrong + missed;
    const durationSeconds = Math.max((Date.now() - startTime) / 1000, 1);
    const accuracy = total ? Math.round((correct / total) * 100) : 0;
    const speed = Math.round(correct / (durationSeconds / 60));
    const isPassed = lives > 0 && accuracy >= Number(config.level.required_accuracy || 80) && correct >= Math.floor(config.level.total_letters * 0.7);
    const result = {
        layout_code: config.layoutCode,
        animal_code: config.animalCode,
        level_number: config.level.level,
        total_letters: total,
        correct_letters: correct,
        wrong_letters: wrong,
        missed_letters: missed,
        early_hits: earlyHits,
        late_hits: lateHits,
        accuracy_percent: accuracy,
        duration_seconds: durationSeconds,
        speed_cpm: speed,
        is_passed: isPassed
    };
    let saveResult = null;
    try { saveResult = await saveAttempt(result); } catch (error) { console.error('typing trainer save failed', error); }
    const nextLevel = config.level.level + 1;
    const nextLink = isPassed ? `<a class="typing-btn green-btn" href="/typing-trainer/game?layout=${config.layoutCode}&animal=${config.animalCode}&level=${nextLevel}&student=${encodeURIComponent(config.student)}">Следующий уровень</a>` : '';
    message.innerHTML = `<div class="typing-result-card"><h2>${isPassed ? 'Уровень пройден!' : 'Попробуй ещё раз'}</h2><p>Точность: ${accuracy}%</p><p>Скорость: ${speed} зн/мин</p><p>Правильно: ${correct}, ошибок: ${wrong}, пропущено: ${missed}</p><div class="typing-actions"><button class="typing-btn blue-btn" onclick="restartTypingGame()">Повторить</button>${nextLink}</div></div>`;
}

function restartTypingGame() {
    window.location.reload();
}

document.addEventListener('keydown', handleKey);
updateStats();
setTimeout(createBlock, 700);
