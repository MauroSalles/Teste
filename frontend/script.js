const API_URL = window.API_URL || "http://localhost:5000";

const outputEl = document.getElementById("output");
const cmdInput = document.getElementById("cmd");
const sendBtn = document.getElementById("send-btn");
const typingIndicator = document.getElementById("typing-indicator");
const autocompleteHint = document.getElementById("autocomplete-hint");

// ── Tab-completion corpus ────────────────────────────────────────────────────
const COMMANDS = [
  "ajuda", "limpar", "status",
  "listar sabores", "listar pedidos",
  "add sabor ", "atualizar sabor ", "remover sabor ",
  "fazer pedido ", "ver estoque",
  "set estoque ", "add estoque ", "reduzir estoque ",
];
const COMMANDS_LOWER = COMMANDS.map((c) => c.toLowerCase());

function getCompletionHint(value) {
  if (!value) return "";
  const lower = value.toLowerCase();
  const idx = COMMANDS_LOWER.findIndex((c) => c.startsWith(lower) && c !== lower);
  return idx >= 0 ? COMMANDS[idx] : "";
}

// ── Command history ──────────────────────────────────────────────────────────
const history = [];
let historyIndex = -1;

function pushHistory(cmd) {
  if (cmd && history[history.length - 1] !== cmd) {
    history.push(cmd);
  }
  historyIndex = history.length;
}

cmdInput.addEventListener("input", () => {
  const hint = getCompletionHint(cmdInput.value.trim());
  if (autocompleteHint) autocompleteHint.textContent = hint ? `Tab → ${hint}` : "";
});

cmdInput.addEventListener("keydown", (e) => {
  if (e.key === "Tab") {
    e.preventDefault();
    const hint = getCompletionHint(cmdInput.value.trim());
    if (hint) {
      cmdInput.value = hint;
      if (autocompleteHint) autocompleteHint.textContent = "";
    }
    return;
  }
  if (e.key === "Enter") {
    enviarComando();
    return;
  }
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (historyIndex > 0) {
      historyIndex--;
      cmdInput.value = history[historyIndex];
      if (autocompleteHint) autocompleteHint.textContent = "";
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
    if (autocompleteHint) autocompleteHint.textContent = "";
  }
});

// ── Output helpers ───────────────────────────────────────────────────────────
let _appendBatch = 0;

function appendOutput(text, isCommand = false) {
  const prefix = isCommand ? "❯ " : "  ";
  const span = document.createElement("span");
  span.className = "output-line";
  // Skip animation when many lines are appended in the same tick (e.g. long listings)
  if (_appendBatch > 1) span.style.animation = "none";
  span.textContent = prefix + text + "\n";
  outputEl.appendChild(span);
  const container = document.getElementById("output-container");
  container.scrollTop = container.scrollHeight;
  _appendBatch++;
  requestAnimationFrame(() => { _appendBatch = 0; });
}

function clearOutput() {
  outputEl.textContent = "";
}

// ── Loading state ────────────────────────────────────────────────────────────
function setLoading(loading) {
  sendBtn.disabled = loading;
  cmdInput.disabled = loading;
  if (typingIndicator) typingIndicator.classList.toggle("visible", loading);
}

// ── Main send function ───────────────────────────────────────────────────────
async function enviarComando() {
  const cmd = cmdInput.value.trim();
  if (!cmd) return;

  pushHistory(cmd);
  appendOutput(cmd, true);
  cmdInput.value = "";
  if (autocompleteHint) autocompleteHint.textContent = "";

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

