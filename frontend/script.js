/* ── Config ──────────────────────────────────────────────────────── */
const API_URL = (window.API_URL || "http://localhost:5000").replace(/\/$/, "");

/* ── State ───────────────────────────────────────────────────────── */
let saboresCache = [];
let confirmCallback = null;

/* ── Helpers ─────────────────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function fmtBRL(val) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(val);
}

function fmtDate(iso) {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(new Date(iso));
}

/* ── Toast ───────────────────────────────────────────────────────── */
function toast(msg, type = "info", duration = 3500) {
  const container = $("#toast-container");
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  const icons = { success: "✓", error: "✕", info: "ℹ", warning: "⚠" };
  el.innerHTML = `<span>${icons[type] || "ℹ"}</span><span>${msg}</span>`;
  el.style.setProperty("--dur", `${duration / 1000}s`);
  container.appendChild(el);
  el.addEventListener("animationend", (e) => {
    if (e.animationName === "toast-out") el.remove();
  });
}

/* ── API ─────────────────────────────────────────────────────────── */
async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.error || `HTTP ${res.status}`);
  }
  return body;
}

/* ── Navigation ──────────────────────────────────────────────────── */
function navigate(page) {
  $$(".nav-item").forEach((el) => el.classList.toggle("active", el.dataset.page === page));
  $$(".page").forEach((el) => el.classList.toggle("active", el.id === `page-${page}`));
  const titles = { dashboard: "Dashboard", sabores: "Sabores", pedidos: "Pedidos", estoque: "Estoque" };
  $("#page-title").textContent = titles[page] || page;
  loadPage(page);
}

$$(".nav-item").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    navigate(el.dataset.page);
    if (window.innerWidth <= 768) $("#sidebar").classList.remove("open");
  });
});

$("#menu-toggle").addEventListener("click", () => {
  $("#sidebar").classList.toggle("open");
});

/* ── Page Loader ─────────────────────────────────────────────────── */
async function loadPage(page) {
  switch (page) {
    case "dashboard": await loadDashboard(); break;
    case "sabores":   await loadSabores(); break;
    case "pedidos":   await loadPedidos(); break;
    case "estoque":   await loadEstoque(); break;
  }
}

$("#refresh-btn").addEventListener("click", () => {
  const active = $(".nav-item.active")?.dataset.page || "dashboard";
  loadPage(active);
  toast("Dados atualizados", "info", 2000);
});

/* ── Dashboard ───────────────────────────────────────────────────── */
async function loadDashboard() {
  try {
    const data = await apiFetch("/api/dashboard");

    $("#kpi-receita-val").textContent = fmtBRL(data.total_receita || 0);
    $("#kpi-pedidos-val").textContent = data.total_pedidos ?? "0";
    $("#kpi-ticket-val").textContent = fmtBRL(data.ticket_medio || 0);
    $("#kpi-sabores-val").textContent = data.total_sabores ?? "0";

    // Top sabores
    const topList = $("#top-sabores-list");
    if (!data.top_sabores || data.top_sabores.length === 0) {
      topList.innerHTML = '<div class="empty-state"><div class="empty-icon">🍨</div><p>Nenhum pedido registrado ainda.</p></div>';
    } else {
      const rankClasses = ["gold", "silver", "bronze"];
      topList.innerHTML = data.top_sabores
        .map(
          (s, i) => `<div class="top-sabor-item">
            <div class="top-rank ${rankClasses[i] || ""}">${i + 1}</div>
            <div class="top-sabor-name">${escHtml(s.nome)}</div>
            <div class="top-sabor-qty">${s.quantidade} un.</div>
          </div>`
        )
        .join("");
    }

    // Alertas estoque
    const alertasList = $("#alertas-estoque-list");
    if (!data.alertas_estoque || data.alertas_estoque.length === 0) {
      alertasList.innerHTML = '<div class="empty-state"><div class="empty-icon">✅</div><p>Estoque normalizado.</p></div>';
    } else {
      alertasList.innerHTML = data.alertas_estoque
        .map((a) => {
          const qtd = parseInt(a.quantidade, 10);
          const badgeCls = qtd === 0 ? "badge-danger" : "badge-warning";
          const label = qtd === 0 ? "Sem estoque" : `${qtd} un.`;
          return `<div class="alerta-item">
            <span>${escHtml(a.nome)}</span>
            <span class="badge ${badgeCls}">${label}</span>
          </div>`;
        })
        .join("");
    }
  } catch (err) {
    toast(`Erro ao carregar dashboard: ${err.message}`, "error");
  }
}

