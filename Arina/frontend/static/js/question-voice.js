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
