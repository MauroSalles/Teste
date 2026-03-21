const API_URL = (window.API_URL || "http://localhost:5000");

const outputEl = document.getElementById("output");
const inputEl  = document.getElementById("cmd");

/** Append a line to the terminal output */
function appendLine(text, cssClass = "system") {
  const p = document.createElement("p");
  p.className = `line ${cssClass}`;
  p.textContent = text;
  outputEl.appendChild(p);
  outputEl.scrollTop = outputEl.scrollHeight;
}

/** Send the current command to the backend */
async function enviarComando() {
  const cmd = inputEl.value.trim();
  if (!cmd) return;

  appendLine(`gelateria> ${cmd}`, "user");
  inputEl.value = "";

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

    // Choose colour based on content hints
    let cssClass = "success";
    if (/^erro/i.test(resposta)) cssClass = "error";
    else if (/^comandos disponíveis/i.test(resposta)) cssClass = "info";

    appendLine(resposta, cssClass);
  } catch (err) {
    appendLine(`Falha ao conectar ao servidor: ${err.message}`, "error");
  }
}

/** Allow Enter key to submit */
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") enviarComando();
});

/** Command history navigation */
const history = [];
let historyIndex = -1;

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (historyIndex < history.length - 1) {
      historyIndex++;
      inputEl.value = history[history.length - 1 - historyIndex];
    }
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIndex > 0) {
      historyIndex--;
      inputEl.value = history[history.length - 1 - historyIndex];
    } else {
      historyIndex = -1;
      inputEl.value = "";
    }
  } else if (e.key === "Enter") {
    const cmd = inputEl.value.trim();
    if (cmd) {
      history.push(cmd);
      historyIndex = -1;
    }
  }
});
