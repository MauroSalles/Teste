/**
 * app.js — Main application: navigation, views, sabores, pedido forms, toasts.
 */

// ── View navigation ───────────────────────────────────────────────────────
function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const target = document.getElementById(`view-${name}`);
  if (target) {
    target.classList.add('active');
    target.classList.remove('hidden');
  }

  document.querySelectorAll('.nav-link').forEach(l => {
    l.classList.toggle('active', l.dataset.view === name);
  });

  // Load data for view
  if (name === 'sabores') loadSabores();
  if (name === 'pedido')  loadSaboresForSelect();
  if (name === 'home')    loadStats();
  if (name === 'admin')   loadAdminDashboard();
}

// ── Navbar links ──────────────────────────────────────────────────────────
document.querySelectorAll('.nav-link[data-view]').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const view = link.dataset.view;
    if (view === 'admin' && !isAdmin()) {
      showToast('Acesso restrito a administradores.', 'error');
      return;
    }
    showView(view);
    // Close hamburger menu on mobile
    document.querySelector('.navbar-menu')?.classList.remove('open');
  });
});

// Hamburger menu
document.getElementById('hamburger')?.addEventListener('click', () => {
  const menu = document.querySelector('.navbar-menu');
  const expanded = menu?.classList.toggle('open');
  document.getElementById('hamburger').setAttribute('aria-expanded', expanded);
});

// ── Theme toggle ──────────────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  applyTheme(saved);
}

function applyTheme(theme) {
  document.body.classList.toggle('theme-dark',  theme === 'dark');
  document.body.classList.toggle('theme-light', theme === 'light');
  const icon = document.getElementById('theme-icon');
  if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('theme', theme);
}

document.getElementById('theme-toggle')?.addEventListener('click', () => {
  const current = localStorage.getItem('theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
});

// ── Toast notifications ───────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('removing');
    toast.addEventListener('animationend', () => toast.remove());
  }, duration);
}

// ── Modals ────────────────────────────────────────────────────────────────
function openModal(name) {
  const modal = document.getElementById(`modal-${name}`);
  if (modal) modal.classList.remove('hidden');
}

function closeModal(name) {
  const modal = document.getElementById(`modal-${name}`);
  if (modal) modal.classList.add('hidden');
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal:not(.hidden)').forEach(m => m.classList.add('hidden'));
  }
});

// Login button
document.addEventListener('click', (e) => {
  if (e.target.id === 'btn-login') openModal('login');
});

// ── Home stats ────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const sabores = await Api.sabores.list();
    const el = document.getElementById('stat-sabores');
    if (el) el.textContent = sabores.length;
  } catch (_) {}

  if (isAdmin()) {
    try {
      const dash = await Api.dashboard.get();
      const pedEl   = document.getElementById('stat-pedidos');
      const recEl   = document.getElementById('stat-receita');
      if (pedEl) pedEl.textContent = dash.total_pedidos;
      if (recEl) recEl.textContent = `R$ ${dash.receita_hoje.toFixed(2)}`;
    } catch (_) {}
  }
}

// ── Sabores list ──────────────────────────────────────────────────────────
let allSabores = [];

async function loadSabores() {
  const grid = document.getElementById('sabores-grid');
  if (!grid) return;

  // Show skeletons
  grid.innerHTML = '<div class="skeleton-card"></div>'.repeat(4);

  try {
    allSabores = await Api.sabores.list();
    renderSaboresGrid(allSabores);
  } catch (err) {
    grid.innerHTML = `<p class="text-muted">Erro ao carregar sabores: ${err.message}</p>`;
  }
}

function renderSaboresGrid(sabores) {
  const grid = document.getElementById('sabores-grid');
  if (!grid) return;

  const iceEmojis = ['🍦', '🍧', '🍨', '🌸', '🌿', '🍓', '🍋', '🍫', '🥥', '🍊'];

  if (!sabores.length) {
    grid.innerHTML = '<p class="text-muted">Nenhum sabor cadastrado.</p>';
    return;
  }

  grid.innerHTML = sabores.map((s, i) => `
    <div class="sabor-card lift" role="listitem">
      <div class="sabor-card-icon">${iceEmojis[i % iceEmojis.length]}</div>
      <div class="sabor-card-nome">${escapeHtml(s.nome)}</div>
      <div class="sabor-card-preco">R$ ${parseFloat(s.preco).toFixed(2)}</div>
      <button class="btn btn-primary btn-sm" onclick="quickOrder('${escapeHtml(s.nome)}')">Pedir</button>
    </div>
  `).join('');
}

