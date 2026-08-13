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
let currentTargetIndex = 0;
let finished = false;
let currentBlock = null;
let startTime = Date.now();
let blockTimer = null;
const hitZoneLeft = 180;
const hitZoneRight = 282;
const startX = 1050;
const speedPx = 8;
const frameMs = 24;

const FINGER_BY_KEY = {
    ru: {'Ф':'l-pinky','Ы':'l-ring','В':'l-middle','А':'l-index','О':'r-index','Л':'r-middle','Д':'r-ring','Ж':'r-pinky','Э':'r-pinky','П':'l-pinky','Р':'l-index','К':'l-middle','Е':'l-index','М':'l-index','И':'r-index','С':'l-middle','Т':'r-index'},
    en: {'A':'l-pinky','S':'l-ring','D':'l-middle','F':'l-index','J':'r-index','K':'r-middle','L':'r-ring',';':'r-pinky','E':'l-middle','I':'r-middle','R':'l-index','U':'r-index','T':'l-index','Y':'r-index','C':'l-middle','M':'r-index'}
};

function getAuthStorage() { if (localStorage.getItem('arinaAccessToken')) return localStorage; if (sessionStorage.getItem('arinaAccessToken')) return sessionStorage; return null; }
function getAccessToken() { const storage = getAuthStorage(); return storage ? storage.getItem('arinaAccessToken') : ''; }
async function loadProgress() { const token = getAccessToken(); if (!token) return null; const response = await fetch(`/api/typing-trainer/progress?layout=${config.layoutCode}`, {headers: {'Authorization': `Bearer ${token}`}}); if (!response.ok) return null; return response.json(); }

function freezeGameScene() {
    document.body.classList.add('typing-game-ended');
    if (scene) scene.classList.add('game-ended');
    const animal = document.getElementById('typingAnimal');
    if (animal) animal.classList.add('animal-stopped');
}

function removeAllBlocks() {
    document.querySelectorAll('.letter-block').forEach(block => block.remove());
    currentBlock = null;
}

async function ensureLevelIsUnlocked() {
    const progressPayload = await loadProgress().catch(() => null);
    const progress = progressPayload && progressPayload.progress ? progressPayload.progress : null;
    if (!progress) return true;
    if (Number(config.level.level) <= Number(progress.max_unlocked_level || 1)) return true;
    finished = true;
    freezeGameScene();
    clearInterval(blockTimer);
    removeAllBlocks();
    clearKeyboardHighlights();
    message.innerHTML = `<div class="typing-result-card"><h2>Уровень пока закрыт</h2><p>Сначала пройди уровень ${progress.max_unlocked_level}.</p><div class="typing-actions"><a class="typing-btn blue-btn" href="/typing-trainer/game?layout=${config.layoutCode}&animal=${config.animalCode}&level=${progress.max_unlocked_level}&student=${encodeURIComponent(config.student)}">К открытому уровню</a></div></div>`;
    return false;
}

function randomTarget() { const targets = Array.isArray(config.level.chunks) && config.level.chunks.length ? config.level.chunks : config.level.letters; return targets[Math.floor(Math.random() * targets.length)]; }
function getExpectedChar() { if (!currentBlock) return ''; return (currentBlock.dataset.letter || '').charAt(currentTargetIndex).toUpperCase(); }
function keySelector(value) { return `.typing-key[data-key="${String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"]`; }
function clearKeyboardHighlights() { document.querySelectorAll('.typing-key.active-key').forEach(key => key.classList.remove('active-key')); document.querySelectorAll('.finger-dot.active-finger').forEach(dot => dot.classList.remove('active-finger')); }
function highlightExpectedKey() {
    clearKeyboardHighlights();
    const expected = getExpectedChar();
    if (!expected) return;
    const keyElement = document.querySelector(keySelector(expected));
    if (keyElement) keyElement.classList.add('active-key');
    const finger = (FINGER_BY_KEY[config.layoutCode] || {})[expected];
    if (finger) document.querySelectorAll(`.finger-dot[data-finger="${finger}"]`).forEach(dot => dot.classList.add('active-finger'));
}
function renderTargetProgress() { if (!currentBlock) return; const target = currentBlock.dataset.letter || ''; currentBlock.innerHTML = `<span class="typed-part">${target.slice(0, currentTargetIndex)}</span><span>${target.slice(currentTargetIndex)}</span>`; }

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
    if (finished || spawned >= config.level.total_letters) { if (!currentBlock) finishGame(); return; }
    const block = document.createElement('div');
    block.className = 'letter-block';
    block.textContent = randomTarget();
    block.dataset.letter = block.textContent;
    block.dataset.x = String(startX);
    block.style.left = `${startX}px`;
    if (block.textContent.length > 1) block.classList.add('chunk-block');
    scene.appendChild(block);
    currentBlock = block;
    currentTargetIndex = 0;
    spawned += 1;
    message.textContent = `Нажми: ${block.dataset.letter}`;
    renderTargetProgress();
    highlightExpectedKey();
    animateBlock(block);
}

