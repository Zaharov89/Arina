(function () {
    const AUTH_PAGES = [
        '/auth/login',
        '/auth/register',
        '/auth/forgot-password',
    ];

    function isAuthPage() {
        return AUTH_PAGES.some(path => window.location.pathname.startsWith(path))
            || window.location.pathname.startsWith('/auth/reset-password')
            || window.location.pathname.startsWith('/auth/activate');
    }

    function getAuthStorage() {
        if (localStorage.getItem('arinaAccessToken') || localStorage.getItem('arinaRefreshToken')) {
            return localStorage;
        }
        if (sessionStorage.getItem('arinaAccessToken') || sessionStorage.getItem('arinaRefreshToken')) {
            return sessionStorage;
        }
        return null;
    }

    function clearAuthData() {
        const keys = ['arinaAccessToken', 'arinaRefreshToken', 'arinaUserId', 'arinaUserEmail', 'arinaRememberMe'];
        keys.forEach(key => {
            localStorage.removeItem(key);
            sessionStorage.removeItem(key);
        });
    }

    function redirectToLogin() {
        if (isAuthPage()) return;
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/auth/login?next=${next}`;
    }

    async function requestJson(url, options) {
        const response = await fetch(url, options);
        const data = await response.json().catch(() => ({}));
        return { response, data };
    }

    async function verifyAccessToken(accessToken) {
        return requestJson('/auth/me', {
            method: 'GET',
            headers: { Authorization: `Bearer ${accessToken}` },
        });
    }

    async function refreshAccessToken(storage) {
        const refreshToken = storage.getItem('arinaRefreshToken');
        if (!refreshToken) return false;

        const rememberMe = storage.getItem('arinaRememberMe') === 'true';
        const { response, data } = await requestJson('/auth/refresh_token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken, remember_me: rememberMe }),
        });

        if (!response.ok || !data.data) return false;

        storage.setItem('arinaAccessToken', data.data.access_token);
        storage.setItem('arinaRefreshToken', data.data.refresh_token);
        storage.setItem('arinaRememberMe', String(rememberMe));
        return true;
    }

    function injectAuthPanel(user) {
        if (document.getElementById('arinaAuthPanel')) return;

        const panel = document.createElement('div');
        panel.id = 'arinaAuthPanel';
        panel.innerHTML = `
            <span class="arina-auth-email">${user.email || ''}</span>
            <button type="button" id="arinaLogoutBtn">Выйти</button>
        `;
        document.body.appendChild(panel);

        document.getElementById('arinaLogoutBtn').addEventListener('click', function () {
            clearAuthData();
            window.location.href = '/auth/login';
        });
    }

    function injectAuthStyles() {
        if (document.getElementById('arinaAuthStyles')) return;

        const style = document.createElement('style');
        style.id = 'arinaAuthStyles';
        style.textContent = `
            #arinaAuthPanel {
                position: fixed;
                top: 12px;
                right: 12px;
                z-index: 9999;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 10px;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.96);
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.14);
                font-family: Arial, sans-serif;
            }
            #arinaAuthPanel .arina-auth-email {
                color: #27407a;
                font-weight: 700;
                font-size: 14px;
                max-width: 240px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            #arinaLogoutBtn {
                border: none;
                border-radius: 8px;
                background: #dc3545;
                color: #fff;
                padding: 7px 10px;
                cursor: pointer;
                font-weight: 700;
            }
            #arinaLogoutBtn:hover {
                background: #c82333;
            }
        `;
        document.head.appendChild(style);
    }

    async function ensureAuthenticated() {
        if (isAuthPage()) return;

        const storage = getAuthStorage();
        if (!storage) {
            redirectToLogin();
            return;
        }

        const accessToken = storage.getItem('arinaAccessToken');
        if (!accessToken) {
            const refreshed = await refreshAccessToken(storage);
            if (!refreshed) {
                clearAuthData();
                redirectToLogin();
            }
            return;
        }

        let { response, data } = await verifyAccessToken(accessToken);

        if (!response.ok) {
            const refreshed = await refreshAccessToken(storage);
            if (!refreshed) {
                clearAuthData();
                redirectToLogin();
                return;
            }

            const newAccessToken = storage.getItem('arinaAccessToken');
            const verified = await verifyAccessToken(newAccessToken);
            response = verified.response;
            data = verified.data;
        }

        if (!response.ok || !data.data) {
            clearAuthData();
            redirectToLogin();
            return;
        }

        storage.setItem('arinaUserId', data.data.user_id);
        storage.setItem('arinaUserEmail', data.data.email);
        injectAuthStyles();
        injectAuthPanel(data.data);
    }

    window.ArinaAuth = {
        clear: clearAuthData,
        getStorage: getAuthStorage,
        ensureAuthenticated,
    };

    document.addEventListener('DOMContentLoaded', ensureAuthenticated);
})();
