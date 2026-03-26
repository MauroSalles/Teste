/* ================================================================
   Gelateria Sistema — Frontend Script
   Features: dark/light toggle, command history, quick chips,
             loading states, error handling, request counter,
             connection status, PWA service worker
   ================================================================ */

const API_URL = window.API_URL || "http://localhost:5000";

// ── DOM references ───────────────────────────────────────────────
const outputEl    = document.getElementById("output");
const outputCont  = document.getElementById("output-container");
const cmdInput    = document.getElementById("cmd");
const sendBtn     = document.getElementById("send-btn");
const btnText     = document.getElementById("btn-text");
const btnSpinner  = document.getElementById("btn-spinner");
const statusDot   = document.getElementById("connection-status");
const reqCounter  = document.getElementById("request-count");
const themeToggle = document.getElementById("theme-toggle");
const themeIcon   = document.getElementById("theme-icon");

// ── State ────────────────────────────────────────────────────────
const history = [];
let historyIndex = -1;
let requestCount = 0;

// ── Theme ────────────────────────────────────────────────────────
(function initTheme() {
  const saved = localStorage.getItem("theme") || "dark";
  applyTheme(saved);
})();

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
  localStorage.setItem("theme", theme);
}

themeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  applyTheme(current === "dark" ? "light" : "dark");
});

// ── Command history ──────────────────────────────────────────────
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

// ── Quick command chips ──────────────────────────────────────────
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    cmdInput.value = chip.dataset.cmd;
    cmdInput.focus();
    enviarComando();
  });
});

// ── Output helpers ───────────────────────────────────────────────
function appendOutput(text, cls = "") {
  const span = document.createElement("span");
  if (cls) span.className = cls + " new-line";
  span.textContent = text + "\n";
  outputEl.appendChild(span);
  outputCont.scrollTop = outputCont.scrollHeight;
}

function appendLine(prefix, text, cls) {
  appendOutput(prefix + text, cls);
}

function clearOutput() {
  outputEl.innerHTML = "";
}

// ── Loading / connection state ───────────────────────────────────
function setLoading(loading) {
  sendBtn.disabled  = loading;
  cmdInput.disabled = loading;
  btnText.hidden    = loading;
  btnSpinner.hidden = !loading;
  statusDot.className = "status-dot " + (loading ? "loading" : "connected");
}

function setDisconnected() {
  statusDot.className = "status-dot disconnected";
}

function updateRequestCounter() {
  requestCount++;
  reqCounter.textContent = requestCount + (requestCount === 1 ? " requisição" : " requisições");
}

// ── Main send function ───────────────────────────────────────────
async function enviarComando() {
  const cmd = cmdInput.value.trim();
  if (!cmd) return;

  pushHistory(cmd);
  appendLine("❯ ", cmd, "line-cmd");
  cmdInput.value = "";

  // Client-side clear
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

    updateRequestCounter();

    if (!response.ok) {
      appendLine("  ", `[Erro HTTP ${response.status}]`, "line-error");
      setDisconnected();
      return;
    }

    const data = await response.json();
    const resposta = data.resposta || "(sem resposta)";

    if (resposta === "__LIMPAR__") {
      clearOutput();
    } else {
      appendLine("  ", resposta, "");
      appendOutput("");
    }

    statusDot.className = "status-dot connected";
  } catch (err) {
    appendLine("  ", `[Erro de conexão: ${err.message}]`, "line-error");
    setDisconnected();
    updateRequestCounter();
  } finally {
    setLoading(false);
    cmdInput.focus();
  }
}

// ── Service Worker (PWA) ─────────────────────────────────────────
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .catch(() => { /* SW optional — silently ignore */ });
  });
}