/* ── Sabores ─────────────────────────────────────────────────────── */
async function loadSabores() {
  const tbody = $("#tbody-sabores");
  tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Carregando…</td></tr>';
  try {
    const [sabores, estoque] = await Promise.all([
      apiFetch("/api/sabores"),
      apiFetch("/api/estoque"),
    ]);
    saboresCache = sabores;
    const estoqueMap = Object.fromEntries(estoque.map((e) => [e.id, e.quantidade]));
    renderSaboresTable(sabores, estoqueMap);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty">Erro: ${escHtml(err.message)}</td></tr>`;
    toast(`Erro ao carregar sabores: ${err.message}`, "error");
  }
}

function renderSaboresTable(sabores, estoqueMap = {}) {
  const tbody = $("#tbody-sabores");
  const query = ($("#search-sabores").value || "").toLowerCase();
  const filtered = query ? sabores.filter((s) => s.nome.toLowerCase().includes(query)) : sabores;

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Nenhum sabor encontrado.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered
    .map((s) => {
      const qtd = estoqueMap[s.id] ?? 0;
      const badgeCls = qtd === 0 ? "badge-danger" : qtd <= 5 ? "badge-warning" : "badge-success";
      const badgeLbl = qtd === 0 ? "Sem estoque" : `${qtd} un.`;
      return `<tr>
        <td>${escHtml(String(s.id))}</td>
        <td>${escHtml(s.nome)}</td>
        <td>${fmtBRL(s.preco)}</td>
        <td><span class="badge ${badgeCls}">${badgeLbl}</span></td>
        <td>
          <div class="action-btns">
            <button class="btn btn-ghost btn-sm js-edit-sabor"
              data-id="${escHtml(String(s.id))}"
              data-nome="${escHtml(s.nome)}"
              data-preco="${escHtml(String(s.preco))}">✏️ Editar</button>
            <button class="btn btn-danger btn-sm js-delete-sabor"
              data-id="${escHtml(String(s.id))}"
              data-nome="${escHtml(s.nome)}">🗑️</button>
          </div>
        </td>
      </tr>`;
    })
    .join("");
}

$("#search-sabores").addEventListener("input", async () => {
  if (saboresCache.length > 0) {
    const estoque = await apiFetch("/api/estoque").catch(() => []);
    const estoqueMap = Object.fromEntries(estoque.map((e) => [e.id, e.quantidade]));
    renderSaboresTable(saboresCache, estoqueMap);
  }
});

// Event delegation for sabores table buttons
$("#tbody-sabores").addEventListener("click", (e) => {
  const editBtn = e.target.closest(".js-edit-sabor");
  const deleteBtn = e.target.closest(".js-delete-sabor");
  if (editBtn) {
    openEditSabor(
      editBtn.dataset.id,
      editBtn.dataset.nome,
      editBtn.dataset.preco,
    );
  } else if (deleteBtn) {
    confirmDelete(deleteBtn.dataset.id, deleteBtn.dataset.nome);
  }
});

$("#btn-add-sabor").addEventListener("click", () => openAddSabor());

function openAddSabor() {
  $("#modal-sabor-title").textContent = "Novo Sabor";
  $("#sabor-id").value = "";
  $("#sabor-nome").value = "";
  $("#sabor-preco").value = "";
  $("#btn-sabor-submit").textContent = "Adicionar";
  openModal("modal-sabor");
  setTimeout(() => $("#sabor-nome").focus(), 50);
}

function openEditSabor(id, nome, preco) {
  $("#modal-sabor-title").textContent = "Editar Sabor";
  $("#sabor-id").value = id;
  $("#sabor-nome").value = nome;
  $("#sabor-preco").value = preco;
  $("#btn-sabor-submit").textContent = "Salvar";
  openModal("modal-sabor");
  setTimeout(() => $("#sabor-preco").focus(), 50);
}

