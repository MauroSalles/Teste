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
  } catch (err) {
    appendOutput(`[Erro de conexão: ${err.message}]`);
    appendOutput("");
  } finally {
    setLoading(false);
    cmdInput.focus();
  }
}

