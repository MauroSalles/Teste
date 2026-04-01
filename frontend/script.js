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

// ── Matrix easter egg ────────────────────────────────────────────────────────
let _matrixActive = false;
let _matrixCanvas = null;
let _matrixRAF = null;

function runMatrix() {
  if (_matrixActive) return;
  _matrixActive = true;

  const canvas = document.createElement("canvas");
  canvas.id = "matrix-canvas";
  canvas.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;cursor:pointer;";
  document.body.appendChild(canvas);
  _matrixCanvas = canvas;

  const ctx = canvas.getContext("2d");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const cols = Math.floor(canvas.width / 16);
  const drops = Array(cols).fill(1);
  const chars = "01アイウエオカキクケコ🍦GELATERIA".split("");

  function frame() {
    ctx.fillStyle = "rgba(0,0,0,0.05)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#00ff41";
    ctx.font = "14px monospace";
    for (let i = 0; i < drops.length; i++) {
      ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * 16, drops[i] * 16);
      if (drops[i] * 16 > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
    _matrixRAF = requestAnimationFrame(frame);
  }

  _matrixRAF = requestAnimationFrame(frame);

  // Click or Escape to exit
  canvas.addEventListener("click", stopMatrix);
  document.addEventListener("keydown", function escHandler(e) {
    if (e.key === "Escape") { stopMatrix(); document.removeEventListener("keydown", escHandler); }
  });
}

function stopMatrix() {
  if (!_matrixActive) return;
  _matrixActive = false;
  cancelAnimationFrame(_matrixRAF);
  if (_matrixCanvas) { _matrixCanvas.remove(); _matrixCanvas = null; }
}

// ── Toast notification ───────────────────────────────────────────────────────
function showToast(msg, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.cssText = "position:fixed;bottom:80px;right:20px;z-index:8000;display:flex;flex-direction:column;gap:8px;";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  const colors = { info: "#00ff41", success: "#00cc44", warning: "#ffaa00", error: "#ff4444" };
  toast.style.cssText = `background:#1a1a1a;color:${colors[type] || colors.info};border:1px solid ${colors[type] || colors.info};border-radius:8px;padding:10px 16px;font-size:0.88em;max-width:280px;opacity:0;transition:opacity 0.3s;`;
  toast.textContent = msg;
  container.appendChild(toast);
  requestAnimationFrame(() => { toast.style.opacity = "1"; });
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 350);
  }, 3500);
}

