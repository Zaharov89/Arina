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

function speakText(text, lang = 'ru-RU') {
    if (!text || !String(text).trim()) return;

    if (!('speechSynthesis' in window)) {
        alert('Ваш браузер не поддерживает озвучивание текста');
        return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(String(text).trim());
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
