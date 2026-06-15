const NAME_PATTERN = /^[A-Za-zА-Яа-яЁё]{1,60}$/;
const EMAIL_PATTERN = /^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,20}$/;
const DANGEROUS_PATTERN = /[<>{}\[\]`'";\\]|--|\/\*|\*\//i;
const PASSWORD_HAS_UPPER = /[A-ZА-ЯЁ]/;
const PASSWORD_HAS_LOWER = /[a-zа-яё]/;
const PASSWORD_HAS_DIGIT = /\d/;
const PASSWORD_HAS_SPECIAL = /[^A-Za-zА-Яа-яЁё0-9]/;

const fieldMap = {
    child_first_name: { input: 'childFirstName', error: 'childFirstNameError' },
    child_last_name: { input: 'childLastName', error: 'childLastNameError' },
    email: { input: 'email', error: 'emailError' },
    password: { input: 'password', error: 'passwordError' },
    password_repeat: { input: 'passwordRepeat', error: 'passwordRepeatError' },
};

function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';

    if (button) {
        button.textContent = visible ? '🙈' : '👁';
        button.setAttribute('aria-label', visible ? 'Скрыть пароль' : 'Показать пароль');
    }
}

function setFieldError(fieldName, message) {
    const field = fieldMap[fieldName];
    if (!field) return;

    const input = document.getElementById(field.input);
    const error = document.getElementById(field.error);
    const wrapper = input ? input.closest('.auth-password-wrapper') : null;

    if (input) input.classList.toggle('invalid', Boolean(message));
    if (wrapper) wrapper.classList.toggle('invalid', Boolean(message));
    if (error) error.textContent = message || '';
}

function clearErrors() {
    Object.keys(fieldMap).forEach(fieldName => setFieldError(fieldName, ''));
    const formMessage = document.getElementById('formMessage');
    formMessage.className = 'form-message';
    formMessage.textContent = '';
}

function validateName(value, title) {
    if (!value) return `${title}: обязательное поле.`;
    if (DANGEROUS_PATTERN.test(value)) return `${title}: запрещены спецсимволы и HTML/SQL-конструкции.`;
    if (!NAME_PATTERN.test(value)) return `${title}: только кириллица или латиница, от 1 до 60 символов.`;
    return '';
}

function validateEmail(value) {
    if (!value) return 'Почта: обязательное поле.';
    if (value.length > 100) return 'Почта: максимум 100 символов.';
    if (DANGEROUS_PATTERN.test(value)) return 'Почта: запрещены HTML/SQL-конструкции и опасные спецсимволы.';
    if (!EMAIL_PATTERN.test(value)) return 'Почта: формат text@example.ru, только латиница.';
    return '';
}

function validatePassword(value) {
    if (!value) return 'Пароль: обязательное поле.';
    if (value.length < 8 || value.length > 20) return 'Пароль: от 8 до 20 символов.';
    if (DANGEROUS_PATTERN.test(value)) return 'Пароль: запрещены опасные SQL/HTML-символы.';
    if (!PASSWORD_HAS_UPPER.test(value)) return 'Пароль: нужна минимум 1 заглавная буква.';
    if (!PASSWORD_HAS_LOWER.test(value)) return 'Пароль: нужна минимум 1 строчная буква.';
    if (!PASSWORD_HAS_DIGIT.test(value)) return 'Пароль: нужна минимум 1 цифра.';
    if (!PASSWORD_HAS_SPECIAL.test(value)) return 'Пароль: нужен минимум 1 спецсимвол.';
    return '';
}

function getPayload() {
    return {
        child_first_name: document.getElementById('childFirstName').value.trim(),
        child_last_name: document.getElementById('childLastName').value.trim(),
        email: document.getElementById('email').value.trim().toLowerCase(),
        password: document.getElementById('password').value,
        password_repeat: document.getElementById('passwordRepeat').value,
    };
}

function validateForm(payload) {
    const errors = {
        child_first_name: validateName(payload.child_first_name, 'Имя ребёнка'),
        child_last_name: validateName(payload.child_last_name, 'Фамилия ребёнка'),
        email: validateEmail(payload.email),
        password: validatePassword(payload.password),
        password_repeat: validatePassword(payload.password_repeat),
    };

    if (!errors.password_repeat && payload.password !== payload.password_repeat) {
        errors.password_repeat = 'Повторите пароль: пароль должен полностью совпадать.';
    }

    Object.entries(errors).forEach(([fieldName, message]) => setFieldError(fieldName, message));
    return Object.values(errors).every(message => !message);
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registrationForm');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        clearErrors();

        const payload = getPayload();
        const formMessage = document.getElementById('formMessage');

        if (!validateForm(payload)) {
            formMessage.className = 'form-message error';
            formMessage.textContent = 'Исправьте ошибки в полях регистрации.';
            return;
        }

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                if (data.errors) {
                    Object.entries(data.errors).forEach(([fieldName, message]) => setFieldError(fieldName, message));
                }
                formMessage.className = 'form-message error';
                formMessage.textContent = data.message || 'Регистрация не выполнена. Проверьте поля.';
                return;
            }

            form.reset();
            formMessage.className = 'form-message success';
            formMessage.textContent = data.message || 'Регистрация успешно завершена. Теперь можно войти в приложение.';
        } catch (error) {
            formMessage.className = 'form-message error';
            formMessage.textContent = `Ошибка отправки формы: ${error}`;
        }
    });
});