// ── Feedback widget ──────────────────────────────────────────────────────────
function createFeedbackWidget() {
  // Floating button
  const btn = document.createElement("button");
  btn.id = "feedback-btn";
  btn.textContent = "💬";
  btn.title = "Enviar Feedback";
  btn.style.cssText = "position:fixed;bottom:20px;right:20px;z-index:7000;width:48px;height:48px;border-radius:50%;border:none;background:#00ff41;color:#000;font-size:1.3em;cursor:pointer;box-shadow:0 2px 10px rgba(0,255,65,0.4);transition:transform 0.2s;";
  btn.addEventListener("mouseenter", () => { btn.style.transform = "scale(1.1)"; });
  btn.addEventListener("mouseleave", () => { btn.style.transform = "scale(1)"; });
  btn.addEventListener("click", () => toggleFeedbackModal(true));
  document.body.appendChild(btn);

  // Modal backdrop
  const backdrop = document.createElement("div");
  backdrop.id = "feedback-backdrop";
  backdrop.style.cssText = "display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:7001;";
  backdrop.addEventListener("click", () => toggleFeedbackModal(false));
  document.body.appendChild(backdrop);

  // Modal panel
  const modal = document.createElement("div");
  modal.id = "feedback-modal";
  modal.style.cssText = "display:none;position:fixed;bottom:80px;right:20px;z-index:7002;background:#111;border:1px solid #00ff41;border-radius:12px;padding:20px;width:300px;font-family:inherit;color:#e0e0e0;";
  modal.innerHTML = `
    <h3 style="color:#00ff41;margin:0 0 12px;font-size:1em;">💬 Enviar Feedback</h3>
    <input id="fb-nome" placeholder="Seu nome *" style="width:100%;margin-bottom:8px;padding:8px;background:#1a1a1a;border:1px solid #333;border-radius:6px;color:#e0e0e0;font-size:0.9em;" />
    <input id="fb-email" placeholder="Email (opcional)" style="width:100%;margin-bottom:8px;padding:8px;background:#1a1a1a;border:1px solid #333;border-radius:6px;color:#e0e0e0;font-size:0.9em;" />
    <textarea id="fb-msg" placeholder="Sua mensagem *" rows="3" style="width:100%;margin-bottom:8px;padding:8px;background:#1a1a1a;border:1px solid #333;border-radius:6px;color:#e0e0e0;font-size:0.9em;resize:vertical;"></textarea>
    <div style="margin-bottom:12px;">
      <span style="font-size:0.85em;color:#888;">Nota: </span>
      <span id="star-rating" style="font-size:1.4em;cursor:pointer;"></span>
    </div>
    <button id="fb-submit" style="width:100%;padding:9px;background:#00ff41;color:#000;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:0.9em;">Enviar</button>
  `;
  document.body.appendChild(modal);

  // Star rating
  let selectedNota = 0;
  const starEl = modal.querySelector("#star-rating");
  function renderStars(hover) {
    const n = hover || selectedNota;
    starEl.textContent = "★".repeat(n) + "☆".repeat(5 - n);
  }
  renderStars(0);
  starEl.addEventListener("mousemove", (e) => {
    const w = starEl.offsetWidth / 5;
    const h = Math.ceil((e.offsetX + 1) / w);
    renderStars(Math.min(5, Math.max(1, h)));
  });
  starEl.addEventListener("mouseleave", () => renderStars(0));
  starEl.addEventListener("click", (e) => {
    const w = starEl.offsetWidth / 5;
    selectedNota = Math.min(5, Math.max(1, Math.ceil((e.offsetX + 1) / w)));
    renderStars(0);
  });

  // Submit
  modal.querySelector("#fb-submit").addEventListener("click", async () => {
    const nome = modal.querySelector("#fb-nome").value.trim();
    const email = modal.querySelector("#fb-email").value.trim();
    const mensagem = modal.querySelector("#fb-msg").value.trim();
    if (!nome || !mensagem || selectedNota === 0) {
      showToast("Preencha nome, mensagem e nota.", "warning");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, email, mensagem, nota: selectedNota }),
      });
      if (res.ok) {
        showToast("Obrigado pelo seu feedback! 🍦", "success");
        toggleFeedbackModal(false);
        modal.querySelector("#fb-nome").value = "";
        modal.querySelector("#fb-email").value = "";
        modal.querySelector("#fb-msg").value = "";
        selectedNota = 0;
        renderStars(0);
      } else {
        const err = await res.json();
        showToast(err.error || "Erro ao enviar.", "error");
      }
    } catch (e) {
      showToast("Erro de conexão.", "error");
    }
  });
}

function toggleFeedbackModal(open) {
  const modal = document.getElementById("feedback-modal");
  const backdrop = document.getElementById("feedback-backdrop");
  if (!modal) return;
  modal.style.display = open ? "block" : "none";
  backdrop.style.display = open ? "block" : "none";
}

// ── Sabor do Dia banner (shown once per day) ─────────────────────────────────
async function mostrarSaborDoDia() {
  const hoje = new Date().toISOString().slice(0, 10);
  if (localStorage.getItem("sabor_do_dia_visto") === hoje) return;
  try {
    const res = await fetch(`${API_URL}/api/sabor-do-dia`);
    if (!res.ok) return;
    const data = await res.json();
    showToast(`🍦 Sabor do Dia: ${data.sabor.nome} — R$ ${parseFloat(data.sabor.preco).toFixed(2)}`, "success");
    localStorage.setItem("sabor_do_dia_visto", hoje);
  } catch (_) { /* ignore if backend is offline */ }
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

    if (resposta === "__LIMPAR__") {
      clearOutput();
    } else if (resposta === "__MATRIX__") {
      runMatrix();
      appendOutput("Entrando na Matrix... (clique ou ESC para sair)");
      appendOutput("");
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

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  createFeedbackWidget();
  mostrarSaborDoDia();
});


