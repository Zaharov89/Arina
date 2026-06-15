let failedAttempts = Number(sessionStorage.getItem('arinaLoginFailedAttempts') || '0');
let captchaResult = null;

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

function setLoginFieldsError(message) {
    setError('loginEmail', 'loginEmailError', message);
    setError('loginPassword', 'loginPasswordError', message);
}

function setMessage(message, type) {
    const box = document.getElementById('loginMessage');
    if (!box) return;
    box.className = `form-message ${type || ''}`;
    box.textContent = message || '';
}

function showToast(message) {
    if (!message) return;

    const oldToast = document.querySelector('.auth-toast');
    if (oldToast) oldToast.remove();

    const toast = document.createElement('div');
    toast.className = 'auth-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('hide'), 4650);
    setTimeout(() => toast.remove(), 5000);
}

function showStoredToast() {
    const message = sessionStorage.getItem('arinaAuthToast');
    if (!message) return;
    sessionStorage.removeItem('arinaAuthToast');
    showToast(message);
}

function generateCaptcha() {
    const a = Math.floor(Math.random() * 8) + 2;
    const b = Math.floor(Math.random() * 8) + 2;
    captchaResult = a + b;
    document.getElementById('captchaQuestion').textContent = `Сколько будет ${a} + ${b}?`;
    document.getElementById('captchaAnswer').value = '';
}

function showCaptchaIfNeeded() {
    const captchaRow = document.getElementById('captchaRow');
    if (!captchaRow) return;

    if (failedAttempts >= 3) {
        captchaRow.style.display = 'block';
        if (captchaResult === null) generateCaptcha();
    } else {
        captchaRow.style.display = 'none';
    }
}

function validateCaptcha() {
    if (failedAttempts < 3) return true;

    const answer = Number(document.getElementById('captchaAnswer').value);
    if (answer !== captchaResult) {
        setError('captchaAnswer', 'captchaError', 'Введите правильный ответ на капчу.');
        return false;
    }

    setError('captchaAnswer', 'captchaError', '');
    return true;
}

function clearAuthStorage() {
    const keys = ['arinaAccessToken', 'arinaRefreshToken', 'arinaUserId', 'arinaUserEmail', 'arinaUserFirstName', 'arinaUserLastName', 'arinaUserDisplayName', 'arinaRememberMe'];
    keys.forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
    });
}

function saveAuthData(data, rememberMe) {
    clearAuthStorage();

    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem('arinaAccessToken', data.access_token);
    storage.setItem('arinaRefreshToken', data.refresh_token);
    storage.setItem('arinaUserId', data.user_id);
    storage.setItem('arinaUserEmail', data.email);
    storage.setItem('arinaUserFirstName', data.first_name || '');
    storage.setItem('arinaUserLastName', data.last_name || '');
    storage.setItem('arinaUserDisplayName', data.display_name || data.email);
    storage.setItem('arinaRememberMe', String(rememberMe));
}

function getNextUrl() {
    const next = new URLSearchParams(window.location.search).get('next');
    if (!next || !next.startsWith('/')) return '/subjects';
    if (next === '/' || next.startsWith('/auth/')) return '/subjects';
    return next;
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    if (!form) return;

    showStoredToast();
    showCaptchaIfNeeded();

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        setLoginFieldsError('');
        setError('captchaAnswer', 'captchaError', '');
        setMessage('', '');

        if (!validateCaptcha()) {
            setMessage('Подтвердите, что вы человек.', 'error');
            return;
        }

        const rememberMe = document.getElementById('rememberMe').checked;
        const payload = {
            login: document.getElementById('loginEmail').value.trim().toLowerCase(),
            password: document.getElementById('loginPassword').value,
            remember_me: rememberMe,
        };

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();

            if (!response.ok) {
                failedAttempts += 1;
                sessionStorage.setItem('arinaLoginFailedAttempts', String(failedAttempts));
                setLoginFieldsError('Логин или пароль не верный');
                setMessage(data.message || 'Неверный логин или пароль', 'error');
                showCaptchaIfNeeded();
                return;
            }

            failedAttempts = 0;
            sessionStorage.setItem('arinaLoginFailedAttempts', '0');
            saveAuthData(data.data, rememberMe);
            setMessage(rememberMe ? 'Вход выполнен успешно. Вы останетесь авторизованы после закрытия браузера.' : 'Вход выполнен успешно. Авторизация действует до закрытия страницы или браузера.', 'success');
            window.location.href = getNextUrl();
        } catch (error) {
            setMessage(`Ошибка авторизации: ${error}`, 'error');
        }
    });
});
