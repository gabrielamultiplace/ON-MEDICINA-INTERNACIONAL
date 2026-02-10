
try {
    
        // Constante de BASE_URL padronizada
        const BASE_URL = 'http://localhost:5000';
        
        // Navegação entre páginas
        document.addEventListener('DOMContentLoaded', function() {
            const navItems = document.querySelectorAll('.nav-item');
            const pages = document.querySelectorAll('.page-content');
            const loginOverlay = document.getElementById('login-overlay');
            const appContainer = document.getElementById('app');
            const loginForm = document.getElementById('login-form');
            const loginFeedback = document.getElementById('login-feedback');
            const userNameElement = document.querySelector('.user-name');
            const settingsModal = document.getElementById('settings-modal');
            const settingsOpenButton = document.getElementById('btn-open-settings');
            const settingsCloseButton = document.getElementById('settings-close');
            const settingsTabs = document.querySelectorAll('.settings-tab');
            const settingsPanels = document.querySelectorAll('.settings-panel');
            const usersTableBody = document.querySelector('#users-table tbody');
            const usersForm = document.getElementById('users-form');
            const usersFeedback = document.getElementById('users-feedback');
            const resetForm = document.getElementById('reset-form');
            const resetFeedback = document.getElementById('reset-feedback');
            const logoutButton = document.getElementById('btn-logout');

            async function apiRequest(path, options = {}) {
                const response = await fetch(path, {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    ...options
                });
                return response;
            }

            function validatePasswordStrength(password) {
                const hasMinLength = password.length >= 8;
                const hasUpper = /[A-Z]/.test(password);
                const hasLower = /[a-z]/.test(password);
                const hasNumber = /\d/.test(password);
                return hasMinLength && hasUpper && hasLower && hasNumber;
            }

            function activateSettingsTab(tabId) {
                settingsTabs.forEach(tab => {
                    tab.classList.toggle('active', tab.dataset.tab === tabId);
                });

                settingsPanels.forEach(panel => {
                    panel.classList.toggle('active', panel.dataset.panel === tabId);
                });

                if (tabId === 'users') {
                    loadUsers();
                }
            }

            function showApp(user) {
                if (userNameElement && user && user.name) {
                    userNameElement.textContent = user.name;
                }
                loginOverlay.style.display = 'none';
                appContainer.classList.remove('app-hidden');
            }

            function showLogin(message) {
                appContainer.classList.add('app-hidden');
                loginOverlay.style.display = 'flex';
                loginFeedback.textContent = message || '';
            }

            async function checkSession() {
                try {
                    const response = await apiRequest('/api/me');
                    if (response.ok) {
                        const data = await response.json();
                        showApp(data.user);
                        return;
                    }
                } catch (error) {
                    // ignore
                }
                showLogin('Faça login para continuar.');
            }

            async function loadUsers() {
                if (!usersTableBody) {
                    return;
                }

                usersTableBody.innerHTML = '';
                usersFeedback.textContent = '';

                try {
                    const response = await apiRequest('/api/users');
                    if (!response.ok) {
                        usersFeedback.textContent = 'Não foi possível carregar usuários.';
                        return;
                    }
                    const data = await response.json();
                    data.users.forEach(user => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${user.name}</td>
                            <td>${user.email}</td>
                            <td>${user.role}</td>
                        `;
                        usersTableBody.appendChild(row);
                    });
                } catch (error) {
                    usersFeedback.textContent = 'Servidor indisponível.';
                }
            }
            
            navItems.forEach(item => {
                item.addEventListener('click', function(e) {
   
    console.log("✅ JavaScript syntax is valid!");
    process.exit(0);
} catch(err) {
    console.error("❌ JavaScript Syntax Error:");
    console.error(err.message);
    process.exit(1);
}