function animateBlock(block) {
    clearInterval(blockTimer);
    blockTimer = setInterval(() => {
        if (finished || block !== currentBlock) { clearInterval(blockTimer); return; }
        const x = Number(block.dataset.x) - speedPx;
        block.dataset.x = String(x);
        block.style.left = `${x}px`;
        if (x < 95) missBlock(block);
    }, frameMs);
}
function removeBlock(block) { clearInterval(blockTimer); clearKeyboardHighlights(); setTimeout(() => { if (block && block.parentElement) block.remove(); currentBlock = null; currentTargetIndex = 0; if (!finished) setTimeout(createBlock, 260); }, 180); }
function hitBlock(block) { block.classList.add('success'); correct += 1; message.textContent = 'Отлично!'; updateStats(); removeBlock(block); }
function failBlock(block, reason) {
    block.classList.add('fail');
    wrong += 1;
    lives -= 1;
    if (reason === 'early') earlyHits += 1;
    if (reason === 'late') lateHits += 1;
    message.textContent = reason === 'wrong' ? 'Не та клавиша!' : reason === 'early' ? 'Рано!' : 'Поздно!';
    updateStats();
    if (lives <= 0) { setTimeout(finishGame, 180); return; }
    removeBlock(block);
}
function missBlock(block) {
    missed += 1;
    lives -= 1;
    message.textContent = 'Поздно! Кубик убежал.';
    updateStats();
    if (lives <= 0) { setTimeout(finishGame, 180); return; }
    removeBlock(block);
}

function handleKey(event) {
    if (finished || !currentBlock) return;
    const pressed = event.key.length === 1 ? event.key.toUpperCase() : event.key;
    const expected = getExpectedChar();
    const x = Number(currentBlock.dataset.x);
    if (pressed !== expected) { failBlock(currentBlock, 'wrong'); return; }
    if (x > hitZoneRight) { failBlock(currentBlock, 'early'); return; }
    if (x < hitZoneLeft) { failBlock(currentBlock, 'late'); return; }
    currentTargetIndex += 1;
    const target = currentBlock.dataset.letter || '';
    if (currentTargetIndex >= target.length) { hitBlock(currentBlock); return; }
    renderTargetProgress();
    highlightExpectedKey();
    message.textContent = `Продолжай: ${target.slice(currentTargetIndex)}`;
}

async function saveAttempt(result) { const token = getAccessToken(); if (!token) return null; const response = await fetch('/api/typing-trainer/attempts', {method: 'POST', headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`}, body: JSON.stringify(result)}); return response.json(); }
async function finishGame() {
    if (finished) return;
    finished = true;
    clearInterval(blockTimer);
    clearKeyboardHighlights();
    freezeGameScene();
    removeAllBlocks();
    const total = correct + wrong + missed;
    const durationSeconds = Math.max((Date.now() - startTime) / 1000, 1);
    const accuracy = total ? Math.round((correct / total) * 100) : 0;
    const speed = Math.round(correct / (durationSeconds / 60));
    const isPassed = lives > 0 && accuracy >= Number(config.level.required_accuracy || 80) && correct >= Math.floor(config.level.total_letters * 0.7);
    const result = {layout_code: config.layoutCode, animal_code: config.animalCode, level_number: config.level.level, total_letters: total, correct_letters: correct, wrong_letters: wrong, missed_letters: missed, early_hits: earlyHits, late_hits: lateHits, accuracy_percent: accuracy, duration_seconds: durationSeconds, speed_cpm: speed, is_passed: isPassed};
    let saveResult = null;
    try { saveResult = await saveAttempt(result); } catch (error) { console.error('typing trainer save failed', error); }
    sessionStorage.setItem('typingTrainerLastResult', JSON.stringify({...result, save_status: saveResult ? saveResult.status : 'not_saved'}));
    const nextLevel = config.level.level + 1;
    const maxUnlocked = saveResult && saveResult.progress ? Number(saveResult.progress.max_unlocked_level) : config.level.level;
    const nextLink = isPassed && nextLevel <= maxUnlocked ? `<a class="typing-btn green-btn" href="/typing-trainer/game?layout=${config.layoutCode}&animal=${config.animalCode}&level=${nextLevel}&student=${encodeURIComponent(config.student)}">Следующий уровень</a>` : '';
    const resultLink = `<a class="typing-btn orange-btn" href="/typing-trainer/result?layout=${config.layoutCode}&animal=${config.animalCode}&student=${encodeURIComponent(config.student)}">Подробный результат</a>`;
    message.innerHTML = `<div class="typing-result-card"><h2>${isPassed ? 'Уровень пройден!' : 'Попробуй ещё раз'}</h2><p>Точность: ${accuracy}%</p><p>Скорость: ${speed} зн/мин</p><p>Правильно: ${correct}, ошибок: ${wrong}, пропущено: ${missed}</p><div class="typing-actions"><button class="typing-btn blue-btn" onclick="restartTypingGame()">Повторить</button>${resultLink}${nextLink}</div></div>`;
}
function restartTypingGame() { window.location.reload(); }
async function startTypingGame() { document.addEventListener('keydown', handleKey); updateStats(); const unlocked = await ensureLevelIsUnlocked(); if (unlocked) setTimeout(createBlock, 700); }
startTypingGame();
