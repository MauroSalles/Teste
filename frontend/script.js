const API_URL = window.API_URL || "http://localhost:5000";

const outputEl = document.getElementById("output");
const cmdInput = document.getElementById("cmd");

function appendOutput(text, isCommand = false) {
  const prefix = isCommand ? "❯ " : "  ";
  outputEl.textContent += prefix + text + "\n";
  const container = document.getElementById("output-container");
  container.scrollTop = container.scrollHeight;
}

async function enviarComando() {
  const cmd = cmdInput.value.trim();
  if (!cmd) return;

  appendOutput(cmd, true);
  cmdInput.value = "";

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
    appendOutput(data.resposta || "(sem resposta)");
  } catch (err) {
    appendOutput(`[Erro de conexão: ${err.message}]`);
  }

  appendOutput("");
}

cmdInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") enviarComando();
});
