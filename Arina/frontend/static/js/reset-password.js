const DANGEROUS_PATTERN = /[<>{}\[\]`'";\\]|--|\/\*|\*\//i;
const PASSWORD_HAS_UPPER = /[A-ZА-ЯЁ]/;
const PASSWORD_HAS_LOWER = /[a-zа-яё]/;
const PASSWORD_HAS_DIGIT = /\d/;
const PASSWORD_HAS_SPECIAL = /[^A-Za-zА-Яа-яЁё0-9]/;

function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';

    if (button) {
        button.textContent = '👁';
        button.classList.toggle('password-visible', visible);
        button.setAttribute('aria-label', visible ? 'Скрыть пароль' : 'Показать пароль');
    }
}

function setError(inputId, errorId, message) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    const wrapper = input ? input.closest('.auth-input-wrapper, .auth-password-wrapper') : null;

    if (input) input.classList.toggle('invalid', Boolean(message));
    if (wrapper) wrapper.classList.toggle('invalid', Boolean(message));
    if (error) error.textContent = message || '';
}

function setMessage(message, type) {
    const box = document.getElementById('resetMessage');
    if (!box) return;
    box.className = `form-message ${type || ''}`;
    box.textContent = message || '';
}

function normalizeServerError(message) {
    if (!message) return '';
    return String(message).replace(/^.*?:\s*/, '').trim();
}

function validatePassword(value) {
    if (!value) return 'обязательное поле.';
    if (value.length < 8 || value.length > 20) return 'от 8 до 20 символов.';
    if (DANGEROUS_PATTERN.test(value)) return 'запрещены опасные спецсимволы.';
    if (!PASSWORD_HAS_UPPER.test(value)) return 'нужна минимум 1 заглавная буква.';
    if (!PASSWORD_HAS_LOWER.test(value)) return 'нужна минимум 1 строчная буква.';
    if (!PASSWORD_HAS_DIGIT.test(value)) return 'нужна минимум 1 цифра.';
    if (!PASSWORD_HAS_SPECIAL.test(value)) return 'нужен минимум 1 спецсимвол.';
    return '';
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('resetPasswordForm');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        setError('newPassword', 'newPasswordError', '');
        setError('newPasswordRepeat', 'newPasswordRepeatError', '');
        setMessage('', '');

        const password = document.getElementById('newPassword').value;
        const passwordRepeat = document.getElementById('newPasswordRepeat').value;
        const token = form.dataset.token;
        const passwordError = validatePassword(password);
        const repeatError = password !== passwordRepeat ? 'Не соответствует введенному паролю' : '';

        if (passwordError || repeatError) {
            setError('newPassword', 'newPasswordError', passwordError);
            setError('newPasswordRepeat', 'newPasswordRepeatError', repeatError);
            setMessage('Исправьте ошибки в полях.', 'error');
            return;
        }

        try {
            const response = await fetch(`/auth/reset-password/${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password, password_repeat: passwordRepeat }),
            });
            const data = await response.json();

            if (!response.ok) {
                if (data.errors) {
                    if (data.errors.password) setError('newPassword', 'newPasswordError', normalizeServerError(data.errors.password));
                    if (data.errors.password_repeat) setError('newPasswordRepeat', 'newPasswordRepeatError', 'Не соответствует введенному паролю');
                }
                setMessage(data.message || 'Не удалось заменить пароль.', 'error');
                return;
            }

            form.reset();
            setMessage(data.message || 'Пароль успешно заменён.', 'success');
        } catch (error) {
            setMessage(`Ошибка замены пароля: ${error}`, 'error');
        }
    });
});
