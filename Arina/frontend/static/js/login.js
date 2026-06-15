let failedAttempts = Number(localStorage.getItem('arinaLoginFailedAttempts') || '0');
let captchaResult = null;

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
}

function setError(inputId, errorId, message) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    if (input) input.classList.toggle('invalid', Boolean(message));
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
    const keys = ['arinaAccessToken', 'arinaRefreshToken', 'arinaUserId', 'arinaUserEmail', 'arinaRememberMe'];
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
    storage.setItem('arinaRememberMe', String(rememberMe));
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    if (!form) return;

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
                localStorage.setItem('arinaLoginFailedAttempts', String(failedAttempts));
                setLoginFieldsError('Логин или пароль не верный');
                setMessage(data.message || 'Логин или пароль не верный', 'error');
                showCaptchaIfNeeded();
                return;
            }

            failedAttempts = 0;
            localStorage.setItem('arinaLoginFailedAttempts', '0');
            saveAuthData(data.data, rememberMe);
            setMessage(rememberMe ? 'Вход выполнен успешно. Вы останетесь авторизованы после закрытия браузера.' : 'Вход выполнен успешно. Авторизация действует до закрытия страницы или браузера.', 'success');
        } catch (error) {
            setMessage(`Ошибка авторизации: ${error}`, 'error');
        }
    });
});
