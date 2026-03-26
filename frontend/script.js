const API_URL = window.API_URL || "http://localhost:5000";

const outputEl = document.getElementById("output");
const cmdInput = document.getElementById("cmd");
const sendBtn = document.getElementById("send-btn");

// ── Command history ──────────────────────────────────────────────────────────
const history = [];
let historyIndex = -1;

function pushHistory(cmd) {
  if (cmd && history[history.length - 1] !== cmd) {
    history.push(cmd);
  }
  historyIndex = history.length;
}

cmdInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    enviarComando();
    return;
  }
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (historyIndex > 0) {
      historyIndex--;
      cmdInput.value = history[historyIndex];
    }
  }
  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIndex < history.length - 1) {
      historyIndex++;
      cmdInput.value = history[historyIndex];
    } else {
      historyIndex = history.length;
      cmdInput.value = "";
    }
  }
});

// ── Output helpers ───────────────────────────────────────────────────────────
function appendOutput(text, isCommand = false) {
  const prefix = isCommand ? "❯ " : "  ";
  outputEl.textContent += prefix + text + "\n";
  const container = document.getElementById("output-container");
  container.scrollTop = container.scrollHeight;
}

function clearOutput() {
  outputEl.textContent = "";
}

// ── Loading state ────────────────────────────────────────────────────────────
function setLoading(loading) {
  sendBtn.disabled = loading;
  cmdInput.disabled = loading;
  sendBtn.textContent = loading ? "..." : "Enviar";
}

// ── Main send function ───────────────────────────────────────────────────────
async function enviarComando() {
  const cmd = cmdInput.value.trim();
  if (!cmd) return;

  pushHistory(cmd);
  appendOutput(cmd, true);
  cmdInput.value = "";

  // Handle client-side commands
  if (cmd === "limpar") {
    clearOutput();
    return;
  }

  setLoading(true);
  try {
    const response = await fetch(`${API_URL}/cmd`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comando: cmd }),
    });

    if (!response.ok) {
      appendOutput(`[Erro HTTP ${response.status}]`);
      return;
    }

    const data = await response.json();
    const resposta = data.resposta || "(sem resposta)";

    // Server can also signal a clear
    if (resposta === "__LIMPAR__") {
      clearOutput();
    } else {
      appendOutput(resposta);
      appendOutput("");
    }

    // Refresh dashboard after mutating commands
    const mutatingPrefixes = [
      "fazer pedido", "add sabor", "remover sabor", "atualizar sabor",
      "add cliente", "add pontos", "add ingrediente",
      "abrir caixa", "fechar caixa", "add despesa",
      "set estoque", "add estoque", "reduzir estoque",
    ];
    if (mutatingPrefixes.some((p) => cmd.startsWith(p))) {
      carregarDashboard();
    }
  } catch (err) {
    appendOutput(`[Erro de conexão: ${err.message}]`);
    appendOutput("");
  } finally {
    setLoading(false);
    cmdInput.focus();
  }
}

// ── Dashboard ────────────────────────────────────────────────────────────────
function fmt(value) {
  return "R$ " + Number(value).toFixed(2);
}

async function carregarDashboard() {
  const spinner = document.getElementById("dash-spinner");
  if (spinner) spinner.style.display = "block";
  try {
    const res = await fetch(`${API_URL}/api/dashboard/kpis`);
    if (!res.ok) return;
    const d = await res.json();

    // KPIs
    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    set("kpi-pedidos-hoje", d.kpis.pedidos_hoje);
    set("kpi-fat-hoje",     fmt(d.kpis.faturamento_hoje));
    set("kpi-fat-mes",      fmt(d.kpis.faturamento_mes));
    set("kpi-ticket",       fmt(d.kpis.ticket_medio));

    // Top sabores
    const list = document.getElementById("top-sabores-list");
    if (list) {
      list.innerHTML = d.top_sabores.length
        ? d.top_sabores.map((s, i) =>
            `<li>
              <span class="rank">${i + 1}.</span>
              <span class="flavor-name" title="${s.nome}">${s.nome}</span>
              <span class="units">${s.unidades_vendidas}u</span>
            </li>`
          ).join("")
        : "<li><span class='flavor-name' style='color:#555'>sem dados</span></li>";
    }

    // Alerts
    const alertaBadge = document.getElementById("alerta-ingredientes");
    if (alertaBadge) {
      alertaBadge.textContent = d.alertas_ingredientes;
      alertaBadge.className = "alert-badge " + (d.alertas_ingredientes > 0 ? "" : "ok");
    }

    // Caixa
    const caixaEl = document.getElementById("caixa-status");
    if (caixaEl) {
      caixaEl.textContent  = d.caixa_aberta ? "🟢 Aberto" : "🔴 Fechado";
      caixaEl.style.color  = d.caixa_aberta ? "#00ff41"    : "#ff4444";
    }
  } catch (err) {
    // silently fail — backend may not be running locally
    console.error("Dashboard load error:", err.message);
  } finally {
    if (spinner) spinner.style.display = "none";
  }
}

// Load dashboard on startup and refresh every 60 s
carregarDashboard();
setInterval(carregarDashboard, 60_000);


