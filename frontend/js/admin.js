/**
 * admin.js — Admin dashboard: charts, KPI cards, CRUD for sabores & estoque.
 */

let chartVendas = null;
let chartSabores = null;

async function loadAdminDashboard() {
  if (!isAdmin()) { showView('home'); return; }

  try {
    const dash = await Api.dashboard.get();
    renderKPIs(dash);
    renderCharts(dash);
  } catch (err) {
    showToast(`Erro ao carregar dashboard: ${err.message}`, 'error');
  }

  loadAdminSabores();
  loadAdminEstoque();
}

// ── KPIs ──────────────────────────────────────────────────────────────────
function renderKPIs(dash) {
  const fmt = (v) => `R$ ${parseFloat(v).toFixed(2)}`;

  setValue('kpi-receita-total', fmt(dash.receita_total));
  setValue('kpi-total-pedidos', dash.total_pedidos);
  setValue('kpi-total-sabores', dash.total_sabores);
  setValue('kpi-sem-estoque',   dash.sabores_sem_estoque);
}

function setValue(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// ── Charts ────────────────────────────────────────────────────────────────
function renderCharts(dash) {
  if (typeof Chart === 'undefined') return;

  const darkMode = document.body.classList.contains('theme-dark');
  const textColor = darkMode ? '#9999bb' : '#4a4a6a';
  const gridColor = darkMode ? '#33335a' : '#e0e0ee';

  Chart.defaults.color = textColor;

  // Vendas semana (line)
  const vendasCtx = document.getElementById('chart-vendas')?.getContext('2d');
  if (vendasCtx) {
    if (chartVendas) chartVendas.destroy();
    chartVendas = new Chart(vendasCtx, {
      type: 'line',
      data: {
        labels: dash.vendas_semana.map(v => v.dia),
        datasets: [{
          label: 'Receita (R$)',
          data: dash.vendas_semana.map(v => v.receita),
          borderColor: '#6c63ff',
          backgroundColor: 'rgba(108,99,255,0.15)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#6c63ff',
          pointRadius: 5,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: gridColor } },
          y: { grid: { color: gridColor }, beginAtZero: true },
        },
      },
    });
  }

  // Top sabores (doughnut)
  const saboresCtx = document.getElementById('chart-sabores')?.getContext('2d');
  if (saboresCtx && dash.top_sabores.length) {
    if (chartSabores) chartSabores.destroy();
    const palette = ['#6c63ff','#ff6b6b','#51cf66','#fcc419','#4dabf7','#f06595'];
    chartSabores = new Chart(saboresCtx, {
      type: 'doughnut',
      data: {
        labels: dash.top_sabores.map(s => s.nome),
        datasets: [{
          data: dash.top_sabores.map(s => s.total_vendido),
          backgroundColor: palette,
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
      },
    });
  }
}

// ── Sabores management ─────────────────────────────────────────────────────
async function loadAdminSabores() {
  const container = document.getElementById('admin-sabores-list');
  if (!container) return;
  try {
    const sabores = await Api.sabores.list();
    if (!sabores.length) { container.innerHTML = '<p class="text-muted">Nenhum sabor.</p>'; return; }
    container.innerHTML = `
      <table>
        <thead>
          <tr><th>ID</th><th>Nome</th><th>Preço</th><th>Ações</th></tr>
        </thead>
        <tbody>
          ${sabores.map(s => `
            <tr>
              <td>${s.id}</td>
              <td>${escapeHtml(s.nome)}</td>
              <td>R$ ${parseFloat(s.preco).toFixed(2)}</td>
              <td>
                <button class="btn btn-danger btn-sm admin-del-sabor" data-id="${s.id}" data-nome="${escapeHtml(s.nome)}">Remover</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    // Attach click handlers after rendering (avoids inline onclick XSS risk)
    container.querySelectorAll('.admin-del-sabor').forEach(btn => {
      btn.addEventListener('click', () => deleteSabor(parseInt(btn.dataset.id), btn.dataset.nome));
    });
  } catch (err) {
    container.innerHTML = `<p class="text-muted">Erro: ${err.message}</p>`;
  }
}

async function deleteSabor(id, nome) {
  if (!confirm(`Remover sabor "${nome}"?`)) return;
  try {
    await Api.sabores.remove(id);
    showToast(`Sabor "${nome}" removido.`, 'success');
    loadAdminSabores();
    loadAdminEstoque();
  } catch (err) {
    showToast(`Erro: ${err.message}`, 'error');
  }
}

// Add sabor modal
document.getElementById('btn-add-sabor')?.addEventListener('click', () => openModal('add-sabor'));

document.getElementById('form-add-sabor')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const nome  = document.getElementById('add-sabor-nome').value.trim();
  const preco = parseFloat(document.getElementById('add-sabor-preco').value);
  const errEl = document.getElementById('add-sabor-error');
  errEl.classList.add('hidden');

  if (!nome || isNaN(preco) || preco < 0) {
    errEl.textContent = 'Preencha nome e preço válido.';
    errEl.classList.remove('hidden');
    return;
  }

  try {
    await Api.sabores.create(nome, preco);
    closeModal('add-sabor');
    showToast(`Sabor "${nome}" adicionado!`, 'success');
    document.getElementById('form-add-sabor').reset();
    loadAdminSabores();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
});

// ── Estoque management ─────────────────────────────────────────────────────
async function loadAdminEstoque() {
  const container = document.getElementById('admin-estoque-list');
  if (!container) return;
  try {
    const estoque = await Api.estoque.list();
    container.innerHTML = `
      <table>
        <thead><tr><th>Sabor</th><th>Quantidade</th><th>Atualizar</th></tr></thead>
        <tbody>
          ${estoque.map(e => `
            <tr>
              <td>${escapeHtml(e.nome)}</td>
              <td id="est-${e.id}">${e.quantidade}</td>
              <td>
                <input type="number" min="0" value="${e.quantidade}" id="inp-est-${e.id}"
                  style="width:80px;padding:4px 8px;background:var(--bg-elevated);border:1px solid var(--border-color);border-radius:4px;color:var(--text-primary);"
                />
                <button class="btn btn-secondary btn-sm" onclick="updateEstoque(${e.id})">Salvar</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">Erro: ${err.message}</p>`;
  }
}

async function updateEstoque(saborId) {
  const input = document.getElementById(`inp-est-${saborId}`);
  const qtd = parseInt(input?.value);
  if (isNaN(qtd) || qtd < 0) { showToast('Quantidade inválida.', 'error'); return; }
  try {
    const result = await Api.estoque.set(saborId, qtd);
    document.getElementById(`est-${saborId}`).textContent = result.quantidade;
    showToast('Estoque atualizado!', 'success');
  } catch (err) {
    showToast(`Erro: ${err.message}`, 'error');
  }
}

window.loadAdminDashboard = loadAdminDashboard;
window.deleteSabor = deleteSabor;
window.updateEstoque = updateEstoque;
