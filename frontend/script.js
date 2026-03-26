const API_URL = window.API_URL || "http://localhost:5000";

// ── Session ID ───────────────────────────────────────────────────────────────
function getSessionId() {
  let sid = sessionStorage.getItem("energy_session");
  if (!sid) {
    sid = "s-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 9);
    sessionStorage.setItem("energy_session", sid);
  }
  return sid;
}

// ── Energy state ─────────────────────────────────────────────────────────────
const energyState = {
  score: 50,
  mood: "feliz",
  purpose: "",
  band: "medium",
  batteryLevel: null,
  deviceMotion: "still",
};

const MOOD_EMOJI = {
  feliz: "😊", triste: "😔", cansado: "😴", motivado: "💪",
  apaixonado: "😍", estressado: "😤", confuso: "🤔", confiante: "😎",
};

function energyBand(score) {
  if (score >= 90) return "very_high";
  if (score >= 70) return "high";
  if (score >= 50) return "medium";
  if (score >= 30) return "low";
  return "very_low";
}

// ── Behavioral tracking ──────────────────────────────────────────────────────
const behavioralTracker = {
  clickTimestamps: [],
  scrollEvents: [],
  keystrokeTimes: [],
  backspaceCount: 0,

  recordClick() {
    const now = Date.now();
    this.clickTimestamps.push(now);
    if (this.clickTimestamps.length > 20) this.clickTimestamps.shift();
  },

  avgClickSpeedMs() {
    const ts = this.clickTimestamps;
    if (ts.length < 2) return null;
    const diffs = ts.slice(1).map((t, i) => t - ts[i]);
    return Math.round(diffs.reduce((a, b) => a + b, 0) / diffs.length);
  },

  recordScroll(delta) {
    this.scrollEvents.push({ delta: Math.abs(delta), t: Date.now() });
    if (this.scrollEvents.length > 30) this.scrollEvents.shift();
  },

  scrollPattern() {
    const evs = this.scrollEvents;
    if (evs.length < 3) return "unknown";
    const avg = evs.reduce((a, e) => a + e.delta, 0) / evs.length;
    return avg > 120 ? "aggressive" : avg > 40 ? "normal" : "gentle";
  },

  recordKeystroke(isBackspace) {
    this.keystrokeTimes.push(Date.now());
    if (isBackspace) this.backspaceCount++;
    if (this.keystrokeTimes.length > 50) this.keystrokeTimes.shift();
  },

  typingSpeedCPM() {
    const ts = this.keystrokeTimes;
    if (ts.length < 5) return null;
    const span = (ts[ts.length - 1] - ts[0]) / 60000;
    return span > 0 ? Math.round(ts.length / span) : null;
  },

  stressLevel() {
    // Higher backspace rate + aggressive scroll + fast clicks = stress
    const bpRate = this.keystrokeTimes.length > 0
      ? this.backspaceCount / this.keystrokeTimes.length : 0;
    const scroll = this.scrollPattern();
    const clickMs = this.avgClickSpeedMs();
    let stress = 30;
    if (bpRate > 0.15) stress += 20;
    if (scroll === "aggressive") stress += 20;
    if (clickMs !== null && clickMs < 400) stress += 20;
    return Math.min(100, stress);
  },
};

// ── Device motion ─────────────────────────────────────────────────────────────
if (window.DeviceMotionEvent) {
  window.addEventListener("devicemotion", (e) => {
    const acc = e.acceleration;
    if (!acc) return;
    const magnitude = Math.sqrt(
      (acc.x || 0) ** 2 + (acc.y || 0) ** 2 + (acc.z || 0) ** 2
    );
    if (magnitude > 15) energyState.deviceMotion = "active";
    else if (magnitude > 5) energyState.deviceMotion = "moving";
    else energyState.deviceMotion = "still";
  }, { passive: true });
}

// ── Battery API ───────────────────────────────────────────────────────────────
async function initBattery() {
  try {
    if (!navigator.getBattery) return;
    const battery = await navigator.getBattery();
    function updateBattery() {
      const pct = Math.round(battery.level * 100);
      energyState.batteryLevel = pct;
      const notice = document.getElementById("battery-notice");
      if (notice) notice.hidden = pct > 20;
    }
    updateBattery();
    battery.addEventListener("levelchange", updateBattery);
  } catch (_) { /* not supported */ }
}

// ── Time-based defaults ───────────────────────────────────────────────────────
function timeBasedEnergyDefault() {
  const h = new Date().getHours();
  if (h >= 6  && h <  9) return 75;
  if (h >= 9  && h < 12) return 85;
  if (h >= 12 && h < 14) return 55;
  if (h >= 14 && h < 17) return 40;
  if (h >= 17 && h < 19) return 65;
  if (h >= 19 && h < 21) return 72;
  if (h >= 21 && h < 24) return 60;
  return 30; // late night
}

// ── Apply energy theme ────────────────────────────────────────────────────────
function applyEnergyTheme(score) {
  const band = energyBand(score);
  energyState.band = band;
  document.body.setAttribute("data-energy", band);

  const fill = document.getElementById("energy-mini-fill");
  const scoreDisplay = document.getElementById("energy-score-display");
  if (fill) fill.style.width = score + "%";
  if (scoreDisplay) scoreDisplay.textContent = score;

  const moodDisplay = document.getElementById("energy-mood-display");
  if (moodDisplay) moodDisplay.textContent = MOOD_EMOJI[energyState.mood] || "😊";
}

