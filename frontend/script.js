const API_URL = window.API_URL || "http://localhost:5000";

const outputEl = document.getElementById("output");
const inputEl  = document.getElementById("cmd");
const sendBtn  = document.getElementById("send-btn");
const loaderEl = document.getElementById("loader");

/** Append a line (or multi-line block) to the terminal output */
function appendLine(text, cssClass = "system") {
  const p = document.createElement("p");
  p.className = `line ${cssClass}`;
  p.textContent = text;
  outputEl.appendChild(p);
  outputEl.scrollTop = outputEl.scrollHeight;
}

/** Clear all output lines, keeping only the welcome messages */
function clearOutput() {
  outputEl.innerHTML =
    '<p class="line system">🍦 Tela limpa. Digite <span class="cmd-highlight">ajuda</span> para ver os comandos.</p>';
}

/** Show / hide the loading indicator and lock input during requests */
function setLoading(loading) {
  loaderEl.hidden = !loading;
  inputEl.disabled = loading;
  sendBtn.disabled = loading;
  if (!loading) inputEl.focus();
}

/** Classify a response text into a CSS class */
function classifyResponse(text) {
  if (/^erro/i.test(text))            return "error";
  if (/^comandos disponíveis/i.test(text)) return "info";
  if (/^tela limpa/i.test(text))      return "system";
  return "success";
}

/** Command history (renamed to avoid shadowing window.history) */
const cmdHistory = [];
let historyIndex = -1;

/** Send the current command to the backend */
async function enviarComando() {
  const cmd = inputEl.value.trim();
  if (!cmd) return;

  // Push to history only if it differs from the last entry (avoids duplicates
  // when the user navigates history and re-submits the same command)
  if (cmdHistory.length === 0 || cmdHistory[cmdHistory.length - 1] !== cmd) {
    cmdHistory.push(cmd);
  }
  historyIndex = -1;

  appendLine(`gelateria> ${cmd}`, "user");
  inputEl.value = "";

  setLoading(true);
  try {
    const response = await fetch(`${API_URL}/cmd`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comando: cmd }),
    });

    if (!response.ok) {
      appendLine(`Erro HTTP ${response.status}`, "error");
      return;
    }

    const data = await response.json();
    const resposta = data.resposta || "(sem resposta)";

    if (resposta === "__CLEAR__") {
      clearOutput();
      return;
    }

    appendLine(resposta, classifyResponse(resposta));
  } catch (err) {
    appendLine(`Falha ao conectar ao servidor: ${err.message}`, "error");
  } finally {
    setLoading(false);
  }
}

/** Single keydown listener handles Enter, ArrowUp and ArrowDown */
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    enviarComando();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    if (historyIndex < cmdHistory.length - 1) {
      historyIndex++;
      inputEl.value = cmdHistory[cmdHistory.length - 1 - historyIndex];
    }
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIndex > 0) {
      historyIndex--;
      inputEl.value = cmdHistory[cmdHistory.length - 1 - historyIndex];
    } else {
      historyIndex = -1;
      inputEl.value = "";
    }
  }
});