// Live search
document.getElementById('search-sabores')?.addEventListener('input', (e) => {
  const q = e.target.value.toLowerCase();
  renderSaboresGrid(allSabores.filter(s => s.nome.toLowerCase().includes(q)));
});

// Quick order from sabor card
function quickOrder(nome) {
  showView('pedido');
  const select = document.getElementById('pedido-sabor');
  if (select) {
    const opt = Array.from(select.options).find(o => o.text === nome);
    if (opt) { select.value = opt.value; updatePedidoPreview(); }
  }
}

// ── Pedido form ───────────────────────────────────────────────────────────
async function loadSaboresForSelect() {
  const select = document.getElementById('pedido-sabor');
  if (!select) return;
  try {
    const sabores = await Api.sabores.list();
    select.innerHTML = '<option value="">Selecione um sabor...</option>' +
      sabores.map(s => `<option value="${escapeHtml(s.nome)}" data-preco="${s.preco}">${escapeHtml(s.nome)} — R$ ${parseFloat(s.preco).toFixed(2)}</option>`).join('');
  } catch (_) {}
}

function updatePedidoPreview() {
  const select = document.getElementById('pedido-sabor');
  const qtdEl  = document.getElementById('pedido-qtd');
  const preview = document.getElementById('pedido-preview');
  const previewText = document.getElementById('preview-text');

  if (!select || !qtdEl || !preview) return;
  const opt = select.options[select.selectedIndex];
  const preco = parseFloat(opt?.dataset?.preco);
  const qtd   = parseInt(qtdEl.value);

  if (opt?.value && qtd > 0 && !isNaN(preco)) {
    preview.classList.remove('hidden');
    previewText.textContent = `${qtd}× ${opt.text.split(' —')[0]} = R$ ${(preco * qtd).toFixed(2)}`;
  } else {
    preview.classList.add('hidden');
  }
}

document.getElementById('pedido-sabor')?.addEventListener('change', updatePedidoPreview);
document.getElementById('pedido-qtd')?.addEventListener('input', updatePedidoPreview);

document.getElementById('form-pedido')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const select = document.getElementById('pedido-sabor');
  const qtdEl  = document.getElementById('pedido-qtd');
  const resultEl = document.getElementById('pedido-result');
  const btn    = document.getElementById('btn-pedido');

  const sabor = select?.value;
  const qtd   = parseInt(qtdEl?.value);

  // Validation
  document.getElementById('err-sabor').textContent = sabor ? '' : 'Selecione um sabor.';
  document.getElementById('err-qtd').textContent   = (qtd >= 1) ? '' : 'Insira uma quantidade válida.';
  if (!sabor || qtd < 1) return;

  btn.classList.add('loading');
  btn.disabled = true;
  resultEl.className = 'result-msg hidden';

  try {
    const pedido = await Api.pedidos.create(sabor, qtd);
    resultEl.textContent = `✅ Pedido #${pedido.id} confirmado! Total: R$ ${pedido.total.toFixed(2)}`;
    resultEl.className   = 'result-msg success';
    select.value = '';
    qtdEl.value  = 1;
    document.getElementById('pedido-preview').classList.add('hidden');
    showToast(`Pedido de ${qtd}× ${sabor} confirmado!`, 'success');
  } catch (err) {
    resultEl.textContent = `❌ ${err.message}`;
    resultEl.className   = 'result-msg error';
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
});

// ── Helpers ───────────────────────────────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Initialise ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  await initAuth();
  renderAuthState();
  loadStats();
});

// Expose globals
window.showView   = showView;
window.openModal  = openModal;
window.closeModal = closeModal;
window.showToast  = showToast;
window.quickOrder = quickOrder;
window.escapeHtml = escapeHtml;