$("#form-sabor").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = $("#sabor-id").value;
  const nome = $("#sabor-nome").value.trim();
  const preco = parseFloat($("#sabor-preco").value);

  const btn = $("#btn-sabor-submit");
  btn.disabled = true;
  btn.textContent = "Salvando…";

  try {
    if (id) {
      await apiFetch(`/api/sabores/${id}`, { method: "PUT", body: JSON.stringify({ preco }) });
      toast(`Preço de '${nome}' atualizado!`, "success");
    } else {
      await apiFetch("/api/sabores", { method: "POST", body: JSON.stringify({ nome, preco }) });
      toast(`Sabor '${nome}' adicionado!`, "success");
    }
    closeModal("modal-sabor");
    await loadSabores();
  } catch (err) {
    toast(`Erro: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = id ? "Salvar" : "Adicionar";
  }
});

function confirmDelete(id, nome) {
  $("#confirm-msg").textContent = `Remover o sabor "${nome}"? Esta ação não pode ser desfeita.`;
  confirmCallback = async () => {
    try {
      await apiFetch(`/api/sabores/${id}`, { method: "DELETE" });
      toast(`Sabor '${nome}' removido.`, "success");
      closeModal("modal-confirm");
      await loadSabores();
    } catch (err) {
      toast(`Erro: ${err.message}`, "error");
    }
  };
  openModal("modal-confirm");
}

$("#btn-confirm-ok").addEventListener("click", () => confirmCallback && confirmCallback());

/* ── Pedidos ─────────────────────────────────────────────────────── */
async function loadPedidos() {
  const tbody = $("#tbody-pedidos");
  tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Carregando…</td></tr>';
  try {
    const [pedidos, sabores] = await Promise.all([
      apiFetch("/api/pedidos"),
      apiFetch("/api/sabores"),
    ]);
    const precoMap = Object.fromEntries(sabores.map((s) => [s.nome, parseFloat(s.preco)]));

    if (pedidos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Nenhum pedido registrado ainda.</td></tr>';
      return;
    }

    tbody.innerHTML = pedidos
      .map((p) => {
        const valor = (precoMap[p.sabor] || 0) * p.quantidade;
        return `<tr>
          <td>#${p.id}</td>
          <td>${escHtml(p.sabor)}</td>
          <td>${p.quantidade}</td>
          <td>${fmtBRL(valor)}</td>
          <td>${fmtDate(p.data)}</td>
        </tr>`;
      })
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty">Erro: ${escHtml(err.message)}</td></tr>`;
    toast(`Erro ao carregar pedidos: ${err.message}`, "error");
  }
}

$("#btn-add-pedido").addEventListener("click", async () => {
  // Populate sabor select
  const sel = $("#pedido-sabor");
  sel.innerHTML = '<option value="">Selecione um sabor…</option>';
  try {
    const sabores = await apiFetch("/api/sabores");
    saboresCache = sabores;
    sabores.forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.nome;
      opt.dataset.preco = s.preco;
      opt.textContent = `${s.nome} — ${fmtBRL(s.preco)}`;
      sel.appendChild(opt);
    });
  } catch (err) {
    toast(`Erro ao carregar sabores: ${err.message}`, "error");
  }

  $("#pedido-qtd").value = "1";
  $("#pedido-total-preview").hidden = true;
  openModal("modal-pedido");
});

function updatePedidoTotal() {
  const sel = $("#pedido-sabor");
  const qtd = parseInt($("#pedido-qtd").value, 10) || 0;
  const selectedOpt = sel.options[sel.selectedIndex];
  const preco = selectedOpt ? parseFloat(selectedOpt.dataset.preco || "0") : 0;
  const preview = $("#pedido-total-preview");
  if (preco && qtd > 0) {
    $("#pedido-total-val").textContent = fmtBRL(preco * qtd);
    preview.hidden = false;
  } else {
    preview.hidden = true;
  }
}

$("#pedido-sabor").addEventListener("change", updatePedidoTotal);
$("#pedido-qtd").addEventListener("input", updatePedidoTotal);

