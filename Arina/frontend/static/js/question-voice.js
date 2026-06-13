function injectQuestionVoiceStyles() {
    if (document.getElementById('questionVoiceStyles')) return;

    const style = document.createElement('style');
    style.id = 'questionVoiceStyles';
    style.textContent = `
        .question-sound-btn { background: #5d92e0; color: white; border: none; border-radius: 10px; padding: 12px 20px; font-size: 16px; cursor: pointer; transition: all 0.3s; min-width: 150px; }
        .question-sound-btn:hover { background: #4a7bc9; transform: scale(1.05); }
    `;
    document.head.appendChild(style);
}

injectQuestionVoiceStyles();

function getQuestionOnlyText(text) {
    return String(text || '')
        .split('\n')
        .filter(line => {
            const normalized = line.trim().toLowerCase();
            return normalized &&
                !normalized.startsWith('варианты:') &&
                !normalized.startsWith('ответ:') &&
                !normalized.startsWith('правильный ответ:') &&
                !normalized.startsWith('ваш ответ:');
        })
        .map(line => {
            const normalized = line.trim().toLowerCase();

            if (normalized.startsWith('напиши слово:')) {
                return 'Напиши слово';
            }

            if (normalized.startsWith('напиши предложение:')) {
                return 'Напиши предложение';
            }

            return line.trim();
        })
        .join(' ')
        .trim();
}

function speakText(text, lang = 'ru-RU') {
    const questionOnlyText = getQuestionOnlyText(text);
    if (!questionOnlyText) return;

    if (!('speechSynthesis' in window)) {
        alert('Ваш браузер не поддерживает озвучивание текста');
        return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(questionOnlyText);
    utterance.lang = lang;
    utterance.rate = 0.9;

    const voices = window.speechSynthesis.getVoices();
    const selectedVoice = voices.find(voice => voice.lang && voice.lang.startsWith(lang.slice(0, 2)));
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }

    window.speechSynthesis.speak(utterance);
}

function speakQuestion(elementId = 'questionDisplay', lang = 'ru-RU') {
    const questionElement = document.getElementById(elementId);
    if (!questionElement) return;
    speakText(questionElement.textContent || '', lang);
}

if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {};
}
