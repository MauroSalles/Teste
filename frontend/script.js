const API_URL = window.API_URL || "http://localhost:5000";

// ── Theme persistence ────────────────────────────────────────────────────────
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = document.getElementById("theme-toggle");
  if (btn) btn.textContent = theme === "light" ? "🌞" : "🌙";
  localStorage.setItem("theme", theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  applyTheme(current === "light" ? "dark" : "light");
}

// Apply saved theme on load
applyTheme(localStorage.getItem("theme") || "dark");

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

  // ── Matrix easter egg ──────────────────────────────────────────────────────
  if (cmd === "matrix") {
    runMatrix();
    return;
  }

  // ── pedir <sabor> <quantidade> ─────────────────────────────────────────────
  const orderMatch = cmd.match(/^pedir\s+(.+?)\s+(\d+)$/i);
  if (orderMatch) {
    await handlePedir(orderMatch[1].trim(), parseInt(orderMatch[2]));
    setLoading(false);
    cmdInput.focus();
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
  } catch (err) {
    appendOutput(`[Erro de conexão: ${err.message}]`);
    appendOutput("");
  } finally {
    setLoading(false);
    cmdInput.focus();
  }
}



// ── pedir command — multi-step order flow ────────────────────────────────────
async function handlePedir(saborNome, quantidade) {
  setLoading(true);
  appendOutput(`Buscando sabor "${saborNome}"...`);
  let sabores = [];
  try {
    const r = await fetch(`${API_URL}/api/sabores`);
    sabores = await r.json();
  } catch {
    appendOutput("[Erro ao buscar sabores]");
    return;
  }
  const sabor = sabores.find(s => s.nome.toLowerCase().includes(saborNome.toLowerCase()));
  if (!sabor) {
    appendOutput(`Sabor "${saborNome}" não encontrado. Use 'listar' para ver os sabores.`);
    return;
  }
  const total = (parseFloat(sabor.preco) * quantidade).toFixed(2);
  appendOutput(`✅ Sabor: ${sabor.nome} × ${quantidade} = R$ ${total}`);
  appendOutput("Forma de pagamento: [1] PIX  [2] Cartão  [3] Dinheiro");

  // Prompt payment selection via a one-shot input listener
  const payChoice = await promptUser("Escolha (1/2/3): ");
  const payMap = { "1": "pix", "2": "cartao", "3": "dinheiro" };
  const metodo = payMap[payChoice] || "pix";

  if (metodo === "pix") {
    appendOutput("🔑 Chave PIX: gelateria@pix.key");
    appendOutput(generateQrAscii("gelateria@pix.key"));
  }

  appendOutput(`💳 Pagamento via ${metodo.toUpperCase()} selecionado.`);
  appendOutput("Confirmando pedido...");

  try {
    const r = await fetch(`${API_URL}/api/pedidos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sabor_id: sabor.id, quantidade }),
    });
    if (r.ok) {
      const d = await r.json();
      appendOutput(`🎉 Pedido #${d.id || "OK"} confirmado! Total: R$ ${total}`);
    } else {
      appendOutput(`[Erro ao confirmar pedido: ${r.status}]`);
    }
  } catch {
    appendOutput(`[Erro de conexão — pedido não confirmado]`);
  }
}

function promptUser(label) {
  return new Promise(resolve => {
    appendOutput(label);
    const originalHandler = cmdInput.onkeydown;
    cmdInput.disabled = false;
    sendBtn.disabled = true;
    cmdInput.value = "";
    cmdInput.focus();
    function handler(e) {
      if (e.key === "Enter") {
        const val = cmdInput.value.trim();
        cmdInput.value = "";
        cmdInput.removeEventListener("keydown", handler);
        resolve(val);
      }
    }
    cmdInput.addEventListener("keydown", handler);
  });
}

function generateQrAscii(key) {
  // Deterministic ASCII QR art from pix key
  const lines = [
    "  ██████  ░░░░  ██████  ",
    "  █    █  ░░░░  █    █  ",
    "  █ ██ █  ░░░░  █ ██ █  ",
    "  █    █  ░░░░  █    █  ",
    "  ██████  ░░░░  ██████  ",
    "  ░░░░░░░░░░░░░░░░░░░░  ",
    "  ██░░██░░██░░██░░██░░  ",
    "  ░░██░░██░░██░░██░░██  ",
    "  ██████  ░░░░░░░░░░░░  ",
    "  █    █  ░░░░░░░░░░░░  ",
    "  █ ██ █  ░░░░░░░░░░░░  ",
    "  █    █  ░░░░░░░░░░░░  ",
    "  ██████  ░░░░░░░░░░░░  ",
  ];
  return lines.join("\n");
}

// ── Matrix easter egg ────────────────────────────────────────────────────────
function runMatrix() {
  const chars = "ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  appendOutput("🟢 Iniciando Matrix...");
  const duration = 5000;
  const interval = 120;
  const end = Date.now() + duration;
  const timer = setInterval(() => {
    if (Date.now() > end) {
      clearInterval(timer);
      appendOutput("🟢 Matrix finalizado.");
      cmdInput.focus();
      return;
    }
    let line = "  ";
    for (let i = 0; i < 50; i++) {
      line += chars[Math.floor(Math.random() * chars.length)];
    }
    outputEl.textContent += line + "\n";
    const container = document.getElementById("output-container");
    container.scrollTop = container.scrollHeight;
  }, interval);
}
