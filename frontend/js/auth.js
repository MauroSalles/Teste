/**
 * auth.js — Login / register / logout UI logic.
 */

let currentUser = null;

// ── State helpers ─────────────────────────────────────────────────────────
function getUser()  { return currentUser; }
function isAdmin()  { return currentUser && currentUser.role === 'admin'; }
function isLogged() { return !!currentUser; }

// ── Init: restore session on load ─────────────────────────────────────────
async function initAuth() {
  if (!TokenStore.access) return;
  try {
    currentUser = await Api.auth.me();
    renderAuthState();
  } catch (_) {
    TokenStore.clear();
    currentUser = null;
  }
}

// ── Render auth UI ────────────────────────────────────────────────────────
function renderAuthState() {
  const authArea  = document.getElementById('auth-area');
  const adminItem = document.getElementById('admin-nav-item');

  if (currentUser) {
    authArea.innerHTML = `
      <span class="text-muted" style="font-size:.85rem">👋 ${currentUser.nome.split(' ')[0]}</span>
      <button class="btn btn-secondary btn-sm" onclick="handleLogout()">Sair</button>
    `;
    if (adminItem) {
      adminItem.classList.toggle('hidden', !isAdmin());
    }
  } else {
    authArea.innerHTML = `<button class="btn btn-secondary btn-sm" id="btn-login" onclick="openModal('login')">Login</button>`;
    if (adminItem) adminItem.classList.add('hidden');
  }
}

// ── Login ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const formLogin = document.getElementById('form-login');
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const senha = document.getElementById('login-senha').value;
      const errEl = document.getElementById('login-error');
      errEl.classList.add('hidden');

      try {
        const data = await Api.auth.login(email, senha);
        TokenStore.set(data.access_token, data.refresh_token);
        currentUser = data.user;
        renderAuthState();
        closeModal('login');
        showToast('Login efetuado com sucesso! 🎉', 'success');
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.remove('hidden');
      }
    });
  }

  // Register form
  const formRegister = document.getElementById('form-register');
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      const nome  = document.getElementById('reg-nome').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const senha = document.getElementById('reg-senha').value;
      const errEl = document.getElementById('register-error');
      errEl.classList.add('hidden');

      try {
        const data = await Api.auth.register(nome, email, senha);
        TokenStore.set(data.access_token, data.refresh_token);
        currentUser = data.user;
        renderAuthState();
        closeModal('register');
        showToast('Conta criada com sucesso! 🎉', 'success');
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.remove('hidden');
      }
    });
  }
});

// ── Logout ────────────────────────────────────────────────────────────────
async function handleLogout() {
  try {
    await Api.auth.logout(TokenStore.refresh);
  } catch (_) {}
  TokenStore.clear();
  currentUser = null;
  renderAuthState();
  showToast('Logout efetuado.', 'info');
  showView('home');
}

// ── Modal switches ────────────────────────────────────────────────────────
function switchToRegister() {
  closeModal('login');
  openModal('register');
}

window.getUser    = getUser;
window.isAdmin    = isAdmin;
window.isLogged   = isLogged;
window.initAuth   = initAuth;
window.handleLogout = handleLogout;
window.switchToRegister = switchToRegister;
