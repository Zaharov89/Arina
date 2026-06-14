document.addEventListener('keydown', function(event) {
    if (event.key !== 'Enter') return;

    const activeElement = document.activeElement;
    const activeTag = activeElement ? activeElement.tagName.toLowerCase() : '';

    if (activeTag === 'textarea') return;

    const answerInput = document.getElementById('answerInput');

    // Пока поле ввода активно и не отключено, Enter обрабатывает старый
    // предметный обработчик. Этот общий обработчик нужен для второго Enter,
    // когда поле уже отключено после проверки ответа.
    if (answerInput && activeElement === answerInput && !answerInput.disabled) {
        return;
    }

    const checkBtn = document.getElementById('checkBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (!checkBtn || !nextBtn) return;

    event.preventDefault();

    if (!checkBtn.disabled) {
        checkBtn.click();
        return;
    }

    if (!nextBtn.disabled) {
        nextBtn.click();
    }
});
