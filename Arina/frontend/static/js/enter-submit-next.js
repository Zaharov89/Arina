document.addEventListener('keydown', function(event) {
    if (event.key !== 'Enter') return;

    const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
    if (activeTag === 'textarea') return;

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
