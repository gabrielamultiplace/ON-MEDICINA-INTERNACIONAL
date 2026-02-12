
        // Constante de BASE_URL padronizada - usa URL atual automaticamente
        const BASE_URL = window.location.origin;
        
        // Navegação global (inline onclick fallback)
        function navigateTo(pageId) {
            try {
                // Remove active from all nav items 
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                // Add active to clicked
                const clickedNav = document.querySelector('.nav-item[data-page="' + pageId + '"]');
                if (clickedNav) clickedNav.classList.add('active');
                // Switch pages
                document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
                const target = document.getElementById(pageId);
                if (target) target.classList.add('active');
                // Load data for specific pages
                if (pageId === 'gestao-pacientes' && typeof carregarListaPacientes === 'function') {
                    carregarListaPacientes();
                }
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } catch(err) {
                console.error('Navigation error:', err);
            }
        }

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
                        'Content-Type': 'application/json',
                        'ngrok-skip-browser-warning': 'true'
                    },
                    ...options
                });
                if (!response.ok) {
                    const errData = await response.json().catch(() => ({ message: 'Erro na requisição' }));
                    const err = new Error(errData.message || 'Erro ' + response.status);
                    err.status = response.status;
                    err.data = errData;
                    throw err;
                }
                const text = await response.text();
                return text ? JSON.parse(text) : {};
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
                if (tabId === 'assinatura') {
                    carregarConfigAssinatura();
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
                    const data = await apiRequest('/api/me');
                    showApp(data.user);

                    // Verificar callbacks de assinatura digital
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('signature_callback') === 'true') {
                        const sessionId = urlParams.get('session_id');
                        const status = urlParams.get('status');
                        if (status === 'authenticated' && sessionId) {
                            // Backend faz tudo server-side: GET /credentials + POST /signatures
                            try {
                                const execRes = await apiRequest('/api/assinatura/executar', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ session_id: sessionId })
                                });
                                if (execRes.status === 'signed') {
                                    alert('✅ Documento assinado digitalmente com certificado ICP-Brasil!\n\n' +
                                          'Titular: ' + (execRes.certificate_subject || 'Certificado confirmado') + '\n' +
                                          'Emissor: ' + (execRes.certificate_issuer || ''));
                                } else {
                                    alert('⚠️ Assinatura pendente: ' + (execRes.message || execRes.error || 'Erro desconhecido'));
                                }
                            } catch(sigErr) {
                                console.warn('Erro ao finalizar assinatura:', sigErr);
                                alert('⚠️ Erro ao finalizar assinatura. Tente novamente.');
                            }
                        }
                        // Limpar query string
                        window.history.replaceState({}, '', window.location.pathname);
                    }
                    if (urlParams.get('cert_callback') === 'true') {
                        alert('✅ Certificado digital vinculado com sucesso!');
                        window.history.replaceState({}, '', window.location.pathname);
                    }
                    return;
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
                    const data = await apiRequest('/api/users');
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
                    e.preventDefault();
                    try {
                        navItems.forEach(nav => nav.classList.remove('active'));
                        this.classList.add('active');
                        
                        const pageId = this.getAttribute('data-page');
                        console.log('Nav click:', pageId);
                        
                        pages.forEach(page => page.classList.remove('active'));
                        const targetPage = document.getElementById(pageId);
                        if (targetPage) {
                            targetPage.classList.add('active');
                        } else {
                            console.error('Page not found:', pageId);
                        }
                        
                        // Load data when navigating to specific pages
                        if (pageId === 'gestao-pacientes') {
                            carregarListaPacientes();
                        }
                        
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    } catch(err) {
                        console.error('Nav error:', err);
                    }
                });
            });

            if (loginForm) {
                loginForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    loginFeedback.textContent = '';

                    const email = document.getElementById('login-email').value.trim();
                    const password = document.getElementById('login-password').value;

                    try {
                        const data = await apiRequest('/api/login', {
                            method: 'POST',
                            body: JSON.stringify({ email, password })
                        });
                        showApp(data.user);
                    } catch (error) {
                        loginFeedback.textContent = (error.data && error.data.message) || 'Credenciais inválidas.';
                    }
                });
            }

            if (settingsOpenButton) {
                settingsOpenButton.addEventListener('click', function() {
                    settingsModal.classList.add('active');
                    activateSettingsTab('users');
                    // Populate config links
                    const linkCadastro = document.getElementById('link-cadastro-medico');
                    if (linkCadastro) linkCadastro.value = BASE_URL + '/?registerMedico=true';
                    const linkPaciente = document.getElementById('link-cadastro-paciente');
                    if (linkPaciente) linkPaciente.value = BASE_URL + '/?registerPaciente=true';
                    // Load webhook config
                    carregarWebhookConfig();
                });
            }

            if (settingsCloseButton) {
                settingsCloseButton.addEventListener('click', function() {
                    settingsModal.classList.remove('active');
                });
            }

            if (settingsModal) {
                settingsModal.addEventListener('click', function(e) {
                    if (e.target === settingsModal) {
                        settingsModal.classList.remove('active');
                    }
                });
            }

            if (settingsTabs.length) {
                settingsTabs.forEach(tab => {
                    tab.addEventListener('click', function() {
                        activateSettingsTab(this.dataset.tab);
                    });
                });
            }

            if (usersForm) {
                usersForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    usersFeedback.textContent = '';

                    const name = document.getElementById('user-name').value.trim();
                    const email = document.getElementById('user-email').value.trim();
                    const password = document.getElementById('user-password').value;
                    const confirmPassword = document.getElementById('user-password-confirm').value;
                    const role = document.getElementById('user-role').value;

                    if (password !== confirmPassword) {
                        usersFeedback.textContent = 'As senhas não conferem.';
                        return;
                    }

                    if (!validatePasswordStrength(password)) {
                        usersFeedback.textContent = 'A senha deve ter 8+ caracteres, com maiúscula, minúscula e número.';
                        return;
                    }

                    try {
                        await apiRequest('/api/users', {
                            method: 'POST',
                            body: JSON.stringify({ name, email, password, role })
                        });
                        usersForm.reset();
                        loadUsers();
                    } catch (error) {
                        usersFeedback.textContent = (error.data && error.data.message) || 'Erro ao criar usuário.';
                    }
                });
            }

            if (resetForm) {
                resetForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    resetFeedback.textContent = '';

                    const email = document.getElementById('reset-email').value.trim();
                    const newPassword = document.getElementById('reset-password').value;
                    const confirmPassword = document.getElementById('reset-password-confirm').value;

                    if (newPassword !== confirmPassword) {
                        resetFeedback.textContent = 'As senhas não conferem.';
                        return;
                    }

                    if (!validatePasswordStrength(newPassword)) {
                        resetFeedback.textContent = 'A senha deve ter 8+ caracteres, com maiúscula, minúscula e número.';
                        return;
                    }

                    try {
                        await apiRequest('/api/users/reset-password', {
                            method: 'POST',
                            body: JSON.stringify({ email, new_password: newPassword })
                        });
                        resetForm.reset();
                        resetFeedback.textContent = 'Senha atualizada com sucesso.';
                    } catch (error) {
                        resetFeedback.textContent = (error.data && error.data.message) || 'Erro ao resetar senha.';
                    }
                });
            }

            if (logoutButton) {
                logoutButton.addEventListener('click', async function() {
                    try {
                        await apiRequest('/api/logout', { method: 'POST' });
                    } catch (error) {
                        // ignore
                    }
                    showLogin('Sessão encerrada.');
                });
            }

            // ========== ADMIN KANBAN DRAG AND DROP ==========
            let draggedAdminCard = null;

            function initAdminKanban() {
                const adminBoard = document.querySelector('.admin-kanban-board');
                if (!adminBoard) return;

                const adminCards = adminBoard.querySelectorAll('.admin-card[draggable="true"]');
                
                adminCards.forEach(card => {
                    card.addEventListener('dragstart', handleAdminDragStart);
                    card.addEventListener('dragend', handleAdminDragEnd);
                    card.addEventListener('dragover', handleAdminDragOver);
                    card.addEventListener('drop', handleAdminDrop);

                    // Botão de editar
                    const editBtn = card.querySelector('.btn-card-action.edit');
                    if (editBtn) {
                        editBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            openEditModuleModal(card);
                        });
                    }

                    // Botão de excluir
                    const deleteBtn = card.querySelector('.btn-card-action.delete');
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            deleteAdminModule(card);
                        });
                    }
                });

                // Botão adicionar módulo
                const addModuleBtn = document.getElementById('btn-add-admin-module');
                if (addModuleBtn) {
                    addModuleBtn.addEventListener('click', openAddModuleModal);
                }
            }

            function handleAdminDragStart(e) {
                draggedAdminCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            }

            function handleAdminDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('.admin-card').forEach(card => {
                    card.classList.remove('drag-over');
                });
                saveAdminModulesOrder();
            }

            function handleAdminDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';

                const afterElement = getDragAfterElement(e.clientY);
                const draggable = document.querySelector('.dragging');
                const adminBoard = document.querySelector('.admin-kanban-board');
                
                if (afterElement == null) {
                    const addBtn = document.getElementById('btn-add-admin-module');
                    adminBoard.insertBefore(draggable, addBtn);
                } else {
                    adminBoard.insertBefore(draggable, afterElement);
                }

                return false;
            }

            function handleAdminDrop(e) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                return false;
            }

            function getDragAfterElement(y) {
                const adminBoard = document.querySelector('.admin-kanban-board');
                const draggableElements = [...adminBoard.querySelectorAll('.admin-card:not(.dragging)')];

                return draggableElements.reduce((closest, child) => {
                    const box = child.getBoundingClientRect();
                    const offset = y - box.top - box.height / 2;
                    
                    if (offset < 0 && offset > closest.offset) {
                        return { offset: offset, element: child };
                    } else {
                        return closest;
                    }
                }, { offset: Number.NEGATIVE_INFINITY }).element;
            }

            function saveAdminModulesOrder() {
                const adminBoard = document.querySelector('.admin-kanban-board');
                const cards = adminBoard.querySelectorAll('.admin-card');
                const order = Array.from(cards).map(card => card.dataset.module);
                localStorage.setItem('adminModulesOrder', JSON.stringify(order));
            }

            function loadAdminModulesOrder() {
                const savedOrder = localStorage.getItem('adminModulesOrder');
                if (!savedOrder) return;

                const order = JSON.parse(savedOrder);
                const adminBoard = document.querySelector('.admin-kanban-board');
                const addBtn = document.getElementById('btn-add-admin-module');
                
                order.forEach(moduleId => {
                    const card = adminBoard.querySelector(`.admin-card[data-module="${moduleId}"]`);
                    if (card) {
                        adminBoard.insertBefore(card, addBtn);
                    }
                });
            }

            function openEditModuleModal(card) {
                const module = card.dataset.module;
                const title = card.querySelector('.admin-card-header h3').textContent;
                const icon = card.querySelector('.admin-card-header i').className;
                const items = Array.from(card.querySelectorAll('.admin-list li')).map(li => {
                    return li.textContent.trim();
                });
                const buttonText = card.querySelector('.btn-admin').textContent;

                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 600px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-edit"></i> Editar Módulo</h2>
                            <button class="btn-close-modal" id="btn-close-edit-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="edit-module-title">Título do Módulo</label>
                                <input type="text" id="edit-module-title" value="${title}" required>
                            </div>
                            <div class="form-group">
                                <label for="edit-module-icon">Ícone (classe Font Awesome)</label>
                                <input type="text" id="edit-module-icon" value="${icon}" required>
                                <small>Ex: fas fa-user-md</small>
                            </div>
                            <div class="form-group">
                                <label>Itens da Lista</label>
                                <div id="edit-items-container">
                                    ${items.map((item, idx) => `
                                        <div class="edit-item-row" style="display: flex; gap: 8px; margin-bottom: 8px;">
                                            <input type="text" class="edit-item-input" value="${item}" style="flex: 1;">
                                            <button class="btn-remove-item" style="background: #D81B60; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;"><i class="fas fa-trash"></i></button>
                                        </div>
                                    `).join('')}
                                </div>
                                <button id="btn-add-edit-item" style="margin-top: 8px; background: #00897B; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;"><i class="fas fa-plus"></i> Adicionar Item</button>
                            </div>
                            <div class="form-group">
                                <label for="edit-module-button">Texto do Botão</label>
                                <input type="text" id="edit-module-button" value="${buttonText}" required>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-edit">Cancelar</button>
                            <button class="btn-primary" id="btn-save-edit">Salvar</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                // Event listeners
                modal.querySelector('#btn-close-edit-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('#btn-cancel-edit').addEventListener('click', () => modal.remove());
                
                modal.querySelector('#btn-add-edit-item').addEventListener('click', () => {
                    const container = modal.querySelector('#edit-items-container');
                    const newRow = document.createElement('div');
                    newRow.className = 'edit-item-row';
                    newRow.style.cssText = 'display: flex; gap: 8px; margin-bottom: 8px;';
                    newRow.innerHTML = `
                        <input type="text" class="edit-item-input" placeholder="Novo item" style="flex: 1;">
                        <button class="btn-remove-item" style="background: #D81B60; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;"><i class="fas fa-trash"></i></button>
                    `;
                    container.appendChild(newRow);
                    attachRemoveItemListener(newRow.querySelector('.btn-remove-item'));
                });

                modal.querySelectorAll('.btn-remove-item').forEach(btn => {
                    attachRemoveItemListener(btn);
                });

                function attachRemoveItemListener(btn) {
                    btn.addEventListener('click', () => btn.parentElement.remove());
                }

                modal.querySelector('#btn-save-edit').addEventListener('click', () => {
                    const newTitle = modal.querySelector('#edit-module-title').value.trim();
                    const newIcon = modal.querySelector('#edit-module-icon').value.trim();
                    const newItems = Array.from(modal.querySelectorAll('.edit-item-input'))
                        .map(input => input.value.trim())
                        .filter(text => text.length > 0);
                    const newButtonText = modal.querySelector('#edit-module-button').value.trim();

                    if (!newTitle || !newIcon || newItems.length === 0 || !newButtonText) {
                        alert('Preencha todos os campos obrigatórios.');
                        return;
                    }

                    // Atualizar card
                    card.querySelector('.admin-card-header h3').textContent = newTitle;
                    card.querySelector('.admin-card-header i').className = newIcon;
                    
                    const listUl = card.querySelector('.admin-list');
                    listUl.innerHTML = newItems.map(item => `
                        <li><i class="fas fa-check-circle"></i> ${item}</li>
                    `).join('');

                    card.querySelector('.btn-admin').textContent = newButtonText;

                    modal.remove();
                    saveAdminModulesData();
                });
            }

            function deleteAdminModule(card) {
                const title = card.querySelector('.admin-card-header h3').textContent;
                if (!confirm(`Deseja realmente excluir o módulo "${title}"?`)) {
                    return;
                }
                card.remove();
                saveAdminModulesOrder();
                saveAdminModulesData();
            }

            function openAddModuleModal() {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 600px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Novo Módulo</h2>
                            <button class="btn-close-modal" id="btn-close-add-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="add-module-title">Título do Módulo</label>
                                <input type="text" id="add-module-title" placeholder="Ex: Gestão de Contratos" required>
                            </div>
                            <div class="form-group">
                                <label for="add-module-icon">Ícone (classe Font Awesome)</label>
                                <input type="text" id="add-module-icon" placeholder="Ex: fas fa-file-contract" required>
                                <small>Acesse <a href="https://fontawesome.com/icons" target="_blank">fontawesome.com</a> para ver todos os ícones</small>
                            </div>
                            <div class="form-group">
                                <label>Itens da Lista</label>
                                <div id="add-items-container">
                                    <div class="add-item-row" style="display: flex; gap: 8px; margin-bottom: 8px;">
                                        <input type="text" class="add-item-input" placeholder="Item 1" style="flex: 1;">
                                        <button class="btn-remove-item" style="background: #D81B60; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;"><i class="fas fa-trash"></i></button>
                                    </div>
                                </div>
                                <button id="btn-add-new-item" style="margin-top: 8px; background: #00897B; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;"><i class="fas fa-plus"></i> Adicionar Item</button>
                            </div>
                            <div class="form-group">
                                <label for="add-module-button">Texto do Botão</label>
                                <input type="text" id="add-module-button" placeholder="Ex: Acessar Módulo" required>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-add">Cancelar</button>
                            <button class="btn-primary" id="btn-save-add">Adicionar</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                // Event listeners
                modal.querySelector('#btn-close-add-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('#btn-cancel-add').addEventListener('click', () => modal.remove());
                
                modal.querySelector('#btn-add-new-item').addEventListener('click', () => {
                    const container = modal.querySelector('#add-items-container');
                    const newRow = document.createElement('div');
                    newRow.className = 'add-item-row';
                    newRow.style.cssText = 'display: flex; gap: 8px; margin-bottom: 8px;';
                    newRow.innerHTML = `
                        <input type="text" class="add-item-input" placeholder="Novo item" style="flex: 1;">
                        <button class="btn-remove-item" style="background: #D81B60; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;"><i class="fas fa-trash"></i></button>
                    `;
                    container.appendChild(newRow);
                    attachRemoveItemListener(newRow.querySelector('.btn-remove-item'));
                });

                modal.querySelectorAll('.btn-remove-item').forEach(btn => {
                    attachRemoveItemListener(btn);
                });

                function attachRemoveItemListener(btn) {
                    btn.addEventListener('click', () => btn.parentElement.remove());
                }

                modal.querySelector('#btn-save-add').addEventListener('click', () => {
                    const title = modal.querySelector('#add-module-title').value.trim();
                    const icon = modal.querySelector('#add-module-icon').value.trim();
                    const items = Array.from(modal.querySelectorAll('.add-item-input'))
                        .map(input => input.value.trim())
                        .filter(text => text.length > 0);
                    const buttonText = modal.querySelector('#add-module-button').value.trim();

                    if (!title || !icon || items.length === 0 || !buttonText) {
                        alert('Preencha todos os campos obrigatórios.');
                        return;
                    }

                    // Criar ID único
                    const moduleId = title.toLowerCase()
                        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                        .replace(/[^a-z0-9]/g, '-')
                        .replace(/-+/g, '-')
                        .replace(/^-|-$/g, '');

                    // Criar novo card
                    const newCard = document.createElement('div');
                    newCard.className = 'admin-card';
                    newCard.draggable = true;
                    newCard.dataset.module = moduleId;
                    newCard.innerHTML = `
                        <div class="admin-card-actions">
                            <button class="btn-card-action edit" title="Editar"><i class="fas fa-edit"></i></button>
                            <button class="btn-card-action delete" title="Excluir"><i class="fas fa-trash"></i></button>
                        </div>
                        <div class="admin-card-header">
                            <i class="${icon}"></i>
                            <h3>${title}</h3>
                        </div>
                        <div class="admin-card-body">
                            <ul class="admin-list">
                                ${items.map(item => `<li><i class="fas fa-check-circle"></i> ${item}</li>`).join('')}
                            </ul>
                            <button class="btn-admin">${buttonText}</button>
                        </div>
                    `;

                    // Inserir antes do botão "Adicionar Módulo"
                    const adminBoard = document.querySelector('.admin-kanban-board');
                    const addBtn = document.getElementById('btn-add-admin-module');
                    adminBoard.insertBefore(newCard, addBtn);

                    // Adicionar event listeners
                    newCard.addEventListener('dragstart', handleAdminDragStart);
                    newCard.addEventListener('dragend', handleAdminDragEnd);
                    newCard.addEventListener('dragover', handleAdminDragOver);
                    newCard.addEventListener('drop', handleAdminDrop);

                    newCard.querySelector('.btn-card-action.edit').addEventListener('click', (e) => {
                        e.stopPropagation();
                        openEditModuleModal(newCard);
                    });

                    newCard.querySelector('.btn-card-action.delete').addEventListener('click', (e) => {
                        e.stopPropagation();
                        deleteAdminModule(newCard);
                    });

                    modal.remove();
                    saveAdminModulesOrder();
                    saveAdminModulesData();
                });
            }

            function saveAdminModulesData() {
                const adminBoard = document.querySelector('.admin-kanban-board');
                const cards = adminBoard.querySelectorAll('.admin-card');
                const modulesData = Array.from(cards).map(card => ({
                    id: card.dataset.module,
                    title: card.querySelector('.admin-card-header h3').textContent,
                    icon: card.querySelector('.admin-card-header i').className,
                    items: Array.from(card.querySelectorAll('.admin-list li')).map(li => li.textContent.trim()),
                    buttonText: card.querySelector('.btn-admin').textContent
                }));
                localStorage.setItem('adminModulesData', JSON.stringify(modulesData));
            }

            // ========== KANBAN COMERCIAL ==========
            // ========== KANBAN COMERCIAL ==========
            let draggedComercialCard = null;

            function initComercialKanban() {
                const kanbanBoard = document.getElementById('kanban-comercial');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handleComercialDragStart);
                    card.addEventListener('dragend', handleComercialDragEnd);
                    card.addEventListener('click', function(e) {
                        if (!e.target.closest('.btn-card-delete')) {
                            const leadId = this.dataset.leadId;
                            if (leadId) {
                                fetch(`/api/leads/${leadId}`).then(r => r.json()).then(lead => {
                                    openLeadDetailsModal(lead);
                                }).catch(e => console.error(e));
                            }
                        }
                    });
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handleComercialDragOver);
                    cardsContainer.addEventListener('drop', (e) => handleComercialDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handleComercialDragLeave);

                    // Botão adicionar card
                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadComercialKanbanData();
                updateColumnCounts();

                // Botão voltar
                const btnBack = document.getElementById('btn-back-comercial');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('comercial').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }

                setupColumnReordering('kanban-comercial', 'comercial');
            }

            // ========== KANBAN PAINEL (principal) ==========
            let draggedPainelCard = null;

            function initPainelKanban() {
                const painelSection = document.getElementById('painel');
                if (!painelSection) return;

                const kanbanBoard = painelSection.querySelector('.kanban-board');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handlePainelDragStart);
                    card.addEventListener('dragend', handlePainelDragEnd);
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handlePainelDragOver);
                    cardsContainer.addEventListener('drop', (e) => handlePainelDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handlePainelDragLeave);

                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddPainelCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadPainelKanbanData();
                updateColumnCounts();
                setupColumnReordering('kanban-painel', 'painel');
            }

            function handlePainelDragStart(e) {
                draggedPainelCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handlePainelDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#painel .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                savePainelKanbanData();
            }

            function handlePainelDragOver(e) {
                if (e.preventDefault) e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handlePainelDragLeave(e) {
                if (e.target === this) this.classList.remove('drag-over');
            }

            function handlePainelDrop(e, container) {
                if (e.stopPropagation) e.stopPropagation();
                container.classList.remove('drag-over');

                if (draggedPainelCard && draggedPainelCard.parentNode !== container) {
                    container.appendChild(draggedPainelCard);
                    updateColumnCounts();
                    savePainelKanbanData();
                }
                return false;
            }

            function openAddPainelCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title-painel">Título do Card</label>
                                <input type="text" id="card-title-painel" placeholder="Ex: Tarefa X" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description-painel">Descrição</label>
                                <textarea id="card-description-painel" placeholder="Detalhes" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority-painel">Prioridade</label>
                                <select id="card-priority-painel">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="card-responsible-painel">Responsável</label>
                                <input type="text" id="card-responsible-painel" placeholder="Nome do responsável">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card-painel">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card-painel">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card-painel');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card-painel');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title-painel').value.trim();
                    const description = modal.querySelector('#card-description-painel').value.trim();
                    const priority = modal.querySelector('#card-priority-painel').value;
                    const responsible = modal.querySelector('#card-responsible-painel').value.trim();

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ${responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${responsible}</div></div>` : ''}
                    `;

                    newCard.addEventListener('dragstart', handlePainelDragStart);
                    newCard.addEventListener('dragend', handlePainelDragEnd);

                    newCard.querySelector('.btn-card-delete').addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            savePainelKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    savePainelKanbanData();
                    modal.remove();
                });
            }

            function savePainelKanbanData() {
                const painelSection = document.getElementById('painel');
                if (!painelSection) return;
                const kanbanBoard = painelSection.querySelector('.kanban-board');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium',
                        responsible: card.querySelector('.card-meta-item')?.textContent.replace(/\s+/g, ' ').trim().substring(1) || ''
                    }));
                });

                localStorage.setItem('painelKanbanData', JSON.stringify(data));
            }

            function loadPainelKanbanData() {
                // Carregar dados salvos do Painel do localStorage
                const data = localStorage.getItem('painelKanbanData');
                if (!data) {
                    // Se não houver dados salvos, sincronizar com Comercial
                    syncPainelWithComercial();
                    return;
                }

                const kanbanData = JSON.parse(data);
                const painelSection = document.getElementById('painel');
                if (!painelSection) return;
                const kanbanBoard = painelSection.querySelector('.kanban-board');

                Object.keys(kanbanData).forEach(columnTitle => {
                    const column = kanbanBoard.querySelector(`[data-column-title="${columnTitle}"]`);
                    if (!column) return;

                    const container = column.querySelector('.kanban-cards');
                    kanbanData[columnTitle].forEach(cardData => {
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                </div>
                                <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ${cardData.responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${cardData.responsible}</div></div>` : ''}
                        `;

                        card.addEventListener('dragstart', handlePainelDragStart);
                        card.addEventListener('dragend', handlePainelDragEnd);

                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm('Excluir este card?')) {
                                card.remove();
                                updateColumnCounts();
                                savePainelKanbanData();
                            }
                        });

                        container.appendChild(card);
                    });
                });
            }

            function handleComercialDragStart(e) {
                draggedComercialCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handleComercialDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#kanban-comercial .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                saveComercialKanbanData();
            }

            function handleComercialDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handleComercialDragLeave(e) {
                if (e.target === this) {
                    this.classList.remove('drag-over');
                }
            }

            function handleComercialDrop(e, container) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                container.classList.remove('drag-over');
                
                if (draggedComercialCard && draggedComercialCard.parentNode !== container) {
                    container.appendChild(draggedComercialCard);
                    updateColumnCounts();
                    saveComercialKanbanData();
                }
                return false;
            }

            function openAddCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title">Título do Card</label>
                                <input type="text" id="card-title" placeholder="Ex: Proposta X" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description">Descrição</label>
                                <textarea id="card-description" placeholder="Detalhes do lead/oportunidade" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority">Prioridade</label>
                                <select id="card-priority">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="card-responsible">Responsável</label>
                                <input type="text" id="card-responsible" placeholder="Nome do responsável">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title').value.trim();
                    const description = modal.querySelector('#card-description').value.trim();
                    const priority = modal.querySelector('#card-priority').value;
                    const responsible = modal.querySelector('#card-responsible').value.trim();

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ${responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${responsible}</div></div>` : ''}
                    `;

                    newCard.addEventListener('dragstart', handleComercialDragStart);
                    newCard.addEventListener('dragend', handleComercialDragEnd);

                    const deleteBtn = newCard.querySelector('.btn-card-delete');
                    deleteBtn.addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            saveComercialKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    saveComercialKanbanData();
                    modal.remove();
                });
            }

            function saveComercialKanbanData() {
                const kanbanBoard = document.getElementById('kanban-comercial');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium',
                        responsible: card.querySelector('.card-meta-item')?.textContent.replace(/\s+/g, ' ').trim().substring(1) || '',
                        leadId: card.dataset.leadId || ''
                    }));
                });

                localStorage.setItem('comercialKanbanData', JSON.stringify(data));
                syncPainelWithComercial();
            }

            function syncPainelWithComercial() {
                const comercialData = JSON.parse(localStorage.getItem('comercialKanbanData') || '{}');
                const painelSection = document.getElementById('painel');
                if (!painelSection) return;

                const kanbanBoard = painelSection.querySelector('.kanban-board');
                if (!kanbanBoard) return;
                
                const comercialColumn = kanbanBoard.querySelector('[data-column-title="Comercial"]');
                if (!comercialColumn) return;

                const comercialCards = comercialColumn.querySelector('.kanban-cards');
                comercialCards.innerHTML = '';

                // Carregar cards de todas as colunas do Comercial
                Object.keys(comercialData).forEach(columnTitle => {
                    comercialData[columnTitle].forEach(cardData => {
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.dataset.leadId = cardData.leadId;
                        card.dataset.comercialColumn = columnTitle;

                        const getColorForColumn = (col) => {
                            const colors = {
                                'Entrada de Lead': '#FFC107',
                                'Em Análise': '#2196F3',
                                'Aprovado': '#4CAF50',
                                'Rejeitado': '#F44336'
                            };
                            return colors[col] || '#999999';
                        };

                        const tagColor = getColorForColumn(columnTitle);

                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    <div style="margin-top: 8px; display: flex; gap: 6px; align-items: center;">
                                        <span style="display: inline-block; background-color: ${tagColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">
                                            ${columnTitle}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        `;

                        card.addEventListener('click', () => {
                            // Navegar para Administrativo -> Comercial
                            document.getElementById('painel').classList.remove('active');
                            document.getElementById('administrativo').classList.add('active');
                            const comercialSubTab = document.getElementById('comercial');
                            if (comercialSubTab) comercialSubTab.classList.add('active');
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                            
                            // Highlight do card
                            setTimeout(() => {
                                const cardInComercial = Array.from(document.querySelectorAll('#kanban-comercial .kanban-card'))
                                    .find(c => c.querySelector('.card-title')?.textContent === cardData.title);
                                if (cardInComercial) {
                                    cardInComercial.style.boxShadow = '0 0 10px rgba(255, 193, 7, 0.8)';
                                    cardInComercial.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                }
                            }, 300);
                        });

                        card.addEventListener('dragstart', handlePainelDragStart);
                        card.addEventListener('dragend', handlePainelDragEnd);

                        comercialCards.appendChild(card);
                    });
                });

                updateColumnCounts();
            }

            function loadLeadsFromBackend() {
                fetch('/api/leads')
                    .then(r => r.json())
                    .then(leads => {
                        if (!Array.isArray(leads) || leads.length === 0) return;
                        
                        // Verificar cards existentes para evitar duplicatas
                        const kanbanBoard = document.getElementById('kanban-comercial');
                        if (!kanbanBoard) return;
                        const existingIds = new Set(
                            Array.from(kanbanBoard.querySelectorAll('.kanban-card[data-lead-id]'))
                                .map(c => c.dataset.leadId)
                        );
                        
                        leads.forEach(lead => {
                            if (!existingIds.has(lead.id)) {
                                createLeadCard(lead);
                            }
                        });
                    })
                    .catch(e => console.error('Error loading leads:', e));
            }

            function loadComercialKanbanData() {
                const data = localStorage.getItem('comercialKanbanData');
                if (!data) return;

                const kanbanData = JSON.parse(data);
                const kanbanBoard = document.getElementById('kanban-comercial');

                // Deduplicar cards por leadId antes de carregar
                const seenLeadIds = new Set();

                Object.keys(kanbanData).forEach(columnTitle => {
                    const column = kanbanBoard.querySelector(`[data-column-title="${columnTitle}"]`);
                    if (!column) return;

                    const container = column.querySelector('.kanban-cards');
                    kanbanData[columnTitle].forEach(cardData => {
                        // Pular duplicatas de lead
                        if (cardData.leadId) {
                            if (seenLeadIds.has(cardData.leadId)) return;
                            seenLeadIds.add(cardData.leadId);
                        }
                        
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.dataset.leadId = cardData.leadId;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                </div>
                                <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ${cardData.responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${cardData.responsible}</div></div>` : ''}
                        `;

                        card.addEventListener('dragstart', handleComercialDragStart);
                        card.addEventListener('dragend', handleComercialDragEnd);
                        card.addEventListener('click', function(e) {
                            if (!e.target.closest('.btn-card-delete')) {
                                const leadId = this.dataset.leadId;
                                if (leadId) {
                                    fetch(`/api/leads/${leadId}`).then(r => r.json()).then(lead => {
                                        openLeadDetailsModal(lead);
                                    }).catch(e => console.error(e));
                                }
                            }
                        });

                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm('Excluir este card?')) {
                                card.remove();
                                updateColumnCounts();
                                saveComercialKanbanData();
                            }
                        });

                        container.appendChild(card);
                    });
                });
            }

            // ========== KANBAN ÁREA MÉDICA ==========
            let draggedAreaMedicaCard = null;

            function initAreaMedicaKanban() {
                const kanbanBoard = document.getElementById('kanban-area-medica');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handleAreaMedicaDragStart);
                    card.addEventListener('dragend', handleAreaMedicaDragEnd);
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handleAreaMedicaDragOver);
                    cardsContainer.addEventListener('drop', (e) => handleAreaMedicaDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handleAreaMedicaDragLeave);

                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddAreaMedicaCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadAreaMedicaKanbanData();
                updateColumnCounts();

                const btnBack = document.getElementById('btn-back-area-medica');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('area-medica').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }

                // Buttons for doctors management
                const btnDoctorsList = document.getElementById('btn-doctors-list');
                const btnBackToKanban = document.getElementById('btn-back-to-kanban');
                const kanbanView = document.getElementById('area-medica-kanban-view');
                const doctorsView = document.getElementById('area-medica-doctors-view');

                if (btnDoctorsList) {
                    btnDoctorsList.addEventListener('click', () => {
                        kanbanView.style.display = 'none';
                        doctorsView.style.display = 'block';
                        loadAndDisplayDoctorsListAreaMedica();
                    });
                }

                if (btnBackToKanban) {
                    btnBackToKanban.addEventListener('click', () => {
                        kanbanView.style.display = 'block';
                        doctorsView.style.display = 'none';
                    });
                }

                setupColumnReordering('kanban-area-medica', 'area-medica');
            }

            function handleAreaMedicaDragStart(e) {
                draggedAreaMedicaCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handleAreaMedicaDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#kanban-area-medica .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                saveAreaMedicaKanbanData();
            }

            function handleAreaMedicaDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handleAreaMedicaDragLeave(e) {
                if (e.target === this) {
                    this.classList.remove('drag-over');
                }
            }

            function handleAreaMedicaDrop(e, container) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                container.classList.remove('drag-over');

                if (draggedAreaMedicaCard && draggedAreaMedicaCard.parentNode !== container) {
                    container.appendChild(draggedAreaMedicaCard);
                    updateColumnCounts();
                    saveAreaMedicaKanbanData();
                }
                return false;
            }

            function openAddAreaMedicaCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title-area">Título do Card</label>
                                <input type="text" id="card-title-area" placeholder="Ex: Consulta João" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description-area">Descrição</label>
                                <textarea id="card-description-area" placeholder="Detalhes do atendimento" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority-area">Prioridade</label>
                                <select id="card-priority-area">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="card-responsible-area">Responsável</label>
                                <input type="text" id="card-responsible-area" placeholder="Nome do responsável">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card-area">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card-area">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card-area');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card-area');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title-area').value.trim();
                    const description = modal.querySelector('#card-description-area').value.trim();
                    const priority = modal.querySelector('#card-priority-area').value;
                    const responsible = modal.querySelector('#card-responsible-area').value.trim();

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ${responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${responsible}</div></div>` : ''}
                    `;

                    newCard.addEventListener('dragstart', handleAreaMedicaDragStart);
                    newCard.addEventListener('dragend', handleAreaMedicaDragEnd);

                    newCard.querySelector('.btn-card-delete').addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            saveAreaMedicaKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    saveAreaMedicaKanbanData();
                    modal.remove();
                });
            }

            function saveAreaMedicaKanbanData() {
                const kanbanBoard = document.getElementById('kanban-area-medica');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium',
                        responsible: card.querySelector('.card-meta-item')?.textContent.replace(/\s+/g, ' ').trim().substring(1) || ''
                    }));
                });

                localStorage.setItem('areaMedicaKanbanData', JSON.stringify(data));
            }

            function loadAreaMedicaKanbanData() {
                const data = localStorage.getItem('areaMedicaKanbanData');
                if (!data) return;

                const kanbanData = JSON.parse(data);
                const kanbanBoard = document.getElementById('kanban-area-medica');

                Object.keys(kanbanData).forEach(columnTitle => {
                    const column = kanbanBoard.querySelector(`[data-column-title="${columnTitle}"]`);
                    if (!column) return;

                    const container = column.querySelector('.kanban-cards');
                    kanbanData[columnTitle].forEach(cardData => {
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                </div>
                                <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ${cardData.responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${cardData.responsible}</div></div>` : ''}
                        `;

                        card.addEventListener('dragstart', handleAreaMedicaDragStart);
                        card.addEventListener('dragend', handleAreaMedicaDragEnd);

                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm('Excluir este card?')) {
                                card.remove();
                                updateColumnCounts();
                                saveAreaMedicaKanbanData();
                            }
                        });

                        container.appendChild(card);
                    });
                });
            }

            // ========== FINANCEIRO - TABS & LOGIC ==========

            function initFinanceiroKanban() {
                // Tab switching
                document.querySelectorAll('.fin-tab-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.querySelectorAll('.fin-tab-btn').forEach(b => { b.classList.remove('active'); b.style.background = '#1a5d52'; });
                        this.classList.add('active');
                        this.style.background = '';
                        const tab = this.getAttribute('data-fin-tab');
                        document.querySelectorAll('.fin-tab-content').forEach(t => { t.style.display = 'none'; t.classList.remove('active'); });
                        const target = document.getElementById('fin-tab-' + tab);
                        if (target) { target.style.display = ''; target.classList.add('active'); }
                    });
                });

                // Back button
                const btnBack = document.getElementById('btn-back-financeiro');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('financeiro').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }

                // Load all data
                loadCentrosCusto();
                loadPlanoContas();
                loadFluxoCaixa();
                loadConciliacao();
                loadFinDashboard();
                initRelatorios();

                // Button handlers
                const btnAddCentro = document.getElementById('btn-add-centro');
                if (btnAddCentro) btnAddCentro.addEventListener('click', () => openCentroModal(null));

                const btnAddPlano = document.getElementById('btn-add-plano');
                if (btnAddPlano) btnAddPlano.addEventListener('click', () => openPlanoContaModal(null));

                const btnAddMov = document.getElementById('btn-add-movimento');
                if (btnAddMov) btnAddMov.addEventListener('click', () => openMovimentoModal());

                const btnAddBanco = document.getElementById('btn-add-banco');
                if (btnAddBanco) btnAddBanco.addEventListener('click', () => openBancoModal());

                const fluxoMes = document.getElementById('fluxo-mes');
                if (fluxoMes) fluxoMes.addEventListener('change', () => loadFluxoCaixa());
            }

            // --- Centros de Custo ---
            function loadCentrosCusto() {
                const tbody = document.getElementById('centros-custo-tbody');
                if (!tbody) return;
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:20px;color:#888;">Carregando...</td></tr>';
                fetch('/api/centros-custo').then(r => r.json()).then(data => {
                    const grupos = data.grupos || [];
                    if (!grupos.length) {
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:20px;color:#888;">Nenhum centro cadastrado</td></tr>';
                        return;
                    }
                    tbody.innerHTML = '';
                    grupos.forEach(g => {
                        const subs = g.subgrupos || [];
                        if (!subs.length) {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `<td style="padding:10px;font-weight:bold;color:#0E4D42;border-bottom:1px solid #eee;">${g.nome}</td>
                                <td style="padding:10px;border-bottom:1px solid #eee;color:#999;">-</td>
                                <td style="padding:10px;text-align:center;border-bottom:1px solid #eee;">-</td>
                                <td style="padding:10px;text-align:center;border-bottom:1px solid #eee;">
                                    <button onclick="openCentroModal(${g.id})" style="background:#0E4D42;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;margin-right:4px;" title="Editar"><i class="fas fa-edit"></i></button>
                                    <button onclick="deleteCentro(${g.id})" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>
                                </td>`;
                            tbody.appendChild(tr);
                        } else {
                            subs.forEach((s, i) => {
                                const tr = document.createElement('tr');
                                tr.style.borderBottom = '1px solid #eee';
                                tr.innerHTML = `<td style="padding:10px;${i === 0 ? 'font-weight:bold;color:#0E4D42;' : 'color:#ccc;'}">${i === 0 ? g.nome : ''}</td>
                                    <td style="padding:10px;">${s.nome}</td>
                                    <td style="padding:10px;text-align:center;"><span style="background:${s.status === 'Ativo' ? '#e8f5e9' : '#ffebee'};color:${s.status === 'Ativo' ? '#2e7d32' : '#c62828'};padding:2px 10px;border-radius:10px;font-size:11px;">${s.status}</span></td>
                                    <td style="padding:10px;text-align:center;">
                                        ${i === 0 ? `<button onclick="openCentroModal(${g.id})" style="background:#0E4D42;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;margin-right:4px;" title="Editar"><i class="fas fa-edit"></i></button><button onclick="deleteCentro(${g.id})" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>` : ''}
                                    </td>`;
                                tbody.appendChild(tr);
                            });
                        }
                    });
                }).catch(() => {
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:20px;color:#D81B60;">Erro ao carregar</td></tr>';
                });
            }

            function openCentroModal(grupoId) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                const isNew = !grupoId;
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-sitemap"></i> ${isNew ? 'Novo Grupo' : 'Editar Grupo'}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group"><label>Nome do Grupo</label><input id="centro-nome" value="" placeholder="Ex: Produtos e Servicos"></div>
                            <div class="form-group"><label>Subgrupos (um por linha)</label><textarea id="centro-subs" rows="5" placeholder="Medicos&#10;Clinica Verde&#10;Dentista"></textarea></div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-cancel-centro">Cancelar</button>
                            <button class="btn-primary btn-save-centro">Salvar</button>
                        </div>
                    </div>`;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel-centro').addEventListener('click', () => modal.remove());

                if (grupoId) {
                    fetch('/api/centros-custo').then(r => r.json()).then(data => {
                        const g = (data.grupos || []).find(x => x.id === grupoId);
                        if (g) {
                            modal.querySelector('#centro-nome').value = g.nome;
                            modal.querySelector('#centro-subs').value = (g.subgrupos || []).map(s => s.nome).join('\n');
                        }
                    });
                }

                modal.querySelector('.btn-save-centro').addEventListener('click', async () => {
                    const nome = modal.querySelector('#centro-nome').value.trim();
                    if (!nome) { alert('Nome e obrigatorio'); return; }
                    const subsText = modal.querySelector('#centro-subs').value.trim();
                    const subgrupos = subsText ? subsText.split('\n').filter(s => s.trim()).map(s => ({ nome: s.trim(), status: 'Ativo' })) : [];
                    const body = { nome, subgrupos };
                    try {
                        const url = grupoId ? '/api/centros-custo/' + grupoId : '/api/centros-custo';
                        const method = grupoId ? 'PUT' : 'POST';
                        await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
                        modal.remove();
                        loadCentrosCusto();
                    } catch(e) { alert('Erro ao salvar'); }
                });
            }

            async function deleteCentro(grupoId) {
                if (!confirm('Excluir este grupo?')) return;
                await fetch('/api/centros-custo/' + grupoId, { method: 'DELETE' });
                loadCentrosCusto();
            }

            // --- Plano de Contas ---
            function loadPlanoContas() {
                const tbody = document.getElementById('plano-contas-tbody');
                if (!tbody) return;
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#888;">Carregando...</td></tr>';
                fetch('/api/plano-contas').then(r => r.json()).then(data => {
                    const contas = data.plano_contas || [];
                    if (!contas.length) {
                        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#888;">Nenhuma conta cadastrada</td></tr>';
                        return;
                    }
                    tbody.innerHTML = '';
                    contas.forEach(c => {
                        const subs = c.subcategorias || [];
                        if (!subs.length) {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `<td style="padding:10px;font-weight:bold;color:#0E4D42;border-bottom:1px solid #eee;">${c.grupo}</td>
                                <td style="padding:10px;border-bottom:1px solid #eee;">${c.categoria}</td>
                                <td style="padding:10px;border-bottom:1px solid #eee;color:#999;">-</td>
                                <td style="padding:10px;text-align:center;border-bottom:1px solid #eee;">-</td>
                                <td style="padding:10px;text-align:center;border-bottom:1px solid #eee;">
                                    <button onclick="openPlanoContaModal(${c.id})" style="background:#0E4D42;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;margin-right:4px;" title="Editar"><i class="fas fa-edit"></i></button>
                                    <button onclick="deletePlanoConta(${c.id})" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>
                                </td>`;
                            tbody.appendChild(tr);
                        } else {
                            subs.forEach((s, i) => {
                                const tr = document.createElement('tr');
                                tr.style.borderBottom = '1px solid #eee';
                                tr.innerHTML = `<td style="padding:10px;${i === 0 ? 'font-weight:bold;color:#0E4D42;' : 'color:#ccc;'}">${i === 0 ? c.grupo : ''}</td>
                                    <td style="padding:10px;${i === 0 ? '' : 'color:#ccc;'}">${i === 0 ? c.categoria : ''}</td>
                                    <td style="padding:10px;">${s.nome}</td>
                                    <td style="padding:10px;text-align:center;"><span style="background:${(s.status||'').includes('Ativo') ? '#e8f5e9' : '#ffebee'};color:${(s.status||'').includes('Ativo') ? '#2e7d32' : '#c62828'};padding:2px 10px;border-radius:10px;font-size:11px;">${s.status || 'Ativo'}</span></td>
                                    <td style="padding:10px;text-align:center;">
                                        ${i === 0 ? `<button onclick="openPlanoContaModal(${c.id})" style="background:#0E4D42;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;margin-right:4px;" title="Editar"><i class="fas fa-edit"></i></button><button onclick="deletePlanoConta(${c.id})" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>` : ''}
                                    </td>`;
                                tbody.appendChild(tr);
                            });
                        }
                    });
                }).catch(() => {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#D81B60;">Erro ao carregar</td></tr>';
                });
            }

            function openPlanoContaModal(contaId) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                const isNew = !contaId;
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-list-ol"></i> ${isNew ? 'Nova Conta' : 'Editar Conta'}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group"><label>Grupo</label><input id="plano-grupo" value="" placeholder="Ex: Receita Bruta"></div>
                            <div class="form-group"><label>Categoria</label><input id="plano-cat" value="" placeholder="Ex: Receita com produtos"></div>
                            <div class="form-group"><label>Subcategorias (uma por linha)</label><textarea id="plano-subs" rows="5" placeholder="Fitoterapico&#10;Microbiota&#10;Mitocondria"></textarea></div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-cancel-plano">Cancelar</button>
                            <button class="btn-primary btn-save-plano">Salvar</button>
                        </div>
                    </div>`;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel-plano').addEventListener('click', () => modal.remove());

                if (contaId) {
                    fetch('/api/plano-contas').then(r => r.json()).then(data => {
                        const c = (data.plano_contas || []).find(x => x.id === contaId);
                        if (c) {
                            modal.querySelector('#plano-grupo').value = c.grupo;
                            modal.querySelector('#plano-cat').value = c.categoria;
                            modal.querySelector('#plano-subs').value = (c.subcategorias || []).map(s => s.nome).join('\n');
                        }
                    });
                }

                modal.querySelector('.btn-save-plano').addEventListener('click', async () => {
                    const grupo = modal.querySelector('#plano-grupo').value.trim();
                    const categoria = modal.querySelector('#plano-cat').value.trim();
                    if (!grupo) { alert('Grupo e obrigatorio'); return; }
                    const subsText = modal.querySelector('#plano-subs').value.trim();
                    const subcategorias = subsText ? subsText.split('\n').filter(s => s.trim()).map(s => ({ nome: s.trim(), status: 'Ativo/Exibido' })) : [];
                    const body = { grupo, categoria, subcategorias };
                    try {
                        const url = contaId ? '/api/plano-contas/' + contaId : '/api/plano-contas';
                        const method = contaId ? 'PUT' : 'POST';
                        await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
                        modal.remove();
                        loadPlanoContas();
                    } catch(e) { alert('Erro ao salvar'); }
                });
            }

            async function deletePlanoConta(contaId) {
                if (!confirm('Excluir esta conta?')) return;
                await fetch('/api/plano-contas/' + contaId, { method: 'DELETE' });
                loadPlanoContas();
            }

            // --- Fluxo de Caixa ---
            function loadFluxoCaixa() {
                const tbody = document.getElementById('fluxo-caixa-tbody');
                if (!tbody) return;
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#888;">Carregando...</td></tr>';
                const mesSelect = document.getElementById('fluxo-mes');
                const mesSel = mesSelect ? mesSelect.value : '';

                fetch('/api/fluxo-caixa').then(r => r.json()).then(movimentos => {
                    // Filter by month if selected
                    let filtered = movimentos;
                    if (mesSel) {
                        filtered = movimentos.filter(m => {
                            const d = m.data || '';
                            return d.substring(5, 7) === mesSel;
                        });
                    }

                    // Sort by date
                    filtered.sort((a, b) => (a.data || '').localeCompare(b.data || ''));

                    let totalEntradas = 0, totalSaidas = 0, saldoAcum = 0;
                    filtered.forEach(m => {
                        if (m.tipo === 'entrada') totalEntradas += m.valor;
                        else totalSaidas += m.valor;
                    });

                    const elEnt = document.getElementById('fluxo-entradas');
                    const elSai = document.getElementById('fluxo-saidas');
                    const elSal = document.getElementById('fluxo-saldo');
                    if (elEnt) elEnt.textContent = 'R$ ' + totalEntradas.toLocaleString('pt-BR', {minimumFractionDigits:2});
                    if (elSai) elSai.textContent = 'R$ ' + totalSaidas.toLocaleString('pt-BR', {minimumFractionDigits:2});
                    if (elSal) elSal.textContent = 'R$ ' + (totalEntradas - totalSaidas).toLocaleString('pt-BR', {minimumFractionDigits:2});

                    if (!filtered.length) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#888;">Nenhum movimento neste periodo</td></tr>';
                        return;
                    }
                    tbody.innerHTML = '';
                    saldoAcum = 0;
                    filtered.forEach(m => {
                        const isEntrada = m.tipo === 'entrada';
                        saldoAcum += isEntrada ? m.valor : -m.valor;
                        const tr = document.createElement('tr');
                        tr.style.borderBottom = '1px solid #eee';
                        tr.innerHTML = `
                            <td style="padding:10px;">${m.data || '-'}</td>
                            <td style="padding:10px;">${m.descricao || '-'}</td>
                            <td style="padding:10px;text-align:right;color:#2e7d32;">${isEntrada ? 'R$ ' + m.valor.toLocaleString('pt-BR', {minimumFractionDigits:2}) : ''}</td>
                            <td style="padding:10px;text-align:right;color:#c62828;">${!isEntrada ? 'R$ ' + m.valor.toLocaleString('pt-BR', {minimumFractionDigits:2}) : ''}</td>
                            <td style="padding:10px;text-align:right;font-weight:bold;color:${saldoAcum >= 0 ? '#2e7d32' : '#c62828'};">R$ ${saldoAcum.toLocaleString('pt-BR', {minimumFractionDigits:2})}</td>
                            <td style="padding:10px;text-align:center;">
                                <button onclick="deleteFluxoMov('${m.id}')" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>
                            </td>`;
                        tbody.appendChild(tr);
                    });
                }).catch(() => {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#D81B60;">Erro ao carregar</td></tr>';
                });
            }

            function openMovimentoModal() {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-money-bill-wave"></i> Novo Movimento</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                                <div class="form-group"><label>Data</label><input type="date" id="mov-data" value="${new Date().toISOString().split('T')[0]}"></div>
                                <div class="form-group"><label>Tipo</label><select id="mov-tipo"><option value="entrada">Entrada</option><option value="saida">Saida</option></select></div>
                            </div>
                            <div class="form-group"><label>Descricao</label><input id="mov-desc" placeholder="Ex: Pagamento consulta"></div>
                            <div class="form-group"><label>Valor (R$)</label><input type="number" id="mov-valor" step="0.01" min="0" placeholder="0,00"></div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-cancel-mov">Cancelar</button>
                            <button class="btn-primary btn-save-mov">Salvar</button>
                        </div>
                    </div>`;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel-mov').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-save-mov').addEventListener('click', async () => {
                    const body = {
                        data: modal.querySelector('#mov-data').value,
                        tipo: modal.querySelector('#mov-tipo').value,
                        descricao: modal.querySelector('#mov-desc').value.trim(),
                        valor: parseFloat(modal.querySelector('#mov-valor').value) || 0
                    };
                    if (!body.descricao || body.valor <= 0) { alert('Preencha todos os campos'); return; }
                    try {
                        await fetch('/api/fluxo-caixa', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
                        modal.remove();
                        loadFluxoCaixa();
                        loadFinDashboard();
                    } catch(e) { alert('Erro ao salvar'); }
                });
            }

            async function deleteFluxoMov(movId) {
                if (!confirm('Excluir este movimento?')) return;
                await fetch('/api/fluxo-caixa/' + movId, { method: 'DELETE' });
                loadFluxoCaixa();
                loadFinDashboard();
            }

            // --- Conciliacao Bancaria ---
            function loadConciliacao() {
                const bancosContainer = document.getElementById('bancos-container');
                const tbody = document.getElementById('conciliacao-tbody');
                if (!bancosContainer && !tbody) return;

                fetch('/api/conciliacao').then(r => r.json()).then(data => {
                    const bancos = data.bancos || [];
                    const movs = data.movimentos || [];

                    // Render bank cards
                    if (bancosContainer) {
                        if (!bancos.length) {
                            bancosContainer.innerHTML = '<div style="padding:20px;color:#888;text-align:center;grid-column:1/-1;">Nenhum banco cadastrado</div>';
                        } else {
                            bancosContainer.innerHTML = '';
                            bancos.forEach(b => {
                                const card = document.createElement('div');
                                card.style.cssText = 'background:linear-gradient(135deg,#1565C0,#1976D2);color:white;padding:16px;border-radius:12px;position:relative;';
                                card.innerHTML = `
                                    <button onclick="deleteBanco('${b.id}')" style="position:absolute;top:8px;right:8px;background:rgba(255,255,255,0.2);color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>
                                    <div style="font-size:11px;opacity:0.8;"><i class="fas fa-university"></i> ${b.nome}</div>
                                    <div style="font-size:11px;opacity:0.7;">Ag: ${b.agencia || '-'} | Cc: ${b.conta || '-'}</div>
                                    <div style="font-size:22px;font-weight:bold;margin-top:8px;">R$ ${(b.saldo || 0).toLocaleString('pt-BR', {minimumFractionDigits:2})}</div>
                                `;
                                bancosContainer.appendChild(card);
                            });
                        }
                    }

                    // Render movements
                    if (tbody) {
                        if (!movs.length) {
                            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#888;">Nenhum movimento</td></tr>';
                        } else {
                            tbody.innerHTML = '';
                            movs.forEach(m => {
                                const tr = document.createElement('tr');
                                tr.style.borderBottom = '1px solid #eee';
                                const statusColor = m.status === 'conciliado' ? '#2e7d32' : (m.status === 'pendente' ? '#e67e22' : '#c62828');
                                tr.innerHTML = `
                                    <td style="padding:10px;">${m.data || '-'}</td>
                                    <td style="padding:10px;">${m.descricao || '-'}</td>
                                    <td style="padding:10px;text-align:right;">R$ ${(m.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits:2})}</td>
                                    <td style="padding:10px;text-align:center;"><span style="background:${statusColor}20;color:${statusColor};padding:2px 10px;border-radius:10px;font-size:11px;cursor:pointer;" onclick="toggleConciliacaoStatus('${m.id}','${m.status}')">${m.status || 'pendente'}</span></td>
                                    <td style="padding:10px;text-align:center;">
                                        <button onclick="deleteConciliacaoMov('${m.id}')" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>
                                    </td>`;
                                tbody.appendChild(tr);
                            });
                        }
                    }
                }).catch(() => {
                    if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#D81B60;">Erro ao carregar</td></tr>';
                });
            }

            function openBancoModal() {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-university"></i> Cadastrar Banco</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group"><label>Nome do Banco</label><input id="banco-nome" placeholder="Ex: Banco do Brasil"></div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                                <div class="form-group"><label>Agencia</label><input id="banco-ag" placeholder="0001"></div>
                                <div class="form-group"><label>Conta</label><input id="banco-cc" placeholder="12345-6"></div>
                            </div>
                            <div class="form-group"><label>Saldo Inicial (R$)</label><input type="number" id="banco-saldo" step="0.01" value="0"></div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-cancel-banco">Cancelar</button>
                            <button class="btn-primary btn-save-banco">Salvar</button>
                        </div>
                    </div>`;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel-banco').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-save-banco').addEventListener('click', async () => {
                    const body = {
                        nome: modal.querySelector('#banco-nome').value.trim(),
                        agencia: modal.querySelector('#banco-ag').value.trim(),
                        conta: modal.querySelector('#banco-cc').value.trim(),
                        saldo: parseFloat(modal.querySelector('#banco-saldo').value) || 0
                    };
                    if (!body.nome) { alert('Nome e obrigatorio'); return; }
                    try {
                        await fetch('/api/conciliacao/bancos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
                        modal.remove();
                        loadConciliacao();
                    } catch(e) { alert('Erro ao salvar'); }
                });
            }

            async function deleteBanco(bancoId) {
                if (!confirm('Excluir este banco?')) return;
                await fetch('/api/conciliacao/bancos/' + bancoId, { method: 'DELETE' });
                loadConciliacao();
            }

            async function toggleConciliacaoStatus(movId, currentStatus) {
                const newStatus = currentStatus === 'pendente' ? 'conciliado' : 'pendente';
                await fetch('/api/conciliacao/movimentos/' + movId, {
                    method: 'PUT',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({ status: newStatus })
                });
                loadConciliacao();
            }

            async function deleteConciliacaoMov(movId) {
                if (!confirm('Excluir este movimento?')) return;
                await fetch('/api/conciliacao/movimentos/' + movId, { method: 'DELETE' });
                loadConciliacao();
            }

            // --- Dashboard ---
            function loadFinDashboard() {
                fetch('/api/fluxo-caixa').then(r => r.json()).then(movimentos => {
                    const now = new Date();
                    const mesAtual = String(now.getMonth() + 1).padStart(2, '0');
                    const doMes = movimentos.filter(m => (m.data || '').substring(5, 7) === mesAtual);
                    let entradas = 0, saidas = 0;
                    doMes.forEach(m => { if (m.tipo === 'entrada') entradas += m.valor; else saidas += m.valor; });
                    
                    const elEnt = document.getElementById('fin-total-entradas');
                    const elSai = document.getElementById('fin-total-saidas');
                    const elSal = document.getElementById('fin-saldo');
                    if (elEnt) elEnt.textContent = 'R$ ' + entradas.toLocaleString('pt-BR', {minimumFractionDigits:2});
                    if (elSai) elSai.textContent = 'R$ ' + saidas.toLocaleString('pt-BR', {minimumFractionDigits:2});
                    if (elSal) elSal.textContent = 'R$ ' + (entradas - saidas).toLocaleString('pt-BR', {minimumFractionDigits:2});

                    // Simple chart with Chart.js if available
                    try {
                        const ctx = document.getElementById('fin-chart');
                        if (ctx && typeof Chart !== 'undefined') {
                            if (ctx._chartInstance) ctx._chartInstance.destroy();
                            const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
                            const entArr = new Array(12).fill(0);
                            const saiArr = new Array(12).fill(0);
                            movimentos.forEach(m => {
                                const mi = parseInt((m.data || '').substring(5, 7)) - 1;
                                if (mi >= 0 && mi < 12) {
                                    if (m.tipo === 'entrada') entArr[mi] += m.valor;
                                    else saiArr[mi] += m.valor;
                                }
                            });
                            ctx._chartInstance = new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: meses,
                                    datasets: [
                                        { label: 'Entradas', data: entArr, backgroundColor: '#2e7d32' },
                                        { label: 'Saidas', data: saiArr, backgroundColor: '#c62828' }
                                    ]
                                },
                                options: { responsive: true, scales: { y: { beginAtZero: true } } }
                            });
                        }
                    } catch(e) { /* Chart.js not available */ }
                }).catch(() => {});
            }

            // --- Relatorios ---
            function initRelatorios() {
                document.querySelectorAll('.rel-card').forEach(card => {
                    card.addEventListener('click', function() {
                        const tipo = this.getAttribute('data-rel');
                        generateRelatorio(tipo);
                    });
                });

                const btnExport = document.getElementById('btn-export-rel');
                if (btnExport) btnExport.addEventListener('click', () => {
                    const content = document.getElementById('rel-conteudo');
                    if (content) {
                        const blob = new Blob([content.innerHTML], { type: 'text/html' });
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = 'relatorio.html';
                        a.click();
                    }
                });
            }

            async function generateRelatorio(tipo) {
                const output = document.getElementById('relatorio-output');
                const titulo = document.getElementById('rel-titulo');
                const conteudo = document.getElementById('rel-conteudo');
                if (!output || !conteudo) return;
                output.style.display = '';
                conteudo.innerHTML = '<div style="text-align:center;padding:20px;"><i class="fas fa-spinner fa-spin"></i> Gerando relatorio...</div>';

                try {
                    const [fluxoRes, planoRes] = await Promise.all([
                        fetch('/api/fluxo-caixa').then(r => r.json()),
                        fetch('/api/plano-contas').then(r => r.json())
                    ]);

                    const movimentos = fluxoRes || [];
                    const plano = planoRes.plano_contas || [];

                    if (tipo === 'dre') {
                        titulo.textContent = 'DRE - Demonstracao de Resultado';
                        let receitas = 0, custos = 0, despesas = 0;
                        movimentos.forEach(m => {
                            if (m.tipo === 'entrada') receitas += m.valor;
                            else {
                                const desc = (m.descricao || '').toLowerCase();
                                if (desc.includes('custo')) custos += m.valor;
                                else despesas += m.valor;
                            }
                        });
                        const lucro = receitas - custos - despesas;
                        conteudo.innerHTML = `
                            <table style="width:100%;border-collapse:collapse;">
                                <tr style="background:#e8f5e9;"><td style="padding:10px;font-weight:bold;">Receita Bruta</td><td style="padding:10px;text-align:right;font-weight:bold;color:#2e7d32;">R$ ${receitas.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>
                                <tr style="background:#ffebee;"><td style="padding:10px;font-weight:bold;">(-) Custos</td><td style="padding:10px;text-align:right;color:#c62828;">R$ ${custos.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>
                                <tr style="background:#fff3e0;"><td style="padding:10px;font-weight:bold;">(-) Despesas</td><td style="padding:10px;text-align:right;color:#e67e22;">R$ ${despesas.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>
                                <tr style="background:${lucro >= 0 ? '#e8f5e9' : '#ffebee'};border-top:2px solid #0E4D42;"><td style="padding:12px;font-weight:bold;font-size:16px;">Resultado Liquido</td><td style="padding:12px;text-align:right;font-weight:bold;font-size:16px;color:${lucro >= 0 ? '#2e7d32' : '#c62828'};">R$ ${lucro.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>
                            </table>`;
                    } else if (tipo === 'receitas') {
                        titulo.textContent = 'Relatorio de Receitas';
                        const recs = movimentos.filter(m => m.tipo === 'entrada');
                        const total = recs.reduce((s, m) => s + m.valor, 0);
                        let html = '<table style="width:100%;border-collapse:collapse;"><thead><tr style="background:#0E4D42;color:white;"><th style="padding:10px;text-align:left;">Data</th><th style="padding:10px;text-align:left;">Descricao</th><th style="padding:10px;text-align:right;">Valor</th></tr></thead><tbody>';
                        recs.forEach(m => { html += `<tr style="border-bottom:1px solid #eee;"><td style="padding:8px;">${m.data}</td><td style="padding:8px;">${m.descricao}</td><td style="padding:8px;text-align:right;color:#2e7d32;">R$ ${m.valor.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>`; });
                        html += `</tbody><tfoot><tr style="background:#e8f5e9;font-weight:bold;"><td colspan="2" style="padding:10px;">TOTAL</td><td style="padding:10px;text-align:right;color:#2e7d32;">R$ ${total.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr></tfoot></table>`;
                        conteudo.innerHTML = recs.length ? html : '<p style="text-align:center;color:#888;">Nenhuma receita registrada</p>';
                    } else if (tipo === 'despesas') {
                        titulo.textContent = 'Relatorio de Despesas';
                        const desps = movimentos.filter(m => m.tipo === 'saida');
                        const total = desps.reduce((s, m) => s + m.valor, 0);
                        let html = '<table style="width:100%;border-collapse:collapse;"><thead><tr style="background:#c62828;color:white;"><th style="padding:10px;text-align:left;">Data</th><th style="padding:10px;text-align:left;">Descricao</th><th style="padding:10px;text-align:right;">Valor</th></tr></thead><tbody>';
                        desps.forEach(m => { html += `<tr style="border-bottom:1px solid #eee;"><td style="padding:8px;">${m.data}</td><td style="padding:8px;">${m.descricao}</td><td style="padding:8px;text-align:right;color:#c62828;">R$ ${m.valor.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>`; });
                        html += `</tbody><tfoot><tr style="background:#ffebee;font-weight:bold;"><td colspan="2" style="padding:10px;">TOTAL</td><td style="padding:10px;text-align:right;color:#c62828;">R$ ${total.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr></tfoot></table>`;
                        conteudo.innerHTML = desps.length ? html : '<p style="text-align:center;color:#888;">Nenhuma despesa registrada</p>';
                    } else if (tipo === 'comparativo') {
                        titulo.textContent = 'Comparativo Mensal';
                        const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
                        let html = '<table style="width:100%;border-collapse:collapse;"><thead><tr style="background:#1565C0;color:white;"><th style="padding:10px;">Mes</th><th style="padding:10px;text-align:right;">Entradas</th><th style="padding:10px;text-align:right;">Saidas</th><th style="padding:10px;text-align:right;">Saldo</th></tr></thead><tbody>';
                        for (let i = 0; i < 12; i++) {
                            const mm = String(i + 1).padStart(2, '0');
                            const ent = movimentos.filter(m => m.tipo === 'entrada' && (m.data||'').substring(5,7) === mm).reduce((s,m) => s + m.valor, 0);
                            const sai = movimentos.filter(m => m.tipo === 'saida' && (m.data||'').substring(5,7) === mm).reduce((s,m) => s + m.valor, 0);
                            if (ent || sai) {
                                html += `<tr style="border-bottom:1px solid #eee;"><td style="padding:8px;">${meses[i]}</td><td style="padding:8px;text-align:right;color:#2e7d32;">R$ ${ent.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td><td style="padding:8px;text-align:right;color:#c62828;">R$ ${sai.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td><td style="padding:8px;text-align:right;font-weight:bold;color:${(ent-sai) >= 0 ? '#2e7d32' : '#c62828'};">R$ ${(ent-sai).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>`;
                            }
                        }
                        html += '</tbody></table>';
                        conteudo.innerHTML = html;
                    }
                } catch(e) {
                    conteudo.innerHTML = '<p style="text-align:center;color:#D81B60;">Erro ao gerar relatorio</p>';
                }
            }

            // Stub save function for column reorder compatibility
            function saveFinanceiroKanbanData() { /* no-op - financeiro uses API now */ }

            // ========== KANBAN JUDICIAL ==========
            let draggedJudicialCard = null;

            function initJudicialKanban() {
                const kanbanBoard = document.getElementById('kanban-judicial');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handleJudicialDragStart);
                    card.addEventListener('dragend', handleJudicialDragEnd);
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handleJudicialDragOver);
                    cardsContainer.addEventListener('drop', (e) => handleJudicialDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handleJudicialDragLeave);

                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddJudicialCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadJudicialKanbanData();
                updateColumnCounts();
                setupColumnReordering('kanban-judicial', 'judicial');

                const btnBack = document.getElementById('btn-back-judicial');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('judicial').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }
            }

            function handleJudicialDragStart(e) {
                draggedJudicialCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handleJudicialDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#kanban-judicial .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                saveJudicialKanbanData();
            }

            function handleJudicialDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handleJudicialDragLeave(e) {
                if (e.target === this) {
                    this.classList.remove('drag-over');
                }
            }

            function handleJudicialDrop(e, container) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                container.classList.remove('drag-over');

                if (draggedJudicialCard && draggedJudicialCard.parentNode !== container) {
                    container.appendChild(draggedJudicialCard);
                    updateColumnCounts();
                    saveJudicialKanbanData();
                }
                return false;
            }

            function openAddJudicialCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title-jud">Título do Card</label>
                                <input type="text" id="card-title-jud" placeholder="Ex: Processo ANVISA" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description-jud">Descrição</label>
                                <textarea id="card-description-jud" placeholder="Detalhes do processo" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority-jud">Prioridade</label>
                                <select id="card-priority-jud">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="card-responsible-jud">Responsável</label>
                                <input type="text" id="card-responsible-jud" placeholder="Nome do responsável">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card-jud">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card-jud">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card-jud');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card-jud');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title-jud').value.trim();
                    const description = modal.querySelector('#card-description-jud').value.trim();
                    const priority = modal.querySelector('#card-priority-jud').value;
                    const responsible = modal.querySelector('#card-responsible-jud').value.trim();

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ${responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${responsible}</div></div>` : ''}
                    `;

                    newCard.addEventListener('dragstart', handleJudicialDragStart);
                    newCard.addEventListener('dragend', handleJudicialDragEnd);

                    newCard.querySelector('.btn-card-delete').addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            saveJudicialKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    saveJudicialKanbanData();
                    modal.remove();
                });
            }

            function saveJudicialKanbanData() {
                const kanbanBoard = document.getElementById('kanban-judicial');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium',
                        responsible: card.querySelector('.card-meta-item')?.textContent.replace(/\s+/g, ' ').trim().substring(1) || ''
                    }));
                });

                localStorage.setItem('judicialKanbanData', JSON.stringify(data));
            }

            function loadJudicialKanbanData() {
                const data = localStorage.getItem('judicialKanbanData');
                if (!data) return;

                const kanbanData = JSON.parse(data);
                const kanbanBoard = document.getElementById('kanban-judicial');

                Object.keys(kanbanData).forEach(columnTitle => {
                    const column = kanbanBoard.querySelector(`[data-column-title="${columnTitle}"]`);
                    if (!column) return;

                    const container = column.querySelector('.kanban-cards');
                    kanbanData[columnTitle].forEach(cardData => {
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                </div>
                                <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ${cardData.responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${cardData.responsible}</div></div>` : ''}
                        `;

                        card.addEventListener('dragstart', handleJudicialDragStart);
                        card.addEventListener('dragend', handleJudicialDragEnd);

                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm('Excluir este card?')) {
                                card.remove();
                                updateColumnCounts();
                                saveJudicialKanbanData();
                            }
                        });

                        container.appendChild(card);
                    });
                });
            }

            // ========== IMPORTAÇÃO MEDICAMENTO KANBAN ==========
            let draggedImportacaoCard = null;

            function initImportacaoKanban() {
                const kanbanBoard = document.getElementById('kanban-importacao');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handleImportacaoDragStart);
                    card.addEventListener('dragend', handleImportacaoDragEnd);
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handleImportacaoDragOver);
                    cardsContainer.addEventListener('drop', (e) => handleImportacaoDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handleImportacaoDragLeave);

                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddImportacaoCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadImportacaoKanbanData();
                updateColumnCounts();
                setupColumnReordering('kanban-importacao', 'importacao');

                const btnBack = document.getElementById('btn-back-importacao');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('importacao').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }
            }

            function handleImportacaoDragStart(e) {
                draggedImportacaoCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handleImportacaoDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#kanban-importacao .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                saveImportacaoKanbanData();
            }

            function handleImportacaoDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handleImportacaoDragLeave(e) {
                if (e.target === this) {
                    this.classList.remove('drag-over');
                }
            }

            function handleImportacaoDrop(e, container) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                container.classList.remove('drag-over');

                if (draggedImportacaoCard && draggedImportacaoCard.parentNode !== container) {
                    container.appendChild(draggedImportacaoCard);
                    updateColumnCounts();
                    saveImportacaoKanbanData();
                }
                return false;
            }

            function openAddImportacaoCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title-imp">Título do Card</label>
                                <input type="text" id="card-title-imp" placeholder="Ex: Importação Azitromicina 500mg" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description-imp">Descrição</label>
                                <textarea id="card-description-imp" placeholder="Detalhes da importação (lote, quantidade, etc.)" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority-imp">Prioridade</label>
                                <select id="card-priority-imp">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="card-responsible-imp">Responsável</label>
                                <input type="text" id="card-responsible-imp" placeholder="Nome do responsável">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card-imp">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card-imp">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card-imp');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card-imp');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title-imp').value.trim();
                    const description = modal.querySelector('#card-description-imp').value.trim();
                    const priority = modal.querySelector('#card-priority-imp').value;
                    const responsible = modal.querySelector('#card-responsible-imp').value.trim();

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ${responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${responsible}</div></div>` : ''}
                    `;

                    newCard.addEventListener('dragstart', handleImportacaoDragStart);
                    newCard.addEventListener('dragend', handleImportacaoDragEnd);

                    newCard.querySelector('.btn-card-delete').addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            saveImportacaoKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    saveImportacaoKanbanData();
                    modal.remove();
                });
            }

            function saveImportacaoKanbanData() {
                const kanbanBoard = document.getElementById('kanban-importacao');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium',
                        responsible: card.querySelector('.card-meta-item')?.textContent.replace(/\s+/g, ' ').trim().substring(1) || ''
                    }));
                });

                localStorage.setItem('importacaoKanbanData', JSON.stringify(data));
            }

            function loadImportacaoKanbanData() {
                const data = localStorage.getItem('importacaoKanbanData');
                if (!data) return;

                const kanbanData = JSON.parse(data);
                const kanbanBoard = document.getElementById('kanban-importacao');

                Object.keys(kanbanData).forEach(columnTitle => {
                    const column = kanbanBoard.querySelector(`[data-column-title="${columnTitle}"]`);
                    if (!column) return;

                    const container = column.querySelector('.kanban-cards');
                    kanbanData[columnTitle].forEach(cardData => {
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                </div>
                                <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ${cardData.responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${cardData.responsible}</div></div>` : ''}
                        `;

                        card.addEventListener('dragstart', handleImportacaoDragStart);
                        card.addEventListener('dragend', handleImportacaoDragEnd);

                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm('Excluir este card?')) {
                                card.remove();
                                updateColumnCounts();
                                saveImportacaoKanbanData();
                            }
                        });

                        container.appendChild(card);
                    });
                });
            }

            // ========== IMPORTACAO - TABS + MEDICAMENTOS ==========
            
            // Tab switching
            document.querySelectorAll('.imp-tab-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    document.querySelectorAll('.imp-tab-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    const tab = this.getAttribute('data-imp-tab');
                    document.querySelectorAll('.imp-tab-content').forEach(t => t.style.display = 'none');
                    document.getElementById('imp-tab-' + tab).style.display = '';
                });
            });

            // Load medicamentos from API
            function loadMedicamentosGrid() {
                const grid = document.getElementById('medicamentos-grid');
                if (!grid) return;
                grid.innerHTML = '<div style="text-align:center;padding:40px;color:#888;"><i class="fas fa-spinner fa-spin" style="font-size:24px;"></i><p>Carregando...</p></div>';
                
                fetch('/api/medicamentos').then(r => r.json()).then(meds => {
                    if (!meds || !meds.length) {
                        grid.innerHTML = '<div style="text-align:center;padding:40px;color:#888;"><i class="fas fa-box-open" style="font-size:36px;"></i><p>Nenhum medicamento cadastrado</p></div>';
                        return;
                    }
                    grid.innerHTML = '';
                    meds.forEach(med => {
                        const card = document.createElement('div');
                        card.style.cssText = 'background:white;border-radius:12px;padding:16px;border-left:4px solid #0E4D42;box-shadow:0 2px 8px rgba(0,0,0,0.08);cursor:pointer;transition:transform 0.2s;';
                        card.onmouseover = () => card.style.transform = 'translateY(-2px)';
                        card.onmouseout = () => card.style.transform = '';
                        card.innerHTML = `
                            <div style="display:flex;justify-content:space-between;align-items:start;">
                                <div style="flex:1;">
                                    <div style="font-weight:bold;color:#0E4D42;font-size:14px;margin-bottom:6px;">${med.nome}</div>
                                    <div style="font-size:12px;color:#666;margin-bottom:4px;"><i class="fas fa-flask"></i> ${med.laboratorio || 'N/A'}</div>
                                    <div style="font-size:12px;color:#666;margin-bottom:4px;"><i class="fas fa-tag"></i> ${med.tipo || 'N/A'} | ${med.volume || ''}</div>
                                    <div style="font-size:11px;color:#999;">${med.concentracao ? med.concentracao.substring(0, 60) + '...' : ''}</div>
                                </div>
                                <div style="display:flex;gap:4px;">
                                    <button class="btn-med-edit" data-id="${med.id}" style="background:#0E4D42;color:white;border:none;padding:6px 10px;border-radius:6px;cursor:pointer;font-size:11px;" title="Editar"><i class="fas fa-edit"></i></button>
                                    <button class="btn-med-delete" data-id="${med.id}" style="background:#D81B60;color:white;border:none;padding:6px 10px;border-radius:6px;cursor:pointer;font-size:11px;" title="Excluir"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                            <div style="margin-top:8px;font-size:11px;color:#888;">ID: ${med.id}</div>
                        `;
                        card.querySelector('.btn-med-edit').addEventListener('click', (e) => { e.stopPropagation(); openEditMedicamentoModal(med); });
                        card.querySelector('.btn-med-delete').addEventListener('click', (e) => { e.stopPropagation(); deleteMedicamento(med); });
                        card.addEventListener('click', () => openMedicamentoDetailModal(med));
                        grid.appendChild(card);
                    });
                }).catch(() => {
                    grid.innerHTML = '<div style="text-align:center;padding:40px;color:#D81B60;"><i class="fas fa-exclamation-triangle" style="font-size:36px;"></i><p>Erro ao carregar medicamentos</p></div>';
                });
            }

            function openMedicamentoDetailModal(med) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:600px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-pills"></i> ${med.nome}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <table style="width:100%;border-collapse:collapse;">
                                <tr><td style="padding:8px;font-weight:bold;color:#0E4D42;width:40%;">ID</td><td style="padding:8px;">${med.id}</td></tr>
                                <tr style="background:#f9f9f9;"><td style="padding:8px;font-weight:bold;color:#0E4D42;">Laboratorio</td><td style="padding:8px;">${med.laboratorio || 'N/A'}</td></tr>
                                <tr><td style="padding:8px;font-weight:bold;color:#0E4D42;">Tipo</td><td style="padding:8px;">${med.tipo || 'N/A'}</td></tr>
                                <tr style="background:#f9f9f9;"><td style="padding:8px;font-weight:bold;color:#0E4D42;">Volume</td><td style="padding:8px;">${med.volume || 'N/A'}</td></tr>
                                <tr><td style="padding:8px;font-weight:bold;color:#0E4D42;">Concentracao</td><td style="padding:8px;font-size:12px;">${med.concentracao || 'N/A'}</td></tr>
                                <tr style="background:#f9f9f9;"><td style="padding:8px;font-weight:bold;color:#0E4D42;">Posologia</td><td style="padding:8px;font-size:12px;">${med.posologia || 'N/A'}</td></tr>
                                <tr><td style="padding:8px;font-weight:bold;color:#0E4D42;">Dosagem/ml</td><td style="padding:8px;">${med.dosagem_ml || 'N/A'}</td></tr>
                                <tr style="background:#f9f9f9;"><td style="padding:8px;font-weight:bold;color:#0E4D42;">Observacoes</td><td style="padding:8px;">${med.observacoes || 'N/A'}</td></tr>
                            </table>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-close-det">Fechar</button>
                            <button class="btn-primary btn-edit-det">Editar</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-close-det').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-edit-det').addEventListener('click', () => { modal.remove(); openEditMedicamentoModal(med); });
            }

            function openEditMedicamentoModal(med) {
                const isNew = !med;
                const m = med || {};
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:600px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-${isNew ? 'plus' : 'edit'}"></i> ${isNew ? 'Novo Medicamento' : 'Editar - ' + m.nome}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group"><label>Nome</label><input id="med-nome" value="${m.nome || ''}" required></div>
                            <div class="form-group"><label>Laboratório / Marca</label><input id="med-lab" value="${m.laboratorio || ''}"></div>
                            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
                                <div class="form-group"><label>Tipo</label><select id="med-tipo" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;">
                                    <option value="Óleo" ${(m.tipo||'')==='Óleo'?'selected':''}>Óleo</option>
                                    <option value="Gummy" ${(m.tipo||'')==='Gummy'?'selected':''}>Gummy</option>
                                    <option value="Cápsula" ${(m.tipo||'')==='Cápsula'?'selected':''}>Cápsula</option>
                                    <option value="Tópico" ${(m.tipo||'')==='Tópico'?'selected':''}>Tópico</option>
                                    <option value="Outro" ${(m.tipo||'')==='Outro'?'selected':''}>Outro</option>
                                </select></div>
                                <div class="form-group"><label>Espectro</label><select id="med-espectro" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;">
                                    <option value="full_spectrum" ${(m.espectro||'')==='full_spectrum'?'selected':''}>Full Spectrum</option>
                                    <option value="broad_spectrum" ${(m.espectro||'')==='broad_spectrum'?'selected':''}>Broad Spectrum</option>
                                    <option value="isolado" ${(m.espectro||'')==='isolado'?'selected':''}>Isolado</option>
                                </select></div>
                                <div class="form-group"><label>Volume (texto)</label><input id="med-vol" value="${m.volume || ''}"></div>
                            </div>
                            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;background:#f0fdf4;padding:12px;border-radius:8px;border:1px solid #bbf7d0;margin-bottom:12px;">
                                <div class="form-group" style="margin-bottom:0;"><label style="color:#065f46;font-weight:700;">Volume (ml) *</label><input id="med-volume-ml" type="number" step="0.1" value="${m.volume_ml || ''}" placeholder="Ex: 30" style="border-color:#059669;"></div>
                                <div class="form-group" style="margin-bottom:0;"><label style="color:#065f46;font-weight:700;">Concentração (mg/ml) *</label><input id="med-conc-mg-ml" type="number" step="0.01" value="${m.concentration_mg_ml || ''}" placeholder="Ex: 100" style="border-color:#059669;"></div>
                                <div class="form-group" style="margin-bottom:0;"><label style="color:#065f46;font-weight:700;">Gotas por ml</label><input id="med-drops-ml" type="number" value="${m.drops_per_ml || 20}" placeholder="20" style="border-color:#059669;"></div>
                            </div>
                            <p style="font-size:11px;color:#6b7280;margin:-6px 0 12px 0;"><i class="fas fa-calculator" style="color:#059669;"></i> Campos verdes são obrigatórios para a Calculadora Cannabis (24 meses)</p>
                            <div class="form-group"><label>Concentração (texto descritivo)</label><textarea id="med-conc" rows="2">${m.concentracao || ''}</textarea></div>
                            <div class="form-group"><label>Posologia Padrão</label><textarea id="med-pos" rows="2">${m.posologia || ''}</textarea></div>
                            <div class="form-group"><label>Dosagem/ml</label><input id="med-dos" value="${m.dosagem_ml || ''}"></div>
                            <div class="form-group"><label>Fornecedor</label><input id="med-fornecedor" value="${m.fornecedor || ''}" placeholder="Nome do fornecedor para importação"></div>
                            <div class="form-group"><label>Observações</label><textarea id="med-obs" rows="2">${m.observacoes || ''}</textarea></div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-cancel-med">Cancelar</button>
                            <button class="btn-primary btn-save-med">Salvar</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel-med').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-save-med').addEventListener('click', async () => {
                    const nome = modal.querySelector('#med-nome').value.trim();
                    if (!nome) { alert('Nome e obrigatorio'); return; }
                    const body = {
                        nome,
                        laboratorio: modal.querySelector('#med-lab').value.trim(),
                        tipo: modal.querySelector('#med-tipo').value.trim(),
                        espectro: modal.querySelector('#med-espectro').value.trim(),
                        volume: modal.querySelector('#med-vol').value.trim(),
                        volume_ml: parseFloat(modal.querySelector('#med-volume-ml').value) || 0,
                        concentration_mg_ml: parseFloat(modal.querySelector('#med-conc-mg-ml').value) || 0,
                        drops_per_ml: parseInt(modal.querySelector('#med-drops-ml').value) || 20,
                        concentracao: modal.querySelector('#med-conc').value.trim(),
                        posologia: modal.querySelector('#med-pos').value.trim(),
                        dosagem_ml: modal.querySelector('#med-dos').value.trim(),
                        fornecedor: modal.querySelector('#med-fornecedor').value.trim(),
                        observacoes: modal.querySelector('#med-obs').value.trim()
                    };
                    try {
                        const url = isNew ? '/api/medicamentos' : '/api/medicamentos/' + m.id;
                        const method = isNew ? 'POST' : 'PUT';
                        const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
                        if (res.ok) {
                            alert(isNew ? 'Medicamento criado com sucesso!' : 'Medicamento atualizado!');
                            modal.remove();
                            loadMedicamentosGrid();
                        } else {
                            alert('Erro ao salvar');
                        }
                    } catch(e) { alert('Erro de conexao'); }
                });
            }

            async function deleteMedicamento(med) {
                if (!confirm('Excluir medicamento "' + med.nome + '"?')) return;
                try {
                    const res = await fetch('/api/medicamentos/' + med.id, { method: 'DELETE' });
                    if (res.ok) {
                        alert('Medicamento excluido!');
                        loadMedicamentosGrid();
                    } else { alert('Erro ao excluir'); }
                } catch(e) { alert('Erro de conexao'); }
            }

            // Buttons
            const btnNovoMed = document.getElementById('btn-novo-medicamento');
            if (btnNovoMed) btnNovoMed.addEventListener('click', () => openEditMedicamentoModal(null));

            const btnNovaImp = document.getElementById('btn-nova-importacao');
            if (btnNovaImp) btnNovaImp.addEventListener('click', () => {
                // Switch to importacoes tab and open add card
                document.querySelectorAll('.imp-tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelector('.imp-tab-btn[data-imp-tab="importacoes"]').classList.add('active');
                document.querySelectorAll('.imp-tab-content').forEach(t => t.style.display = 'none');
                document.getElementById('imp-tab-importacoes').style.display = '';
                const firstCol = document.querySelector('#kanban-importacao .kanban-column .kanban-cards');
                if (firstCol) openAddImportacaoCardModal(firstCol, 'Solicitado');
            });

            // Load medicamentos on page init
            loadMedicamentosGrid();

            // ========== INTELIGÊNCIA ARTIFICIAL KANBAN ==========
            let draggedIaCard = null;

            function initIaKanban() {
                const kanbanBoard = document.getElementById('kanban-ia');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handleIaDragStart);
                    card.addEventListener('dragend', handleIaDragEnd);
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handleIaDragOver);
                    cardsContainer.addEventListener('drop', (e) => handleIaDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handleIaDragLeave);

                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddIaCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadIaKanbanData();
                updateColumnCounts();
                setupColumnReordering('kanban-ia', 'ia');

                const btnBack = document.getElementById('btn-back-ia');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('ia').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }
            }

            function handleIaDragStart(e) {
                draggedIaCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handleIaDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#kanban-ia .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                saveIaKanbanData();
            }

            function handleIaDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handleIaDragLeave(e) {
                if (e.target === this) {
                    this.classList.remove('drag-over');
                }
            }

            function handleIaDrop(e, container) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                container.classList.remove('drag-over');

                if (draggedIaCard && draggedIaCard.parentNode !== container) {
                    container.appendChild(draggedIaCard);
                    updateColumnCounts();
                    saveIaKanbanData();
                }
                return false;
            }

            function openAddIaCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title-ia">Título do Card</label>
                                <input type="text" id="card-title-ia" placeholder="Ex: Algoritmo de Predição" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description-ia">Descrição</label>
                                <textarea id="card-description-ia" placeholder="Detalhes do projeto de IA (modelo, dataset, tecnologia, etc.)" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority-ia">Prioridade</label>
                                <select id="card-priority-ia">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="card-responsible-ia">Responsável</label>
                                <input type="text" id="card-responsible-ia" placeholder="Nome do responsável">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card-ia">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card-ia">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card-ia');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card-ia');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title-ia').value.trim();
                    const description = modal.querySelector('#card-description-ia').value.trim();
                    const priority = modal.querySelector('#card-priority-ia').value;
                    const responsible = modal.querySelector('#card-responsible-ia').value.trim();

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ${responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${responsible}</div></div>` : ''}
                    `;

                    newCard.addEventListener('dragstart', handleIaDragStart);
                    newCard.addEventListener('dragend', handleIaDragEnd);

                    newCard.querySelector('.btn-card-delete').addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            saveIaKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    saveIaKanbanData();
                    modal.remove();
                });
            }

            function saveIaKanbanData() {
                const kanbanBoard = document.getElementById('kanban-ia');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium',
                        responsible: card.querySelector('.card-meta-item')?.textContent.replace(/\s+/g, ' ').trim().substring(1) || ''
                    }));
                });

                localStorage.setItem('iaKanbanData', JSON.stringify(data));
            }

            function loadIaKanbanData() {
                const data = localStorage.getItem('iaKanbanData');
                if (!data) return;

                const kanbanData = JSON.parse(data);
                const kanbanBoard = document.getElementById('kanban-ia');

                Object.keys(kanbanData).forEach(columnTitle => {
                    const column = kanbanBoard.querySelector(`[data-column-title="${columnTitle}"]`);
                    if (!column) return;

                    const container = column.querySelector('.kanban-cards');
                    kanbanData[columnTitle].forEach(cardData => {
                        const card = document.createElement('div');
                        card.className = `kanban-card ${cardData.priority}`;
                        card.draggable = true;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div style="flex: 1;">
                                    <div class="card-title">${cardData.title}</div>
                                    ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                </div>
                                <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ${cardData.responsible ? `<div class="card-meta"><div class="card-meta-item"><i class="fas fa-user"></i> ${cardData.responsible}</div></div>` : ''}
                        `;

                        card.addEventListener('dragstart', handleIaDragStart);
                        card.addEventListener('dragend', handleIaDragEnd);

                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm('Excluir este card?')) {
                                card.remove();
                                updateColumnCounts();
                                saveIaKanbanData();
                            }
                        });

                        container.appendChild(card);
                    });
                });
            }

            // Função para atualizar contadores
            function updateColumnCounts() {
                document.querySelectorAll('.kanban-column').forEach(column => {
                    const count = column.querySelectorAll('.kanban-card').length;
                    const countElement = column.querySelector('.kanban-column-count');
                    if (countElement) {
                        countElement.textContent = count;
                    }
                });
            }

            // Drag and Drop para os cards Kanban
            let draggedCard = null;

            function attachCardDnD(card) {
                card.addEventListener('dragstart', function() {
                    draggedCard = this;
                    this.classList.add('dragging');
                });

                card.addEventListener('dragend', function() {
                    this.classList.remove('dragging');
                    draggedCard = null;
                });
            }

            function attachColumnDnD(column) {
                column.addEventListener('dragover', function(e) {
                    e.preventDefault();
                });

                column.addEventListener('drop', function(e) {
                    e.preventDefault();
                    if (draggedCard) {
                        this.appendChild(draggedCard);
                        updateColumnCounts();
                    }
                });
            }

            document.querySelectorAll('.kanban-card').forEach(attachCardDnD);
            document.querySelectorAll('.kanban-cards').forEach(attachColumnDnD);

            // Adicionar interatividade aos botões: handlers específicos são registrados por cada kanban (Comercial, Área Médica, Financeiro, Judicial, Importação, IA, Painel)
            // Aqui não registramos um handler genérico para evitar sobrescrever handlers específicos.

            // Incluir e excluir colunas
            const addColumnButton = document.getElementById('btn-add-column');
            const removeColumnButton = document.getElementById('btn-remove-column');
            const kanbanBoard = document.querySelector('.kanban-board');

            function normalizeTitle(title) {
                return title.trim().toLowerCase();
            }

            function toTitleCase(text) {
                return text
                    .trim()
                    .toLowerCase()
                    .split(/\s+/)
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            }

            function createColumn(title) {
                const column = document.createElement('div');
                column.className = 'kanban-column';
                column.setAttribute('data-column-title', title);

                column.innerHTML = `
                    <div class="kanban-column-header">
                        <div class="kanban-column-title">
                            🗂️ ${title}
                            <span class="kanban-column-count">0</span>
                        </div>
                        <div class="kanban-column-actions">
                            <button class="btn-column-action"><i class="fas fa-ellipsis-h"></i></button>
                        </div>
                    </div>
                    <div class="kanban-cards"></div>
                    <button class="btn-add-card"><i class="fas fa-plus"></i> Adicionar card</button>
                `;

                const cardsContainer = column.querySelector('.kanban-cards');
                attachColumnDnD(cardsContainer);

                // Não registrar handler de adicionar card aqui — cada kanban específico registra seu próprio handler.

                return column;
            }

            if (addColumnButton) {
                addColumnButton.addEventListener('click', function() {
                    const title = prompt('Nome da nova coluna:');
                    if (!title || !title.trim()) {
                        return;
                    }

                    const formattedTitle = toTitleCase(title);
                    const normalized = normalizeTitle(formattedTitle);
                    const exists = Array.from(document.querySelectorAll('.kanban-column'))
                        .some(col => normalizeTitle(col.getAttribute('data-column-title') || col.textContent) === normalized);

                    if (exists) {
                        alert('Já existe uma coluna com esse nome.');
                        return;
                    }

                    const newColumn = createColumn(formattedTitle);
                    kanbanBoard.appendChild(newColumn);

                    // Configurar DnD e botão de adicionar para a nova coluna (comportamento do Painel)
                    const cardsContainer = newColumn.querySelector('.kanban-cards');
                    attachColumnDnD(cardsContainer);
                    const addCardBtnNew = newColumn.querySelector('.btn-add-card');
                    if (addCardBtnNew && newColumn.closest('#painel')) {
                        addCardBtnNew.addEventListener('click', () => openAddPainelCardModal(cardsContainer, newColumn.getAttribute('data-column-title')));
                    }

                    updateColumnCounts();
                });
            }

            if (removeColumnButton) {
                removeColumnButton.addEventListener('click', function() {
                    const title = prompt('Nome da coluna a excluir:');
                    if (!title || !title.trim()) {
                        return;
                    }

                    const normalized = normalizeTitle(title);
                    const columns = Array.from(document.querySelectorAll('.kanban-column'));
                    const columnToRemove = columns.find(col => normalizeTitle(col.getAttribute('data-column-title') || col.textContent) === normalized);

                    if (!columnToRemove) {
                        alert('Coluna não encontrada.');
                        return;
                    }

                    columnToRemove.remove();
                    updateColumnCounts();
                });
            }

            // Column actions menu (rename/delete) via three-dot button
            function closeColumnMenu() {
                const existing = document.querySelector('.column-menu');
                if (existing) existing.remove();
            }

            function openColumnMenu(button, column) {
                closeColumnMenu();
                const rect = button.getBoundingClientRect();
                const menu = document.createElement('div');
                menu.className = 'column-menu';

                const editBtn = document.createElement('button');
                editBtn.type = 'button';
                editBtn.innerText = 'Editar nome da coluna';
                editBtn.addEventListener('click', () => {
                    closeColumnMenu();
                    const current = column.getAttribute('data-column-title') || '';

                    const renameModal = document.createElement('div');
                    renameModal.className = 'modal-overlay';
                    renameModal.innerHTML = `
                        <div class="modal-content" style="max-width:420px;">
                            <div class="modal-header">
                                <h2><i class="fas fa-edit"></i> Renomear Coluna</h2>
                                <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                            </div>
                            <div class="modal-body">
                                <div class="form-group">
                                    <label for="rename-column-input">Nome da coluna</label>
                                    <input id="rename-column-input" type="text" value="${current}">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button class="btn-secondary" id="btn-cancel-rename">Cancelar</button>
                                <button class="btn-primary" id="btn-save-rename"><i class="fas fa-check"></i> Salvar</button>
                            </div>
                        </div>
                    `;

                    document.body.appendChild(renameModal);

                    const closeRename = () => renameModal.remove();
                    renameModal.querySelector('.btn-close-modal').addEventListener('click', closeRename);
                    renameModal.querySelector('#btn-cancel-rename').addEventListener('click', closeRename);

                    renameModal.querySelector('#btn-save-rename').addEventListener('click', () => {
                        const input = renameModal.querySelector('#rename-column-input');
                        const newName = input.value.trim();
                        if (!newName) {
                            alert('Nome inválido.');
                            return;
                        }

                        const formatted = toTitleCase(newName);

                        // prevent duplicate names within the same board
                        const boardSection = column.closest('.page-content');
                        const columnsInBoard = boardSection.querySelectorAll('.kanban-column');
                        const normalized = normalizeTitle(formatted);
                        const duplicate = Array.from(columnsInBoard).some(col => col !== column && normalizeTitle(col.getAttribute('data-column-title') || '') === normalized);
                        if (duplicate) {
                            alert('Já existe uma coluna com esse nome nesta tela. Escolha outro nome.');
                            return;
                        }

                        column.setAttribute('data-column-title', formatted);
                        const titleEl = column.querySelector('.kanban-column-title');
                        const countEl = column.querySelector('.kanban-column-count');
                        if (titleEl) {
                            // reset title content while preserving count badge
                            titleEl.textContent = formatted;
                            if (countEl) titleEl.appendChild(countEl);
                        }

                        updateColumnCounts();

                        // persist depending on the section
                        const sectionId = boardSection ? boardSection.id : '';
                        if (sectionId === 'painel') savePainelKanbanData();
                        else if (sectionId === 'comercial') saveComercialKanbanData();
                        else if (sectionId === 'area-medica') saveAreaMedicaKanbanData();
                        else if (sectionId === 'financeiro') saveFinanceiroKanbanData();
                        else if (sectionId === 'judicial') saveJudicialKanbanData();
                        else if (sectionId === 'importacao') saveImportacaoKanbanData();
                        else if (sectionId === 'ia') saveIaKanbanData();

                        closeRename();
                    });
                });

                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.innerText = 'Excluir coluna';
                deleteBtn.addEventListener('click', () => {
                    if (!confirm('Deseja realmente excluir esta coluna e seus cards?')) {
                        closeColumnMenu();
                        return;
                    }
                    column.remove();
                    updateColumnCounts();

                    const boardSection = column.closest('.page-content');
                    const sectionId = boardSection ? boardSection.id : '';
                    if (sectionId === 'painel') savePainelKanbanData();
                    else if (sectionId === 'comercial') saveComercialKanbanData();
                    else if (sectionId === 'area-medica') saveAreaMedicaKanbanData();
                    else if (sectionId === 'financeiro') saveFinanceiroKanbanData();
                    else if (sectionId === 'judicial') saveJudicialKanbanData();
                    else if (sectionId === 'importacao') saveImportacaoKanbanData();
                    else if (sectionId === 'ia') saveIaKanbanData();

                    closeColumnMenu();
                });

                menu.appendChild(editBtn);
                menu.appendChild(deleteBtn);

                // append menu inside the column header for consistent positioning
                const header = column.querySelector('.kanban-column-header') || column;
                header.style.position = 'relative';
                header.appendChild(menu);

                // position menu relative to header / button
                const menuRect = menu.getBoundingClientRect();
                const headerRect = header.getBoundingClientRect();
                // place menu anchored to the right of the header, below the header area
                let left = rect.right - headerRect.left - menuRect.width;
                if (left < 8) left = rect.left - headerRect.left;
                let top = rect.bottom - headerRect.top + 8;
                // ensure it doesn't overflow header bottom
                if (top + menuRect.height > headerRect.height + 300) top = rect.top - headerRect.top - menuRect.height - 8;
                menu.style.left = `${Math.max(6, left)}px`;
                menu.style.top = `${top}px`;

                // close when clicking elsewhere
                setTimeout(() => {
                    document.addEventListener('click', function onDocClick(e) {
                        if (!menu.contains(e.target) && !button.contains(e.target)) {
                            closeColumnMenu();
                            document.removeEventListener('click', onDocClick);
                        }
                    });
                }, 0);
            }

            // delegate clicks on column action buttons
            document.addEventListener('click', function(e) {
                const btn = e.target.closest('.btn-column-action');
                if (!btn) return;
                e.preventDefault();
                e.stopPropagation();

                const column = btn.closest('.kanban-column');
                if (!column) return;
                openColumnMenu(btn, column);
            });

            // Inicializar Admin Kanban
            initAdminKanban();
            loadAdminModulesOrder();

            // Limpar duplicatas acumuladas no localStorage
            (function cleanupLocalStorageKanbans() {
                ['comercialKanbanData', 'painelKanbanData'].forEach(key => {
                    const raw = localStorage.getItem(key);
                    if (!raw) return;
                    try {
                        const data = JSON.parse(raw);
                        const seenLeadIds = new Set();
                        const seenTitles = new Set();
                        let changed = false;
                        Object.keys(data).forEach(col => {
                            const original = data[col].length;
                            data[col] = data[col].filter(card => {
                                if (card.leadId) {
                                    if (seenLeadIds.has(card.leadId)) return false;
                                    seenLeadIds.add(card.leadId);
                                    return true;
                                }
                                const k = card.title + '|' + col;
                                if (seenTitles.has(k)) return false;
                                seenTitles.add(k);
                                return true;
                            });
                            if (data[col].length !== original) changed = true;
                        });
                        if (changed) localStorage.setItem(key, JSON.stringify(data));
                    } catch(e) {}
                });
            })();

            // Inicializar Painel (principal)
            initPainelKanban();

            // Inicializar Comercial Kanban
            initComercialKanban();
            loadLeadsFromBackend();

            // Inicializar Financeiro Kanban
            initFinanceiroKanban();

            // Inicializar Judicial Kanban
            initJudicialKanban();

            // Inicializar Inteligência Artificial Kanban
            initIaKanban();

            // Inicializar Importação Kanban
            initImportacaoKanban();

            // Inicializar Gestão de Médicos Kanban
            initGestaoMedicosKanban();

            // Layout toggle: vertical/horizontal view (supports multiple buttons on different pages)
            const toggleBtns = document.querySelectorAll('.btn-toggle-view');
            function applyViewMode(mode) {
                const boards = document.querySelectorAll('.kanban-board');
                boards.forEach(b => {
                    if (mode === 'vertical') b.classList.add('vertical-view');
                    else b.classList.remove('vertical-view');
                });
                localStorage.setItem('kanbanViewMode', mode);
                toggleBtns.forEach(tb => {
                    if (tb) tb.innerHTML = mode === 'vertical' ? '<i class="fas fa-arrows-alt-h"></i> Visual Horizontal' : '<i class="fas fa-arrows-alt-v"></i> Visual Empilhado';
                });
            }

            toggleBtns.forEach(tb => {
                tb.addEventListener('click', function() {
                    const current = localStorage.getItem('kanbanViewMode') || 'horizontal';
                    const next = current === 'vertical' ? 'horizontal' : 'vertical';
                    applyViewMode(next);
                });
            });

            // apply saved preference on load; if none, use sensible defaults per page
            (function applyInitialView() {
                const saved = localStorage.getItem('kanbanViewMode');
                if (saved) {
                    applyViewMode(saved);
                    return;
                }

                // determine active page id
                const activePage = document.querySelector('.page-content.active');
                const pageId = activePage ? activePage.id : '';

                // sensible defaults per page
                const defaults = {
                    'painel': 'horizontal',
                    'comercial': 'horizontal',
                    'financeiro': 'horizontal',
                    'area-medica': 'vertical',
                    'judicial': 'vertical',
                    'importacao': 'vertical',
                    'ia': 'vertical',
                    'administrativo': 'horizontal'
                };

                const defaultForPage = defaults[pageId] || (window.innerWidth < 480 ? 'vertical' : 'horizontal');
                applyViewMode(defaultForPage);
            })();

            // Self-test runner: simulate create -> rename -> delete column on the Painel board
            async function runKanbanSelfTest() {
                const results = [];
                try {
                    const painelBoard = document.querySelector('#painel .kanban-board');
                    if (!painelBoard) {
                        results.push({ step: 'find-board', ok: false, msg: 'Painel board not found' });
                        throw new Error('Board not found');
                    }

                    const initialCols = painelBoard.querySelectorAll('.kanban-column').length;
                    results.push({ step: 'initial-column-count', ok: true, count: initialCols });

                    // 1) Create column
                    const testTitle = 'Auto Test Column';
                    const newCol = createColumn(testTitle);
                    painelBoard.appendChild(newCol);
                    updateColumnCounts();
                    results.push({ step: 'create-column', ok: true, msg: `created ${testTitle}` });

                    // 2) Persist current painel state
                    savePainelKanbanData();
                    results.push({ step: 'save-after-create', ok: true });

                    // 3) Rename the newly created column programmatically
                    const created = Array.from(painelBoard.querySelectorAll('.kanban-column')).find(c => (c.getAttribute('data-column-title') || '').includes(testTitle));
                    if (!created) throw new Error('Created column not found');
                    const newName = 'Auto Test Column Renamed';
                    created.setAttribute('data-column-title', newName);
                    const titleEl = created.querySelector('.kanban-column-title');
                    const countEl = created.querySelector('.kanban-column-count');
                    if (titleEl) {
                        titleEl.textContent = newName;
                        if (countEl) titleEl.appendChild(countEl);
                    }
                    updateColumnCounts();
                    savePainelKanbanData();
                    results.push({ step: 'rename-column', ok: true, msg: `renamed to ${newName}` });

                    // 4) Verify localStorage contains the renamed column key (may be empty array)
                    const data = JSON.parse(localStorage.getItem('painelKanbanData') || '{}');
                    const hasRenamedKey = Object.prototype.hasOwnProperty.call(data, newName);
                    results.push({ step: 'verify-storage-rename', ok: !!hasRenamedKey, msg: hasRenamedKey ? 'found' : 'not found' });

                    // 5) Delete the column
                    created.remove();
                    updateColumnCounts();
                    savePainelKanbanData();
                    results.push({ step: 'delete-column', ok: true });

                    // 6) Verify storage no longer contains renamed key
                    const dataAfter = JSON.parse(localStorage.getItem('painelKanbanData') || '{}');
                    const stillHas = Object.prototype.hasOwnProperty.call(dataAfter, newName);
                    results.push({ step: 'verify-storage-delete', ok: !stillHas, msg: stillHas ? 'still present' : 'removed' });

                } catch (err) {
                    results.push({ step: 'error', ok: false, msg: err.message });
                }

                const summary = { timestamp: new Date().toISOString(), results };
                localStorage.setItem('kanbanSelfTestResults', JSON.stringify(summary));
                console.group('Kanban Self Test');
                console.log(summary);
                console.groupEnd();

                // show modal with brief results
                const passed = results.every(r => r.ok);
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:520px;">
                        <div class="modal-header">
                            <h2>${passed ? '<i class="fas fa-check-circle" style="color:green"></i> Teste concluído' : '<i class="fas fa-exclamation-circle" style="color:#d32f2f"></i> Teste com falhas'}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <ul style="list-style: none; padding: 0;">
                                ${results.map(r => `<li style="margin-bottom:8px;">${r.ok ? '[✓]' : '[✗]'} <strong>${r.step}</strong>: ${r.msg || ''}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-primary" id="btn-close-selftest">Fechar</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('#btn-close-selftest').addEventListener('click', () => modal.remove());
            }

            // Run automatically if URL contains runSelfTest=true
            try {
                const params = new URLSearchParams(window.location.search);
                if (params.get('runSelfTest') === 'true') {
                    setTimeout(() => runKanbanSelfTest(), 700);
                }
            } catch (e) {
                // ignore
            }

            // Run a full sweep across multiple modules when runSelfTestAll=true
            async function runKanbanSelfTestForModule(sectionId) {
                const results = [];
                try {
                    const board = document.querySelector(`#${sectionId} .kanban-board`);
                    if (!board) {
                        results.push({ step: 'find-board', ok: false, msg: 'board not found' });
                        return { module: sectionId, results };
                    }

                    const testTitle = 'Auto Test Column';
                    const newCol = createColumn(testTitle);
                    board.appendChild(newCol);
                    updateColumnCounts();
                    results.push({ step: 'create-column', ok: true });

                    // persist via appropriate save function
                    const saveMap = {
                        'painel': savePainelKanbanData,
                        'comercial': saveComercialKanbanData,
                        'area-medica': saveAreaMedicaKanbanData,
                        'financeiro': saveFinanceiroKanbanData,
                        'judicial': saveJudicialKanbanData,
                        'importacao': saveImportacaoKanbanData,
                        'ia': saveIaKanbanData
                    };

                    const saver = saveMap[sectionId];
                    if (saver) { saver(); results.push({ step: 'save-after-create', ok: true }); }

                    // rename
                    const created = Array.from(board.querySelectorAll('.kanban-column')).find(c => (c.getAttribute('data-column-title') || '').includes(testTitle));
                    if (!created) throw new Error('created column not found');
                    const newName = 'Auto Test Column Renamed';
                    created.setAttribute('data-column-title', newName);
                    const titleEl = created.querySelector('.kanban-column-title');
                    const countEl = created.querySelector('.kanban-column-count');
                    if (titleEl) { titleEl.textContent = newName; if (countEl) titleEl.appendChild(countEl); }
                    updateColumnCounts();
                    if (saver) { saver(); }
                    results.push({ step: 'rename-column', ok: true });

                    // verify storage contains renamed key (best-effort)
                    const storageKeyMap = {
                        'painel': 'painelKanbanData',
                        'comercial': 'comercialKanbanData',
                        'area-medica': 'areaMedicaKanbanData',
                        'financeiro': 'financeiroKanbanData',
                        'judicial': 'judicialKanbanData',
                        'importacao': 'importacaoKanbanData',
                        'ia': 'iaKanbanData'
                    };
                    const sk = storageKeyMap[sectionId];
                    if (sk) {
                        const data = JSON.parse(localStorage.getItem(sk) || '{}');
                        const has = Object.prototype.hasOwnProperty.call(data, newName);
                        results.push({ step: 'verify-storage-rename', ok: !!has });
                    }

                    // delete created column
                    created.remove();
                    updateColumnCounts();
                    if (saver) { saver(); }
                    results.push({ step: 'delete-column', ok: true });

                    if (sk) {
                        const dataAfter = JSON.parse(localStorage.getItem(sk) || '{}');
                        const stillHas = Object.prototype.hasOwnProperty.call(dataAfter, newName);
                        results.push({ step: 'verify-storage-delete', ok: !stillHas });
                    }

                } catch (err) {
                    results.push({ step: 'error', ok: false, msg: err.message });
                }
                return { module: sectionId, results };
            }

            async function runKanbanSelfTestAll() {
                const modules = ['painel','comercial','area-medica','financeiro','judicial','importacao','ia'];
                const allResults = [];
                for (const m of modules) {
                    // small delay to let DOM updates settle
                    // eslint-disable-next-line no-await-in-loop
                    await new Promise(r => setTimeout(r, 300));
                    // eslint-disable-next-line no-await-in-loop
                    const res = await runKanbanSelfTestForModule(m);
                    allResults.push(res);
                }

                const summary = { timestamp: new Date().toISOString(), allResults };
                localStorage.setItem('kanbanSelfTestAllResults', JSON.stringify(summary));
                console.group('Kanban Self Test All');
                console.log(summary);
                console.groupEnd();

                // show a combined modal
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                const listHtml = allResults.map(r => `
                    <li style="margin-bottom:8px;"><strong>${r.module}</strong>: ${r.results.every(x=>x.ok) ? '[OK]' : '[ERRO]lhas'}</li>
                `).join('');
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:640px;">
                        <div class="modal-header">
                            <h2>Self Test - Todos os Módulos</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <ul style="list-style:none;padding:0;">${listHtml}</ul>
                            <p style="margin-top:12px;font-size:13px;color:#666">Detalhes salvos em localStorage → <code>kanbanSelfTestAllResults</code></p>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-primary" id="btn-close-selftest-all">Fechar</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('#btn-close-selftest-all').addEventListener('click', () => modal.remove());
            }

            try {
                const paramsAll = new URLSearchParams(window.location.search);
                if (paramsAll.get('runSelfTestAll') === 'true') {
                    setTimeout(() => runKanbanSelfTestAll(), 900);
                }
            } catch (e) {
                // ignore
            }

            // ========== KANBAN GESTÃO DE MÉDICOS ==========
            let draggedGestaoMedicosCard = null;

            function initGestaoMedicosKanban() {
                const kanbanBoard = document.getElementById('kanban-gestao-medicos');
                if (!kanbanBoard) return;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const cards = kanbanBoard.querySelectorAll('.kanban-card');

                cards.forEach(card => {
                    card.addEventListener('dragstart', handleGestaoMedicosDragStart);
                    card.addEventListener('dragend', handleGestaoMedicosDragEnd);
                });

                columns.forEach(column => {
                    const cardsContainer = column.querySelector('.kanban-cards');
                    cardsContainer.addEventListener('dragover', handleGestaoMedicosDragOver);
                    cardsContainer.addEventListener('drop', (e) => handleGestaoMedicosDrop(e, cardsContainer));
                    cardsContainer.addEventListener('dragleave', handleGestaoMedicosDragLeave);

                    const addCardBtn = column.querySelector('.btn-add-card');
                    if (addCardBtn) {
                        addCardBtn.addEventListener('click', () => openAddGestaoMedicosCardModal(cardsContainer, column.getAttribute('data-column-title')));
                    }
                });

                loadGestaoMedicosKanbanData();
                loadDoctorsIntoGestaoKanban();
                updateColumnCounts();
                setupColumnReordering('kanban-gestao-medicos', 'gestao-medicos');

                const btnBack = document.getElementById('btn-back-gestao-medicos');
                if (btnBack) {
                    btnBack.addEventListener('click', () => {
                        document.getElementById('gestao-medicos').classList.remove('active');
                        document.getElementById('administrativo').classList.add('active');
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                }

                // Botão Cadastrar Médico dentro da seção
                const btnAddDoctor = document.getElementById('btn-add-doctor-gestao');
                if (btnAddDoctor) {
                    btnAddDoctor.addEventListener('click', () => openDoctorRegistrationForm());
                }

                // Botão Gerenciar Médicos - abre lista de médicos cadastrados
                const btnManage = document.getElementById('btn-manage-doctors');
                if (btnManage) {
                    btnManage.addEventListener('click', () => openAdminDoctorsList());
                }
            }

            function handleGestaoMedicosDragStart(e) {
                draggedGestaoMedicosCard = this;
                this.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }

            function handleGestaoMedicosDragEnd(e) {
                this.classList.remove('dragging');
                document.querySelectorAll('#kanban-gestao-medicos .kanban-cards').forEach(container => {
                    container.classList.remove('drag-over');
                });
                saveGestaoMedicosKanbanData();
            }

            function handleGestaoMedicosDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                return false;
            }

            function handleGestaoMedicosDragLeave(e) {
                if (e.target === this) {
                    this.classList.remove('drag-over');
                }
            }

            function handleGestaoMedicosDrop(e, container) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                container.classList.remove('drag-over');

                if (draggedGestaoMedicosCard && draggedGestaoMedicosCard.parentNode !== container) {
                    container.appendChild(draggedGestaoMedicosCard);
                    updateColumnCounts();
                    saveGestaoMedicosKanbanData();
                }
                return false;
            }

            function openAddGestaoMedicosCardModal(container, columnTitle) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Adicionar Card - ${columnTitle}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="card-title-gestao">Título/Médico</label>
                                <input type="text" id="card-title-gestao" placeholder="Nome do médico ou descrição" required>
                            </div>
                            <div class="form-group">
                                <label for="card-description-gestao">Anotações/Status</label>
                                <textarea id="card-description-gestao" placeholder="Detalhes do acompanhamento" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="card-priority-gestao">Prioridade</label>
                                <select id="card-priority-gestao">
                                    <option value="priority-low">Baixa</option>
                                    <option value="priority-medium" selected>Média</option>
                                    <option value="priority-high">Alta</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-card-gestao">Cancelar</button>
                            <button class="btn-primary" id="btn-save-card-gestao">Adicionar Card</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                const cancelBtn = modal.querySelector('#btn-cancel-card-gestao');
                closeBtn.addEventListener('click', () => modal.remove());
                cancelBtn.addEventListener('click', () => modal.remove());

                const saveBtn = modal.querySelector('#btn-save-card-gestao');
                saveBtn.addEventListener('click', () => {
                    const title = modal.querySelector('#card-title-gestao').value.trim();
                    const description = modal.querySelector('#card-description-gestao').value.trim();
                    const priority = modal.querySelector('#card-priority-gestao').value;

                    if (!title) {
                        alert('Título é obrigatório.');
                        return;
                    }

                    const newCard = document.createElement('div');
                    newCard.className = `kanban-card ${priority}`;
                    newCard.draggable = true;
                    newCard.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <div class="card-title">${title}</div>
                                ${description ? `<div class="card-description">${description}</div>` : ''}
                            </div>
                            <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;

                    newCard.addEventListener('dragstart', handleGestaoMedicosDragStart);
                    newCard.addEventListener('dragend', handleGestaoMedicosDragEnd);

                    newCard.querySelector('.btn-card-delete').addEventListener('click', () => {
                        if (confirm('Excluir este card?')) {
                            newCard.remove();
                            updateColumnCounts();
                            saveGestaoMedicosKanbanData();
                        }
                    });

                    container.appendChild(newCard);
                    updateColumnCounts();
                    saveGestaoMedicosKanbanData();
                    modal.remove();
                });
            }

            function saveGestaoMedicosKanbanData() {
                const kanbanBoard = document.getElementById('kanban-gestao-medicos');
                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                const data = {};

                columns.forEach(column => {
                    const columnTitle = column.getAttribute('data-column-title');
                    const cards = column.querySelectorAll('.kanban-card');
                    data[columnTitle] = Array.from(cards).map(card => ({
                        title: card.querySelector('.card-title').textContent,
                        description: card.querySelector('.card-description')?.textContent || '',
                        priority: Array.from(card.classList).find(c => c.startsWith('priority-')) || 'priority-medium'
                    }));
                });

                localStorage.setItem('gestaoMedicosKanbanData', JSON.stringify(data));
            }

            function loadGestaoMedicosKanbanData() {
                const data = localStorage.getItem('gestaoMedicosKanbanData');
                if (!data) return;

                try {
                    const parsed = JSON.parse(data);
                    Object.keys(parsed).forEach(columnTitle => {
                        const column = Array.from(document.querySelectorAll('#kanban-gestao-medicos .kanban-column')).find(col => (col.getAttribute('data-column-title')||'') === columnTitle);
                        if (!column) return;
                        const container = column.querySelector('.kanban-cards');
                        parsed[columnTitle].forEach(cardData => {
                            const card = document.createElement('div');
                            card.className = `kanban-card ${cardData.priority}`;
                            card.draggable = true;
                            card.innerHTML = `
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                    <div style="flex: 1;">
                                        <div class="card-title">${cardData.title}</div>
                                        ${cardData.description ? `<div class="card-description">${cardData.description}</div>` : ''}
                                    </div>
                                    <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            `;
                            card.addEventListener('dragstart', handleGestaoMedicosDragStart);
                            card.addEventListener('dragend', handleGestaoMedicosDragEnd);
                            card.querySelector('.btn-card-delete').addEventListener('click', () => {
                                if (confirm('Excluir este card?')) {
                                    card.remove();
                                    updateColumnCounts();
                                    saveGestaoMedicosKanbanData();
                                }
                            });
                            container.appendChild(card);
                        });
                    });
                    updateColumnCounts();
                } catch (e) {
                    // ignore
                }
            }

            // ---------- Load doctors from API into gestao-medicos kanban ----------
            function loadDoctorsIntoGestaoKanban() {
                fetchDoctorsFromServerOrLocal().then(doctors => {
                    if (!doctors || !doctors.length) return;
                    const kanbanBoard = document.getElementById('kanban-gestao-medicos');
                    if (!kanbanBoard) return;

                    doctors.forEach(doc => {
                        // Check if card already exists
                        const existing = kanbanBoard.querySelector(`.kanban-card[data-doctor-id="${doc.id}"]`);
                        if (existing) return;

                        // Determine which column based on status (default: Novo)
                        const status = (doc.status || 'Novo');
                        let column = Array.from(kanbanBoard.querySelectorAll('.kanban-column')).find(col => 
                            (col.getAttribute('data-column-title') || '').toLowerCase() === status.toLowerCase()
                        );
                        if (!column) {
                            column = kanbanBoard.querySelector('.kanban-column[data-column-title="Novo"]');
                        }
                        if (!column) return;

                        const container = column.querySelector('.kanban-cards');
                        const card = document.createElement('div');
                        card.className = 'kanban-card priority-medium';
                        card.draggable = true;
                        card.setAttribute('data-doctor-id', doc.id);
                        card.innerHTML = `
                            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                                <div style="flex:1;">
                                    <div class="card-title">${doc.name}</div>
                                    <div class="card-description">
                                        <small>CRM: ${doc.crm || 'N/A'} | ${doc.specialty || 'N/A'}</small><br>
                                        <small>${doc.email || ''}</small>
                                    </div>
                                </div>
                                <div style="display:flex;gap:4px;">
                                    <button class="btn-card-edit" title="Editar" style="background:#0E4D42;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:12px;"><i class="fas fa-edit"></i></button>
                                    <button class="btn-card-delete" title="Excluir" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:12px;"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        `;
                        card.addEventListener('dragstart', handleGestaoMedicosDragStart);
                        card.addEventListener('dragend', handleGestaoMedicosDragEnd);
                        card.querySelector('.btn-card-delete').addEventListener('click', () => {
                            if (confirm(`Excluir médico ${doc.name}?`)) {
                                fetch('/api/doctors/' + doc.id, { method: 'DELETE' }).catch(() => {});
                                card.remove();
                                updateColumnCounts();
                            }
                        });
                        card.querySelector('.btn-card-edit').addEventListener('click', () => {
                            openEditDoctorModal(doc, () => {
                                // Refresh the kanban
                                const allCards = kanbanBoard.querySelectorAll('.kanban-card[data-doctor-id]');
                                allCards.forEach(c => c.remove());
                                loadDoctorsIntoGestaoKanban();
                                updateColumnCounts();
                            });
                        });
                        container.appendChild(card);
                    });
                    updateColumnCounts();
                }).catch(() => {});
            }

            // ---------- Create card in gestao-medicos kanban for a new doctor ----------
            function createGestaoMedicosCard(doctor) {
                const kanbanBoard = document.getElementById('kanban-gestao-medicos');
                if (!kanbanBoard) return;
                const column = kanbanBoard.querySelector('.kanban-column[data-column-title="Novo"]');
                if (!column) return;
                const container = column.querySelector('.kanban-cards');
                // avoid duplicate
                const existing = kanbanBoard.querySelector(`.kanban-card[data-doctor-id="${doctor.id}"]`);
                if (existing) return;

                const card = document.createElement('div');
                card.className = 'kanban-card priority-medium';
                card.draggable = true;
                card.setAttribute('data-doctor-id', doctor.id);
                card.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                        <div style="flex:1;">
                            <div class="card-title">${doctor.name}</div>
                            <div class="card-description">
                                <small>CRM: ${doctor.crm || 'N/A'} | ${doctor.specialty || 'N/A'}</small><br>
                                <small>${doctor.email || ''}</small>
                            </div>
                        </div>
                        <div style="display:flex;gap:4px;">
                            <button class="btn-card-edit" title="Editar" style="background:#0E4D42;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:12px;"><i class="fas fa-edit"></i></button>
                            <button class="btn-card-delete" title="Excluir" style="background:#D81B60;color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:12px;"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                `;
                card.addEventListener('dragstart', handleGestaoMedicosDragStart);
                card.addEventListener('dragend', handleGestaoMedicosDragEnd);
                card.querySelector('.btn-card-delete').addEventListener('click', () => {
                    if (confirm(`Excluir médico ${doctor.name}?`)) {
                        fetch('/api/doctors/' + doctor.id, { method: 'DELETE' }).catch(() => {});
                        card.remove();
                        updateColumnCounts();
                    }
                });
                container.appendChild(card);
                updateColumnCounts();
            }

            // ---------- Doctor registration form (public link) ----------
            function openDoctorRegistrationForm(prefill = {}) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:760px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-user-md"></i> Cadastro Médico - Trabalhe Conosco</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <form id="doctor-registration-form">
                                <h3>Passo 1: Identificação Profissional</h3>
                                <div class="form-group"><label>Nome Completo</label><input id="doc-name" required></div>
                                <div class="form-group"><label>CPF</label><input id="doc-cpf"></div>
                                <div class="form-group"><label>CRM</label><input id="doc-crm"></div>
                                <div class="form-group"><label>UF do CRM</label><input id="doc-crm-uf"></div>
                                <div class="form-group"><label>Especialidade(s) Principal</label><input id="doc-specialty"></div>
                                <div class="form-group"><label>Número do RQE</label><input id="doc-rqe"></div>

                                <h3>Passo 2: Perfil na Plataforma</h3>
                                <div class="form-group"><label>Foto de Perfil Profissional</label><input id="doc-photo" type="file" accept="image/*"><small style="color:#888;display:block;margin-top:4px;">Envie uma foto nitida, com boa iluminacao e fundo neutro.</small></div>
                                <div class="form-group"><label>Breve Biografia (Mini-curriculo)</label><textarea id="doc-bio" rows="3" placeholder="Descreva sua formacao, experiencia e foco de atuacao..."></textarea></div>
                                <div class="form-group"><label>E-mail de Acesso (este sera seu login)</label><input id="doc-email" type="email" required></div>
                                <div class="form-group"><label>Senha de Acesso</label><input id="doc-password" type="password" required minlength="8" placeholder="Minimo 8 caracteres, maiuscula, minuscula e numero"></div>
                                <div class="form-group"><label>Confirmar Senha</label><input id="doc-password-confirm" type="password" required minlength="8"></div>
                                <div class="form-group"><label>Telefone de Contato (WhatsApp)</label><input id="doc-phone"></div>
                                <div class="form-group"><label>Você atuará como</label>
                                    <select id="doc-person-type">
                                        <option value="pf">Pessoa Física</option>
                                        <option value="pj">Pessoa Jurídica</option>
                                    </select>
                                </div>

                                <h3>Passo 3: Dados para Faturamento e Repasses</h3>
                                <div class="form-group"><label>Endereço Completo</label><input id="doc-address"></div>
                                <div class="form-group"><label>Banco</label><input id="doc-bank"></div>
                                <div class="form-group"><label>Agência</label><input id="doc-agency"></div>
                                <div class="form-group"><label>Conta Corrente</label><input id="doc-account"></div>
                                <div class="form-group"><label>Chave PIX (opcional)</label><input id="doc-pix"></div>

                                <div id="pj-section" style="display:none;">
                                    <h4>Dados Pessoa Jurídica</h4>
                                    <div class="form-group"><label>Razão Social</label><input id="doc-company-name"></div>
                                    <div class="form-group"><label>CNPJ</label><input id="doc-cnpj"></div>
                                    <div class="form-group"><label>Endereço da Empresa</label><input id="doc-company-address"></div>
                                    <div class="form-group"><label>Banco (PJ)</label><input id="doc-bank-pj"></div>
                                    <div class="form-group"><label>Agência (PJ)</label><input id="doc-agency-pj"></div>
                                    <div class="form-group"><label>Conta (PJ)</label><input id="doc-account-pj"></div>
                                </div>

                                <h3>Passo 4: Documentos</h3>
                                <div class="form-group"><label>Upload CRM (frente/verso)</label><input id="doc-crm-files" type="file" accept="image/*,application/pdf" multiple></div>

                            </form>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-doctor">Cancelar</button>
                            <button class="btn-primary" id="btn-save-doctor">Salvar Cadastro</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const close = () => modal.remove();
                modal.querySelector('.btn-close-modal').addEventListener('click', close);
                modal.querySelector('#btn-cancel-doctor').addEventListener('click', close);

                // toggle PJ section
                modal.querySelector('#doc-person-type').addEventListener('change', function() {
                    modal.querySelector('#pj-section').style.display = this.value === 'pj' ? 'block' : 'none';
                });

                // handle file uploads: convert to base64 and store temporarily on the form element
                function readFileAsDataURL(file) {
                    return new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onload = () => resolve(reader.result);
                        reader.onerror = reject;
                        reader.readAsDataURL(file);
                    });
                }

                modal.querySelector('#btn-save-doctor').addEventListener('click', async () => {
                    const formEl = modal.querySelector('#doctor-registration-form');
                    const name = formEl.querySelector('#doc-name').value.trim();
                    const email = formEl.querySelector('#doc-email').value.trim();
                    const password = formEl.querySelector('#doc-password').value;
                    const passwordConfirm = formEl.querySelector('#doc-password-confirm').value;
                    if (!name || !email) {
                        alert('Nome e e-mail sao obrigatorios.');
                        return;
                    }
                    if (!password || password.length < 8) {
                        alert('A senha deve ter no minimo 8 caracteres.');
                        return;
                    }
                    if (password !== passwordConfirm) {
                        alert('As senhas nao conferem.');
                        return;
                    }
                    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password)) {
                        alert('A senha deve conter maiuscula, minuscula e numero.');
                        return;
                    }

                    // collect data
                    const doctor = {
                        name,
                        cpf: formEl.querySelector('#doc-cpf').value.trim(),
                        crm: formEl.querySelector('#doc-crm').value.trim(),
                        crm_uf: formEl.querySelector('#doc-crm-uf').value.trim(),
                        specialty: formEl.querySelector('#doc-specialty').value.trim(),
                        rqe: formEl.querySelector('#doc-rqe').value.trim(),
                        bio: formEl.querySelector('#doc-bio').value.trim(),
                        email,
                        phone: formEl.querySelector('#doc-phone').value.trim(),
                        person_type: formEl.querySelector('#doc-person-type').value,
                        address: formEl.querySelector('#doc-address').value.trim(),
                        bank: formEl.querySelector('#doc-bank').value.trim(),
                        agency: formEl.querySelector('#doc-agency').value.trim(),
                        account: formEl.querySelector('#doc-account').value.trim(),
                        pix: formEl.querySelector('#doc-pix').value.trim(),
                        company_name: formEl.querySelector('#doc-company-name').value.trim(),
                        cnpj: formEl.querySelector('#doc-cnpj').value.trim(),
                        company_address: formEl.querySelector('#doc-company-address').value.trim(),
                        created_at: new Date().toISOString()
                    };

                    // collect files
                    const photoInput = formEl.querySelector('#doc-photo');
                    const crmFiles = formEl.querySelector('#doc-crm-files');

                    // Try server API first
                    let serverDoctor = null;
                    try {
                        const formData = new FormData();
                        formData.append('name', doctor.name);
                        formData.append('email', doctor.email);
                        formData.append('cpf', doctor.cpf);
                        formData.append('crm', doctor.crm);
                        formData.append('crm_uf', doctor.crm_uf);
                        formData.append('specialty', doctor.specialty);
                        formData.append('rqe', doctor.rqe);
                        formData.append('bio', doctor.bio);
                        formData.append('phone', doctor.phone);
                        formData.append('password', password);
                        formData.append('person_type', doctor.person_type);
                        formData.append('address', doctor.address);
                        formData.append('bank', doctor.bank);
                        formData.append('agency', doctor.agency);
                        formData.append('account', doctor.account);
                        formData.append('pix', doctor.pix);
                        formData.append('company_name', doctor.company_name);
                        formData.append('cnpj', doctor.cnpj);
                        formData.append('company_address', doctor.company_address);

                        if (photoInput && photoInput.files && photoInput.files[0]) formData.append('photo', photoInput.files[0]);
                        if (crmFiles && crmFiles.files && crmFiles.files.length) {
                            for (let i=0;i<crmFiles.files.length;i++) formData.append('crm_files', crmFiles.files[i]);
                        }

                        const res = await fetch('/api/doctors', { method: 'POST', body: formData });
                        if (res.ok) {
                            serverDoctor = await res.json();
                        }
                    } catch (e) {
                        // server may be unavailable - fallback to localStorage
                        serverDoctor = null;
                    }

                    if (serverDoctor) {
                        // server persisted - create cards in both kanbans
                        createGestaoMedicosCard(serverDoctor);
                        createFinanceiroMedicosCard(serverDoctor);
                        ensureMedicoFormLink();
                        alert(`Cadastro realizado com sucesso!\n\nMédico: ${serverDoctor.name}\nID: ${serverDoctor.id}`);
                        close();
                        return;
                    }

                    // Fallback: convert files to base64 and save locally
                    if (photoInput && photoInput.files && photoInput.files[0]) {
                        try { doctor.photo = await readFileAsDataURL(photoInput.files[0]); } catch(e) { doctor.photo = null; }
                    }
                    doctor.crm_docs = [];
                    if (crmFiles && crmFiles.files && crmFiles.files.length) {
                        for (let i=0;i<crmFiles.files.length;i++) {
                            try { // eslint-disable-next-line no-await-in-loop
                                const dataUrl = await readFileAsDataURL(crmFiles.files[i]);
                                doctor.crm_docs.push({ name: crmFiles.files[i].name, data: dataUrl });
                            } catch (e) {}
                        }
                    }

                    // assign id and save to localStorage
                    doctor.id = 'med-' + Date.now();
                    const saved = JSON.parse(localStorage.getItem('medicos') || '[]');
                    saved.push(doctor);
                    localStorage.setItem('medicos', JSON.stringify(saved));

                    createGestaoMedicosCard(doctor);
                    createFinanceiroMedicosCard(doctor);
                    ensureMedicoFormLink();
                    alert(`Cadastro salvo com sucesso!\n\nMédico: ${doctor.name}\nID: ${doctor.id}`);
                    close();
                });
            }

            function ensureMedicoFormLink() {
                // add the form link into the IA admin-card list as 'Formulario Medico Trabalhe conosco' (idempotent)
                const adminBoard = document.querySelector('.admin-kanban-board');
                const iaCard = adminBoard.querySelector('.admin-card[data-module="ia"]');
                if (!iaCard) return;

                const list = iaCard.querySelector('.admin-list');
                const linkText = 'Formulario Medico Trabalhe conosco';
                const existing = Array.from(list.querySelectorAll('li')).find(li => li.textContent.includes(linkText));
                const formUrl = BASE_URL + '/?registerMedico=true';
                if (!existing) {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-check-circle"></i> <a href="${formUrl}" target="_blank">${linkText}</a>`;
                    list.appendChild(li);
                    saveAdminModulesData();
                } else {
                    // update link if needed
                    const a = existing.querySelector('a');
                    if (a) a.href = formUrl;
                }
            }

            function ensurePacienteFormLink() {
                // add the patient form link into the IA section (idempotent)
                const iaSection = document.getElementById('ia');
                if (!iaSection) return;

                // Find the kanban board
                const kanbanBoard = iaSection.querySelector('.kanban-board');
                if (!kanbanBoard) return;

                // Find or create a card for patient forms
                const formUrl = BASE_URL + '/?registerPaciente=true';

                // Try to find existing card
                let formCard = Array.from(kanbanBoard.querySelectorAll('.kanban-card')).find(
                    card => card.textContent.includes('Formulário Paciente')
                );

                if (!formCard) {
                    // Create a new card in the first column (Desenvolvimento)
                    const firstColumn = kanbanBoard.querySelector('.kanban-column');
                    if (!firstColumn) return;

                    const cardsContainer = firstColumn.querySelector('.kanban-cards');
                    const newCard = document.createElement('div');
                    newCard.className = 'kanban-card priority-high';
                    newCard.style.background = '#f0f4f8';
                    newCard.style.borderLeft = '4px solid #0E4D42';
                    newCard.innerHTML = `
                        <div style="display:flex;justify-content:space-between;align-items:start;">
                            <div style="flex:1;">
                                <div class="card-title">Formulário Paciente</div>
                                <div class="card-description" style="margin-top:8px;"><strong>Link de Acesso:</strong><br><a href="${formUrl}" target="_blank" style="color:#0E4D42;text-decoration:underline;font-weight:bold;">Clique aqui para acessar o formulário</a></div>
                            </div>
                        </div>
                    `;
                    cardsContainer.appendChild(newCard);
                }
            }

            // Call ensurePacienteFormLink when patient registration is completed
            function callEnsurePacienteFormLink() {
                try {
                    ensurePacienteFormLink();
                } catch (e) {
                    console.log('IA section not yet available');
                }
            }

            // ---------- Admin list + edit UI for registered doctors ----------
            function fetchDoctorsFromServerOrLocal() {
                return fetch('/api/doctors').then(r => { if (r.ok) return r.json(); throw new Error('server'); }).catch(()=> {
                    return JSON.parse(localStorage.getItem('medicos') || '[]');
                });
            }

            function openAdminDoctorsList() {
                fetchDoctorsFromServerOrLocal().then(doctors => {
                    const modal = document.createElement('div');
                    modal.className = 'modal-overlay';
                    modal.innerHTML = `
                        <div class="modal-content" style="max-width:900px;">
                            <div class="modal-header"><h2>Gerenciar Médicos Cadastrados</h2><button class="btn-close-modal"><i class="fas fa-times"></i></button></div>
                            <div class="modal-body"><div id="admin-doctors-list" style="max-height:60vh;overflow:auto;"></div></div>
                            <div class="modal-footer"><button class="btn-secondary btn-close">Fechar</button></div>
                        </div>
                    `;
                    document.body.appendChild(modal);
                    modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                    modal.querySelector('.btn-close').addEventListener('click', () => modal.remove());

                    const list = modal.querySelector('#admin-doctors-list');
                    if (!doctors || !doctors.length) {
                        list.innerHTML = '<p>Nenhum médico cadastrado.</p>';
                        return;
                    }

                    doctors.forEach(doc => {
                        const row = document.createElement('div');
                        row.style.display = 'flex'; row.style.justifyContent = 'space-between'; row.style.alignItems = 'center'; row.style.padding = '8px 0'; row.style.borderBottom = '1px solid #eee';
                        row.innerHTML = `<div><strong>${doc.name}</strong><div style="font-size:12px;color:#666">${doc.email || ''} • ${doc.crm || ''}</div></div>`;
                        const actions = document.createElement('div');
                        const btnEdit = document.createElement('button'); btnEdit.className='btn-secondary'; btnEdit.textContent='Editar';
                        const btnRecreate = document.createElement('button'); btnRecreate.className='btn-primary'; btnRecreate.style.marginLeft='8px'; btnRecreate.textContent='Recriar Card';
                        actions.appendChild(btnEdit); actions.appendChild(btnRecreate); row.appendChild(actions);

                        btnEdit.addEventListener('click', () => { openEditDoctorModal(doc, () => { modal.remove(); openAdminDoctorsList(); }); });
                        btnRecreate.addEventListener('click', () => { createFinanceiroMedicosCard(doc); alert('Card (re)criado para ' + doc.name); });

                        list.appendChild(row);
                    });
                }).catch(e => console.error(e));
            }

            function openEditDoctorModal(doctor, onSaved) {
                const cert = doctor.certificado_digital || {};
                const certStatus = cert.status || 'pendente';
                const certBadge = certStatus === 'vinculado' || certStatus === 'vinculado_simulado'
                    ? '<span style="color:#059669;font-weight:600;"><i class="fas fa-check-circle"></i> Vinculado</span>'
                    : '<span style="color:#f59e0b;font-weight:600;"><i class="fas fa-exclamation-circle"></i> Pendente</span>';

                const modal = document.createElement('div');
                modal.className='modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:760px;">
                        <div class="modal-header"><h2>Editar Médico</h2><button class="btn-close-modal"><i class="fas fa-times"></i></button></div>
                        <div class="modal-body" style="max-height:70vh;overflow-y:auto;">
                            <form id="edit-doctor-form">
                                <div class="form-group"><label>Nome Completo</label><input id="edit-doc-name" value="${doctor.name || ''}"></div>
                                <div class="form-group"><label>E-mail</label><input id="edit-doc-email" value="${doctor.email || ''}"></div>
                                <div class="form-group"><label>CRM</label><input id="edit-doc-crm" value="${doctor.crm || ''}"></div>
                                <div class="form-group"><label>Especialidade</label><input id="edit-doc-specialty" value="${doctor.specialty || ''}"></div>
                                <div class="form-group"><label>Telefone</label><input id="edit-doc-phone" value="${doctor.phone || ''}"></div>
                                <div class="form-group"><label>Foto de Perfil (substituir)</label><input id="edit-doc-photo" type="file" accept="image/*"></div>

                                <!-- Certificado Digital -->
                                <div style="margin-top:20px;padding:16px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;">
                                    <h4 style="margin:0 0 12px;color:#166534;font-size:14px;"><i class="fas fa-certificate" style="margin-right:6px;"></i> Certificado Digital ICP-Brasil &nbsp;${certBadge}</h4>
                                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                                        <div class="form-group" style="margin:0;">
                                            <label style="font-size:12px;">CPF do Médico (somente números)</label>
                                            <input id="edit-doc-cpf" value="${cert.cpf || ''}" placeholder="00000000000" maxlength="11" style="width:100%;padding:8px;border:1px solid #d1d5db;border-radius:6px;">
                                        </div>
                                        <div class="form-group" style="margin:0;">
                                            <label style="font-size:12px;">Provedor Preferido</label>
                                            <select id="edit-doc-provedor" style="width:100%;padding:8px;border:1px solid #d1d5db;border-radius:6px;">
                                                <option value="integraicp" ${cert.provedor_preferido==='integraicp'?'selected':''}>IntegraICP</option>
                                                <option value="vidaas" ${cert.provedor_preferido==='vidaas'?'selected':''}>Vidaas (Valid)</option>
                                                <option value="soluti" ${cert.provedor_preferido==='soluti'?'selected':''}>BirdID (Soluti)</option>
                                            </select>
                                        </div>
                                    </div>
                                    ${cert.certificado_nome ? `
                                    <div style="margin-top:10px;padding:10px;background:#fff;border-radius:6px;font-size:12px;color:#374151;">
                                        <div><strong>Titular:</strong> ${cert.certificado_nome || ''}</div>
                                        <div><strong>Emissor:</strong> ${cert.certificado_emissor || ''}</div>
                                        <div><strong>Validade:</strong> ${cert.certificado_validade || ''}</div>
                                    </div>` : ''}
                                    <div style="margin-top:12px;display:flex;gap:8px;">
                                        <button type="button" id="btn-vincular-cert" style="padding:8px 16px;background:linear-gradient(135deg,#059669,#047857);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;">
                                            <i class="fas fa-link"></i> Vincular Certificado
                                        </button>
                                        <button type="button" id="btn-salvar-cert" style="padding:8px 16px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;">
                                            <i class="fas fa-save"></i> Salvar Dados Certificado
                                        </button>
                                    </div>
                                    <p style="margin:8px 0 0;font-size:11px;color:#6b7280;">O médico precisa ter certificado digital em nuvem (Vidaas, BirdID, etc.) para assinatura ICP-Brasil.</p>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer"><button class="btn-secondary btn-cancel">Cancelar</button><button class="btn-primary btn-save-main">Salvar Médico</button></div>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel').addEventListener('click', () => modal.remove());

                // Vincular certificado via IntegraICP
                modal.querySelector('#btn-vincular-cert').addEventListener('click', async () => {
                    const cpf = modal.querySelector('#edit-doc-cpf').value.replace(/\D/g, '');
                    if (!cpf || cpf.length !== 11) { alert('Informe o CPF do médico (11 dígitos)'); return; }
                    const btn = modal.querySelector('#btn-vincular-cert');
                    btn.disabled = true;
                    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Iniciando...';
                    try {
                        const res = await apiRequest(`/api/doctors/${doctor.id}/certificado/vincular`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ cpf })
                        });
                        if (res.mode === 'integraicp' && res.auth_url) {
                            window.open(res.auth_url, '_blank', 'width=600,height=700');
                            alert('Uma janela foi aberta para autenticação no provedor ICP-Brasil. Após autenticar, o certificado será vinculado automaticamente.');
                        } else {
                            alert(res.message || 'Certificado vinculado (modo simulado)');
                        }
                    } catch(e) { alert('Erro ao vincular: ' + (e.message || e)); }
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-link"></i> Vincular Certificado';
                });

                // Salvar dados do certificado
                modal.querySelector('#btn-salvar-cert').addEventListener('click', async () => {
                    const cpf = modal.querySelector('#edit-doc-cpf').value.replace(/\D/g, '');
                    const provedor = modal.querySelector('#edit-doc-provedor').value;
                    try {
                        await apiRequest(`/api/doctors/${doctor.id}/certificado`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ cpf, provedor_preferido: provedor })
                        });
                        alert('Dados do certificado salvos.');
                    } catch(e) { alert('Erro ao salvar: ' + (e.message || e)); }
                });

                // Salvar dados gerais do médico
                modal.querySelector('.btn-save-main').addEventListener('click', async () => {
                    const form = modal.querySelector('#edit-doctor-form');
                    doctor.name = form.querySelector('#edit-doc-name').value.trim();
                    doctor.email = form.querySelector('#edit-doc-email').value.trim();
                    doctor.crm = form.querySelector('#edit-doc-crm').value.trim();
                    doctor.specialty = form.querySelector('#edit-doc-specialty').value.trim();
                    doctor.phone = form.querySelector('#edit-doc-phone').value.trim();

                    const photoInput = form.querySelector('#edit-doc-photo');
                    if (photoInput && photoInput.files && photoInput.files[0]) {
                        try { doctor.photo = await (new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result);r.onerror=rej;r.readAsDataURL(photoInput.files[0]);})); } catch(e){}
                    }

                    // try server update
                    try {
                        const fd = new FormData();
                        fd.append('name', doctor.name);
                        fd.append('email', doctor.email);
                        fd.append('crm', doctor.crm);
                        fd.append('specialty', doctor.specialty);
                        fd.append('phone', doctor.phone);
                        if (photoInput && photoInput.files && photoInput.files[0]) fd.append('photo', photoInput.files[0]);
                        const res = await fetch('/api/doctors/' + encodeURIComponent(doctor.id), { method: 'PUT', body: fd });
                        if (res.ok) {
                            const saved = await res.json();
                            updateCardForDoctor(saved);
                        } else throw new Error('no-server');
                    } catch (e) {
                        // fallback to localStorage
                        const arr = JSON.parse(localStorage.getItem('medicos')||'[]');
                        const idx = arr.findIndex(d=>d.id===doctor.id);
                        if (idx !== -1) { arr[idx]=doctor; localStorage.setItem('medicos', JSON.stringify(arr)); }
                        updateCardForDoctor(doctor);
                    }

                    alert('Alterações salvas.');
                    modal.remove();
                    if (onSaved) onSaved();
                });
            }

            function createFinanceiroMedicosCard(doctor) {
                // Financeiro agora usa sistema de abas com API - nao precisa de kanban card
                // Medicos sao gerenciados pela secao Gestao de Medicos
            }

            function updateCardForDoctor(doctor) {
                // Financeiro agora usa sistema de abas com API
            }

            // ===== PACIENTE REGISTRATION FORM (4-step form) =====
            function openPatientRegistrationForm(leadId = null, prefill = {}) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:760px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-user-injured"></i> Cadastro de Paciente</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <form id="patient-registration-form">
                                <!-- Step 1: Dados Informativos -->
                                <div class="patient-step" id="step-1">
                                    <h3>Passo 1 de 4: Dados Informativos do Paciente</h3>
                                    <div class="form-group"><label>Nome Completo *</label><input id="patient-name" required></div>
                                    <div class="form-group"><label>CPF *</label><input id="patient-cpf" required></div>
                                    <div class="form-group"><label>Data de Nascimento *</label><input id="patient-dob" type="date" required></div>
                                    <div id="guardian-section" style="display:none;border:1px solid #ddd;padding:12px;border-radius:4px;margin:12px 0;">
                                        <h4>Dados do Responsável (menores de 18 anos)</h4>
                                        <div class="form-group"><label>Nome Completo do Responsável *</label><input id="guardian-name"></div>
                                        <div class="form-group"><label>CPF do Responsável *</label><input id="guardian-cpf"></div>
                                    </div>
                                    <div class="form-group"><label>Telefone (WhatsApp) *</label><input id="patient-phone" required></div>
                                    <div class="form-group"><label>Endereço Completo *</label><textarea id="patient-address" required></textarea></div>
                                    <div class="form-group"><label>E-mail *</label><input id="patient-email" type="email" required></div>
                                </div>

                                <!-- Step 2: Dados Diagnóstico -->
                                <div class="patient-step" id="step-2" style="display:none;">
                                    <h3>Passo 2 de 4: Dados Diagnóstico do Paciente</h3>
                                    <div class="form-group"><label style="font-size: 16px; font-weight: 600;">Peso (kg) *</label><input id="patient-weight" type="number" step="0.1" required></div>
                                    
                                    <div class="form-group" style="margin-top: 20px;">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Condição Principal para Atendimento *</label>
                                        <div style="display:grid;grid-template-columns:1fr;gap:2px;">
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="Autismo"> Autismo</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="TDAH"> TDAH</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="Ansiedade/Depressão"> Ansiedade/Depressão</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="Diabetes/Pré-diabetes"> Diabetes/Pré-diabetes</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="Fibromialgia"> Fibromialgia</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="Epilepsia"> Epilepsia</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="condition-main" value="Outro"> Outro (especificar)</label>
                                        </div>
                                        <input id="patient-condition-main-other" placeholder="Especifique a condição" style="display:none;margin-top:8px;width:100%;padding:8px;border:1px solid #ccc;border-radius:4px;">
                                    </div>

                                    <div class="form-group" style="margin-top: 20px;">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Diagnósticos Prévios *</label>
                                        <div style="display:grid;grid-template-columns:1fr;gap:2px;">
                                            <label style="font-size: 14px;"><input type="checkbox" class="diagnosis-prev" value="Hipertensão"> Hipertensão</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="diagnosis-prev" value="Doenças cardíacas"> Doenças cardíacas</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="diagnosis-prev" value="Câncer"> Câncer</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="diagnosis-prev" value="Distúrbios neurológicos"> Distúrbios neurológicos</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="diagnosis-prev" value="Alergias"> Alergias (especificar)</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="diagnosis-prev" value="Nenhum"> Nenhum</label>
                                        </div>
                                        <input id="patient-diagnosis-allergies" placeholder="Especifique alergias" style="display:none;margin-top:8px;width:100%;padding:8px;border:1px solid #ccc;border-radius:4px;">
                                    </div>

                                    <div class="form-group" style="margin-top: 20px;">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Histórico Familiar Relevante *</label>
                                        <div style="display:grid;grid-template-columns:1fr;gap:2px;">
                                            <label style="font-size: 14px;"><input type="checkbox" class="family-history" value="Doenças genéticas"> Doenças genéticas</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="family-history" value="Diabetes"> Diabetes</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="family-history" value="Alzheimer/Parkinson"> Alzheimer/Parkinson</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="family-history" value="Outro"> Outro (especificar)</label>
                                        </div>
                                        <input id="patient-family-history-other" placeholder="Especifique o histórico" style="display:none;margin-top:8px;width:100%;padding:8px;border:1px solid #ccc;border-radius:4px;">
                                    </div>

                                    <div class="form-group"><label style="font-size: 16px; font-weight: 600;">Medicações em Uso (nome e dosagem)</label><textarea id="patient-medications" rows="3"></textarea></div>
                                    <div class="form-group"><label style="font-size: 16px; font-weight: 600;">Cirurgias Anteriores</label><textarea id="patient-surgeries" rows="3"></textarea></div>
                                </div>

                                <!-- Step 3: Sintomas e Objetivo da Consulta -->
                                <div class="patient-step" id="step-3" style="display:none;">
                                    <h3>Passo 3 de 4: Sintomas e Objetivos</h3>
                                    <div class="form-group"><label style="font-size: 16px; font-weight: 600;">Sintomas Atuais (duração, intensidade, fatores agravantes) *</label><textarea id="patient-symptoms" required rows="4"></textarea></div>

                                    <div class="form-group" style="margin-top: 20px;">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Objetivo da Consulta *</label>
                                        <div style="display:grid;grid-template-columns:1fr;gap:2px;">
                                            <label style="font-size: 14px;"><input type="radio" name="consultation-objective" value="Iniciar tratamento com óleo de cannabis"> Iniciar tratamento com óleo de cannabis</label>
                                            <label style="font-size: 14px;"><input type="radio" name="consultation-objective" value="Exames genéticos"> Exames genéticos</label>
                                            <label style="font-size: 14px;"><input type="radio" name="consultation-objective" value="Ajuste de suplementos"> Ajuste de suplementos</label>
                                            <label style="font-size: 14px;"><input type="radio" name="consultation-objective" value="Segunda opinião médica"> Segunda opinião médica</label>
                                            <label style="font-size: 14px;"><input type="radio" name="consultation-objective" value="Outro"> Outro (especificar)</label>
                                        </div>
                                        <input id="patient-objective-other" placeholder="Especifique o objetivo" style="display:none;margin-top:8px;width:100%;padding:8px;border:1px solid #ccc;border-radius:4px;">
                                    </div>

                                    <div class="form-group" style="margin-top: 20px;">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Exames Recentes (marque os anexados)</label>
                                        <div style="display:grid;grid-template-columns:1fr;gap:2px;">
                                            <label style="font-size: 14px;"><input type="checkbox" class="recent-exams" value="Hemograma completo"> Hemograma completo</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="recent-exams" value="Teste genético"> Teste genético</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="recent-exams" value="Laudo psiquiátrico"> Laudo psiquiátrico</label>
                                            <label style="font-size: 14px;"><input type="checkbox" class="recent-exams" value="Imagens (RM/Tomografia)"> Imagens (RM/Tomografia)</label>
                                        </div>
                                    </div>
                                </div>

                                <!-- Step 4: Hábitos -->
                                <div class="patient-step" id="step-4" style="display:none;">
                                    <h3>Passo 4 de 4: Hábitos</h3>
                                    
                                    <div class="form-group">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Tabagismo *</label>
                                        <div style="display:flex; gap:8px;">
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="tabagismo" value="Sim"> Sim</label>
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="tabagismo" value="Não"> Não</label>
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Consumo de álcool *</label>
                                        <div style="display:flex; gap:8px;">
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="alcool" value="Sim"> Sim</label>
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="alcool" value="Não"> Não</label>
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Atividade física regular *</label>
                                        <div style="display:flex; gap:8px;">
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="atividade_fisica" value="Sim"> Sim</label>
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="atividade_fisica" value="Não"> Não</label>
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label style="font-size: 16px; font-weight: 600; margin-bottom: 12px; display: block;">Dieta específica *</label>
                                        <div style="display:flex; gap:8px; margin-bottom:10px;">
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="dieta" value="Sim" id="dieta-sim"> Sim</label>
                                            <label style="font-size: 14px; display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="radio" name="dieta" value="Não"> Não</label>
                                        </div>
                                        <input id="patient-diet-specific" placeholder="Especifique a dieta" style="display:none;margin-top:8px;width:100%;padding:8px;border:1px solid #ccc;border-radius:4px;">
                                    </div>
                                </div>

                            </form>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-patient">Cancelar</button>
                            <button class="btn-secondary" id="btn-prev-patient" style="display:none;">← Anterior</button>
                            <button class="btn-primary" id="btn-next-patient">Próximo →</button>
                            <button class="btn-primary" id="btn-save-patient" style="display:none;">✓ Finalizar</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const close = () => modal.remove();
                modal.querySelector('.btn-close-modal').addEventListener('click', close);
                modal.querySelector('#btn-cancel-patient').addEventListener('click', close);

                const form = modal.querySelector('#patient-registration-form');
                let currentStep = 1;
                const totalSteps = 4;

                const updateStepDisplay = () => {
                    for (let i = 1; i <= totalSteps; i++) {
                        const step = modal.querySelector(`#step-${i}`);
                        if (step) step.style.display = i === currentStep ? 'block' : 'none';
                    }
                    modal.querySelector('#btn-prev-patient').style.display = currentStep > 1 ? 'inline-block' : 'none';
                    modal.querySelector('#btn-next-patient').style.display = currentStep < totalSteps ? 'inline-block' : 'none';
                    modal.querySelector('#btn-save-patient').style.display = currentStep === totalSteps ? 'inline-block' : 'none';
                };

                // Check age to show guardian section
                const dobInput = modal.querySelector('#patient-dob');
                dobInput.addEventListener('change', function() {
                    const dob = new Date(this.value);
                    const today = new Date();
                    const age = today.getFullYear() - dob.getFullYear();
                    const guardianSection = modal.querySelector('#guardian-section');
                    if (age < 18) {
                        guardianSection.style.display = 'block';
                        guardianSection.querySelectorAll('input[required]').forEach(el => el.required = true);
                    } else {
                        guardianSection.style.display = 'none';
                        guardianSection.querySelectorAll('input[required]').forEach(el => el.required = false);
                    }
                });

                // Handle conditional fields
                const handleConditionalFields = () => {
                    // Condition Main - Other
                    const conditionOther = modal.querySelector('input[value="Outro"].condition-main');
                    if (conditionOther) {
                        conditionOther.addEventListener('change', function() {
                            modal.querySelector('#patient-condition-main-other').style.display = this.checked ? 'block' : 'none';
                        });
                    }

                    // Diagnosis Allergies
                    const diagnosisAllergies = modal.querySelector('input[value="Alergias"].diagnosis-prev');
                    if (diagnosisAllergies) {
                        diagnosisAllergies.addEventListener('change', function() {
                            modal.querySelector('#patient-diagnosis-allergies').style.display = this.checked ? 'block' : 'none';
                        });
                    }

                    // Family History Other
                    const familyOther = modal.querySelector('input[value="Outro"].family-history');
                    if (familyOther) {
                        familyOther.addEventListener('change', function() {
                            modal.querySelector('#patient-family-history-other').style.display = this.checked ? 'block' : 'none';
                        });
                    }

                    // Consultation Objective Other
                    const objectiveOther = modal.querySelector('input[value="Outro"][name="consultation-objective"]');
                    if (objectiveOther) {
                        objectiveOther.addEventListener('change', function() {
                            modal.querySelector('#patient-objective-other').style.display = this.checked ? 'block' : 'none';
                        });
                    }

                    // Diet Specific
                    const dietSimRadios = modal.querySelectorAll('input[name="dieta"]');
                    dietSimRadios.forEach(radio => {
                        radio.addEventListener('change', function() {
                            modal.querySelector('#patient-diet-specific').style.display = this.value === 'Sim' ? 'block' : 'none';
                        });
                    });
                };

                handleConditionalFields();

                modal.querySelector('#btn-next-patient').addEventListener('click', () => {
                    if (currentStep < totalSteps) {
                        currentStep++;
                        updateStepDisplay();
                        modal.querySelector('.modal-body').scrollTop = 0;
                    }
                });

                modal.querySelector('#btn-prev-patient').addEventListener('click', () => {
                    if (currentStep > 1) {
                        currentStep--;
                        updateStepDisplay();
                        modal.querySelector('.modal-body').scrollTop = 0;
                    }
                });

                modal.querySelector('#btn-save-patient').addEventListener('click', async () => {
                    const name = form.querySelector('#patient-name').value.trim();
                    const cpf = form.querySelector('#patient-cpf').value.trim();
                    const email = form.querySelector('#patient-email').value.trim();
                    const phone = form.querySelector('#patient-phone').value.trim();
                    
                    if (!name || !cpf || !email || !phone) {
                        alert('Preencha todos os campos obrigatórios.');
                        return;
                    }

                    const patient = {
                        name,
                        cpf,
                        dob: form.querySelector('#patient-dob').value,
                        guardian_name: form.querySelector('#guardian-name').value.trim() || null,
                        guardian_cpf: form.querySelector('#guardian-cpf').value.trim() || null,
                        phone,
                        address: form.querySelector('#patient-address').value.trim(),
                        email,
                        weight: form.querySelector('#patient-weight').value,
                        condition_main: Array.from(form.querySelectorAll('.condition-main:checked')).map(el => el.value).join(', '),
                        condition_main_other: form.querySelector('#patient-condition-main-other').value.trim(),
                        diagnosis_prev: Array.from(form.querySelectorAll('.diagnosis-prev:checked')).map(el => el.value).join(', '),
                        diagnosis_allergies: form.querySelector('#patient-diagnosis-allergies').value.trim(),
                        family_history: Array.from(form.querySelectorAll('.family-history:checked')).map(el => el.value).join(', '),
                        family_history_other: form.querySelector('#patient-family-history-other').value.trim(),
                        medications: form.querySelector('#patient-medications').value.trim(),
                        surgeries: form.querySelector('#patient-surgeries').value.trim(),
                        symptoms: form.querySelector('#patient-symptoms').value.trim(),
                        consultation_objective: form.querySelector('input[name="consultation-objective"]:checked')?.value || '',
                        consultation_objective_other: form.querySelector('#patient-objective-other').value.trim(),
                        recent_exams: Array.from(form.querySelectorAll('.recent-exams:checked')).map(el => el.value).join(', '),
                        tabagismo: form.querySelector('input[name="tabagismo"]:checked')?.value || '',
                        alcool: form.querySelector('input[name="alcool"]:checked')?.value || '',
                        atividade_fisica: form.querySelector('input[name="atividade_fisica"]:checked')?.value || '',
                        dieta: form.querySelector('input[name="dieta"]:checked')?.value || '',
                        diet_specific: form.querySelector('#patient-diet-specific').value.trim(),
                        created_at: new Date().toISOString()
                    };

                    // Capturar leadId da URL se existir
                    const urlParams = new URLSearchParams(window.location.search);
                    const linkedLeadId = urlParams.get('leadId');
                    if (linkedLeadId) {
                        patient.linked_lead_id = linkedLeadId;
                    }

                    // Try to save via server API
                    try {
                        const res = await fetch('/api/leads', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(patient)
                        });
                        if (res.ok) {
                            const serverPatient = await res.json();
                            callEnsurePacienteFormLink();
                            const msg = linkedLeadId 
                                ? `SUCESSO: Cadastro realizado com sucesso!\n\nID do Paciente: ${serverPatient.id}\nVinculado ao Lead: #${linkedLeadId}`
                                : `SUCESSO: Cadastro de paciente realizado com sucesso!\n\nID do Paciente: ${serverPatient.id}`;
                            alert(msg);
                            close();
                            return;
                        }
                    } catch (e) {
                        console.error('Server error:', e);
                    }

                    // Fallback to localStorage
                    patient.id = 'pac-' + Date.now();
                    const saved = JSON.parse(localStorage.getItem('pacientes') || '[]');
                    saved.push(patient);
                    localStorage.setItem('pacientes', JSON.stringify(saved));
                    callEnsurePacienteFormLink();
                    const msgLocal = linkedLeadId
                        ? `SUCESSO: Cadastro salvo localmente!\n\nID do Paciente: ${patient.id}\nVinculado ao Lead: #${linkedLeadId}`
                        : `SUCESSO: Cadastro salvo localmente!\n\nID do Paciente: ${patient.id}`;
                    alert(msgLocal);
                    close();
                });

                updateStepDisplay();
            }

            // ===== OPEN LEAD DETAILS MODAL =====
            function openLeadDetailsModal(lead) {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                const formUrl = BASE_URL + '/?registerPaciente=true&leadId=' + encodeURIComponent(lead.id);
                
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 600px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-info-circle"></i> Detalhes do Lead #${lead.id}</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <div style="display: grid; gap: 12px;">
                                <div>
                                    <strong>ID do Lead:</strong><br>
                                    <span style="font-size: 18px; color: #0E4D42; font-weight: bold;">${lead.id}</span>
                                </div>
                                <div>
                                    <strong>Responsável:</strong><br>
                                    ${lead.responsible || 'N/A'}
                                </div>
                                <div>
                                    <strong>Fonte:</strong><br>
                                    ${lead.source || 'N/A'}
                                </div>
                                <div style="border-top: 1px solid #ddd; padding-top: 12px; margin-top: 12px;">
                                    <strong>Status:</strong><br>
                                    ${lead.status || 'Entrada de Lead'}
                                </div>
                                <div>
                                    <strong>Data de Criação:</strong><br>
                                    ${new Date(lead.created_at).toLocaleDateString('pt-BR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}
                                </div>
                                <div style="background: #f9f9f9; padding: 12px; border-radius: 4px; margin-top: 12px;">
                                    <strong style="color: #0E4D42;">Link para o Paciente Preencher Formulário:</strong><br>
                                    <div style="margin-top: 8px; word-break: break-all; font-size: 12px; background: white; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                                        <code>${formUrl}</code>
                                    </div>
                                    <button class="btn-primary" id="btn-copy-link" style="margin-top: 8px; width: 100%;">
                                        <i class="fas fa-copy"></i> Copiar Link
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary btn-close-modal">Fechar</button>
                            <a href="${formUrl}" target="_blank" class="btn-primary" style="text-decoration: none;">
                                <i class="fas fa-external-link-alt"></i> Abrir Formulário
                            </a>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const closeBtn = modal.querySelector('.btn-close-modal');
                closeBtn.addEventListener('click', () => modal.remove());

                const copyBtn = modal.querySelector('#btn-copy-link');
                copyBtn.addEventListener('click', () => {
                    navigator.clipboard.writeText(formUrl).then(() => {
                        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copiado!';
                        setTimeout(() => {
                            copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copiar Link';
                        }, 2000);
                    });
                });
            }

            // ===== CREATE LEAD CARD (in Entrada de Lead column) =====
            function openCreateLeadModal() {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 600px;">
                        <div class="modal-header">
                            <h2><i class="fas fa-plus"></i> Novo Lead de Paciente</h2>
                            <button class="btn-close-modal"><i class="fas fa-times"></i></button>
                        </div>
                        <div class="modal-body">
                            <form id="lead-creation-form">
                                <div class="form-group">
                                    <label for="lead-responsible">Responsável pelo Atendimento *</label>
                                    <input type="text" id="lead-responsible" placeholder="Nome do comercial/atendente" required>
                                </div>
                                <div class="form-group">
                                    <label for="lead-source">Como chegou na plataforma? *</label>
                                    <select id="lead-source" required>
                                        <option value="">Selecione...</option>
                                        <option value="Indicação">Indicação</option>
                                        <option value="Tráfego Pago">Tráfego Pago</option>
                                        <option value="Vendedor Externo">Vendedor Externo</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>
                                        <input type="checkbox" id="lead-auto-form"> Gerar link de formulário automático para o paciente preencher
                                    </label>
                                    <div style="font-size:12px;color:#666;margin-top:4px;">
                                        O paciente receberá um link para preencher um formulário detalhado com suas informações de saúde.
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" id="btn-cancel-lead">Cancelar</button>
                            <button class="btn-primary" id="btn-create-lead">Criar Lead</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const close = () => modal.remove();
                modal.querySelector('.btn-close-modal').addEventListener('click', close);
                modal.querySelector('#btn-cancel-lead').addEventListener('click', close);

                modal.querySelector('#btn-create-lead').addEventListener('click', async () => {
                    const responsible = modal.querySelector('#lead-responsible').value.trim();
                    const source = modal.querySelector('#lead-source').value.trim();
                    const autoForm = modal.querySelector('#lead-auto-form').checked;

                    if (!responsible || !source) {
                        alert('Preencha os campos obrigatórios.');
                        return;
                    }

                    // Create lead via API
                    const leadData = {
                        responsible,
                        source,
                        auto_form: autoForm,
                        status: 'Entrada de Lead',
                        created_at: new Date().toISOString()
                    };

                    let lead = null;
                    try {
                        const res = await fetch('/api/leads', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(leadData)
                        });
                        if (res.ok) {
                            lead = await res.json();
                        }
                    } catch (e) {
                        console.error('Server error:', e);
                    }

                    // Fallback to localStorage (get next ID from leads)
                    if (!lead) {
                        const savedLeads = JSON.parse(localStorage.getItem('leads') || '[]');
                        let maxId = 0;
                        for (let l of savedLeads) {
                            try {
                                const idNum = parseInt(l.id);
                                if (!isNaN(idNum) && idNum > maxId) {
                                    maxId = idNum;
                                }
                            } catch (e) {}
                        }
                        const nextId = String(maxId + 1).padStart(2, '0');
                        lead = { ...leadData, id: nextId };
                        savedLeads.push(lead);
                        localStorage.setItem('leads', JSON.stringify(savedLeads));
                    }

                    // Create card in Entrada de Lead column
                    createLeadCard(lead);
                    callEnsurePacienteFormLink();
                    close();
                    alert(`Lead criado com sucesso!\n\nID do Lead: ${lead.id}`);
                });
            }

            function createLeadCard(lead) {
                const kanbanBoard = document.getElementById('kanban-comercial');
                if (!kanbanBoard) return;

                // Find 'Entrada de Lead' column
                const column = Array.from(kanbanBoard.querySelectorAll('.kanban-column')).find(
                    col => (col.getAttribute('data-column-title') || '').toLowerCase() === 'entrada de lead'
                );
                if (!column) return;

                const cardsContainer = column.querySelector('.kanban-cards');
                const formUrl = BASE_URL + '/?registerPaciente=true&leadId=' + encodeURIComponent(lead.id);

                const newCard = document.createElement('div');
                newCard.className = 'kanban-card priority-high';
                newCard.draggable = true;
                newCard.dataset.leadId = lead.id;
                newCard.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div style="flex: 1;">
                            <div class="card-title">Lead #${lead.id}</div>
                            <div class="card-description" style="margin-top:8px;font-size:13px;">
                                <div><strong>Responsável:</strong> ${lead.responsible_user || lead.responsible || 'N/A'}</div>
                                <div><strong>Fonte:</strong> ${lead.lead_source || lead.source || 'N/A'}</div>
                            </div>
                        </div>
                        <button class="btn-card-delete" style="background: #D81B60; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div style="margin-top:12px;padding-top:8px;border-top:1px solid #ddd;">
                        <strong style="font-size:12px;color:#0E4D42;">Link do Formulário:</strong><br>
                        <div style="display: flex; gap: 4px; margin-top: 4px;">
                            <input type="text" value="${formUrl}" readonly style="flex: 1; padding: 6px; font-size: 11px; border: 1px solid #ddd; border-radius: 3px; background: white; color: #333;">
                            <button class="btn-copy-lead-link" data-url="${formUrl}" style="background: #0E4D42; color: white; border: none; padding: 6px 10px; border-radius: 3px; cursor: pointer; font-size: 11px; white-space: nowrap;">
                                <i class="fas fa-copy"></i> Copiar
                            </button>
                        </div>
                        <a href="${formUrl}" target="_blank" style="display: inline-block; color:#0E4D42; text-decoration: underline; font-weight: bold; font-size: 11px; margin-top: 6px;">Ou clique aqui para abrir</a>
                    </div>
                `;

                newCard.addEventListener('dragstart', handleComercialDragStart);
                newCard.addEventListener('dragend', handleComercialDragEnd);
                newCard.addEventListener('click', (e) => {
                    if (!e.target.closest('.btn-card-delete') && !e.target.closest('.btn-copy-lead-link') && !e.target.closest('a')) {
                        e.stopPropagation();
                        openLeadDetailsModal(lead);
                    }
                });

                const deleteBtn = newCard.querySelector('.btn-card-delete');
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (confirm('Remover este lead?')) {
                        newCard.remove();
                        // Delete from API
                        fetch(`/api/leads/${lead.id}`, { method: 'DELETE' }).catch(e => console.error(e));
                        // Update counts
                        updateColumnCounts();
                        saveComercialKanbanData();
                    }
                });

                // Adicionar evento de clique para copiar link
                const copyBtn = newCard.querySelector('.btn-copy-lead-link');
                if (copyBtn) {
                    copyBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const url = copyBtn.dataset.url;
                        navigator.clipboard.writeText(url).then(() => {
                            const originalText = copyBtn.innerHTML;
                            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copiado!';
                            setTimeout(() => {
                                copyBtn.innerHTML = originalText;
                            }, 2000);
                        });
                    });
                }

                cardsContainer.appendChild(newCard);
                updateColumnCounts();
                saveComercialKanbanData();
            }

            // Modify the "Adicionar Card" button in Entrada de Lead to open lead creation modal
            document.addEventListener('click', function(e) {
                const btnAddCard = e.target.closest('.btn-add-card');
                if (!btnAddCard) return;

                const column = btnAddCard.closest('.kanban-column');
                if (!column) return;

                const columnTitle = column.getAttribute('data-column-title');
                if (columnTitle && columnTitle.toLowerCase() === 'entrada de lead') {
                    e.preventDefault();
                    e.stopPropagation();
                    openCreateLeadModal();
                }
            }, true);

            // If URL contains registerPaciente or registerMedico, bypass login and open form
            try {
                const p = new URLSearchParams(window.location.search);
                if (p.get('registerPaciente') === 'true' || p.get('registerMedico') === 'true') {
                    // Hide login overlay and show app for registration
                    const loginOverlay = document.getElementById('login-overlay');
                    const appMain = document.getElementById('app');
                    if (loginOverlay) loginOverlay.style.display = 'none';
                    if (appMain) appMain.classList.remove('app-hidden');
                    
                    if (p.get('registerPaciente') === 'true') {
                        setTimeout(() => openPatientRegistrationForm(), 400);
                    }
                    if (p.get('registerMedico') === 'true') {
                        setTimeout(() => openDoctorRegistrationForm(), 400);
                    }
                }
            } catch(e) {}

            // Botão Acessar Comercial - usar delegação de eventos
            document.addEventListener('click', function(e) {
                const btnComercial = e.target.closest('.btn-acessar-comercial');
                const btnFinanceiro = e.target.closest('.btn-acessar-financeiro');
                const btnJudicial = e.target.closest('.btn-acessar-judicial');
                const btnImportacao = e.target.closest('.btn-acessar-importacao');
                const btnIa = e.target.closest('.btn-acessar-ia');
                const btnCadastrarMedico = e.target.closest('.btn-cadastrar-medico');
                const btnPacientes = e.target.closest('.btn-acessar-pacientes');

                if (btnPacientes) {
                    e.preventDefault();
                    e.stopPropagation();
                    document.querySelectorAll('.page-content').forEach(page => page.classList.remove('active'));
                    const sec = document.getElementById('gestao-pacientes');
                    if (sec) sec.classList.add('active');
                    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                    const pacNav = document.querySelector('.nav-item[data-page="gestao-pacientes"]');
                    if (pacNav) pacNav.classList.add('active');
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    carregarListaPacientes();
                    return;
                }

                if (btnCadastrarMedico) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const adminSection = document.getElementById('administrativo');
                    const gestaoMedicosSection = document.getElementById('gestao-medicos');
                    
                    document.querySelectorAll('.page-content').forEach(page => {
                        page.classList.remove('active');
                    });
                    
                    if (gestaoMedicosSection) {
                        gestaoMedicosSection.classList.add('active');
                    }
                    
                    if (adminSection) {
                        adminSection.classList.remove('active');
                    }
                    
                    // Update sidebar active state
                    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                    const medicoNav = document.querySelector('.nav-item[data-page="gestao-medicos"]');
                    if (medicoNav) medicoNav.classList.add('active');
                    
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    return;
                }

                if (btnComercial || btnFinanceiro || btnJudicial || btnImportacao || btnIa) {
                    e.preventDefault();
                    e.stopPropagation();

                    const adminSection = document.getElementById('administrativo');
                    const comercialSection = document.getElementById('comercial');
                    const financeiroSection = document.getElementById('financeiro');
                    const judicialSection = document.getElementById('judicial');
                    const importacaoSection = document.getElementById('importacao');
                    const iaSection = document.getElementById('ia');

                    document.querySelectorAll('.page-content').forEach(page => {
                        page.classList.remove('active');
                    });

                    if (btnComercial && comercialSection) {
                        comercialSection.classList.add('active');
                    }

                    if (btnFinanceiro && financeiroSection) {
                        financeiroSection.classList.add('active');
                    }

                    if (btnJudicial && judicialSection) {
                        judicialSection.classList.add('active');
                    }

                    if (btnImportacao && importacaoSection) {
                        importacaoSection.classList.add('active');
                    }

                    if (btnIa && iaSection) {
                        iaSection.classList.add('active');
                    }

                    if (adminSection) {
                        adminSection.classList.remove('active');
                    }

                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            }, true);

            // ---------- Doctors Management in Area Medica ----------
            function loadAndDisplayDoctorsListAreaMedica() {
                fetch('/api/doctors').then(r => r.json()).then(doctors => {
                    const container = document.querySelector('#area-medica-doctors-list');
                    if (!container) return;
                    if (!doctors || !doctors.length) {
                        container.innerHTML = '<p style="text-align:center;padding:30px;color:#666;">Nenhum médico cadastrado.</p>';
                        return;
                    }
                    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;">';
                    doctors.forEach(doc => {
                        const photoUrl = doc.photo_url || 'https://via.placeholder.com/150?text=' + encodeURIComponent(doc.name);
                        html += `
                            <div style="background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;transition:all 0.3s;">
                                <img src="${photoUrl}" alt="${doc.name}" style="width:100%;height:180px;object-fit:cover;background:#eee;">
                                <div style="padding:16px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                        <h3 style="margin:0;font-size:16px;color:#0E4D42;">${doc.name}</h3>
                                        <span style="background:#0E4D42;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;">ID: ${doc.id}</span>
                                    </div>
                                    <p style="margin:0 0 8px 0;font-size:12px;color:#666;">${doc.email || ""}</p>
                                    <p style="margin:0 0 8px 0;font-size:12px;color:#888;">CRM: ${doc.crm || "N/A"} • ${doc.crm_uf || ""}</p>
                                    <p style="margin:0 0 12px 0;font-size:12px;color:#888;"><strong>Especialidade:</strong> ${doc.specialty || "N/A"}</p>
                                    <div style="display:flex;gap:8px;">
                                        <button class="btn-admin btn-edit-doctor-area-medica" data-doctor-id="${doc.id}" style="flex:1;padding:8px;background:#0E4D42;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px;">Editar</button>
                                        <button class="btn-admin btn-delete-doctor-area-medica" data-doctor-id="${doc.id}" style="flex:1;padding:8px;background:#d32f2f;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px;">Deletar</button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    container.innerHTML = html;

                    // attach event handlers
                    document.querySelectorAll('.btn-edit-doctor-area-medica').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const docId = e.target.getAttribute('data-doctor-id');
                            const doc = doctors.find(d => d.id === docId);
                            if (doc) openEditDoctorModalAdmin(doc, () => loadAndDisplayDoctorsListAreaMedica());
                        });
                    });
                    document.querySelectorAll('.btn-delete-doctor-area-medica').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const docId = e.target.getAttribute('data-doctor-id');
                            const doc = doctors.find(d => d.id === docId);
                            if (doc && confirm('Tem certeza que deseja deletar ' + doc.name + '?')) {
                                fetch('/api/doctors/' + encodeURIComponent(docId), { method: 'DELETE' }).then(r => {
                                    if (r.ok) {
                                        alert('Médico deletado.');
                                        loadAndDisplayDoctorsListAreaMedica();
                                    }
                                });
                            }
                        });
                    });
                }).catch(e => {
                    const container = document.querySelector('#area-medica-doctors-list');
                    if (container) container.innerHTML = '<p style="color:#d32f2f;text-align:center;">Erro ao carregar médicos.</p>';
                });
            }

            // ---------- Admin Doctors Management Page ----------
            function loadAndDisplayDoctorsList() {
                fetch('/api/doctors').then(r => r.json()).then(doctors => {
                    const container = document.querySelector('#admin-doctors-list-container');
                    if (!container) return;
                    if (!doctors || !doctors.length) {
                        container.innerHTML = '<p style="text-align:center;padding:30px;color:#666;">Nenhum médico cadastrado.</p>';
                        return;
                    }
                    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;">';
                    doctors.forEach(doc => {
                        const photoUrl = doc.photo_url || 'https://via.placeholder.com/150?text=' + encodeURIComponent(doc.name);
                        html += `
                            <div style="background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;transition:all 0.3s;">
                                <img src="${photoUrl}" alt="${doc.name}" style="width:100%;height:180px;object-fit:cover;background:#eee;">
                                <div style="padding:16px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                        <h3 style="margin:0;font-size:16px;color:#0E4D42;">${doc.name}</h3>
                                        <span style="background:#0E4D42;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;">ID: ${doc.id}</span>
                                    </div>
                                    <p style="margin:0 0 8px 0;font-size:12px;color:#666;">${doc.email || ""}</p>
                                    <p style="margin:0 0 8px 0;font-size:12px;color:#888;">CRM: ${doc.crm || "N/A"} • ${doc.crm_uf || ""}</p>
                                    <p style="margin:0 0 12px 0;font-size:12px;color:#888;"><strong>Especialidade:</strong> ${doc.specialty || "N/A"}</p>
                                    <div style="display:flex;gap:8px;">
                                        <button class="btn-admin btn-edit-doctor" data-doctor-id="${doc.id}" style="flex:1;padding:8px;background:#0E4D42;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px;">Editar</button>
                                        <button class="btn-admin btn-delete-doctor" data-doctor-id="${doc.id}" style="flex:1;padding:8px;background:#d32f2f;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px;">Deletar</button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    container.innerHTML = html;

                    // attach event handlers
                    document.querySelectorAll('.btn-edit-doctor').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const docId = e.target.getAttribute('data-doctor-id');
                            const doc = doctors.find(d => d.id === docId);
                            if (doc) openEditDoctorModalAdmin(doc);
                        });
                    });
                    document.querySelectorAll('.btn-delete-doctor').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const docId = e.target.getAttribute('data-doctor-id');
                            const doc = doctors.find(d => d.id === docId);
                            if (doc && confirm('Tem certeza que deseja deletar ' + doc.name + '?')) {
                                fetch('/api/doctors/' + encodeURIComponent(docId), { method: 'DELETE' }).then(r => {
                                    if (r.ok) {
                                        alert('Médico deletado.');
                                        loadAndDisplayDoctorsList();
                                    }
                                });
                            }
                        });
                    });
                }).catch(e => {
                    const container = document.querySelector('#admin-doctors-list-container');
                    if (container) container.innerHTML = '<p style="color:#d32f2f;text-align:center;">Erro ao carregar médicos.</p>';
                });
            }

            function openEditDoctorModalAdmin(doctor) {
                const cert = doctor.certificado_digital || {};
                const certStatus = cert.status || 'pendente';
                const certBadgeAdmin = certStatus === 'vinculado' || certStatus === 'vinculado_simulado'
                    ? '<span style="color:#059669;font-size:12px;"><i class="fas fa-check-circle"></i> Vinculado</span>'
                    : '<span style="color:#f59e0b;font-size:12px;"><i class="fas fa-exclamation-circle"></i> Pendente</span>';

                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width:660px;">
                        <div class="modal-header"><h2>Editar Médico: ${doctor.name}</h2><button class="btn-close-modal"><i class="fas fa-times"></i></button></div>
                        <div class="modal-body" style="max-height:70vh;overflow-y:auto;">
                            <form id="edit-doctor-admin-form">
                                <div class="form-group"><label>Nome Completo</label><input id="edit-doc-name" value="${doctor.name || ""}" required></div>
                                <div class="form-group"><label>E-mail</label><input id="edit-doc-email" value="${doctor.email || ""}" required></div>
                                <div class="form-group"><label>CPF</label><input id="edit-doc-cpf-admin" value="${doctor.cpf || cert.cpf || ""}"></div>
                                <div class="form-group"><label>CRM</label><input id="edit-doc-crm" value="${doctor.crm || ""}"></div>
                                <div class="form-group"><label>UF CRM</label><input id="edit-doc-crm-uf" value="${doctor.crm_uf || ""}"></div>
                                <div class="form-group"><label>Especialidade</label><input id="edit-doc-specialty" value="${doctor.specialty || ""}"></div>
                                <div class="form-group"><label>RQE</label><input id="edit-doc-rqe" value="${doctor.rqe || ""}"></div>
                                <div class="form-group"><label>Telefone</label><input id="edit-doc-phone" value="${doctor.phone || ""}"></div>
                                <div class="form-group"><label>Foto de Perfil</label><input id="edit-doc-photo" type="file" accept="image/*"></div>

                                <!-- Certificado Digital -->
                                <div style="margin-top:16px;padding:14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
                                    <h4 style="margin:0 0 8px;color:#166534;font-size:13px;"><i class="fas fa-certificate"></i> Certificado Digital &nbsp;${certBadgeAdmin}</h4>
                                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                                        <div class="form-group" style="margin:0;"><label style="font-size:11px;">CPF (certificado)</label><input id="edit-doc-cert-cpf" value="${cert.cpf || doctor.cpf || ''}" placeholder="00000000000" style="width:100%;padding:6px;border:1px solid #d1d5db;border-radius:4px;font-size:12px;"></div>
                                        <div class="form-group" style="margin:0;"><label style="font-size:11px;">Provedor</label>
                                            <select id="edit-doc-cert-provedor" style="width:100%;padding:6px;border:1px solid #d1d5db;border-radius:4px;font-size:12px;">
                                                <option value="integraicp" ${cert.provedor_preferido==='integraicp'?'selected':''}>IntegraICP</option>
                                                <option value="vidaas" ${cert.provedor_preferido==='vidaas'?'selected':''}>Vidaas</option>
                                                <option value="soluti" ${cert.provedor_preferido==='soluti'?'selected':''}>BirdID</option>
                                            </select>
                                        </div>
                                    </div>
                                    ${cert.certificado_nome ? `<p style="margin:6px 0 0;font-size:11px;color:#374151;"><strong>Titular:</strong> ${cert.certificado_nome} | <strong>Emissor:</strong> ${cert.certificado_emissor || 'N/A'}</p>` : ''}
                                    <div style="margin-top:8px;display:flex;gap:6px;">
                                        <button type="button" class="btn-vincular-cert-admin" style="padding:6px 12px;background:#059669;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:11px;"><i class="fas fa-link"></i> Vincular</button>
                                        <button type="button" class="btn-salvar-cert-admin" style="padding:6px 12px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:11px;"><i class="fas fa-save"></i> Salvar Cert.</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer"><button class="btn-secondary btn-cancel">Cancelar</button><button class="btn-primary btn-save">Salvar</button></div>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('.btn-close-modal').addEventListener('click', () => modal.remove());
                modal.querySelector('.btn-cancel').addEventListener('click', () => modal.remove());

                // Vincular certificado
                modal.querySelector('.btn-vincular-cert-admin').addEventListener('click', async () => {
                    const cpf = modal.querySelector('#edit-doc-cert-cpf').value.replace(/\D/g, '');
                    if (!cpf || cpf.length !== 11) { alert('CPF inválido (11 dígitos)'); return; }
                    try {
                        const res = await apiRequest(`/api/doctors/${doctor.id}/certificado/vincular`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ cpf })
                        });
                        if (res.auth_url) {
                            window.open(res.auth_url, '_blank', 'width=600,height=700');
                            alert('Janela de autenticação ICP-Brasil aberta.');
                        } else { alert(res.message || 'Certificado vinculado.'); }
                    } catch(e) { alert('Erro: ' + (e.message || e)); }
                });

                // Salvar dados certificado
                modal.querySelector('.btn-salvar-cert-admin').addEventListener('click', async () => {
                    try {
                        await apiRequest(`/api/doctors/${doctor.id}/certificado`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                cpf: modal.querySelector('#edit-doc-cert-cpf').value.replace(/\D/g, ''),
                                provedor_preferido: modal.querySelector('#edit-doc-cert-provedor').value
                            })
                        });
                        alert('Dados certificado salvos.');
                    } catch(e) { alert('Erro: ' + (e.message || e)); }
                });

                modal.querySelector('.btn-save').addEventListener('click', async () => {
                    const form = modal.querySelector('#edit-doctor-admin-form');
                    const fd = new FormData();
                    fd.append('name', form.querySelector('#edit-doc-name').value.trim());
                    fd.append('email', form.querySelector('#edit-doc-email').value.trim());
                    fd.append('cpf', form.querySelector('#edit-doc-cpf').value.trim());
                    fd.append('crm', form.querySelector('#edit-doc-crm').value.trim());
                    fd.append('crm_uf', form.querySelector('#edit-doc-crm-uf').value.trim());
                    fd.append('specialty', form.querySelector('#edit-doc-specialty').value.trim());
                    fd.append('rqe', form.querySelector('#edit-doc-rqe').value.trim());
                    fd.append('phone', form.querySelector('#edit-doc-phone').value.trim());
                    const photoInput = form.querySelector('#edit-doc-photo');
                    if (photoInput && photoInput.files && photoInput.files[0]) fd.append('photo', photoInput.files[0]);

                    try {
                        const res = await fetch('/api/doctors/' + encodeURIComponent(doctor.id), { method: 'PUT', body: fd });
                        if (res.ok) {
                            alert('Médico atualizado.');
                            modal.remove();
                            loadAndDisplayDoctorsList();
                        } else {
                            alert('Erro ao atualizar.');
                        }
                    } catch (e) {
                        alert('Erro: ' + e.message);
                    }
                });
            }

            // Generic column reordering setup function
            function setupColumnReordering(kanbanBoardId, moduleName) {
                const kanbanBoard = document.getElementById(kanbanBoardId);
                if (!kanbanBoard) return;

                let draggedColumn = null;

                const columns = kanbanBoard.querySelectorAll('.kanban-column');
                columns.forEach(column => {
                    column.draggable = true;
                    
                    column.addEventListener('dragstart', (e) => {
                        draggedColumn = column;
                        column.classList.add('dragging-column');
                        e.dataTransfer.effectAllowed = 'move';
                    });

                    column.addEventListener('dragend', (e) => {
                        column.classList.remove('dragging-column');
                        kanbanBoard.querySelectorAll('.kanban-column').forEach(col => {
                            col.classList.remove('drag-over-column');
                        });
                    });

                    column.addEventListener('dragover', (e) => {
                        if (e.preventDefault) {
                            e.preventDefault();
                        }
                        e.dataTransfer.dropEffect = 'move';
                        if (column !== draggedColumn) {
                            column.classList.add('drag-over-column');
                        }
                        return false;
                    });

                    column.addEventListener('dragleave', (e) => {
                        if (e.target === column) {
                            column.classList.remove('drag-over-column');
                        }
                    });

                    column.addEventListener('drop', (e) => {
                        if (e.stopPropagation) {
                            e.stopPropagation();
                        }
                        column.classList.remove('drag-over-column');

                        if (draggedColumn && draggedColumn !== column) {
                            const allColumns = Array.from(kanbanBoard.querySelectorAll('.kanban-column'));
                            const draggedIndex = allColumns.indexOf(draggedColumn);
                            const targetIndex = allColumns.indexOf(column);

                            if (draggedIndex < targetIndex) {
                                column.parentNode.insertBefore(draggedColumn, column.nextSibling);
                            } else {
                                column.parentNode.insertBefore(draggedColumn, column);
                            }

                            // Save the new column order based on module
                            const saveFunctions = {
                                'kanban-comercial': saveComercialKanbanData,
                                'kanban-painel': savePainelKanbanData,
                                'kanban-area-medica': saveAreaMedicaKanbanData,
                                'kanban-financeiro': saveFinanceiroKanbanData,
                                'kanban-judicial': saveJudicialKanbanData,
                                'kanban-importacao': saveImportacaoKanbanData,
                                'kanban-ia': saveIaKanbanData
                            };

                            const saveFunc = saveFunctions[kanbanBoardId];
                            if (saveFunc) saveFunc();
                        }
                        return false;
                    });
                });
            }

            // ===== GESTÃO DE PACIENTES - JAVASCRIPT =====
            let pacientesData = [];
            let pacienteAtual = null;
            let pacViewMode = 'lista';
            let draggedPacCard = null;

            const KANBAN_ETAPA_LABELS = {
                'formulario_anamnese': 'Formulário/Anamnese',
                'consultas': 'Consultas',
                'solicitacao_teste': 'Solicitação Teste Genético',
                'retorno_resultado': 'Retorno / Resultado',
                'orcamento_prescricao': 'Orçamento Prescrição Cannabis',
                'documentacao_anvisa': 'Documentação Anvisa',
                'medicamento_exportacao': 'Medicamento Exportação',
                'acompanhamento_45': 'Acompanhamento 45 dias'
            };

            const KANBAN_ETAPA_COLORS = {
                'formulario_anamnese': '#FF6F00',
                'consultas': '#00897B',
                'solicitacao_teste': '#5E35B1',
                'retorno_resultado': '#1565C0',
                'orcamento_prescricao': '#2E7D32',
                'documentacao_anvisa': '#C62828',
                'medicamento_exportacao': '#4527A0',
                'acompanhamento_45': '#00695C'
            };

            function switchPacView(mode) {
                pacViewMode = mode;
                document.getElementById('btn-pac-view-lista').classList.toggle('active', mode === 'lista');
                document.getElementById('btn-pac-view-kanban').classList.toggle('active', mode === 'kanban');
                document.getElementById('pac-view-lista-container').style.display = mode === 'lista' ? 'block' : 'none';
                document.getElementById('pac-view-kanban-container').style.display = mode === 'kanban' ? 'block' : 'none';
                if (mode === 'kanban') {
                    carregarKanbanPacientes();
                }
            }

            // --- Kanban Load ---
            async function carregarKanbanPacientes() {
                try {
                    const board = await apiRequest('/api/pacientes/kanban');
                    if (!board) return;
                    
                    const etapas = ['formulario_anamnese','consultas','solicitacao_teste','retorno_resultado','orcamento_prescricao','documentacao_anvisa','medicamento_exportacao','acompanhamento_45'];
                    
                    etapas.forEach(etapa => {
                        const container = document.querySelector(`#kanban-pacientes .kanban-cards[data-etapa="${etapa}"]`);
                        if (!container) return;
                        container.innerHTML = '';
                        
                        const patients = board[etapa] || [];
                        patients.forEach(pac => {
                            const card = criarKanbanPacCard(pac);
                            container.appendChild(card);
                        });
                    });

                    updateKanbanPacCounts();
                    initKanbanPacDragDrop();
                } catch(e) {
                    console.error('Erro ao carregar kanban pacientes:', e);
                }
            }

            function criarKanbanPacCard(pac) {
                const card = document.createElement('div');
                card.className = 'kanban-pac-card';
                card.draggable = true;
                card.dataset.pacienteId = pac.id;
                card.dataset.etapa = pac.kanban_etapa || 'formulario_anamnese';

                const etapaColor = KANBAN_ETAPA_COLORS[pac.kanban_etapa] || '#667eea';
                card.style.borderLeftColor = etapaColor;

                // Calculate days since creation
                let diasInfo = '';
                if (pac.created_at) {
                    const created = new Date(pac.created_at);
                    const now = new Date();
                    const dias = Math.floor((now - created) / (1000 * 60 * 60 * 24));
                    diasInfo = `<div class="pac-card-days"><i class="fas fa-clock"></i> ${dias} dia${dias !== 1 ? 's' : ''} no sistema</div>`;
                }

                // Status badges
                const badges = [];
                if (!pac.anamnese_preenchida) badges.push('<span class="pac-card-badge" style="background:#fff3e0;color:#e65100;">Anamnese pendente</span>');
                if (!pac.documentos_enviados) badges.push('<span class="pac-card-badge" style="background:#e3f2fd;color:#1565c0;">Docs pendentes</span>');

                const initial = (pac.nome || '?')[0].toUpperCase();

                card.innerHTML = `
                    <div style="display:flex;gap:10px;align-items:flex-start;">
                        <div class="pac-card-avatar">${initial}</div>
                        <div style="flex:1;min-width:0;">
                            <div class="pac-card-name" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${pac.nome || ''}">${pac.nome || 'Sem nome'}</div>
                            <div class="pac-card-id">${pac.id}${pac.cpf ? ' • ' + pac.cpf : ''}</div>
                            <div class="pac-card-info">
                                ${pac.medico_responsavel_nome ? `<span><i class="fas fa-user-md"></i> ${pac.medico_responsavel_nome}</span>` : ''}
                                ${pac.telefone ? `<span><i class="fas fa-phone"></i> ${pac.telefone}</span>` : ''}
                            </div>
                            ${badges.length ? `<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:6px;">${badges.join('')}</div>` : ''}
                            ${diasInfo}
                        </div>
                    </div>
                `;

                // Botão mover manual
                const selectMover = criarBotaoMoverKanban(pac);
                card.appendChild(selectMover);

                // Click to open profile
                card.addEventListener('click', (e) => {
                    if (e.defaultPrevented || e.target.tagName === 'SELECT' || e.target.tagName === 'OPTION') return;
                    abrirPerfilPaciente(pac.id);
                });

                return card;
            }

            function updateKanbanPacCounts() {
                document.querySelectorAll('#kanban-pacientes .kanban-column').forEach(col => {
                    const count = col.querySelectorAll('.kanban-pac-card').length;
                    const countEl = col.querySelector('.kanban-column-count');
                    if (countEl) countEl.textContent = count;
                });
            }

            // --- Kanban Drag & Drop ---
            function initKanbanPacDragDrop() {
                const board = document.getElementById('kanban-pacientes');
                if (!board) return;

                const cards = board.querySelectorAll('.kanban-pac-card');
                cards.forEach(card => {
                    card.removeEventListener('dragstart', handlePacDragStart);
                    card.removeEventListener('dragend', handlePacDragEnd);
                    card.addEventListener('dragstart', handlePacDragStart);
                    card.addEventListener('dragend', handlePacDragEnd);
                });

                const containers = board.querySelectorAll('.kanban-cards');
                containers.forEach(container => {
                    // Remove old listeners by cloning
                    const newContainer = container.cloneNode(false);
                    // Move children to new container
                    while (container.firstChild) {
                        newContainer.appendChild(container.firstChild);
                    }
                    container.parentNode.replaceChild(newContainer, container);
                    // Add fresh listeners
                    newContainer.addEventListener('dragover', function(e) {
                        e.preventDefault();
                        e.dataTransfer.dropEffect = 'move';
                        this.classList.add('drag-over');
                    });
                    newContainer.addEventListener('dragleave', function(e) {
                        if (e.target === this || !this.contains(e.relatedTarget)) this.classList.remove('drag-over');
                    });
                    newContainer.addEventListener('drop', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        this.classList.remove('drag-over');
                        handlePacDropOnContainer(this);
                    });
                });
            }

            function handlePacDropOnContainer(container) {
                if (!draggedPacCard) return;
                if (draggedPacCard.parentNode === container) return;

                const pacId = draggedPacCard.dataset.pacienteId;
                const novaEtapa = container.dataset.etapa;
                const etapaAnterior = draggedPacCard.dataset.etapa;

                if (!novaEtapa || novaEtapa === etapaAnterior) return;

                container.appendChild(draggedPacCard);
                draggedPacCard.dataset.etapa = novaEtapa;
                const newColor = KANBAN_ETAPA_COLORS[novaEtapa] || '#667eea';
                draggedPacCard.style.borderLeftColor = newColor;
                updateKanbanPacCounts();

                apiRequest('/api/pacientes/' + pacId + '/kanban-mover', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ etapa: novaEtapa })
                }).catch(function(err) {
                    console.error('Erro ao mover paciente no kanban:', err);
                    const oldContainer = document.querySelector('#kanban-pacientes .kanban-cards[data-etapa="' + etapaAnterior + '"]');
                    if (oldContainer) {
                        oldContainer.appendChild(draggedPacCard);
                        draggedPacCard.dataset.etapa = etapaAnterior;
                        draggedPacCard.style.borderLeftColor = KANBAN_ETAPA_COLORS[etapaAnterior] || '#667eea';
                        updateKanbanPacCounts();
                    }
                    alert('Erro ao mover paciente. Movimentação revertida.');
                });
            }

            function handlePacDragStart(e) {
                draggedPacCard = this;
                this.classList.add('dragging');
                this.style.opacity = '0.5';
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', this.dataset.pacienteId);
            }

            function handlePacDragEnd(e) {
                this.classList.remove('dragging');
                this.style.opacity = '1';
                document.querySelectorAll('#kanban-pacientes .kanban-cards').forEach(c => c.classList.remove('drag-over'));
                draggedPacCard = null;
            }

            // Funções de mover manual substituíram handlePacDragOver/Leave/Drop

            // Adicionar botão de mover manual no card kanban
            function criarBotaoMoverKanban(pac) {
                const select = document.createElement('select');
                select.style.cssText = 'font-size:10px;padding:2px 4px;border:1px solid #ddd;border-radius:4px;background:#fff;cursor:pointer;margin-top:6px;width:100%;';
                select.innerHTML = '<option value="">Mover para...</option>';
                Object.keys(KANBAN_ETAPA_LABELS).forEach(etapa => {
                    if (etapa !== pac.kanban_etapa) {
                        select.innerHTML += '<option value="' + etapa + '">' + KANBAN_ETAPA_LABELS[etapa] + '</option>';
                    }
                });
                select.addEventListener('change', async function(e) {
                    e.stopPropagation();
                    const novaEtapa = this.value;
                    if (!novaEtapa) return;
                    try {
                        await apiRequest('/api/pacientes/' + pac.id + '/kanban-mover', {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ etapa: novaEtapa })
                        });
                        carregarKanbanPacientes();
                    } catch(err) {
                        alert('Erro ao mover paciente');
                    }
                });
                select.addEventListener('click', function(e) { e.stopPropagation(); });
                return select;
            }

            function voltarParaAdmin() {
                document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
                const admin = document.getElementById('administrativo');
                if (admin) admin.classList.add('active');
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                const adminNav = document.querySelector('.nav-item[data-page="administrativo"]');
                if (adminNav) adminNav.classList.add('active');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function voltarParaListaPacientes() {
                document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
                const sec = document.getElementById('gestao-pacientes');
                if (sec) sec.classList.add('active');
                // Update sidebar active state
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                const pacNav = document.querySelector('.nav-item[data-page="gestao-pacientes"]');
                if (pacNav) pacNav.classList.add('active');
                // Refresh current view
                if (pacViewMode === 'kanban') {
                    carregarKanbanPacientes();
                } else {
                    carregarListaPacientes();
                }
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            async function carregarListaPacientes() {
                try {
                    const [pacRes, statsRes] = await Promise.all([
                        apiRequest('/api/pacientes'), apiRequest('/api/pacientes/stats')
                    ]);
                    pacientesData = Array.isArray(pacRes) ? pacRes : [];
                    const stats = statsRes || {};

                    document.getElementById('pacientes-stats-cards').innerHTML = `
                        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:20px;border-radius:12px;">
                            <div style="font-size:28px;font-weight:700;">${stats.total || 0}</div>
                            <div style="font-size:12px;opacity:.8;">Total Pacientes</div>
                        </div>
                        <div style="background:linear-gradient(135deg,#43a047,#2e7d32);color:#fff;padding:20px;border-radius:12px;">
                            <div style="font-size:28px;font-weight:700;">${stats.ativos || 0}</div>
                            <div style="font-size:12px;opacity:.8;">Ativos</div>
                        </div>
                        <div style="background:linear-gradient(135deg,#ff9800,#e65100);color:#fff;padding:20px;border-radius:12px;">
                            <div style="font-size:28px;font-weight:700;">${stats.pendentes_anamnese || 0}</div>
                            <div style="font-size:12px;opacity:.8;">Pendentes Anamnese</div>
                        </div>
                        <div style="background:linear-gradient(135deg,#2196f3,#1565c0);color:#fff;padding:20px;border-radius:12px;">
                            <div style="font-size:28px;font-weight:700;">${stats.pendentes_docs || 0}</div>
                            <div style="font-size:12px;opacity:.8;">Pendentes Documentos</div>
                        </div>
                    `;
                    renderizarListaPacientes(pacientesData);
                } catch(e) {
                    console.error('Erro ao carregar pacientes:', e);
                    document.getElementById('pacientes-lista').innerHTML = '<div style="padding:40px;text-align:center;color:#e74c3c;"><i class="fas fa-exclamation-triangle" style="font-size:24px;"></i><p>Erro ao carregar pacientes</p></div>';
                }
            }

            function renderizarListaPacientes(pac) {
                const el = document.getElementById('pacientes-lista');
                if (!pac.length) {
                    el.innerHTML = '<div style="padding:40px;text-align:center;color:#888;"><i class="fas fa-users" style="font-size:36px;margin-bottom:12px;display:block;"></i><p>Nenhum paciente cadastrado</p><p style="font-size:12px;">Converta leads ou crie novos pacientes</p></div>';
                    return;
                }
                let html = '<div class="pac-list-header pac-list-row"><div>#</div><div>Paciente</div><div>CPF</div><div>Etapa Kanban</div><div>Médico</div><div>Status</div><div>Ações</div></div>';
                pac.forEach((p, i) => {
                    const statusColor = p.status === 'ativo' ? '#4caf50' : '#ff9800';
                    const statusLabel = p.status === 'ativo' ? 'Ativo' : (p.status || 'Pendente');
                    const etapaLabel = KANBAN_ETAPA_LABELS[p.kanban_etapa] || 'Formulário/Anamnese';
                    const etapaColor = KANBAN_ETAPA_COLORS[p.kanban_etapa] || '#667eea';
                    html += `
                        <div class="pac-list-row" onclick="abrirPerfilPaciente('${p.id}')">
                            <div style="color:#888;font-size:11px;">${i+1}</div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:13px;">${(p.nome||'?')[0].toUpperCase()}</div>
                                <div><div style="font-weight:600;color:#1a1a2e;">${p.nome || 'Sem nome'}</div><div style="font-size:11px;color:#888;">${p.id}</div></div>
                            </div>
                            <div>${p.cpf || '-'}</div>
                            <div><span style="background:${etapaColor}15;color:${etapaColor};padding:3px 10px;border-radius:12px;font-size:10px;font-weight:600;border:1px solid ${etapaColor}30;">${etapaLabel}</span></div>
                            <div style="font-size:12px;">${p.medico_responsavel_nome || '<span style="color:#ff9800;">Aguardando</span>'}</div>
                            <div><span style="background:${statusColor}15;color:${statusColor};padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">${statusLabel}</span></div>
                            <div onclick="event.stopPropagation();">
                                <button onclick="abrirPerfilPaciente('${p.id}')" style="background:#667eea;color:#fff;border:none;padding:5px 10px;border-radius:6px;cursor:pointer;font-size:11px;" title="Ver perfil"><i class="fas fa-eye"></i></button>
                                <button onclick="excluirPaciente('${p.id}')" style="background:#e74c3c;color:#fff;border:none;padding:5px 10px;border-radius:6px;cursor:pointer;font-size:11px;margin-left:4px;" title="Excluir"><i class="fas fa-trash"></i></button>
                            </div>
                        </div>`;
                });
                el.innerHTML = html;
            }

            function filtrarPacientes() {
                const q = (document.getElementById('pacientes-search').value || '').toLowerCase();
                const st = document.getElementById('pacientes-filter-status').value;
                let filtered = pacientesData;
                if (q) filtered = filtered.filter(p => (p.nome||'').toLowerCase().includes(q) || (p.cpf||'').includes(q) || (p.id||'').toLowerCase().includes(q));
                if (st) filtered = filtered.filter(p => p.status === st);
                renderizarListaPacientes(filtered);
            }

            async function abrirPerfilPaciente(pacId) {
                try {
                    const pac = await apiRequest('/api/pacientes/' + pacId);
                    console.log('Paciente recebido:', pac);
                    if (!pac || pac.error) { alert('Paciente não encontrado'); return; }
                    pacienteAtual = pac;

                    document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
                    document.getElementById('perfil-paciente').classList.add('active');

                    // Header
                    document.getElementById('perfil-paciente-title').innerHTML = '<i class="fas fa-user"></i> ' + (pac.nome || 'Paciente');
                    document.getElementById('paciente-nome-display').textContent = pac.nome || '-';
                    document.getElementById('paciente-id-badge').textContent = pac.id;
                    const stBadge = document.getElementById('paciente-status-badge');
                    stBadge.textContent = pac.status === 'ativo' ? 'Ativo' : (pac.status || 'Pendente');
                    stBadge.style.background = pac.status === 'ativo' ? '#e8f5e9' : '#fff3e0';
                    stBadge.style.color = pac.status === 'ativo' ? '#2e7d32' : '#e65100';
                    document.getElementById('paciente-cpf-display').textContent = pac.cpf || '-';
                    
                    let idade = pac.idade || '';
                    if (!idade && pac.data_nascimento) {
                        const birth = new Date(pac.data_nascimento);
                        const today = new Date();
                        idade = Math.floor((today - birth) / (365.25 * 24 * 60 * 60 * 1000)) + ' anos';
                    }
                    document.getElementById('paciente-idade-display').textContent = idade ? idade : '-';
                    document.getElementById('paciente-nascimento-display').textContent = pac.data_nascimento ? new Date(pac.data_nascimento + 'T00:00:00').toLocaleDateString('pt-BR') : '-';
                    document.getElementById('paciente-sexo-display').textContent = pac.sexo || '-';
                    document.getElementById('paciente-convenio-display').textContent = pac.convenio || 'Particular';
                    document.getElementById('paciente-diagnostico-display').textContent = pac.diagnostico_atual || 'A definir pela IA';
                    document.getElementById('paciente-medico-display').textContent = pac.medico_responsavel_nome || 'Aguardando agendamento';
                    
                    // Kanban etapa
                    const etapaLabel = KANBAN_ETAPA_LABELS[pac.kanban_etapa] || pac.kanban_etapa || 'Formulário/Anamnese';
                    const etapaColor = KANBAN_ETAPA_COLORS[pac.kanban_etapa] || '#667eea';
                    const etapaEl = document.getElementById('paciente-kanban-etapa-display');
                    etapaEl.textContent = etapaLabel;
                    etapaEl.style.color = etapaColor;

                    // Photo
                    const fotoImg = document.getElementById('paciente-foto-img');
                    const fotoPlaceholder = document.getElementById('paciente-foto-placeholder');
                    if (pac.foto_url) {
                        fotoImg.src = pac.foto_url;
                        fotoImg.style.display = 'block';
                        fotoPlaceholder.style.display = 'none';
                    } else {
                        fotoImg.style.display = 'none';
                        fotoPlaceholder.style.display = 'block';
                    }

                    // Dados Pessoais form
                    document.getElementById('pac-edit-nome').value = pac.nome || '';
                    document.getElementById('pac-edit-cpf').value = pac.cpf || '';
                    document.getElementById('pac-edit-nascimento').value = pac.data_nascimento || '';
                    document.getElementById('pac-edit-sexo').value = pac.sexo || '';
                    document.getElementById('pac-edit-email').value = pac.email || '';
                    document.getElementById('pac-edit-telefone').value = pac.telefone || '';
                    document.getElementById('pac-edit-endereco').value = pac.endereco || '';
                    document.getElementById('pac-edit-convenio').value = pac.convenio || '';
                    document.getElementById('pac-edit-peso').value = pac.peso || '';
                    document.getElementById('pac-edit-responsavel-nome').value = pac.responsavel_nome || '';
                    document.getElementById('pac-edit-responsavel-cpf').value = pac.responsavel_cpf || '';

                    // Reset to first tab (Ficha de Atendimento)
                    document.querySelectorAll('.perfil-pac-tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.pac-tab-content').forEach(c => { c.classList.remove('active'); c.style.display = 'none'; });
                    document.querySelector('.perfil-pac-tab[data-pactab="ficha"]').classList.add('active');
                    const fichaTab = document.getElementById('pactab-ficha');
                    fichaTab.classList.add('active');
                    fichaTab.style.display = 'block';

                    // Close all accordion items
                    document.querySelectorAll('.pron-acc-item').forEach(i => i.classList.remove('open'));

                    carregarFichaAtendimento(pacId, pac);
                    carregarTimeline(pacId);
                    carregarProntuario(pacId);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } catch(e) {
                    console.error('Erro ao abrir perfil:', e);
                    alert('Erro ao carregar dados do paciente');
                }
            }

            function switchPacTab(tabEl) {
                const tabName = tabEl.dataset.pactab;
                document.querySelectorAll('.perfil-pac-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.pac-tab-content').forEach(c => { c.classList.remove('active'); c.style.display = 'none'; });
                tabEl.classList.add('active');
                const content = document.getElementById('pactab-' + tabName);
                if (content) { content.classList.add('active'); content.style.display = 'block'; }
            }

            function togglePronAccordion(headerEl) {
                const item = headerEl.closest('.pron-acc-item');
                if (!item) return;
                const isOpen = item.classList.contains('open');
                // Close all others
                document.querySelectorAll('.pron-acc-item').forEach(i => i.classList.remove('open'));
                // Toggle current
                if (!isOpen) item.classList.add('open');
            }

            // --- Ficha de Atendimento ---
            async function carregarFichaAtendimento(pacId, pacData) {
                try {
                    const ficha = await apiRequest('/api/pacientes/' + pacId + '/ficha');
                    const isEmpty = !ficha.atualizado_em;
                    const origemEl = document.getElementById('ficha-origem-dados');

                    if (isEmpty && pacData) {
                        // Auto-fill from anamnese data
                        const obj = pacData.objetivo_consulta || '';
                        const sintomas = pacData.sintomas || '';
                        document.getElementById('ficha-queixa-principal').value = obj ? (obj + (sintomas ? '\n\nSintomas: ' + sintomas : '')) : sintomas;
                        document.getElementById('ficha-hda').value = sintomas || '';
                        document.getElementById('ficha-doencas-previas').value = (pacData.diagnosticos_previos || '') + (pacData.diagnostico_atual ? (pacData.diagnosticos_previos ? '\n' : '') + 'Condição principal: ' + pacData.diagnostico_atual : '');
                        document.getElementById('ficha-historico-familiar').value = pacData.historico_familiar || '';
                        document.getElementById('ficha-alergias').value = pacData.alergias || '';
                        document.getElementById('ficha-medicacoes').value = pacData.medicacoes || '';
                        document.getElementById('ficha-cirurgias').value = pacData.cirurgias || '';
                        const habitos = [];
                        if (pacData.tabagismo) habitos.push('Tabagismo: ' + pacData.tabagismo);
                        if (pacData.alcool) habitos.push('Álcool: ' + pacData.alcool);
                        if (pacData.atividade_fisica) habitos.push('Atividade física: ' + pacData.atividade_fisica);
                        if (pacData.dieta) habitos.push('Dieta: ' + pacData.dieta);
                        document.getElementById('ficha-habitos').value = habitos.join('\n');
                        document.getElementById('ficha-exame-fisico').value = pacData.exames_recentes ? 'Exames recentes: ' + pacData.exames_recentes : '';
                        document.getElementById('ficha-diagnostico').value = pacData.diagnostico_atual || '';
                        document.getElementById('ficha-estadiamento').value = '';
                        document.getElementById('ficha-conduta').value = '';
                        document.getElementById('ficha-ultima-atualizacao').textContent = '';
                        origemEl.style.display = 'block';
                    } else {
                        // Fill from saved ficha
                        document.getElementById('ficha-queixa-principal').value = ficha.queixa_principal || '';
                        document.getElementById('ficha-hda').value = ficha.hda || '';
                        document.getElementById('ficha-doencas-previas').value = ficha.doencas_previas || '';
                        document.getElementById('ficha-historico-familiar').value = ficha.historico_familiar || '';
                        document.getElementById('ficha-alergias').value = ficha.alergias || '';
                        document.getElementById('ficha-medicacoes').value = ficha.medicacoes || '';
                        document.getElementById('ficha-cirurgias').value = ficha.cirurgias || '';
                        document.getElementById('ficha-habitos').value = ficha.habitos || '';
                        document.getElementById('ficha-exame-fisico').value = ficha.exame_fisico || '';
                        document.getElementById('ficha-diagnostico').value = ficha.diagnostico || '';
                        document.getElementById('ficha-estadiamento').value = ficha.estadiamento || '';
                        document.getElementById('ficha-conduta').value = ficha.conduta || '';
                        origemEl.style.display = 'none';
                        const infoEl = document.getElementById('ficha-ultima-atualizacao');
                        if (ficha.atualizado_em) {
                            const d = new Date(ficha.atualizado_em);
                            infoEl.textContent = 'Última atualização: ' + d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
                        } else {
                            infoEl.textContent = '';
                        }
                    }

                    // Render observações/notas
                    renderObservacoes(ficha.evolucoes || []);

                    // Render prescrições
                    carregarPrescricoesFicha(pacId);

                    // Render envelopes de assinatura do paciente
                    carregarEnvelopesPaciente(pacId);
                } catch(e) {
                    console.log('Ficha não encontrada, preenchendo com anamnese');
                    if (pacData) carregarFichaAtendimento(pacId, null);
                }
            }

            function renderObservacoes(notas) {
                const container = document.getElementById('observacoes-lista');
                const countEl = document.getElementById('observacoes-total-count');
                if (!notas || !notas.length) {
                    container.innerHTML = '<div style="text-align:center;padding:24px;color:#9ca3af;font-size:13px;"><i class="fas fa-clipboard" style="font-size:28px;margin-bottom:8px;display:block;"></i>Nenhuma anotação registrada</div>';
                    countEl.textContent = '';
                    return;
                }
                countEl.textContent = notas.length + ' nota' + (notas.length > 1 ? 's' : '');
                // Most recent first
                const sorted = [...notas].sort((a,b) => new Date(b.data) - new Date(a.data));
                container.innerHTML = sorted.map((nota, i) => {
                    const dt = new Date(nota.data);
                    const dataStr = dt.toLocaleDateString('pt-BR', {day:'2-digit',month:'2-digit',year:'numeric'}) + ' às ' + dt.toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
                    const numNota = sorted.length - i;
                    return `<div style="background:#fff;border-left:3px solid #7c3aed;border-radius:0 8px 8px 0;padding:12px 14px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,.06);">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <div>
                                <span style="font-size:12px;font-weight:700;color:#5b21b6;">Nota #${numNota}</span>
                                <span style="font-size:11px;color:#6b7280;margin-left:10px;"><i class="fas fa-calendar-alt" style="margin-right:3px;"></i>${dataStr}</span>
                            </div>
                            <button onclick="excluirObservacao('${nota.id}')" style="background:none;border:none;color:#ef4444;cursor:pointer;font-size:12px;opacity:.5;transition:opacity .2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=.5" title="Excluir nota"><i class="fas fa-trash-alt"></i></button>
                        </div>
                        <div style="color:#374151;font-size:13px;line-height:1.7;white-space:pre-wrap;word-break:break-word;">${nota.texto}</div>
                    </div>`;
                }).join('');
            }

            async function salvarObservacao() {
                const pacId = document.getElementById('perfil-pac-id')?.textContent?.replace('#','').trim();
                if (!pacId) return;
                const texto = document.getElementById('observacao-texto').value.trim();
                if (!texto) { showToast('Escreva a observação antes de salvar', 'error'); return; }
                try {
                    const resp = await apiRequest('/api/pacientes/' + pacId + '/ficha/evolucao', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({ texto })
                    });
                    showToast('Nota salva com sucesso!', 'success');
                    document.getElementById('observacao-texto').value = '';
                    renderObservacoes(resp.evolucoes || []);
                } catch(e) {
                    showToast('Erro ao salvar nota: ' + e.message, 'error');
                }
            }

            async function excluirObservacao(notaId) {
                if (!confirm('Deseja excluir esta nota?')) return;
                const pacId = document.getElementById('perfil-pac-id')?.textContent?.replace('#','').trim();
                if (!pacId) return;
                try {
                    const resp = await apiRequest('/api/pacientes/' + pacId + '/ficha/evolucao/' + notaId, {
                        method: 'DELETE'
                    });
                    showToast('Nota excluída', 'success');
                    renderObservacoes(resp.evolucoes || []);
                } catch(e) {
                    showToast('Erro ao excluir: ' + e.message, 'error');
                }
            }

            async function salvarFichaAtendimento() {
                const pacId = document.getElementById('perfil-pac-id')?.textContent?.replace('#','').trim();
                if (!pacId) return;
                const ficha = {
                    queixa_principal: document.getElementById('ficha-queixa-principal').value.trim(),
                    hda: document.getElementById('ficha-hda').value.trim(),
                    doencas_previas: document.getElementById('ficha-doencas-previas').value.trim(),
                    historico_familiar: document.getElementById('ficha-historico-familiar').value.trim(),
                    alergias: document.getElementById('ficha-alergias').value.trim(),
                    medicacoes: document.getElementById('ficha-medicacoes').value.trim(),
                    cirurgias: document.getElementById('ficha-cirurgias').value.trim(),
                    habitos: document.getElementById('ficha-habitos').value.trim(),
                    exame_fisico: document.getElementById('ficha-exame-fisico').value.trim(),
                    diagnostico: document.getElementById('ficha-diagnostico').value.trim(),
                    estadiamento: document.getElementById('ficha-estadiamento').value.trim(),
                    conduta: document.getElementById('ficha-conduta').value.trim(),
                    observacoes: ''
                };
                try {
                    await apiRequest('/api/pacientes/' + pacId + '/ficha', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify(ficha)
                    });
                    showToast('Ficha salva com sucesso!', 'success');
                    document.getElementById('ficha-origem-dados').style.display = 'none';
                    const infoEl = document.getElementById('ficha-ultima-atualizacao');
                    const now = new Date();
                    infoEl.textContent = 'Última atualização: ' + now.toLocaleDateString('pt-BR') + ' às ' + now.toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
                } catch(e) {
                    showToast('Erro ao salvar ficha: ' + e.message, 'error');
                }
            }

            // --- Timeline ---
            async function carregarTimeline(pacId) {
                try {
                    const events = await apiRequest('/api/pacientes/' + pacId + '/timeline');
                    const container = document.getElementById('timeline-container');
                    if (!events || !events.length) {
                        container.innerHTML = '<div style="position:absolute;left:14px;top:0;bottom:0;width:2px;background:linear-gradient(180deg,#667eea,#e0e0e0);"></div><div style="text-align:center;padding:40px;color:#888;"><i class="fas fa-clock" style="font-size:36px;margin-bottom:12px;display:block;"></i><p>Nenhum evento na linha do tempo</p></div>';
                        return;
                    }
                    const tipoIcons = { cadastro:'fa-user-plus', consulta:'fa-stethoscope', nota:'fa-sticky-note', evolucao:'fa-chart-line', exame:'fa-flask', prescricao:'fa-prescription', upload:'fa-upload', prontuario:'fa-file-medical', pagamento:'fa-credit-card' };
                    let html = '<div style="position:absolute;left:14px;top:0;bottom:0;width:2px;background:linear-gradient(180deg,#667eea,#e0e0e0);"></div>';
                    events.forEach(ev => {
                        const dt = ev.data ? new Date(ev.data).toLocaleString('pt-BR') : '';
                        const icon = tipoIcons[ev.tipo] || 'fa-circle';
                        html += `
                            <div class="timeline-event tipo-${ev.tipo}">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
                                    <div style="font-weight:700;color:#333;font-size:14px;"><i class="fas ${icon}" style="margin-right:6px;"></i>${ev.titulo}</div>
                                    <div style="font-size:11px;color:#888;white-space:nowrap;">${dt}</div>
                                </div>
                                ${ev.descricao ? `<div style="color:#666;font-size:13px;line-height:1.5;">${ev.descricao}</div>` : ''}
                                <div style="margin-top:6px;font-size:10px;text-transform:uppercase;color:#aaa;font-weight:600;">${ev.tipo}</div>
                            </div>`;
                    });
                    container.innerHTML = html;
                } catch(e) { console.error('Erro timeline:', e); }
            }

            // --- Prontuário ---
            async function carregarProntuario(pacId) {
                try {
                    const pron = await apiRequest('/api/pacientes/' + pacId + '/prontuario');
                    const exames = pron.exames || [];
                    const receituario = pron.receituario || [];
                    const laudos = pron.laudos || [];
                    const anexos = pron.anexos || [];
                    // Update count badges
                    const ce = document.getElementById('pron-count-exames'); if(ce) ce.textContent = exames.length;
                    const cr = document.getElementById('pron-count-receituario'); if(cr) cr.textContent = receituario.length;
                    const cl = document.getElementById('pron-count-laudos'); if(cl) cl.textContent = laudos.length;
                    const ca = document.getElementById('pron-count-anexos'); if(ca) ca.textContent = anexos.length;
                    // Render lists
                    renderPronList('pron-exames-lista', exames, 'exame');
                    renderPronList('pron-receituario-lista', receituario, 'receituario');
                    renderPronList('pron-laudos-lista', laudos, 'laudo');
                    renderPronList('pron-anexos-lista', anexos, 'anexo');
                } catch(e) { console.error('Erro prontuário:', e); }
            }

            function renderPronList(containerId, items, tipo) {
                const el = document.getElementById(containerId);
                if (!items.length) {
                    el.innerHTML = '<div style="text-align:center;padding:30px;color:#888;"><i class="fas fa-folder-open" style="font-size:24px;margin-bottom:8px;display:block;"></i><p style="font-size:13px;">Nenhum registro</p></div>';
                    return;
                }
                // Store items in global for safe referencing (avoids JSON in onclick)
                if (!window._pronItems) window._pronItems = {};
                const icons = { exame:'fa-flask', receituario:'fa-prescription-bottle-alt', laudo:'fa-file-signature', anexo:'fa-paperclip' };
                let html = '';
                items.forEach((item, idx) => {
                    const key = tipo + '_' + idx;
                    window._pronItems[key] = { tipo, item };
                    const dt = item.data ? new Date(item.data).toLocaleString('pt-BR') : '';

                    if (tipo === 'exame') {
                        // Exames: show file-focused card
                        const fileName = item.arquivo_url ? item.arquivo_url.split('/').pop() : '';
                        const ext = fileName ? fileName.split('.').pop().toLowerCase() : '';
                        const fileIcon = ext === 'pdf' ? 'fa-file-pdf' : ['jpg','jpeg','png','gif','webp'].includes(ext) ? 'fa-file-image' : 'fa-file-medical-alt';
                        const hasFile = !!item.arquivo_url;
                        html += `
                            <div class="pron-item" onclick="abrirDocViewerByKey('${key}')" title="Clique para visualizar o exame">
                                <div class="pron-icon exame"><i class="fas ${hasFile ? fileIcon : 'fa-flask'}"></i></div>
                                <div style="flex:1;">
                                    <div style="font-weight:600;color:#333;font-size:14px;">${item.titulo || 'Sem título'}</div>
                                    ${fileName ? `<div style="font-size:11px;color:#6b7280;margin-top:2px;"><i class="fas fa-paperclip" style="margin-right:3px;"></i>${fileName}</div>` : '<div style="font-size:11px;color:#d97706;margin-top:2px;"><i class="fas fa-exclamation-triangle" style="margin-right:3px;"></i>Sem arquivo anexado</div>'}
                                    ${item.descricao ? `<div style="font-size:11px;color:#888;margin-top:1px;">${item.descricao}</div>` : ''}
                                </div>
                                <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                                    <div style="font-size:11px;color:#888;">${dt}</div>
                                    <span style="font-size:11px;color:#2563eb;font-weight:600;"><i class="fas ${hasFile ? 'fa-eye' : 'fa-info-circle'}"></i> ${hasFile ? 'Ver Exame' : 'Detalhes'}</span>
                                </div>
                            </div>`;
                    } else {
                        html += `
                            <div class="pron-item" onclick="abrirDocViewerByKey('${key}')" title="Clique para visualizar o documento">
                                <div class="pron-icon ${tipo}"><i class="fas ${icons[tipo] || 'fa-file'}"></i></div>
                                <div style="flex:1;">
                                    <div style="font-weight:600;color:#333;font-size:14px;">${item.titulo || 'Sem título'}</div>
                                    <div style="font-size:12px;color:#888;">${item.descricao || ''}</div>
                                    ${item.medico_nome ? `<div style="font-size:11px;color:#667eea;margin-top:2px;"><i class="fas fa-user-md"></i> ${item.medico_nome}</div>` : ''}
                                </div>
                                <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                                    <div style="font-size:11px;color:#888;">${dt}</div>
                                    <span style="font-size:11px;color:#00897B;font-weight:600;"><i class="fas fa-eye"></i> Visualizar</span>
                                </div>
                            </div>`;
                    }
                });
                el.innerHTML = html;
            }

            // --- Modais ---
            function abrirModalNovoPaciente() {
                const m = document.getElementById('modal-novo-paciente');
                m.style.display = 'flex';
            }
            function fecharModalNovoPaciente() {
                document.getElementById('modal-novo-paciente').style.display = 'none';
            }

            async function criarNovoPaciente() {
                const nome = document.getElementById('novo-pac-nome').value.trim();
                if (!nome) { alert('Nome é obrigatório'); return; }
                try {
                    await apiRequest('/api/pacientes', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            nome, cpf: document.getElementById('novo-pac-cpf').value,
                            email: document.getElementById('novo-pac-email').value,
                            telefone: document.getElementById('novo-pac-telefone').value,
                            data_nascimento: document.getElementById('novo-pac-nascimento').value,
                            sexo: document.getElementById('novo-pac-sexo').value,
                            convenio: document.getElementById('novo-pac-convenio').value,
                            endereco: document.getElementById('novo-pac-endereco').value,
                            pagamento_confirmado: true
                        })
                    });
                    fecharModalNovoPaciente();
                    carregarListaPacientes();
                    alert('Paciente criado com sucesso!');
                } catch(e) { alert('Erro ao criar paciente'); }
            }

            async function abrirModalConverterLead() {
                const m = document.getElementById('modal-converter-lead');
                m.style.display = 'flex';
                try {
                    const leads = await apiRequest('/api/leads');
                    const sel = document.getElementById('converter-lead-select');
                    sel.innerHTML = '<option value="">Selecione um lead...</option>';
                    (leads || []).forEach(l => {
                        if (l.status !== 'convertido') {
                            sel.innerHTML += `<option value="${l.id}">#${l.id} - ${l.name || l.nome || 'Sem nome'} (${l.email || 'sem email'})</option>`;
                        }
                    });
                } catch(e) { console.error(e); }
            }
            function fecharModalConverterLead() {
                document.getElementById('modal-converter-lead').style.display = 'none';
            }

            async function converterLeadSelecionado() {
                const leadId = document.getElementById('converter-lead-select').value;
                if (!leadId) { alert('Selecione um lead'); return; }
                try {
                    const res = await apiRequest('/api/pacientes/converter-lead', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ lead_id: leadId })
                    });
                    if (res.error) { alert(res.error); return; }
                    fecharModalConverterLead();
                    carregarListaPacientes();
                    alert('Lead convertido em paciente: ' + (res.nome || res.id));
                } catch(e) { alert('Erro ao converter lead'); }
            }

            async function excluirPaciente(pacId) {
                if (!confirm('Tem certeza que quer excluir este paciente?')) return;
                try {
                    await apiRequest('/api/pacientes/' + pacId, { method: 'DELETE' });
                    carregarListaPacientes();
                } catch(e) { alert('Erro ao excluir'); }
            }

            async function salvarDadosPaciente() {
                if (!pacienteAtual) return;
                try {
                    const dados = {
                        nome: document.getElementById('pac-edit-nome').value,
                        cpf: document.getElementById('pac-edit-cpf').value,
                        data_nascimento: document.getElementById('pac-edit-nascimento').value,
                        sexo: document.getElementById('pac-edit-sexo').value,
                        email: document.getElementById('pac-edit-email').value,
                        telefone: document.getElementById('pac-edit-telefone').value,
                        endereco: document.getElementById('pac-edit-endereco').value,
                        convenio: document.getElementById('pac-edit-convenio').value,
                        peso: document.getElementById('pac-edit-peso').value,
                        responsavel_nome: document.getElementById('pac-edit-responsavel-nome').value,
                        responsavel_cpf: document.getElementById('pac-edit-responsavel-cpf').value
                    };
                    await apiRequest('/api/pacientes/' + pacienteAtual.id, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(dados)
                    });
                    alert('Dados salvos com sucesso!');
                    abrirPerfilPaciente(pacienteAtual.id);
                } catch(e) { alert('Erro ao salvar dados'); }
            }

            async function uploadFotoPaciente(input) {
                if (!pacienteAtual || !input.files[0]) return;
                const fd = new FormData();
                fd.append('foto', input.files[0]);
                try {
                    await fetch('/api/pacientes/' + pacienteAtual.id + '/foto', { method: 'POST', body: fd });
                    abrirPerfilPaciente(pacienteAtual.id);
                } catch(e) { alert('Erro ao enviar foto'); }
            }

            // --- Visualizar Documento do Prontuário ---
            let docViewerCurrentItem = null;

            function abrirDocViewerByKey(key) {
                const entry = window._pronItems && window._pronItems[key];
                if (!entry) { console.error('Item não encontrado:', key); return; }
                abrirDocViewer(entry.tipo, entry.item);
            }

            function abrirDocViewer(tipo, item) {
                try {
                    docViewerCurrentItem = item;
                    const overlay = document.getElementById('doc-viewer-overlay');
                    const badge = document.getElementById('doc-viewer-badge');
                    const toolbarTitle = document.getElementById('doc-viewer-toolbar-title');
                    const content = document.getElementById('doc-viewer-content');
                    const downloadBtn = document.getElementById('doc-viewer-download-btn');

                    // Badge
                    const tipoLabels = { receituario:'Receituário Médico', exame:'Resultado de Exame', laudo:'Laudo / Parecer', anexo:'Documento Anexo' };
                    badge.textContent = tipoLabels[tipo] || 'Documento';
                    badge.className = 'doc-type-badge ' + tipo;
                    toolbarTitle.textContent = item.titulo || 'Documento';

                    // Download button
                    if (item.arquivo_url) {
                        downloadBtn.style.display = 'flex';
                        downloadBtn.setAttribute('data-url', item.arquivo_url);
                    } else {
                        downloadBtn.style.display = 'none';
                    }

                    // Patient & date info
                    const pac = pacienteAtual || {};
                    const dataDoc = item.data ? new Date(item.data) : new Date();
                    const dataFormatada = dataDoc.toLocaleDateString('pt-BR');
                    const horaFormatada = dataDoc.toLocaleTimeString('pt-BR', { hour:'2-digit', minute:'2-digit' });
                    const dataGerado = dataDoc.toLocaleDateString('pt-BR') + ' ' + horaFormatada;

                    let html = '';

                    // Check if it's a solicitation document
                    const conteudoCheck = item.conteudo || '';
                    if (conteudoCheck.includes('TIPO_SOLICITACAO:')) {
                        html = renderDocSolicitacao(item, pac, dataFormatada, dataGerado);
                    } else if (tipo === 'receituario') {
                        html = renderDocReceituario(item, pac, dataFormatada, dataGerado);
                    } else if (tipo === 'exame') {
                        html = renderDocExame(item, pac, dataFormatada, dataGerado);
                    } else {
                        html = renderDocGenerico(tipo, item, pac, dataFormatada, dataGerado);
                    }

                    content.innerHTML = html;
                    overlay.classList.add('active');
                    document.body.style.overflow = 'hidden';
                } catch(e) {
                    console.error('Erro ao abrir documento:', e);
                    alert('Erro ao abrir o documento');
                }
            }

            function renderDocReceituario(item, pac, dataFormatada, dataGerado) {
                // Parse conteudo into structured sections
                const conteudo = item.conteudo || item.descricao || '';
                const lines = conteudo.split('\n');
                let medicamentos = [];
                let observacoes = '';
                let medicoInfo = { nome: item.medico_nome || '', crm: '' };
                let currentSection = 'header';
                let currentMed = null;
                let obsLines = [];

                for (let line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed) continue;
                    if (trimmed.startsWith('MEDICAMENTO:') || trimmed.startsWith('Medicamento:')) {
                        currentSection = 'med';
                        currentMed = { nome: trimmed.replace(/^MEDICAMENTO:\s*/i, ''), posologia: '', detalhe: '', qtd: '', duracao: '' };
                        medicamentos.push(currentMed);
                    } else if (trimmed.startsWith('Dosagem:') || trimmed.startsWith('DOSAGEM:')) {
                        if (currentMed) currentMed.detalhe += trimmed + '\n';
                    } else if (trimmed.startsWith('Posologia:') || trimmed.startsWith('POSOLOGIA:')) {
                        if (currentMed) currentMed.posologia = trimmed.replace(/^Posologia:\s*/i, '');
                    } else if (trimmed.startsWith('Duração') || trimmed.startsWith('DURAÇÃO')) {
                        if (currentMed) currentMed.duracao = trimmed.replace(/^Duração[^:]*:\s*/i, '');
                    } else if (trimmed.startsWith('ORIENTAÇÕES:') || trimmed.startsWith('Orientações:')) {
                        currentSection = 'obs';
                    } else if (trimmed.startsWith('OBSERVAÇÕES:') || trimmed.startsWith('Observações:')) {
                        currentSection = 'obs';
                    } else if (trimmed.startsWith('CRM:') || trimmed.startsWith('CRM/')) {
                        medicoInfo.crm = trimmed;
                    } else if (trimmed.startsWith('Dr.') || trimmed.startsWith('Dra.')) {
                        medicoInfo.nome = trimmed;
                    } else if (currentSection === 'obs' || currentSection === 'orientacoes') {
                        obsLines.push(trimmed);
                    } else if (currentSection === 'med' && currentMed) {
                        if (trimmed.startsWith('-')) obsLines.push(trimmed);
                        else currentMed.detalhe += trimmed + '\n';
                    }
                }
                observacoes = obsLines.join('\n');

                // If no structured meds found, create one from description
                if (medicamentos.length === 0) {
                    medicamentos.push({
                        nome: item.titulo || 'Prescrição',
                        posologia: item.descricao || '',
                        detalhe: '',
                        qtd: '',
                        duracao: ''
                    });
                    if (!observacoes) observacoes = conteudo;
                }

                // Build table rows
                let medRows = '';
                medicamentos.forEach(med => {
                    medRows += `<tr>
                        <td>
                            <div class="med-name">${med.nome}</div>
                            ${med.detalhe ? `<div class="med-detail">${med.detalhe.trim().replace(/\n/g, '<br>')}</div>` : ''}
                        </td>
                        <td>
                            ${med.posologia ? `<div class="posologia-main">${med.posologia}</div>` : ''}
                        </td>
                        <td style="text-align:center;">${med.qtd || '-'}</td>
                        <td style="text-align:center;">${med.duracao || '-'}</td>
                    </tr>`;
                });

                return `<div class="doc-page">
                    <div class="doc-page-header">
                        <span class="logo">On Medicina Internacional</span>
                    </div>
                    <div class="doc-page-body">
                        <div class="doc-rx-title">Receituário Médico</div>

                        <div class="doc-rx-info">
                            <div><span class="label">Paciente:</span> ${(pac.nome || 'N/A').toUpperCase()}</div>
                            <div><span class="label">Data:</span> ${dataFormatada}</div>
                            <div><span class="label">CPF:</span> ${pac.cpf || 'N/A'}</div>
                            <div><span class="label">Médico:</span> ${medicoInfo.nome || item.medico_nome || 'N/A'}</div>
                            ${medicoInfo.crm ? `<div></div><div><span class="label">${medicoInfo.crm}</span></div>` : ''}
                        </div>

                        ${item.arquivo_url ? `<div class="doc-download-bar"><span><i class="fas fa-file-pdf" style="color:#dc2626;margin-right:6px;"></i> Arquivo anexado</span><a href="${item.arquivo_url}" target="_blank"><i class="fas fa-download"></i> Baixar</a></div>` : ''}

                        <div class="doc-rx-section-title">Prescrição</div>
                        <table class="doc-rx-table">
                            <thead>
                                <tr>
                                    <th style="width:35%;">Medicamento/Produto</th>
                                    <th style="width:35%;">Posologia/Instruções</th>
                                    <th style="width:10%;">Qtd.</th>
                                    <th style="width:20%;">Duração</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${medRows}
                            </tbody>
                        </table>

                        ${observacoes ? `<div class="doc-rx-obs">
                            <div class="obs-title">Observações Gerais:</div>
                            <div class="obs-text">${observacoes.replace(/\n/g, '<br>')}</div>
                        </div>` : ''}

                        <div class="doc-rx-signature">
                            <div class="sig-line"></div>
                            <div class="sig-name">${medicoInfo.nome || item.medico_nome || ''}</div>
                            ${medicoInfo.crm ? `<div class="sig-crm">${medicoInfo.crm}</div>` : ''}
                        </div>
                    </div>
                    <div class="doc-page-footer">
                        <span>On Medicina API | Gerado em ${dataGerado}</span>
                        <span>Página 1</span>
                    </div>
                </div>`;
            }

            function renderDocExame(item, pac, dataFormatada, dataGerado) {
                const fileName = item.arquivo_url ? item.arquivo_url.split('/').pop() : '';
                const ext = fileName ? fileName.split('.').pop().toLowerCase() : '';
                const isPdf = ext === 'pdf';
                const isImage = ['jpg','jpeg','png','gif','webp','bmp'].includes(ext);

                let fileContent = '';
                if (item.arquivo_url && isPdf) {
                    fileContent = `<div class="doc-exame-file-area">
                        <iframe src="${item.arquivo_url}" style="width:100%;height:500px;border:none;border-radius:4px;"></iframe>
                    </div>
                    <div class="doc-exame-download">
                        <a href="${item.arquivo_url}" target="_blank"><i class="fas fa-external-link-alt"></i> Abrir em nova aba</a>
                        <a href="${item.arquivo_url}" download><i class="fas fa-download"></i> Baixar arquivo</a>
                    </div>`;
                } else if (item.arquivo_url && isImage) {
                    fileContent = `<div class="doc-exame-file-area" style="text-align:center;">
                        <img src="${item.arquivo_url}" style="max-width:100%;max-height:600px;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.1);" alt="${item.titulo || 'Exame'}">
                    </div>
                    <div class="doc-exame-download">
                        <a href="${item.arquivo_url}" target="_blank"><i class="fas fa-external-link-alt"></i> Abrir em nova aba</a>
                        <a href="${item.arquivo_url}" download><i class="fas fa-download"></i> Baixar arquivo</a>
                    </div>`;
                } else if (item.arquivo_url) {
                    fileContent = `<div class="doc-exame-file-area" style="text-align:center;padding:40px;">
                        <i class="fas fa-file-medical-alt" style="font-size:48px;color:#2563eb;margin-bottom:12px;display:block;"></i>
                        <div style="font-size:14px;font-weight:600;color:#374151;margin-bottom:4px;">${fileName}</div>
                        <div style="font-size:12px;color:#6b7280;margin-bottom:16px;">Arquivo de exame enviado pelo paciente</div>
                        <a href="${item.arquivo_url}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:10px 24px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;font-size:13px;"><i class="fas fa-download"></i> Baixar Exame</a>
                    </div>`;
                } else {
                    fileContent = `<div class="doc-exame-file-area" style="text-align:center;padding:40px;">
                        <i class="fas fa-cloud-upload-alt" style="font-size:48px;color:#9ca3af;margin-bottom:12px;display:block;"></i>
                        <div style="font-size:14px;color:#6b7280;">Nenhum arquivo anexado</div>
                        <div style="font-size:12px;color:#9ca3af;margin-top:4px;">O exame ainda não possui arquivo enviado</div>
                    </div>`;
                }

                return `<div class="doc-page">
                    <div class="doc-page-header" style="background:#2563eb;">
                        <span class="logo">On Medicina Internacional</span>
                    </div>
                    <div class="doc-page-body">
                        <div class="doc-gen-title" style="color:#2563eb;">Exame</div>
                        <div class="doc-gen-subtitle">${item.titulo || ''}</div>

                        <div class="doc-gen-patient-bar">
                            <div><span class="label">Paciente:</span> ${(pac.nome || 'N/A').toUpperCase()}</div>
                            <div><span class="label">Data:</span> ${dataFormatada}</div>
                            <div><span class="label">CPF:</span> ${pac.cpf || 'N/A'}</div>
                            <div><span class="label">Enviado por:</span> ${item.medico_nome || 'Paciente'}</div>
                        </div>

                        ${item.descricao ? `<div style="font-size:10pt;color:#555;margin-bottom:12px;padding:8px 12px;background:#f8fafc;border-left:3px solid #2563eb;border-radius:0 4px 4px 0;">${item.descricao}</div>` : ''}

                        ${fileContent}
                    </div>
                    <div class="doc-page-footer">
                        <span>On Medicina API | Gerado em ${dataGerado}</span>
                        <span>Página 1</span>
                    </div>
                </div>`;
            }

            function renderDocGenerico(tipo, item, pac, dataFormatada, dataGerado) {
                const conteudo = item.conteudo || item.descricao || 'Sem conteúdo registrado.';
                const tipoTitles = { exame:'Resultado de Exame', laudo:'Laudo / Parecer Técnico', anexo:'Documento' };
                const tipoColors = { exame:'#2563eb', laudo:'#d97706', anexo:'#4b5563' };
                const color = tipoColors[tipo] || '#059669';

                return `<div class="doc-page">
                    <div class="doc-page-header" style="background:${color};">
                        <span class="logo">On Medicina Internacional</span>
                    </div>
                    <div class="doc-page-body">
                        <div class="doc-gen-title" style="color:${color};">${tipoTitles[tipo] || 'Documento'}</div>
                        <div class="doc-gen-subtitle">${item.titulo || ''}</div>

                        <div class="doc-gen-patient-bar">
                            <div><span class="label">Paciente:</span> ${(pac.nome || 'N/A').toUpperCase()}</div>
                            <div><span class="label">Data:</span> ${dataFormatada}</div>
                            <div><span class="label">CPF:</span> ${pac.cpf || 'N/A'}</div>
                            <div><span class="label">Responsável:</span> ${item.medico_nome || 'N/A'}</div>
                        </div>

                        ${item.arquivo_url ? `<div class="doc-download-bar"><span><i class="fas fa-file-pdf" style="color:#dc2626;margin-right:6px;"></i> Arquivo anexado</span><a href="${item.arquivo_url}" target="_blank"><i class="fas fa-download"></i> Baixar</a></div>` : ''}

                        <div class="doc-gen-body-text">${conteudo}</div>

                        <div class="doc-gen-footer">
                            <div class="doc-gen-footer-doctor">
                                ${item.medico_nome ? `<div class="name">${item.medico_nome}</div>` : ''}
                                <div class="role">Responsável pelo registro</div>
                            </div>
                            <div class="doc-gen-footer-sig">
                                <div class="sig-line"></div>
                                <div class="sig-text">Assinatura Digital</div>
                            </div>
                            <div class="doc-gen-footer-date">${dataFormatada}</div>
                        </div>
                    </div>
                    <div class="doc-page-footer">
                        <span>On Medicina API | Gerado em ${dataGerado}</span>
                        <span>Página 1</span>
                    </div>
                </div>`;
            }

            function renderDocSolicitacao(item, pac, dataFormatada, dataGerado) {
                const conteudo = item.conteudo || '';
                const lines = conteudo.split('\n');
                let tipoSol = '', tituloSol = '', exames = [], observacoes = '';
                let medicoInfo = { nome: item.medico_nome || '', crm: '' };

                for (let line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed) continue;
                    if (trimmed.startsWith('TIPO_SOLICITACAO:')) {
                        tipoSol = trimmed.replace('TIPO_SOLICITACAO:', '').trim();
                    } else if (trimmed.startsWith('TITULO:')) {
                        tituloSol = trimmed.replace('TITULO:', '').trim();
                    } else if (trimmed.startsWith('EXAME:')) {
                        exames.push(trimmed.replace('EXAME:', '').trim());
                    } else if (trimmed.startsWith('OBSERVAÇÕES:')) {
                        observacoes = trimmed.replace('OBSERVAÇÕES:', '').trim();
                    } else if (trimmed.startsWith('CRM:') || trimmed.startsWith('CRM/')) {
                        medicoInfo.crm = trimmed;
                    } else if (trimmed.startsWith('Dr.') || trimmed.startsWith('Dra.')) {
                        medicoInfo.nome = trimmed;
                    }
                }

                const isFarmaco = tipoSol === 'teste_farmacogenetico';
                const headerColor = isFarmaco ? '#7c3aed' : '#2563eb';
                const titulo = tituloSol || (isFarmaco ? 'Solicitação de Teste Farmacogenético' : 'Solicitação de Exames Laboratoriais');

                let examesHtml = '';
                if (isFarmaco) {
                    examesHtml = exames.map(e => `
                        <div style="display:flex;align-items:center;gap:10px;font-size:11pt;padding:10px 16px;background:#f5f3ff;border:2px solid #c4b5fd;border-radius:8px;font-weight:600;color:#5b21b6;margin-bottom:8px;">
                            <i class="fas fa-check-circle" style="color:#7c3aed;"></i> ${e}
                        </div>
                    `).join('');
                } else {
                    examesHtml = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 20px;">' +
                        exames.map(e => `
                            <div style="display:flex;align-items:center;gap:8px;font-size:10pt;padding:4px 0;">
                                <i class="fas fa-check-square" style="color:#2563eb;font-size:13px;"></i> ${e}
                            </div>
                        `).join('') + '</div>';
                }

                return `<div class="doc-page">
                    <div class="doc-page-header" style="background:${headerColor};">
                        <span class="logo">On Medicina Internacional</span>
                    </div>
                    <div class="doc-page-body">
                        <div class="doc-rx-title" style="color:${headerColor};">${titulo}</div>

                        <div class="doc-rx-info">
                            <div><span class="label">Paciente:</span> ${(pac.nome || 'N/A').toUpperCase()}</div>
                            <div><span class="label">Data:</span> ${dataFormatada}</div>
                            <div><span class="label">CPF:</span> ${pac.cpf || 'N/A'}</div>
                            <div><span class="label">Médico:</span> ${medicoInfo.nome || item.medico_nome || 'N/A'}</div>
                            ${medicoInfo.crm ? '<div></div><div><span class="label">' + medicoInfo.crm + '</span></div>' : ''}
                        </div>

                        <div class="doc-rx-section-title">${isFarmaco ? 'Teste Solicitado' : 'Exames Solicitados'}</div>
                        <div style="margin-bottom:20px;">
                            ${examesHtml}
                        </div>

                        ${observacoes ? '<div class="doc-rx-obs"><div class="obs-title">' + (isFarmaco ? 'Justificativa Clínica:' : 'Observações Clínicas:') + '</div><div class="obs-text">' + observacoes.replace(/\\n/g, '<br>') + '</div></div>' : ''}

                        <div class="doc-rx-signature">
                            <div class="sig-line"></div>
                            <div class="sig-name">${medicoInfo.nome || item.medico_nome || ''}</div>
                            ${medicoInfo.crm ? '<div class="sig-crm">' + medicoInfo.crm + '</div>' : ''}
                        </div>
                    </div>
                    <div class="doc-page-footer">
                        <span>On Medicina Internacional | ${titulo}</span>
                        <span>Gerado em ${dataGerado}</span>
                    </div>
                </div>`;
            }

            function fecharDocViewer() {
                document.getElementById('doc-viewer-overlay').classList.remove('active');
                document.body.style.overflow = '';
                docViewerCurrentItem = null;
            }

            // Close document viewer on Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && document.getElementById('doc-viewer-overlay').classList.contains('active')) {
                    fecharDocViewer();
                }
            });

            function imprimirDocumento() {
                window.print();
            }

            function baixarDocumento() {
                const btn = document.getElementById('doc-viewer-download-btn');
                const url = btn.getAttribute('data-url');
                if (url) {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '';
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            }

            // ===== PRESCRIÇÃO MÉDICA CANNABIS (Com Titulação + Calculadora 24 Meses + Laudo) =====
            let prescricaoMedicamentos = [];
            let medicamentosPlataforma = [];
            let prescActiveTab = 'receita';

            // Tab switching
            function switchPrescTab(tab) {
                prescActiveTab = tab;
                ['receita','laudo','exames'].forEach(t => {
                    const panel = document.getElementById('presc-tab-' + t);
                    if (panel) panel.style.display = t === tab ? 'block' : 'none';
                });
                document.querySelectorAll('.presc-tab-btn').forEach(btn => {
                    const isActive = btn.dataset.tab === tab;
                    btn.style.borderBottomColor = isActive ? '#059669' : 'transparent';
                    btn.style.color = isActive ? '#059669' : '#6b7280';
                    if (isActive) btn.classList.add('active'); else btn.classList.remove('active');
                });
            }

            async function abrirModalPrescricao() {
                if (!pacienteAtual) { alert('Nenhum paciente selecionado'); return; }

                prescricaoMedicamentos = [];
                prescActiveTab = 'receita';
                document.getElementById('presc-busca-med').value = '';
                document.getElementById('presc-observacoes').value = '';
                document.getElementById('presc-confirma-assinatura').checked = false;
                document.getElementById('presc-busca-resultados').style.display = 'none';

                // Reset tabs
                switchPrescTab('receita');

                // Fill patient info
                const pac = pacienteAtual;
                document.getElementById('presc-paciente-nome').textContent = pac.nome || 'Paciente';
                const dataHoje = new Date().toLocaleDateString('pt-BR');
                document.getElementById('presc-paciente-info').textContent = `CPF: ${pac.cpf || 'N/A'} | Data: ${dataHoje}`;

                // Fill doctor info from doctors API
                try {
                    const doctors = await apiRequest('/api/doctors');
                    const doc = doctors.find(d => d.status === 'aprovado') || doctors[0];
                    if (doc) {
                        document.getElementById('presc-medico-nome').value = doc.nome || '';
                        document.getElementById('presc-medico-crm').value = doc.crm || '';
                    }
                } catch(e) {
                    console.error('Erro ao carregar médico:', e);
                }

                // Fetch medications from platform
                try {
                    medicamentosPlataforma = await apiRequest('/api/medicamentos');
                } catch(e) {
                    medicamentosPlataforma = [];
                    console.error('Erro ao carregar medicamentos:', e);
                }

                // Pre-fill laudo from anamnese if available
                prefillLaudoFromAnamnese();

                renderPrescricaoMedicamentos();

                const modal = document.getElementById('modal-prescricao');
                modal.style.display = 'flex';
            }

            function prefillLaudoFromAnamnese() {
                if (!pacienteAtual) return;
                // Try to auto-fill from patient data
                const pac = pacienteAtual;
                const cidEl = document.getElementById('laudo-cid');
                const histEl = document.getElementById('laudo-historico');
                const medEl = document.getElementById('laudo-medicacoes');

                // Keep existing values if present
                if (cidEl && !cidEl.value && pac.diagnostico) cidEl.value = pac.diagnostico;
                if (histEl && !histEl.value && pac.anamnese) histEl.value = pac.anamnese;
                if (medEl && !medEl.value && pac.medicacoes_atuais) medEl.value = pac.medicacoes_atuais;
            }

            function fecharModalPrescricao() {
                document.getElementById('modal-prescricao').style.display = 'none';
            }

            function buscarMedicamentosPrescricao(query) {
                const container = document.getElementById('presc-busca-resultados');
                if (!query || query.length < 2) {
                    container.style.display = 'none';
                    return;
                }

                const q = query.toLowerCase();
                const resultados = medicamentosPlataforma.filter(m =>
                    (m.nome || '').toLowerCase().includes(q) ||
                    (m.laboratorio || '').toLowerCase().includes(q) ||
                    (m.tipo || '').toLowerCase().includes(q) ||
                    (m.espectro || '').toLowerCase().includes(q)
                );

                if (resultados.length === 0) {
                    container.innerHTML = '<div style="padding:12px;color:#9ca3af;font-size:13px;text-align:center;">Nenhum medicamento encontrado</div>';
                    container.style.display = 'block';
                    return;
                }

                container.innerHTML = resultados.map(med => `
                    <div onclick="adicionarMedPrescricao('${med.id}')" style="padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;transition:background 0.15s;" onmouseover="this.style.background='#f0fdf4'" onmouseout="this.style.background='#fff'">
                        <div style="font-weight:600;font-size:13px;color:#065f46;">${med.nome || ''}</div>
                        <div style="font-size:11px;color:#6b7280;">
                            ${med.laboratorio ? `<span style="background:#e0f2fe;padding:1px 6px;border-radius:4px;margin-right:6px;">${med.laboratorio}</span>` : ''}
                            ${med.tipo ? `<span style="background:#fef3c7;padding:1px 6px;border-radius:4px;margin-right:6px;">${med.tipo}</span>` : ''}
                            ${med.espectro ? `<span style="background:#d1fae5;padding:1px 6px;border-radius:4px;margin-right:6px;">${med.espectro}</span>` : ''}
                            ${med.concentracao || med.concentration_mg_ml ? `<span>${med.concentration_mg_ml ? med.concentration_mg_ml + 'mg/ml' : med.concentracao}</span>` : ''}
                            ${med.volume_ml ? `<span style="margin-left:6px;">| ${med.volume_ml}ml</span>` : ''}
                        </div>
                    </div>
                `).join('');
                container.style.display = 'block';
            }

            function adicionarMedPrescricao(medId) {
                const med = medicamentosPlataforma.find(m => m.id === medId);
                if (!med) return;

                // Check if already added
                if (prescricaoMedicamentos.find(m => m.id === medId)) {
                    alert('Este medicamento já foi adicionado');
                    return;
                }

                // Default titration plan (escadinha padrão de 4 semanas)
                const defaultTitration = [
                    { period: 'Semana 1', morning: 1, afternoon: 0, night: 1, days: 7 },
                    { period: 'Semana 2', morning: 1, afternoon: 1, night: 1, days: 7 },
                    { period: 'Semana 3', morning: 2, afternoon: 1, night: 2, days: 7 },
                    { period: 'Manutenção', morning: 2, afternoon: 2, night: 2, days: 0 }
                ];

                prescricaoMedicamentos.push({
                    id: med.id,
                    nome: med.nome || '',
                    laboratorio: med.laboratorio || '',
                    tipo: med.tipo || '',
                    concentracao: med.concentracao || '',
                    volume: med.volume || '',
                    volume_ml: med.volume_ml || '',
                    concentration_mg_ml: med.concentration_mg_ml || '',
                    drops_per_ml: med.drops_per_ml || 20,
                    espectro: med.espectro || '',
                    fornecedor: med.fornecedor || '',
                    posologia: med.posologia || '',
                    dosagem: med.dosagem_ml || '',
                    titration_plan: defaultTitration,
                    calcResult: null
                });

                document.getElementById('presc-busca-med').value = '';
                document.getElementById('presc-busca-resultados').style.display = 'none';
                renderPrescricaoMedicamentos();
            }

            function removerMedPrescricao(idx) {
                prescricaoMedicamentos.splice(idx, 1);
                renderPrescricaoMedicamentos();
            }

            function updateTitrationValue(medIdx, rowIdx, field, value) {
                if (prescricaoMedicamentos[medIdx] && prescricaoMedicamentos[medIdx].titration_plan[rowIdx]) {
                    prescricaoMedicamentos[medIdx].titration_plan[rowIdx][field] = parseInt(value) || 0;
                    // Recalc daily total for display
                    renderPrescricaoMedicamentos();
                }
            }

            async function calcularFrascosCannabis(medIdx) {
                const med = prescricaoMedicamentos[medIdx];
                if (!med) return;

                const duracao = parseInt(document.getElementById('presc-duracao-meses')?.value || 24);

                // Check if product has calculator fields
                if (!med.volume_ml || !med.concentration_mg_ml) {
                    alert('⚠️ Este medicamento não possui os campos do calculador preenchidos (Volume ml, Concentração mg/ml). Edite o medicamento no cadastro e preencha os campos verdes.');
                    return;
                }

                const calcBtn = document.getElementById(`calc-btn-${medIdx}`);
                if (calcBtn) {
                    calcBtn.disabled = true;
                    calcBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                }

                try {
                    const result = await apiRequest('/api/cannabis/calcular', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            produto_id: med.id,
                            titration_plan: med.titration_plan,
                            duration_months: duracao
                        })
                    });

                    prescricaoMedicamentos[medIdx].calcResult = result;
                    renderPrescricaoMedicamentos();

                } catch(e) {
                    console.error('Erro no cálculo:', e);
                    alert('Erro ao calcular: ' + (e.message || 'Erro desconhecido'));
                } finally {
                    if (calcBtn) {
                        calcBtn.disabled = false;
                        calcBtn.innerHTML = '<i class="fas fa-calculator"></i> Calcular Frascos';
                    }
                }
            }

            function renderPrescricaoMedicamentos() {
                const container = document.getElementById('presc-medicamentos-lista');
                if (prescricaoMedicamentos.length === 0) {
                    container.innerHTML = '<div class="presc-empty-msg" style="text-align:center;padding:20px;color:#9ca3af;font-size:13px;"><i class="fas fa-arrow-up" style="margin-right:4px;"></i> Busque e adicione medicamentos acima</div>';
                    return;
                }

                container.innerHTML = prescricaoMedicamentos.map((med, idx) => {
                    // Build titration table (escadinha)
                    const titRows = med.titration_plan.map((row, ri) => {
                        const dailyTotal = (row.morning || 0) + (row.afternoon || 0) + (row.night || 0);
                        const isMaintenance = row.period === 'Manutenção';
                        return `
                            <tr style="border-bottom:1px solid #e5e7eb;${isMaintenance ? 'background:#f0fdf4;font-weight:600;' : ''}">
                                <td style="padding:6px 8px;font-size:12px;font-weight:${isMaintenance ? '700' : '500'};color:#065f46;">${row.period}</td>
                                <td style="padding:6px 4px;text-align:center;"><input type="number" min="0" max="20" value="${row.morning}" onchange="updateTitrationValue(${idx},${ri},'morning',this.value)" style="width:46px;text-align:center;padding:4px;border:1px solid #d1d5db;border-radius:4px;font-size:12px;"></td>
                                <td style="padding:6px 4px;text-align:center;"><input type="number" min="0" max="20" value="${row.afternoon}" onchange="updateTitrationValue(${idx},${ri},'afternoon',this.value)" style="width:46px;text-align:center;padding:4px;border:1px solid #d1d5db;border-radius:4px;font-size:12px;"></td>
                                <td style="padding:6px 4px;text-align:center;"><input type="number" min="0" max="20" value="${row.night}" onchange="updateTitrationValue(${idx},${ri},'night',this.value)" style="width:46px;text-align:center;padding:4px;border:1px solid #d1d5db;border-radius:4px;font-size:12px;"></td>
                                <td style="padding:6px 8px;text-align:center;font-weight:700;color:#059669;font-size:13px;">${dailyTotal} gt</td>
                                <td style="padding:6px 8px;text-align:center;font-size:11px;color:#6b7280;">${isMaintenance ? 'contínuo' : row.days + ' dias'}</td>
                            </tr>
                        `;
                    }).join('');

                    // Calc result display
                    let calcResultHtml = '';
                    if (med.calcResult) {
                        const r = med.calcResult;
                        calcResultHtml = `
                            <div style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);border:2px solid #059669;border-radius:10px;padding:14px;margin-top:10px;">
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                                    <i class="fas fa-check-circle" style="color:#059669;font-size:18px;"></i>
                                    <span style="font-weight:700;color:#065f46;font-size:14px;">Resultado do Cálculo Judicial</span>
                                </div>
                                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
                                    <div style="text-align:center;">
                                        <div style="font-size:24px;font-weight:800;color:#059669;">${r.total_drops || 0}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;">Gotas Totais</div>
                                    </div>
                                    <div style="text-align:center;">
                                        <div style="font-size:24px;font-weight:800;color:#059669;">${r.bottles_needed || 0}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;">Frascos Exatos</div>
                                    </div>
                                    <div style="text-align:center;background:#fff;border-radius:8px;padding:6px;">
                                        <div style="font-size:24px;font-weight:800;color:#dc2626;">${r.bottles_with_margin || 0}</div>
                                        <div style="font-size:10px;color:#dc2626;font-weight:700;text-transform:uppercase;">Frascos c/ Margem</div>
                                    </div>
                                    <div style="text-align:center;">
                                        <div style="font-size:24px;font-weight:800;color:#059669;">${r.mg_per_drop ? r.mg_per_drop.toFixed(2) : '—'}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;">mg/gota</div>
                                    </div>
                                </div>
                                <div style="margin-top:8px;font-size:11px;color:#047857;text-align:center;">
                                    <i class="fas fa-info-circle"></i> Margem de 10% aplicada para contingências (perda, derramamento)
                                </div>
                            </div>
                        `;
                    }

                    return `
                    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:16px;margin-bottom:14px;position:relative;">
                        <button onclick="removerMedPrescricao(${idx})" style="position:absolute;top:10px;right:10px;background:#fee2e2;border:none;color:#dc2626;width:28px;height:28px;border-radius:50%;cursor:pointer;font-size:12px;" title="Remover"><i class="fas fa-times"></i></button>

                        <!-- Product header -->
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                            <div style="background:#059669;width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;"><i class="fas fa-cannabis" style="color:#fff;font-size:16px;"></i></div>
                            <div>
                                <div style="font-weight:700;font-size:14px;color:#065f46;">${med.nome}</div>
                                <div style="font-size:11px;color:#6b7280;">
                                    ${med.laboratorio ? `<span style="background:#e0f2fe;padding:1px 6px;border-radius:4px;margin-right:4px;">${med.laboratorio}</span>` : ''}
                                    ${med.espectro ? `<span style="background:#d1fae5;padding:1px 6px;border-radius:4px;margin-right:4px;">${med.espectro}</span>` : ''}
                                    ${med.concentration_mg_ml ? `<span>${med.concentration_mg_ml}mg/ml</span>` : ''}
                                    ${med.volume_ml ? `<span style="margin-left:4px;">| ${med.volume_ml}ml</span>` : ''}
                                    ${med.fornecedor ? `<span style="margin-left:4px;">| ${med.fornecedor}</span>` : ''}
                                </div>
                            </div>
                        </div>

                        <!-- Escadinha de Titulação (Titration Table) -->
                        <div style="margin-bottom:12px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                                <span style="font-weight:700;font-size:12px;color:#065f46;text-transform:uppercase;letter-spacing:0.5px;"><i class="fas fa-stairs" style="margin-right:4px;"></i> Escada de Titulação (Posologia Progressiva)</span>
                                <button id="calc-btn-${idx}" onclick="calcularFrascosCannabis(${idx})" style="padding:6px 14px;background:#059669;color:#fff;border:none;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:4px;"><i class="fas fa-calculator"></i> Calcular Frascos</button>
                            </div>
                            <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
                                <thead>
                                    <tr style="background:#065f46;color:#fff;">
                                        <th style="padding:8px;text-align:left;font-size:11px;font-weight:600;">Período</th>
                                        <th style="padding:8px;text-align:center;font-size:11px;font-weight:600;">☀️ Manhã</th>
                                        <th style="padding:8px;text-align:center;font-size:11px;font-weight:600;">🌤️ Tarde</th>
                                        <th style="padding:8px;text-align:center;font-size:11px;font-weight:600;">🌙 Noite</th>
                                        <th style="padding:8px;text-align:center;font-size:11px;font-weight:600;">Total/dia</th>
                                        <th style="padding:8px;text-align:center;font-size:11px;font-weight:600;">Duração</th>
                                    </tr>
                                </thead>
                                <tbody>${titRows}</tbody>
                            </table>
                        </div>

                        <!-- Observações personalizadas do med -->
                        <div>
                            <label style="font-size:11px;color:#374151;display:block;margin-bottom:2px;">Observações sobre este medicamento</label>
                            <textarea id="presc-med-obs-${idx}" rows="2" placeholder="Instruções específicas: sublingual, com ou sem alimento, horário preferencial..." style="width:100%;padding:8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;resize:vertical;box-sizing:border-box;">${med.posologia || ''}</textarea>
                        </div>

                        ${calcResultHtml}
                    </div>
                    `;
                }).join('');
            }

            // ── Seleção de Provedor ICP-Brasil (Passo 2 do diagrama IntegraICP) ──
            function showClearanceSelection(clearances, sessionId) {
                // Se apenas 1 provedor, abrir direto
                if (clearances.length === 1) {
                    window.open(clearances[0].clearanceEndpoint, 'integraicp_auth', 'width=600,height=700,scrollbars=yes');
                    alert('🔐 Autenticação ICP-Brasil iniciada via ' + clearances[0].productName + '.\n\nApós autenticar com seu certificado digital, a assinatura será finalizada automaticamente.');
                    return;
                }

                // Múltiplos provedores: mostrar modal de seleção
                let overlay = document.getElementById('clearance-overlay');
                if (overlay) overlay.remove();

                overlay = document.createElement('div');
                overlay.id = 'clearance-overlay';
                overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;';

                let html = `<div style="background:#fff;border-radius:16px;padding:32px;max-width:480px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
                    <div style="text-align:center;margin-bottom:24px;">
                        <i class="fas fa-shield-alt" style="font-size:36px;color:#1e293b;margin-bottom:12px;display:block;"></i>
                        <h3 style="margin:0 0 8px;color:#1e293b;font-size:18px;">Selecione o Provedor de Certificado Digital</h3>
                        <p style="margin:0;color:#64748b;font-size:13px;">Escolha o provedor onde seu certificado ICP-Brasil está cadastrado</p>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:12px;">`;

                clearances.forEach((c, idx) => {
                    const iconMap = {
                        'VIDaaS': 'fa-id-badge',
                        'BirdID': 'fa-dove',
                        'SafeID': 'fa-lock',
                        'RemoteID': 'fa-cloud'
                    };
                    const icon = iconMap[c.productName] || 'fa-certificate';
                    html += `<button onclick="selectClearance(${idx})" style="display:flex;align-items:center;gap:16px;padding:16px 20px;background:#f8fafc;border:2px solid #e2e8f0;border-radius:12px;cursor:pointer;transition:all 0.2s;text-align:left;" onmouseover="this.style.borderColor='#1e293b';this.style.background='#f1f5f9'" onmouseout="this.style.borderColor='#e2e8f0';this.style.background='#f8fafc'">
                        <i class="fas ${icon}" style="font-size:24px;color:#1e293b;width:32px;text-align:center;"></i>
                        <div>
                            <div style="font-weight:700;color:#1e293b;font-size:15px;">${c.productName}</div>
                            <div style="color:#64748b;font-size:12px;">${c.providerName}${c.clearanceType === 'IDENTIFICATION' ? ' — Certificado em Nuvem' : ''}</div>
                        </div>
                        <i class="fas fa-chevron-right" style="margin-left:auto;color:#94a3b8;"></i>
                    </button>`;
                });

                html += `</div>
                    <button onclick="document.getElementById('clearance-overlay').remove()" style="width:100%;margin-top:16px;padding:12px;background:none;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;color:#64748b;font-size:13px;">Cancelar</button>
                </div>`;

                overlay.innerHTML = html;
                document.body.appendChild(overlay);

                // Guardar clearances para uso no callback
                window._pendingClearances = clearances;
                window._pendingSessionId = sessionId;
            }

            function selectClearance(idx) {
                const clearances = window._pendingClearances || [];
                const c = clearances[idx];
                if (!c) return;

                // Remover overlay
                const overlay = document.getElementById('clearance-overlay');
                if (overlay) overlay.remove();

                // Passo 3 do diagrama: browser abre clearanceEndpoint → 302 → provedor
                window.open(c.clearanceEndpoint, 'integraicp_auth', 'width=600,height=700,scrollbars=yes');
                alert('🔐 Autenticação iniciada via ' + c.productName + ' (' + c.providerName + ').\n\nAutentique-se com seu certificado digital (QR Code ou OTP).\nApós a autenticação, a assinatura será finalizada automaticamente.');
            }

            async function assinarPrescricao() {
                if (!pacienteAtual) { alert('Nenhum paciente selecionado'); return; }
                if (!document.getElementById('presc-confirma-assinatura').checked) {
                    alert('Confirme a assinatura digital para prosseguir');
                    return;
                }

                const medicoNome = document.getElementById('presc-medico-nome').value;
                const medicoCrm = document.getElementById('presc-medico-crm').value;
                if (!medicoNome || !medicoCrm) {
                    alert('Dados do médico são obrigatórios para assinatura');
                    return;
                }

                const signatureProvider = document.getElementById('presc-signature-provider')?.value || 'vidaas';
                const duracaoMeses = parseInt(document.getElementById('presc-duracao-meses')?.value || 24);

                const btn = document.getElementById('btn-assinar-prescricao');
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando documentação...';

                try {
                    let prescricaoId = null;
                    let laudoId = null;

                    // 1. Save prescription (if medications added)
                    if (prescricaoMedicamentos.length > 0) {
                        const medsPayload = prescricaoMedicamentos.map((med, idx) => ({
                            id: med.id,
                            nome: med.nome,
                            laboratorio: med.laboratorio,
                            tipo: med.tipo,
                            concentracao: med.concentracao,
                            volume: med.volume,
                            volume_ml: med.volume_ml,
                            concentration_mg_ml: med.concentration_mg_ml,
                            drops_per_ml: med.drops_per_ml,
                            espectro: med.espectro,
                            fornecedor: med.fornecedor,
                            posologia: document.getElementById(`presc-med-obs-${idx}`)?.value || med.posologia,
                            titration_plan: med.titration_plan,
                            calcResult: med.calcResult
                        }));

                        const prescResult = await apiRequest(`/api/pacientes/${pacienteAtual.id}/prescricao`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                medicamentos: medsPayload,
                                observacoes: document.getElementById('presc-observacoes').value,
                                medico_id: '',
                                medico_nome: medicoNome,
                                medico_crm: medicoCrm,
                                duracao_meses: duracaoMeses,
                                signature_provider: signatureProvider
                            })
                        });
                        prescricaoId = prescResult.id;
                    }

                    // 2. Save laudo (if tab has content)
                    const laudoCid = document.getElementById('laudo-cid')?.value;
                    const laudoHistorico = document.getElementById('laudo-historico')?.value;
                    const laudoJustificativa = document.getElementById('laudo-justificativa')?.value;
                    if (laudoCid && laudoHistorico) {
                        const laudoResult = await apiRequest(`/api/pacientes/${pacienteAtual.id}/laudo`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                diagnostico_cid: laudoCid,
                                historico_clinico: laudoHistorico,
                                tratamentos_anteriores: document.getElementById('laudo-tratamentos')?.value || '',
                                medicacoes_atuais: document.getElementById('laudo-medicacoes')?.value || '',
                                justificativa_cannabis: laudoJustificativa || '',
                                consequencias_negativa: document.getElementById('laudo-consequencias')?.value || '',
                                hipossuficiencia: document.getElementById('laudo-hipossuficiencia')?.value || '',
                                conclusao: `Diante do exposto, prescrevo o tratamento com cannabis medicinal conforme prescrição anexa.`,
                                medico_nome: medicoNome,
                                medico_crm: medicoCrm
                            })
                        });
                        laudoId = laudoResult.id;
                    }

                    // 3. Save exam requests (if any checked)
                    const examesLab = Array.from(document.querySelectorAll('.presc-exam-lab:checked')).map(el => el.value);
                    const exameFarmaco = document.getElementById('presc-exam-farmaco')?.checked;
                    if (examesLab.length > 0 || exameFarmaco) {
                        const examesPayload = {
                            exames_laboratoriais: examesLab,
                            farmacogenetico: exameFarmaco
                        };
                        // Save exams as part of prontuário
                        await apiRequest(`/api/pacientes/${pacienteAtual.id}/prontuario`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                tipo: 'pedido_exame',
                                titulo: 'Pedido de Exames – Tratamento Cannabis',
                                descricao: `Exames solicitados: ${examesLab.join(', ')}${exameFarmaco ? ', Painel Farmacogenético Cannabis' : ''}`,
                                dados: examesPayload,
                                medico_nome: medicoNome,
                                medico_crm: medicoCrm
                            })
                        });
                    }

                    // 4. Request digital signature via IntegraICP
                    if (prescricaoId) {
                        try {
                            const sigResult = await apiRequest('/api/assinatura/iniciar', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    doc_type: 'prescricao',
                                    doc_id: prescricaoId,
                                    provider: signatureProvider,
                                    medico_nome: medicoNome,
                                    medico_crm: medicoCrm
                                })
                            });

                            if (sigResult.mode === 'integraicp' && sigResult.clearances && sigResult.clearances.length > 0) {
                                // Passo 2 do diagrama: mostrar provedores para seleção
                                showClearanceSelection(sigResult.clearances, sigResult.session_id);
                            } else if (sigResult.mode === 'integraicp' && sigResult.redirect_url) {
                                // Autostart: redirect direto
                                window.open(sigResult.redirect_url, 'integraicp_auth', 'width=600,height=700,scrollbars=yes');
                                alert('🔐 Autenticação ICP-Brasil iniciada.\n\nApós autenticar com seu certificado digital, a assinatura será finalizada automaticamente.');
                            }
                        } catch(sigErr) {
                            console.warn('Assinatura digital pendente:', sigErr);
                        }
                    }

                    // Also sign laudo if exists
                    if (laudoId) {
                        try {
                            const laudoSigResult = await apiRequest('/api/assinatura/iniciar', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    doc_type: 'laudo',
                                    doc_id: laudoId,
                                    provider: signatureProvider,
                                    medico_nome: medicoNome,
                                    medico_crm: medicoCrm
                                })
                            });
                            if (laudoSigResult.mode === 'integraicp' && laudoSigResult.clearances) {
                                // Se prescrição não iniciou auth, usar clearances do laudo
                                if (!prescricaoId) {
                                    showClearanceSelection(laudoSigResult.clearances, laudoSigResult.session_id);
                                }
                                // Se prescricao já iniciou, laudo será assinado na mesma sessão futuramente
                            } else if (laudoSigResult.mode === 'integraicp' && laudoSigResult.redirect_url) {
                                if (!prescricaoId) {
                                    window.open(laudoSigResult.redirect_url, 'integraicp_auth', 'width=600,height=700,scrollbars=yes');
                                }
                            }
                        } catch(sigErr) {
                            console.warn('Assinatura laudo pendente:', sigErr);
                        }
                    }

                    // Build success message
                    let msg = '✅ Documentação salva com sucesso!\n\n';
                    if (prescricaoId) msg += '📋 Receita cannabis assinada e salva\n';
                    if (laudoId) msg += '📄 Laudo Médico Circunstanciado registrado\n';
                    if (examesLab.length > 0 || exameFarmaco) msg += '🧪 Pedido de exames registrado\n';
                    msg += '\nTodos os documentos foram salvos no prontuário do paciente.';
                    alert(msg);

                    fecharModalPrescricao();

                    // Reload prescriptions and prontuário
                    carregarPrescricoesFicha(pacienteAtual.id);
                    if (typeof carregarProntuario === 'function') carregarProntuario(pacienteAtual.id);

                } catch(e) {
                    console.error('Erro ao salvar documentação:', e);
                    alert('Erro ao salvar: ' + (e.message || 'Erro desconhecido'));
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-pen-fancy"></i> Assinar Digitalmente & Salvar';
                }
            }

            async function carregarPrescricoesFicha(pacId) {
                const container = document.getElementById('prescricoes-lista-ficha');
                if (!container) return;

                try {
                    const prescricoes = await apiRequest(`/api/pacientes/${pacId}/prescricoes`);
                    if (!prescricoes || prescricoes.length === 0) {
                        container.innerHTML = '<div style="text-align:center;padding:20px;color:#9ca3af;font-size:13px;"><i class="fas fa-prescription-bottle-alt" style="font-size:28px;margin-bottom:8px;display:block;color:#6ee7b7;"></i>Nenhuma prescrição realizada nesta consulta</div>';
                        return;
                    }

                    container.innerHTML = prescricoes.map(presc => {
                        const dt = presc.data ? new Date(presc.data) : new Date();
                        const dataStr = dt.toLocaleDateString('pt-BR') + ' ' + dt.toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'});
                        const medsNomes = (presc.medicamentos || []).map(m => m.nome).join(', ');
                        const isSigned = presc.is_signed;
                        return `
                            <div style="background:#fff;border:1px solid #d1fae5;border-radius:8px;padding:12px;margin-bottom:8px;transition:all 0.15s;" onmouseover="this.style.borderColor='#059669';this.style.boxShadow='0 2px 8px rgba(5,150,105,0.15)'" onmouseout="this.style.borderColor='#d1fae5';this.style.boxShadow='none'">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                                    <div style="display:flex;align-items:center;gap:6px;cursor:pointer;" onclick="visualizarPrescricao('${presc.id}')">
                                        <i class="fas fa-prescription" style="color:#059669;font-size:14px;"></i>
                                        <span style="font-weight:600;color:#065f46;font-size:13px;">Prescrição Cannabis</span>
                                        <span style="background:${isSigned ? '#d1fae5' : '#fef3c7'};color:${isSigned ? '#065f46' : '#92400e'};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;">${isSigned ? '✓ ASSINADA' : '⏳ PENDENTE'}</span>
                                    </div>
                                    <div style="display:flex;align-items:center;gap:6px;">
                                        <button onclick="event.stopPropagation();abrirEnviarAssinatura('prescricao','${presc.id}')" title="Enviar para assinatura do paciente" style="background:#1e293b;color:#fff;border:none;border-radius:6px;padding:4px 10px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:4px;">
                                            <i class="fas fa-paper-plane"></i> Enviar p/ Paciente
                                        </button>
                                        <span style="font-size:11px;color:#9ca3af;">${dataStr}</span>
                                    </div>
                                </div>
                                <div style="font-size:12px;color:#374151;margin-bottom:4px;cursor:pointer;" onclick="visualizarPrescricao('${presc.id}')">${medsNomes}</div>
                                <div style="font-size:11px;color:#6b7280;">
                                    ${presc.medico_nome || ''} ${presc.medico_crm ? '• ' + presc.medico_crm : ''}
                                    ${presc.duracao_meses ? ' • ' + presc.duracao_meses + ' meses' : ''}
                                </div>
                            </div>
                        `;
                    }).join('');
                } catch(e) {
                    console.error('Erro ao carregar prescrições:', e);
                }
            }

            function visualizarPrescricao(prescId) {
                if (typeof abrirDocViewer === 'function') {
                    apiRequest(`/api/pacientes/${pacienteAtual.id}/prontuario`).then(data => {
                        const receituarios = data.receituario || [];
                        const doc = receituarios.find(r => r.titulo && r.titulo.includes('Prescrição Cannabis'));
                        if (doc) {
                            abrirDocViewer(doc, 'receituario');
                        }
                    }).catch(e => console.error('Erro:', e));
                }
            }

            // ===== INTELLISIGN — Enviar documentos para assinatura do paciente =====
            function abrirEnviarAssinatura(docType, docId) {
                if (!pacienteAtual) { alert('Nenhum paciente selecionado'); return; }

                let overlay = document.getElementById('intellisign-overlay');
                if (overlay) overlay.remove();

                const pacEmail = pacienteAtual.email || '';
                const pacTel = pacienteAtual.telefone || '';

                overlay = document.createElement('div');
                overlay.id = 'intellisign-overlay';
                overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;';
                overlay.innerHTML = `<div style="background:#fff;border-radius:16px;padding:32px;max-width:500px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
                    <div style="text-align:center;margin-bottom:20px;">
                        <i class="fas fa-paper-plane" style="font-size:32px;color:#1e293b;margin-bottom:10px;display:block;"></i>
                        <h3 style="margin:0 0 6px;color:#1e293b;font-size:17px;">Enviar para Assinatura do Paciente</h3>
                        <p style="margin:0;color:#64748b;font-size:12px;">O paciente receberá um link para assinar eletronicamente via Intellisign</p>
                    </div>

                    <div style="background:#f8fafc;border-radius:10px;padding:16px;margin-bottom:16px;">
                        <div style="font-weight:600;color:#1e293b;font-size:13px;margin-bottom:4px;"><i class="fas fa-user" style="margin-right:6px;color:#059669;"></i>${pacienteAtual.nome || 'Paciente'}</div>
                        <div style="font-size:12px;color:#64748b;">${docType === 'prescricao' ? 'Prescrição Cannabis' : 'Laudo Médico'} — ${docId}</div>
                    </div>

                    <div style="margin-bottom:14px;">
                        <label style="display:block;font-weight:600;color:#374151;font-size:12px;margin-bottom:6px;">Canal de envio:</label>
                        <div style="display:flex;gap:8px;">
                            <label style="flex:1;display:flex;align-items:center;gap:8px;padding:12px;border:2px solid #e2e8f0;border-radius:10px;cursor:pointer;transition:all 0.2s;" id="lbl-canal-email" onclick="document.getElementById('canal-email').checked=true;document.getElementById('lbl-canal-email').style.borderColor='#1e293b';document.getElementById('lbl-canal-whats').style.borderColor='#e2e8f0'">
                                <input type="radio" name="envio-canal" id="canal-email" value="email" checked style="display:none;">
                                <i class="fas fa-envelope" style="font-size:18px;color:#1e293b;"></i>
                                <div>
                                    <div style="font-weight:600;font-size:12px;color:#1e293b;">Email</div>
                                    <div style="font-size:11px;color:#64748b;">${pacEmail || 'Não cadastrado'}</div>
                                </div>
                            </label>
                            <label style="flex:1;display:flex;align-items:center;gap:8px;padding:12px;border:2px solid #e2e8f0;border-radius:10px;cursor:pointer;transition:all 0.2s;" id="lbl-canal-whats" onclick="document.getElementById('canal-whatsapp').checked=true;document.getElementById('lbl-canal-whats').style.borderColor='#25d366';document.getElementById('lbl-canal-email').style.borderColor='#e2e8f0'">
                                <input type="radio" name="envio-canal" id="canal-whatsapp" value="whatsapp" style="display:none;">
                                <i class="fab fa-whatsapp" style="font-size:20px;color:#25d366;"></i>
                                <div>
                                    <div style="font-weight:600;font-size:12px;color:#1e293b;">WhatsApp</div>
                                    <div style="font-size:11px;color:#64748b;">${pacTel || 'Não cadastrado'}</div>
                                </div>
                            </label>
                        </div>
                    </div>

                    <div style="margin-bottom:16px;">
                        <label style="display:block;font-weight:600;color:#374151;font-size:12px;margin-bottom:4px;">Mensagem personalizada (opcional):</label>
                        <textarea id="envio-mensagem" rows="3" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;padding:10px;font-size:12px;resize:vertical;box-sizing:border-box;" placeholder="Mensagem adicional para o paciente..."></textarea>
                    </div>

                    <div style="display:flex;gap:10px;">
                        <button onclick="document.getElementById('intellisign-overlay').remove()" style="flex:1;padding:12px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;color:#64748b;font-size:13px;font-weight:600;">Cancelar</button>
                        <button onclick="executarEnvioAssinatura('${docType}','${docId}')" id="btn-enviar-assinatura" style="flex:2;padding:12px;background:linear-gradient(135deg,#1e293b,#0f172a);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:6px;">
                            <i class="fas fa-paper-plane"></i> Enviar para Assinatura
                        </button>
                    </div>
                </div>`;
                document.body.appendChild(overlay);
            }

            async function executarEnvioAssinatura(docType, docId) {
                const btn = document.getElementById('btn-enviar-assinatura');
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';

                const canal = document.getElementById('canal-whatsapp')?.checked ? 'whatsapp' : 'email';
                const mensagem = document.getElementById('envio-mensagem')?.value || '';

                try {
                    const result = await apiRequest('/api/intellisign/enviar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            paciente_id: pacienteAtual.id,
                            doc_type: docType,
                            doc_id: docId,
                            canal: canal,
                            mensagem: mensagem
                        })
                    });

                    if (result.success) {
                        document.getElementById('intellisign-overlay').remove();
                        alert('✅ Documento enviado para assinatura!\n\nEnviado para: ' + result.enviado_para + '\n\nO paciente receberá um link para assinar eletronicamente.');
                        // Reload envelope tracking
                        if (typeof carregarEnvelopesPaciente === 'function') {
                            carregarEnvelopesPaciente(pacienteAtual.id);
                        }
                    } else {
                        alert('⚠️ Erro: ' + (result.error || result.message || 'Erro desconhecido'));
                    }
                } catch(e) {
                    alert('❌ Erro ao enviar: ' + (e.message || 'Erro de conexão'));
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar para Assinatura';
                }
            }

            async function carregarEnvelopesPaciente(pacId) {
                const container = document.getElementById('envelopes-paciente-lista');
                if (!container) return;

                try {
                    const envelopes = await apiRequest(`/api/intellisign/envelopes?paciente_id=${pacId}`);
                    if (!envelopes || envelopes.length === 0) {
                        container.innerHTML = '<div style="text-align:center;padding:16px;color:#9ca3af;font-size:12px;">Nenhum documento enviado para assinatura</div>';
                        return;
                    }

                    const statusMap = {
                        'draft': { label: 'Rascunho', color: '#6b7280', bg: '#f3f4f6', icon: 'fa-file' },
                        'in-transit': { label: 'Aguardando', color: '#d97706', bg: '#fef3c7', icon: 'fa-clock' },
                        'completed': { label: 'Assinado', color: '#059669', bg: '#d1fae5', icon: 'fa-check-circle' },
                        'cancelled': { label: 'Cancelado', color: '#dc2626', bg: '#fee2e2', icon: 'fa-times-circle' },
                        'expired': { label: 'Expirado', color: '#9333ea', bg: '#f3e8ff', icon: 'fa-hourglass-end' }
                    };

                    container.innerHTML = envelopes.map(env => {
                        const st = statusMap[env.status] || statusMap['in-transit'];
                        const dt = env.enviado_em ? new Date(env.enviado_em).toLocaleDateString('pt-BR') : '';
                        return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
                                    <i class="fas ${st.icon}" style="color:${st.color};font-size:12px;"></i>
                                    <span style="font-weight:600;color:#1e293b;font-size:12px;">${env.doc_titulo || env.doc_type}</span>
                                    <span style="background:${st.bg};color:${st.color};padding:1px 6px;border-radius:8px;font-size:9px;font-weight:600;">${st.label}</span>
                                </div>
                                <div style="font-size:11px;color:#6b7280;">${env.canal === 'whatsapp' ? '📱' : '📧'} ${env.enviado_para} • ${dt}</div>
                            </div>
                            <div style="display:flex;gap:4px;">
                                ${env.status === 'in-transit' ? `<button onclick="reenviarNotificacao('${env.id}')" title="Reenviar" style="background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:10px;"><i class="fas fa-redo"></i></button>` : ''}
                                ${env.status === 'completed' ? `<button onclick="downloadEnvelopeAssinado('${env.id}')" title="Download" style="background:#d1fae5;border:1px solid #a7f3d0;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:10px;color:#065f46;"><i class="fas fa-download"></i></button>` : ''}
                                <button onclick="consultarStatusEnvelope('${env.id}')" title="Atualizar status" style="background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:10px;"><i class="fas fa-sync-alt"></i></button>
                            </div>
                        </div>`;
                    }).join('');
                } catch(e) {
                    console.error('Erro ao carregar envelopes:', e);
                }
            }

            async function reenviarNotificacao(envelopeId) {
                if (!confirm('Reenviar notificação para o paciente?')) return;
                try {
                    const result = await apiRequest(`/api/intellisign/reenviar/${envelopeId}`, { method: 'POST' });
                    if (result.success) {
                        alert('✅ Notificação reenviada ao paciente!');
                    } else {
                        alert('⚠️ ' + (result.error || 'Erro ao reenviar'));
                    }
                } catch(e) {
                    alert('Erro: ' + e.message);
                }
            }

            async function consultarStatusEnvelope(envelopeId) {
                try {
                    const result = await apiRequest(`/api/intellisign/envelope/${envelopeId}`);
                    const state = result.envelope?.state || result.envelope?.status || result.local?.status || 'desconhecido';
                    alert('Status: ' + state.toUpperCase());
                    if (pacienteAtual) carregarEnvelopesPaciente(pacienteAtual.id);
                } catch(e) {
                    alert('Erro: ' + e.message);
                }
            }

            function downloadEnvelopeAssinado(envelopeId) {
                window.open(`/api/intellisign/download/${envelopeId}`, '_blank');
            }

            // ===== WEBHOOK CONFIG =====
            async function carregarWebhookConfig() {
                try {
                    const config = await apiRequest('/api/webhooks-config');
                    const urlInput = document.getElementById('webhook-prescricao-url');
                    const ativoInput = document.getElementById('webhook-prescricao-ativo');
                    if (urlInput) urlInput.value = config.prescricao_url || '';
                    if (ativoInput) ativoInput.checked = config.prescricao_ativo || false;
                } catch(e) {
                    console.error('Erro ao carregar webhook config:', e);
                }
            }

            async function salvarWebhookConfig() {
                const feedback = document.getElementById('webhook-feedback');
                try {
                    const url = document.getElementById('webhook-prescricao-url').value;
                    const ativo = document.getElementById('webhook-prescricao-ativo').checked;
                    await apiRequest('/api/webhooks-config', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prescricao_url: url, prescricao_ativo: ativo })
                    });
                    feedback.style.display = 'block';
                    feedback.style.color = '#059669';
                    feedback.textContent = '✅ Configuração salva com sucesso!';
                    setTimeout(() => feedback.style.display = 'none', 3000);
                } catch(e) {
                    feedback.style.display = 'block';
                    feedback.style.color = '#dc2626';
                    feedback.textContent = '❌ Erro ao salvar: ' + (e.message || 'Erro desconhecido');
                }
            }

            async function testarWebhook() {
                const feedback = document.getElementById('webhook-feedback');
                feedback.style.display = 'block';
                feedback.style.color = '#3b82f6';
                feedback.textContent = '⏳ Enviando teste...';
                try {
                    const result = await apiRequest('/api/webhooks-config/test', { method: 'POST' });
                    feedback.style.color = '#059669';
                    feedback.textContent = `✅ ${result.message}`;
                    setTimeout(() => feedback.style.display = 'none', 5000);
                } catch(e) {
                    feedback.style.color = '#dc2626';
                    feedback.textContent = '❌ Erro no teste: ' + (e.data?.error || e.message || 'Falha na conexão');
                }
            }

            // ===== ASSINATURA DIGITAL — CONFIGURAÇÕES =====
            async function carregarConfigAssinatura() {
                try {
                    const config = await apiRequest('/api/assinatura-config');
                    // IntegraICP
                    const chEl = document.getElementById('cfg-integraicp-channel');
                    const cbEl = document.getElementById('cfg-integraicp-callback');
                    if (chEl) chEl.value = config.integraicp_channel_id || '';
                    if (cbEl) cbEl.value = config.integraicp_callback_url || '';
                    // Intellisign
                    const ciEl = document.getElementById('cfg-intellisign-client-id');
                    const csEl = document.getElementById('cfg-intellisign-client-secret');
                    const orgEl = document.getElementById('cfg-intellisign-org');
                    if (ciEl) ciEl.value = config.intellisign_client_id || '';
                    if (csEl) csEl.value = config.intellisign_client_secret_masked || '';
                    if (orgEl) orgEl.value = config.intellisign_organization || '';
                    // Status
                    const stIcp = document.getElementById('status-integraicp');
                    const stIs = document.getElementById('status-intellisign');
                    if (stIcp) {
                        if (config.integraicp_configured) {
                            stIcp.innerHTML = '<span style="color:#059669;"><i class="fas fa-check-circle"></i> Configurado e ativo</span>';
                        } else {
                            stIcp.innerHTML = '<span style="color:#d97706;"><i class="fas fa-exclamation-triangle"></i> Não configurado — modo simulado</span>';
                        }
                    }
                    if (stIs) {
                        if (config.intellisign_configured) {
                            stIs.innerHTML = '<span style="color:#059669;"><i class="fas fa-check-circle"></i> Configurado e ativo</span>';
                        } else {
                            stIs.innerHTML = '<span style="color:#d97706;"><i class="fas fa-exclamation-triangle"></i> Não configurado</span>';
                        }
                    }
                } catch(e) {
                    console.error('Erro ao carregar config assinatura:', e);
                }
                // Carregar dados auxiliares
                carregarCertificadosMedicos();
                carregarHistoricoEnvios();
            }

            async function salvarConfigAssinatura(provider) {
                const feedbackEl = document.getElementById('feedback-' + provider);
                if (feedbackEl) { feedbackEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...'; feedbackEl.style.color = '#3b82f6'; }
                try {
                    const body = {};
                    if (provider === 'integraicp') {
                        body.integraicp_channel_id = document.getElementById('cfg-integraicp-channel')?.value || '';
                        body.integraicp_callback_url = document.getElementById('cfg-integraicp-callback')?.value || '';
                    } else if (provider === 'intellisign') {
                        body.intellisign_client_id = document.getElementById('cfg-intellisign-client-id')?.value || '';
                        const secretVal = document.getElementById('cfg-intellisign-client-secret')?.value || '';
                        if (secretVal && !secretVal.includes('•')) body.intellisign_client_secret = secretVal;
                        body.intellisign_organization = document.getElementById('cfg-intellisign-org')?.value || '';
                    }
                    await apiRequest('/api/assinatura-config', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(body)
                    });
                    if (feedbackEl) { feedbackEl.innerHTML = '<span style="color:#059669;"><i class="fas fa-check-circle"></i> Salvo com sucesso!</span>'; }
                    setTimeout(() => { if (feedbackEl) feedbackEl.innerHTML = ''; }, 3000);
                    carregarConfigAssinatura();
                } catch(e) {
                    if (feedbackEl) { feedbackEl.innerHTML = '<span style="color:#dc2626;"><i class="fas fa-times-circle"></i> Erro: ' + (e.message || 'Falha') + '</span>'; }
                }
            }

            async function testarConexaoAssinatura(provider) {
                const feedbackEl = document.getElementById('feedback-' + provider);
                if (feedbackEl) { feedbackEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testando conexão...'; feedbackEl.style.color = '#3b82f6'; }
                try {
                    const result = await apiRequest('/api/assinatura-config/test/' + provider, { method: 'POST' });
                    if (result.success) {
                        if (feedbackEl) { feedbackEl.innerHTML = '<span style="color:#059669;"><i class="fas fa-check-circle"></i> ' + (result.message || 'Conexão OK!') + '</span>'; }
                    } else {
                        if (feedbackEl) { feedbackEl.innerHTML = '<span style="color:#dc2626;"><i class="fas fa-times-circle"></i> ' + (result.error || 'Falha na conexão') + '</span>'; }
                    }
                    setTimeout(() => { if (feedbackEl) feedbackEl.innerHTML = ''; }, 5000);
                } catch(e) {
                    if (feedbackEl) { feedbackEl.innerHTML = '<span style="color:#dc2626;"><i class="fas fa-times-circle"></i> ' + (e.message || 'Erro de conexão') + '</span>'; }
                }
            }

            function toggleSecretVisibility() {
                const el = document.getElementById('cfg-intellisign-client-secret');
                if (el) el.type = el.type === 'password' ? 'text' : 'password';
            }

            async function carregarCertificadosMedicos() {
                const container = document.getElementById('lista-certificados-medicos');
                if (!container) return;
                try {
                    const doctors = await apiRequest('/api/doctors');
                    const aprovados = doctors.filter(d => d.status === 'aprovado');
                    if (aprovados.length === 0) {
                        container.innerHTML = '<div style="text-align:center;padding:16px;color:#9ca3af;font-size:12px;">Nenhum médico aprovado na plataforma</div>';
                        return;
                    }
                    container.innerHTML = aprovados.map(doc => {
                        const hasCert = doc.certificado_vinculado || false;
                        return `<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:#fff;border:1px solid #fde68a;border-radius:8px;margin-bottom:6px;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <div style="width:36px;height:36px;border-radius:50%;background:${hasCert ? '#d1fae5' : '#f3f4f6'};display:flex;align-items:center;justify-content:center;">
                                    <i class="fas ${hasCert ? 'fa-certificate' : 'fa-user-md'}" style="color:${hasCert ? '#059669' : '#9ca3af'};font-size:14px;"></i>
                                </div>
                                <div>
                                    <div style="font-weight:600;font-size:13px;color:#1f2937;">${doc.nome || 'Médico'}</div>
                                    <div style="font-size:11px;color:#6b7280;">CRM: ${doc.crm || '---'} ${doc.especialidade ? '• ' + doc.especialidade : ''}</div>
                                </div>
                            </div>
                            <div>
                                ${hasCert
                                    ? '<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:600;"><i class="fas fa-check"></i> Certificado vinculado</span>'
                                    : '<span style="background:#fef3c7;color:#92400e;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:600;"><i class="fas fa-exclamation-triangle"></i> Sem certificado</span>'
                                }
                            </div>
                        </div>`;
                    }).join('');
                } catch(e) {
                    container.innerHTML = '<div style="text-align:center;padding:16px;color:#dc2626;font-size:12px;">Erro ao carregar médicos</div>';
                }
            }

            async function carregarHistoricoEnvios() {
                const container = document.getElementById('historico-envios-assinatura');
                if (!container) return;
                try {
                    const envelopes = await apiRequest('/api/intellisign/envelopes');
                    if (!envelopes || envelopes.length === 0) {
                        container.innerHTML = '<div style="text-align:center;padding:16px;color:#9ca3af;font-size:12px;">Nenhum documento enviado para assinatura ainda</div>';
                        return;
                    }
                    const statusMap = {
                        'draft': { label: 'Rascunho', color: '#6b7280', bg: '#f3f4f6', icon: 'fa-file' },
                        'in-transit': { label: 'Aguardando', color: '#d97706', bg: '#fef3c7', icon: 'fa-clock' },
                        'completed': { label: 'Assinado', color: '#059669', bg: '#d1fae5', icon: 'fa-check-circle' },
                        'cancelled': { label: 'Cancelado', color: '#dc2626', bg: '#fee2e2', icon: 'fa-times-circle' },
                        'expired': { label: 'Expirado', color: '#9333ea', bg: '#f3e8ff', icon: 'fa-hourglass-end' }
                    };
                    const ultimos = envelopes.slice(-10).reverse();
                    container.innerHTML = ultimos.map(env => {
                        const st = statusMap[env.status] || statusMap['in-transit'];
                        const dt = env.enviado_em ? new Date(env.enviado_em).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' }) : '';
                        return `<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:#fff;border:1px solid #e9d5ff;border-radius:8px;margin-bottom:4px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <i class="fas ${st.icon}" style="color:${st.color};font-size:12px;"></i>
                                <div>
                                    <div style="font-size:12px;font-weight:600;color:#1f2937;">${env.doc_titulo || env.doc_type || 'Documento'}</div>
                                    <div style="font-size:10px;color:#6b7280;">${env.paciente_nome || ''} • ${env.canal === 'whatsapp' ? '📱' : '📧'} ${env.enviado_para || ''} • ${dt}</div>
                                </div>
                            </div>
                            <span style="background:${st.bg};color:${st.color};padding:2px 8px;border-radius:8px;font-size:9px;font-weight:600;white-space:nowrap;">${st.label}</span>
                        </div>`;
                    }).join('');
                } catch(e) {
                    container.innerHTML = '<div style="text-align:center;padding:16px;color:#dc2626;font-size:12px;">Erro ao carregar histórico</div>';
                }
            }

            // ===== SOLICITAÇÃO DE EXAMES / TESTE FARMACOGENÉTICO =====
            function onEventoTipoChange(value) {
                if (value === 'solicitacao_exames') {
                    fecharModalEventoTimeline();
                    abrirModalSolicitacao('exames');
                } else if (value === 'solicitacao_farmacogenetico') {
                    fecharModalEventoTimeline();
                    abrirModalSolicitacao('farmacogenetico');
                }
            }

            async function abrirModalSolicitacao(tipo) {
                if (!pacienteAtual) { alert('Nenhum paciente selecionado'); return; }
                const pac = pacienteAtual;
                const dataHoje = new Date().toLocaleDateString('pt-BR');

                // Get doctor info
                let medicoNome = '', medicoCrm = '';
                try {
                    const doctors = await apiRequest('/api/doctors');
                    const doc = doctors.find(d => d.status === 'aprovado') || doctors[0];
                    if (doc) { medicoNome = doc.nome || ''; medicoCrm = doc.crm || ''; }
                } catch(e) { console.error('Erro ao carregar médico:', e); }

                if (tipo === 'exames') {
                    // Reset checkboxes
                    document.querySelectorAll('.sol-exame-cb').forEach(cb => cb.checked = false);
                    document.getElementById('sol-exames-obs').value = '';
                    document.getElementById('sol-exames-confirma').checked = false;
                    // Fill patient info
                    document.getElementById('sol-exames-paciente-nome').textContent = (pac.nome || 'N/A').toUpperCase();
                    document.getElementById('sol-exames-data').textContent = dataHoje;
                    document.getElementById('sol-exames-cpf').textContent = pac.cpf || 'N/A';
                    document.getElementById('sol-exames-medico').textContent = medicoNome;
                    document.getElementById('sol-exames-sig-nome').textContent = medicoNome;
                    document.getElementById('sol-exames-sig-crm').textContent = medicoCrm;
                    document.getElementById('sol-exames-footer-data').textContent = 'Gerado em ' + dataHoje;
                    document.getElementById('modal-solicitacao-exames').style.display = 'flex';

                } else if (tipo === 'farmacogenetico') {
                    document.getElementById('sol-farmaco-cannabis-extended').checked = true;
                    document.getElementById('sol-farmaco-obs').value = '';
                    document.getElementById('sol-farmaco-confirma').checked = false;
                    // Fill patient info
                    document.getElementById('sol-farmaco-paciente-nome').textContent = (pac.nome || 'N/A').toUpperCase();
                    document.getElementById('sol-farmaco-data').textContent = dataHoje;
                    document.getElementById('sol-farmaco-cpf').textContent = pac.cpf || 'N/A';
                    document.getElementById('sol-farmaco-medico').textContent = medicoNome;
                    document.getElementById('sol-farmaco-sig-nome').textContent = medicoNome;
                    document.getElementById('sol-farmaco-sig-crm').textContent = medicoCrm;
                    document.getElementById('sol-farmaco-footer-data').textContent = 'Gerado em ' + dataHoje;
                    document.getElementById('modal-solicitacao-farmacogenetico').style.display = 'flex';
                }
            }

            function fecharModalSolicitacao(tipo) {
                if (tipo === 'exames') {
                    document.getElementById('modal-solicitacao-exames').style.display = 'none';
                } else {
                    document.getElementById('modal-solicitacao-farmacogenetico').style.display = 'none';
                }
                // Reset the select
                const sel = document.getElementById('evento-tipo');
                if (sel) sel.value = 'consulta';
            }

            async function assinarSolicitacao(tipo) {
                if (!pacienteAtual) { alert('Nenhum paciente selecionado'); return; }

                let exames = [];
                let observacoes = '';
                let tipoSolicitacao = '';
                let confirmaId = '';
                let btnId = '';

                if (tipo === 'exames') {
                    confirmaId = 'sol-exames-confirma';
                    btnId = 'btn-assinar-sol-exames';
                    tipoSolicitacao = 'exames_laboratoriais';
                    // Collect checked exams
                    document.querySelectorAll('.sol-exame-cb:checked').forEach(cb => exames.push(cb.value));
                    observacoes = document.getElementById('sol-exames-obs').value.trim();
                    if (exames.length === 0) { alert('Selecione pelo menos um exame'); return; }
                } else {
                    confirmaId = 'sol-farmaco-confirma';
                    btnId = 'btn-assinar-sol-farmaco';
                    tipoSolicitacao = 'teste_farmacogenetico';
                    if (document.getElementById('sol-farmaco-cannabis-extended').checked) {
                        exames.push('CANNABIS EXTENDED');
                    }
                    observacoes = document.getElementById('sol-farmaco-obs').value.trim();
                    if (exames.length === 0) { alert('Selecione o teste'); return; }
                }

                if (!document.getElementById(confirmaId).checked) {
                    alert('Confirme a assinatura digital para prosseguir');
                    return;
                }

                const medicoNome = tipo === 'exames'
                    ? document.getElementById('sol-exames-sig-nome').textContent
                    : document.getElementById('sol-farmaco-sig-nome').textContent;
                const medicoCrm = tipo === 'exames'
                    ? document.getElementById('sol-exames-sig-crm').textContent
                    : document.getElementById('sol-farmaco-sig-crm').textContent;

                const btn = document.getElementById(btnId);
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Assinando...';

                try {
                    const result = await apiRequest(`/api/pacientes/${pacienteAtual.id}/solicitacao`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            tipo_solicitacao: tipoSolicitacao,
                            exames: exames,
                            observacoes: observacoes,
                            medico_nome: medicoNome,
                            medico_crm: medicoCrm
                        })
                    });

                    const tipoLabel = tipo === 'exames' ? 'Exames Laboratoriais' : 'Teste Farmacogenético';
                    alert(`✅ Solicitação de ${tipoLabel} assinada e salva nos anexos do paciente!`);
                    fecharModalSolicitacao(tipo);

                    // Reload prontuário and timeline
                    if (typeof carregarProntuario === 'function') carregarProntuario(pacienteAtual.id);
                    if (typeof carregarTimeline === 'function') carregarTimeline(pacienteAtual.id);

                } catch(e) {
                    console.error('Erro ao assinar solicitação:', e);
                    alert('Erro ao salvar solicitação: ' + (e.message || 'Erro desconhecido'));
                } finally {
                    btn.disabled = false;
                    if (tipo === 'exames') {
                        btn.innerHTML = '<i class="fas fa-file-signature"></i> Assinar Solicitação';
                    } else {
                        btn.innerHTML = '<i class="fas fa-file-signature"></i> Assinar Solicitação';
                    }
                }
            }

            function imprimirSolicitacao(tipo) {
                let printArea;
                if (tipo === 'exames') {
                    printArea = document.getElementById('solicitacao-exames-print-area');
                } else {
                    printArea = document.getElementById('solicitacao-farmaco-print-area');
                }
                if (!printArea) return;

                const printWindow = window.open('', '_blank', 'width=800,height=600');
                // Collect relevant styles
                const styles = Array.from(document.querySelectorAll('style')).map(s => s.outerHTML).join('');
                printWindow.document.write(`<!DOCTYPE html><html><head><title>Solicitação</title>${styles}
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                    <style>body{margin:0;padding:20px;background:#fff;} .doc-page{box-shadow:none;margin:0 auto;} @media print{body{padding:0;}}</style>
                </head><body>${printArea.innerHTML}</body></html>`);
                printWindow.document.close();
                setTimeout(() => { printWindow.print(); }, 500);
            }

            // --- Upload Prontuário ---
            function abrirUploadProntuario(tipo) {
                document.getElementById('upload-pron-tipo').value = tipo;
                const labels = { exame:'Enviar Exame', receituario:'Adicionar Receituário', laudo:'Adicionar Laudo', anexo:'Enviar Anexo' };
                const icons = { exame:'fa-flask', receituario:'fa-prescription', laudo:'fa-file-signature', anexo:'fa-paperclip' };
                document.getElementById('modal-upload-title').innerHTML = '<i class="fas ' + (icons[tipo] || 'fa-upload') + '" style="color:#667eea;"></i> ' + (labels[tipo] || 'Enviar Documento');

                // For exames: show file-focused layout
                const descArea = document.getElementById('upload-pron-descricao');
                const tituloInput = document.getElementById('upload-pron-titulo');
                const fileInput = document.getElementById('upload-pron-arquivo');
                if (tipo === 'exame') {
                    descArea.placeholder = 'Observações (opcional)';
                    tituloInput.placeholder = 'Nome do exame *';
                    fileInput.setAttribute('accept', '.pdf,.jpg,.jpeg,.png,.gif,.bmp,.webp,.doc,.docx');
                    // Auto-fill title from filename
                    fileInput.onchange = function() {
                        if (this.files[0] && !tituloInput.value.trim()) {
                            const name = this.files[0].name.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' ');
                            tituloInput.value = name;
                        }
                    };
                } else {
                    descArea.placeholder = 'Descrição (opcional)';
                    tituloInput.placeholder = 'Título do documento *';
                    fileInput.removeAttribute('accept');
                    fileInput.onchange = null;
                }

                // Reset fields
                tituloInput.value = '';
                descArea.value = '';
                fileInput.value = '';

                document.getElementById('modal-upload-prontuario').style.display = 'flex';
            }
            function fecharUploadProntuario() {
                document.getElementById('modal-upload-prontuario').style.display = 'none';
            }

            async function enviarDocProntuario() {
                if (!pacienteAtual) return;
                const tipo = document.getElementById('upload-pron-tipo').value;
                const titulo = document.getElementById('upload-pron-titulo').value.trim();
                const descricao = document.getElementById('upload-pron-descricao').value.trim();
                const arquivo = document.getElementById('upload-pron-arquivo').files[0];

                if (!titulo) { alert('Título é obrigatório'); return; }
                if (tipo === 'exame' && !arquivo) { alert('Para exames é necessário anexar o arquivo do resultado'); return; }

                if (arquivo) {
                    const fd = new FormData();
                    fd.append('arquivo', arquivo);
                    fd.append('tipo', tipo);
                    fd.append('titulo', titulo);
                    fd.append('descricao', descricao);
                    try {
                        await fetch('/api/pacientes/' + pacienteAtual.id + '/prontuario/upload', { method: 'POST', body: fd });
                        fecharUploadProntuario();
                        carregarProntuario(pacienteAtual.id);
                        carregarTimeline(pacienteAtual.id);
                        document.getElementById('upload-pron-titulo').value = '';
                        document.getElementById('upload-pron-descricao').value = '';
                        document.getElementById('upload-pron-arquivo').value = '';
                    } catch(e) { alert('Erro ao enviar arquivo'); }
                } else {
                    try {
                        await apiRequest('/api/pacientes/' + pacienteAtual.id + '/prontuario', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ tipo, titulo, descricao })
                        });
                        fecharUploadProntuario();
                        carregarProntuario(pacienteAtual.id);
                        carregarTimeline(pacienteAtual.id);
                        document.getElementById('upload-pron-titulo').value = '';
                        document.getElementById('upload-pron-descricao').value = '';
                    } catch(e) { alert('Erro ao adicionar registro'); }
                }
            }

            // --- Evento Timeline ---
            function abrirModalEventoTimeline() {
                document.getElementById('modal-evento-timeline').style.display = 'flex';
            }
            function fecharModalEventoTimeline() {
                document.getElementById('modal-evento-timeline').style.display = 'none';
            }

            async function salvarEventoTimeline() {
                if (!pacienteAtual) return;
                const tipo = document.getElementById('evento-tipo').value;
                const titulo = document.getElementById('evento-titulo').value.trim();
                const descricao = document.getElementById('evento-descricao').value.trim();
                if (!titulo) { alert('Título é obrigatório'); return; }
                try {
                    await apiRequest('/api/pacientes/' + pacienteAtual.id + '/timeline', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ tipo, titulo, descricao })
                    });
                    fecharModalEventoTimeline();
                    carregarTimeline(pacienteAtual.id);
                    document.getElementById('evento-titulo').value = '';
                    document.getElementById('evento-descricao').value = '';
                } catch(e) { alert('Erro ao salvar evento'); }
            }

            // === Expor funções para onclick inline ===
            window.switchPacView = switchPacView;
            window.abrirPerfilPaciente = abrirPerfilPaciente;
            window.excluirPaciente = excluirPaciente;
            window.abrirModalNovoPaciente = abrirModalNovoPaciente;
            window.fecharModalNovoPaciente = fecharModalNovoPaciente;
            window.criarNovoPaciente = criarNovoPaciente;
            window.abrirModalConverterLead = abrirModalConverterLead;
            window.fecharModalConverterLead = fecharModalConverterLead;
            window.converterLeadSelecionado = converterLeadSelecionado;
            window.voltarParaAdmin = voltarParaAdmin;
            window.voltarParaListaPacientes = voltarParaListaPacientes;
            window.switchPacTab = switchPacTab;
            window.carregarFichaAtendimento = carregarFichaAtendimento;
            window.salvarFichaAtendimento = salvarFichaAtendimento;
            window.salvarObservacao = salvarObservacao;
            window.excluirObservacao = excluirObservacao;
            window.togglePronAccordion = togglePronAccordion;
            window.abrirUploadProntuario = abrirUploadProntuario;
            window.fecharUploadProntuario = fecharUploadProntuario;
            window.enviarDocProntuario = enviarDocProntuario;
            window.abrirDocViewer = abrirDocViewer;
            window.abrirDocViewerByKey = abrirDocViewerByKey;
            window.fecharDocViewer = fecharDocViewer;
            window.imprimirDocumento = imprimirDocumento;
            window.baixarDocumento = baixarDocumento;
            window.abrirModalEventoTimeline = abrirModalEventoTimeline;
            window.fecharModalEventoTimeline = fecharModalEventoTimeline;
            window.salvarEventoTimeline = salvarEventoTimeline;
            window.salvarDadosPaciente = salvarDadosPaciente;
            window.uploadFotoPaciente = uploadFotoPaciente;
            window.filtrarPacientes = filtrarPacientes;
            window.abrirModalPrescricao = abrirModalPrescricao;
            window.fecharModalPrescricao = fecharModalPrescricao;
            window.buscarMedicamentosPrescricao = buscarMedicamentosPrescricao;
            window.adicionarMedPrescricao = adicionarMedPrescricao;
            window.removerMedPrescricao = removerMedPrescricao;
            window.assinarPrescricao = assinarPrescricao;
            window.showClearanceSelection = showClearanceSelection;
            window.selectClearance = selectClearance;
            window.carregarPrescricoesFicha = carregarPrescricoesFicha;
            window.visualizarPrescricao = visualizarPrescricao;
            window.abrirEnviarAssinatura = abrirEnviarAssinatura;
            window.executarEnvioAssinatura = executarEnvioAssinatura;
            window.carregarEnvelopesPaciente = carregarEnvelopesPaciente;
            window.reenviarNotificacao = reenviarNotificacao;
            window.consultarStatusEnvelope = consultarStatusEnvelope;
            window.downloadEnvelopeAssinado = downloadEnvelopeAssinado;
            window.switchPrescTab = switchPrescTab;
            window.updateTitrationValue = updateTitrationValue;
            window.calcularFrascosCannabis = calcularFrascosCannabis;
            window.prefillLaudoFromAnamnese = prefillLaudoFromAnamnese;
            window.salvarWebhookConfig = salvarWebhookConfig;
            window.testarWebhook = testarWebhook;
            window.carregarWebhookConfig = carregarWebhookConfig;
            window.salvarConfigAssinatura = salvarConfigAssinatura;
            window.testarConexaoAssinatura = testarConexaoAssinatura;
            window.toggleSecretVisibility = toggleSecretVisibility;
            window.carregarConfigAssinatura = carregarConfigAssinatura;
            window.carregarHistoricoEnvios = carregarHistoricoEnvios;
            window.carregarCertificadosMedicos = carregarCertificadosMedicos;
            window.onEventoTipoChange = onEventoTipoChange;
            window.abrirModalSolicitacao = abrirModalSolicitacao;
            window.fecharModalSolicitacao = fecharModalSolicitacao;
            window.assinarSolicitacao = assinarSolicitacao;
            window.imprimirSolicitacao = imprimirSolicitacao;
            window.openCentroModal = typeof openCentroModal !== 'undefined' ? openCentroModal : null;
            window.deleteCentro = typeof deleteCentro !== 'undefined' ? deleteCentro : null;
            window.openPlanoContaModal = typeof openPlanoContaModal !== 'undefined' ? openPlanoContaModal : null;
            window.deletePlanoConta = typeof deletePlanoConta !== 'undefined' ? deletePlanoConta : null;
            window.deleteFluxoMov = typeof deleteFluxoMov !== 'undefined' ? deleteFluxoMov : null;
            window.deleteBanco = typeof deleteBanco !== 'undefined' ? deleteBanco : null;
            window.toggleConciliacaoStatus = typeof toggleConciliacaoStatus !== 'undefined' ? toggleConciliacaoStatus : null;
            window.deleteConciliacaoMov = typeof deleteConciliacaoMov !== 'undefined' ? deleteConciliacaoMov : null;

            checkSession();
        });
    