$("#form-pedido").addEventListener("submit", async (e) => {
  e.preventDefault();
  const sabor_nome = $("#pedido-sabor").value;
  const quantidade = parseInt($("#pedido-qtd").value, 10);
  if (!sabor_nome) { toast("Selecione um sabor.", "warning"); return; }

  const btn = e.target.querySelector('[type="submit"]');
  btn.disabled = true;
  btn.textContent = "Processando…";

  try {
    const res = await apiFetch("/api/pedidos", {
      method: "POST",
      body: JSON.stringify({ sabor_nome, quantidade }),
    });
    toast(`Pedido registrado: ${quantidade}x ${res.sabor} — ${fmtBRL(res.total)}`, "success");
    closeModal("modal-pedido");
    await loadPedidos();
  } catch (err) {
    toast(`Erro: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Confirmar Pedido";
  }
});

/* ── Estoque ─────────────────────────────────────────────────────── */
async function loadEstoque() {
  const tbody = $("#tbody-estoque");
  tbody.innerHTML = '<tr><td colspan="4" class="table-empty">Carregando…</td></tr>';
  try {
    const estoque = await apiFetch("/api/estoque");
    if (estoque.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="table-empty">Nenhum sabor cadastrado.</td></tr>';
      return;
    }
    tbody.innerHTML = estoque
      .map((item) => {
        const qtd = parseInt(item.quantidade, 10);
        const badgeCls = qtd === 0 ? "badge-danger" : qtd <= 5 ? "badge-warning" : "badge-success";
        const badgeLbl = qtd === 0 ? "Sem estoque" : qtd <= 5 ? "Estoque baixo" : "OK";
        return `<tr>
          <td>${escHtml(item.nome)}</td>
          <td>${qtd}</td>
          <td><span class="badge ${badgeCls}">${badgeLbl}</span></td>
          <td>
            <button class="btn btn-ghost btn-sm js-edit-estoque"
              data-id="${escHtml(String(item.id))}"
              data-nome="${escHtml(item.nome)}"
              data-qtd="${qtd}">
              ✏️ Atualizar
            </button>
          </td>
        </tr>`;
      })
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="table-empty">Erro: ${escHtml(err.message)}</td></tr>`;
    toast(`Erro ao carregar estoque: ${err.message}`, "error");
  }
}

// Event delegation for estoque table buttons
$("#tbody-estoque").addEventListener("click", (e) => {
  const btn = e.target.closest(".js-edit-estoque");
  if (btn) openEditEstoque(btn.dataset.id, btn.dataset.nome, btn.dataset.qtd);
});

function openEditEstoque(id, nome, qtdAtual) {
  $("#estoque-sabor-id").value = id;
  $("#estoque-sabor-nome").textContent = nome;
  $("#estoque-qtd").value = qtdAtual;
  openModal("modal-estoque");
  setTimeout(() => $("#estoque-qtd").focus(), 50);
}

$("#form-estoque").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = $("#estoque-sabor-id").value;
  const quantidade = parseInt($("#estoque-qtd").value, 10);
  const btn = e.target.querySelector('[type="submit"]');
  btn.disabled = true;
  btn.textContent = "Salvando…";

  try {
    await apiFetch(`/api/estoque/${id}`, { method: "PUT", body: JSON.stringify({ quantidade }) });
    const nome = $("#estoque-sabor-nome").textContent;
    toast(`Estoque de '${nome}' atualizado para ${quantidade} un.`, "success");
    closeModal("modal-estoque");
    await loadEstoque();
  } catch (err) {
    toast(`Erro: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Salvar";
  }
});

/* ── Modal Helpers ───────────────────────────────────────────────── */
function openModal(id) {
  const el = document.getElementById(id);
  el.removeAttribute("hidden");
  el.addEventListener("click", handleOverlayClose);
}

function closeModal(id) {
  const el = document.getElementById(id);
  el.setAttribute("hidden", "");
  el.removeEventListener("click", handleOverlayClose);
}

function handleOverlayClose(e) {
  if (e.target === e.currentTarget) closeModal(e.currentTarget.id);
}

// Delegate close buttons
document.addEventListener("click", (e) => {
  const closeTarget = e.target.closest("[data-close]");
  if (closeTarget) closeModal(closeTarget.dataset.close);
});

// Close modals with Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    $$(".modal-overlay:not([hidden])").forEach((el) => closeModal(el.id));
  }
});

/* ── Security helpers ────────────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

/* ── Init ────────────────────────────────────────────────────────── */
loadDashboard();