// ── Check-in UI ───────────────────────────────────────────────────────────────
function abrirCheckin() {
  const overlay = document.getElementById("energy-overlay");
  if (overlay) overlay.hidden = false;
  const slider = document.getElementById("energy-slider");
  if (slider) {
    slider.value = timeBasedEnergyDefault();
    atualizarSlider(slider.value);
  }
  // Reset mood selection
  document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
  const defaultMood = document.querySelector('[data-mood="feliz"]');
  if (defaultMood) defaultMood.classList.add("selected");
  energyState.mood = "feliz";
}

function atualizarSlider(val) {
  const label = document.getElementById("energy-value");
  if (label) label.textContent = val;
  const score = parseInt(val, 10);
  // Preview the band colour in the modal border
  const modal = document.getElementById("energy-modal");
  if (modal) {
    const colours = {
      very_high: "#ff4500", high: "#00cfff", medium: "#00ff41",
      low: "#7ec8a0", very_low: "#ffe600",
    };
    modal.style.borderColor = colours[energyBand(score)] || "#00ff41";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Mood selector
  document.querySelectorAll(".mood-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      energyState.mood = btn.dataset.mood;
    });
  });

  // Slider live update
  const slider = document.getElementById("energy-slider");
  if (slider) slider.addEventListener("input", (e) => atualizarSlider(e.target.value));

  // Behavioural tracking on document
  document.addEventListener("click", () => behavioralTracker.recordClick(), { passive: true });
  document.addEventListener("keydown", (e) => {
    behavioralTracker.recordKeystroke(e.key === "Backspace");
  }, { passive: true });
  document.addEventListener("wheel", (e) => {
    behavioralTracker.recordScroll(e.deltaY);
  }, { passive: true });

  initBattery();

  // Open check-in on first visit
  abrirCheckin();
});

function confirmarEnergia() {
  const slider = document.getElementById("energy-slider");
  const purposeInput = document.getElementById("purpose-input");
  const score = slider ? parseInt(slider.value, 10) : timeBasedEnergyDefault();
  const purpose = purposeInput ? purposeInput.value.trim() : "";

  energyState.score = score;
  energyState.purpose = purpose;

  applyEnergyTheme(score);

  const overlay = document.getElementById("energy-overlay");
  if (overlay) overlay.hidden = true;

  // Send check-in to backend (fire-and-forget)
  sendCheckin(score);

  cmdInput.focus();
  appendOutput(`[Energia: ${score}/100 | Humor: ${energyState.mood} | ${MOOD_EMOJI[energyState.mood]}]`);
  appendOutput("");

  // Auto-recommend if score is at extremes
  if (score <= 29 || score >= 90) {
    fetchRecommend(score);
  }
}

async function fetchRecommend(score) {
  try {
    const res = await fetch(`${API_URL}/energy/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        energy_score: score,
        mood: energyState.mood,
        purpose: energyState.purpose,
        hour: new Date().getHours(),
      }),
    });
    if (!res.ok) return;
    const data = await res.json();
    if (data.flavor) {
      appendOutput(`✨ ${data.copy}`);
      appendOutput(`  Recomendação: ${data.flavor} — R$ ${data.price.toFixed(2)}`);
      appendOutput("");
    }
  } catch (_) { /* silent */ }
}

async function sendCheckin(score) {
  try {
    await fetch(`${API_URL}/energy/checkin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        energy_score: score,
        mood: energyState.mood,
        purpose: energyState.purpose,
        battery_level: energyState.batteryLevel,
        device_motion: energyState.deviceMotion,
        click_speed_ms: behavioralTracker.avgClickSpeedMs(),
        scroll_pattern: behavioralTracker.scrollPattern(),
        typing_speed_cpm: behavioralTracker.typingSpeedCPM(),
        stress_level: behavioralTracker.stressLevel(),
        time_of_day: new Date().toTimeString().slice(0, 5),
        day_of_week: ["Domingo","Segunda","Terça","Quarta","Quinta","Sexta","Sábado"][new Date().getDay()],
      }),
    });
  } catch (_) { /* silent */ }
}

// ── Shortcuts ─────────────────────────────────────────────────────────────────
function usarAtalho(cmd) {
  cmdInput.value = cmd;
  enviarComando();
}

// ── Command history ──────────────────────────────────────────────────────────
const outputEl = document.getElementById("output");
const cmdInput = document.getElementById("cmd");
const sendBtn  = document.getElementById("send-btn");

const history = [];
let historyIndex = -1;

function pushHistory(cmd) {
  if (cmd && history[history.length - 1] !== cmd) history.push(cmd);
  historyIndex = history.length;
}

cmdInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") { enviarComando(); return; }
  if (e.key === "ArrowUp") {
    if (historyIndex > 0) {
      e.preventDefault();
      cmdInput.value = history[--historyIndex];
    }
  }
  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIndex < history.length - 1) {
      cmdInput.value = history[++historyIndex];
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

function clearOutput() { outputEl.textContent = ""; }

// ── Loading state ────────────────────────────────────────────────────────────
function setLoading(loading) {
  sendBtn.disabled = loading;
  cmdInput.disabled = loading;
  sendBtn.textContent = loading ? "…" : "Enviar";
}

// ── Main send function ───────────────────────────────────────────────────────
async function enviarComando() {
  const cmd = cmdInput.value.trim();
  if (!cmd) return;

  pushHistory(cmd);
  appendOutput(cmd, true);
  cmdInput.value = "";
  behavioralTracker.recordClick();

  if (cmd === "limpar") { clearOutput(); return; }

  setLoading(true);
  try {
    const response = await fetch(`${API_URL}/cmd`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comando: cmd }),
    });

    if (!response.ok) { appendOutput(`[Erro HTTP ${response.status}]`); return; }

    const data = await response.json();
    const resposta = data.resposta || "(sem resposta)";

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


