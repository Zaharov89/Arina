const EMAIL_PATTERN = /^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,20}$/;
const DANGEROUS_PATTERN = /[<>{}\[\]`'";\\]|--|\/\*|\*\//i;

function setError(inputId, errorId, message) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    const wrapper = input ? input.closest('.auth-input-wrapper, .auth-password-wrapper') : null;

    if (input) input.classList.toggle('invalid', Boolean(message));
    if (wrapper) wrapper.classList.toggle('invalid', Boolean(message));
    if (error) error.textContent = message || '';
}

function setMessage(message, type) {
    const box = document.getElementById('forgotMessage');
    if (!box) return;
    box.className = `form-message ${type || ''}`;
    box.textContent = message || '';
}

function normalizeServerError(message) {
    if (!message) return '';
    return String(message).replace(/^.*?:\s*/, '').trim();
}

function validateEmail(email) {
    if (!email) return 'обязательное поле.';
    if (email.length > 100) return 'максимум 100 символов.';
    if (DANGEROUS_PATTERN.test(email)) return 'запрещены спецсимволы.';
    if (!EMAIL_PATTERN.test(email)) return 'формат text@example.ru, только латиница.';
    return '';
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('forgotPasswordForm');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        setError('forgotEmail', 'forgotEmailError', '');
        setMessage('', '');

        const email = document.getElementById('forgotEmail').value.trim().toLowerCase();
        const emailError = validateEmail(email);
        if (emailError) {
            setError('forgotEmail', 'forgotEmailError', emailError);
            setMessage('Исправьте почту.', 'error');
            return;
        }

        try {
            const response = await fetch('/auth/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }),
            });
            const data = await response.json();

            if (!response.ok) {
                if (data.errors && data.errors.email) setError('forgotEmail', 'forgotEmailError', normalizeServerError(data.errors.email));
                setMessage(data.message || 'Не удалось отправить ссылку.', 'error');
                return;
            }

            let message = data.message || 'Если почта зарегистрирована, ссылка отправлена.';
            if (data.data && data.data.reset_link_dev) {
                message += ` SMTP пока не настроен. Тестовая ссылка: ${data.data.reset_link_dev}`;
            }
            setMessage(message, 'success');
        } catch (error) {
            setMessage(`Ошибка отправки: ${error}`, 'error');
        }
    });
});
