/**
 * gelinho-widget.js — Floating mascot chat widget.
 * Gelinho 🍦 appears in the bottom-left corner.
 * Opens a chat panel on click.
 * Proactively shows a greeting after 30s.
 */

(function () {
  'use strict';

  const API = '';
  const STORAGE_SHOWN = 'gp_gelinho_greeted';

  // Inject styles
  const style = document.createElement('style');
  style.textContent = `
    #gelinho-btn {
      position: fixed;
      bottom: 24px;
      left: 24px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4fc3f7, #0288d1);
      border: none;
      cursor: pointer;
      z-index: 7000;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      box-shadow: 0 4px 20px rgba(79,195,247,0.4);
      transition: transform .2s;
      animation: gelinhoFloat 3s ease-in-out infinite;
    }
    #gelinho-btn:hover { transform: scale(1.1); }
    #gelinho-bubble {
      position: fixed;
      bottom: 92px;
      left: 24px;
      background: #1e2939;
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 14px 14px 14px 2px;
      padding: 12px 16px;
      color: #fff;
      font-size: 14px;
      max-width: 220px;
      z-index: 7001;
      display: none;
      animation: gpBubbleIn .3s ease forwards;
    }
    #gelinho-bubble::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 18px;
      border: 8px solid transparent;
      border-top-color: #1e2939;
      border-bottom: 0;
    }
    #gelinho-panel {
      position: fixed;
      bottom: 24px;
      left: 90px;
      width: 320px;
      max-height: 480px;
      background: #1a1f2e;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      z-index: 7002;
      display: none;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 12px 40px rgba(0,0,0,0.5);
      animation: gpPanelIn .3s cubic-bezier(.175,.885,.32,1.275) forwards;
    }
    #gelinho-panel.open { display: flex; }
    .gelinho-header {
      padding: 16px 18px;
      background: linear-gradient(135deg, #0288d1, #01579b);
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .gelinho-header .gh-avatar { font-size: 28px; }
    .gelinho-header .gh-name  { color: #fff; font-weight: 700; font-size: 15px; }
    .gelinho-header .gh-sub   { color: rgba(255,255,255,0.7); font-size: 12px; }
    .gelinho-header .gh-close {
      margin-left: auto;
      background: none;
      border: none;
      color: rgba(255,255,255,0.7);
      font-size: 18px;
      cursor: pointer;
    }
    .gelinho-msgs {
      flex: 1;
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .gelinho-msg {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.4;
    }
    .gelinho-msg.bot {
      background: rgba(255,255,255,0.07);
      color: #e0e0e0;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .gelinho-msg.user {
      background: #0288d1;
      color: #fff;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }
    .gelinho-typing {
      display: flex;
      gap: 4px;
      align-items: center;
      padding: 10px 14px;
      background: rgba(255,255,255,0.07);
      border-radius: 16px;
      width: fit-content;
      border-bottom-left-radius: 4px;
    }
    .gelinho-typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #aaa;
      animation: gpTyping 1.2s infinite;
    }
    .gelinho-typing span:nth-child(2) { animation-delay: .2s; }
    .gelinho-typing span:nth-child(3) { animation-delay: .4s; }
    .gelinho-input-row {
      display: flex;
      gap: 8px;
      padding: 12px;
      border-top: 1px solid rgba(255,255,255,0.07);
    }
    #gelinho-input {
      flex: 1;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 10px;
      padding: 9px 12px;
      color: #fff;
      font-size: 14px;
      outline: none;
    }
    #gelinho-input::placeholder { color: #555; }
    #gelinho-send {
      background: #0288d1;
      border: none;
      border-radius: 10px;
      padding: 9px 14px;
      color: #fff;
      font-size: 16px;
      cursor: pointer;
      transition: background .2s;
    }
    #gelinho-send:hover { background: #0277bd; }
    @keyframes gelinhoFloat {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-6px); }
    }
    @keyframes gpBubbleIn {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes gpPanelIn {
      from { opacity: 0; transform: scale(.95) translateY(10px); }
      to   { opacity: 1; transform: scale(1) translateY(0); }
    }
    @keyframes gpTyping {
      0%, 60%, 100% { transform: translateY(0); opacity: .6; }
      30%            { transform: translateY(-5px); opacity: 1; }
    }
  `;
  document.head.appendChild(style);

  // Build DOM
  const btn = document.createElement('button');
  btn.id = 'gelinho-btn';
  btn.title = 'Falar com Gelinho';
  btn.textContent = '🍦';
  document.body.appendChild(btn);

  const bubble = document.createElement('div');
  bubble.id = 'gelinho-bubble';
  bubble.textContent = 'Oi! Sou o Gelinho 🍦 Clique para conversar!';
  document.body.appendChild(bubble);

  const panel = document.createElement('div');
  panel.id = 'gelinho-panel';
  panel.innerHTML = `
    <div class="gelinho-header">
      <span class="gh-avatar">🍦</span>
      <div>
        <div class="gh-name">Gelinho</div>
        <div class="gh-sub">Mascote da Gelateria Pro</div>
      </div>
      <button class="gh-close" id="gelinho-close">✕</button>
    </div>
    <div class="gelinho-msgs" id="gelinho-msgs"></div>
    <div class="gelinho-input-row">
      <input id="gelinho-input" placeholder="Mensagem..." autocomplete="off">
      <button id="gelinho-send">➤</button>
    </div>
  `;
  document.body.appendChild(panel);

  const msgs = document.getElementById('gelinho-msgs');

  function addMsg(text, type) {
    const div = document.createElement('div');
    div.className = `gelinho-msg ${type}`;
    div.textContent = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function showTyping() {
    const t = document.createElement('div');
    t.className = 'gelinho-typing';
    t.id = 'gelinho-typing-indicator';
    t.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(t);
    msgs.scrollTop = msgs.scrollHeight;
    return t;
  }

  async function sendMessage(text) {
    if (!text.trim()) return;
    addMsg(text, 'user');
    document.getElementById('gelinho-input').value = '';

    const typing = showTyping();

    const token = localStorage.getItem('token');
    let resposta = 'Desculpe, não consegui responder agora. Tente mais tarde! 🍦';

    if (token) {
      try {
        const r = await fetch(`${API}/api/gelinho/conversa`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ mensagem: text }),
        });
        if (r.ok) {
          const d = await r.json();
          resposta = d.gelinho;
        }
      } catch (_) {}
    } else {
      const fallbacks = [
        'Oi! Faça login para conversar comigo de verdade! 😄',
        'Para uma experiência completa, entre com sua conta! 🍦',
        'Que saudade! Faça seu login e vamos conversar! 🎉',
      ];
      resposta = fallbacks[Math.floor(Math.random() * fallbacks.length)];
    }

    typing.remove();
    addMsg(resposta, 'bot');
  }

  // Load greeting
  async function loadGreeting() {
    const token = localStorage.getItem('token');
    let frase = 'Olá! Que bom te ver por aqui! Já escolheu o sabor de hoje? 😄';
    if (token) {
      try {
        const r = await fetch(`${API}/api/gelinho/frase-do-dia`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (r.ok) {
          const d = await r.json();
          frase = d.frase;
        }
      } catch (_) {}
    }
    addMsg(frase, 'bot');
  }

  let panelOpen = false;

  function openPanel() {
    panel.classList.add('open');
    bubble.style.display = 'none';
    panelOpen = true;
    if (msgs.children.length === 0) loadGreeting();
  }

  function closePanel() {
    panel.classList.remove('open');
    panelOpen = false;
  }

  btn.addEventListener('click', () => {
    if (panelOpen) closePanel(); else openPanel();
  });

  document.getElementById('gelinho-close').addEventListener('click', closePanel);

  document.getElementById('gelinho-send').addEventListener('click', () => {
    sendMessage(document.getElementById('gelinho-input').value);
  });

  document.getElementById('gelinho-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage(e.target.value);
  });

  // Proactive greeting after 30s (once per session)
  if (!sessionStorage.getItem(STORAGE_SHOWN)) {
    setTimeout(() => {
      if (!panelOpen) {
        bubble.style.display = 'block';
        sessionStorage.setItem(STORAGE_SHOWN, '1');
        setTimeout(() => { bubble.style.display = 'none'; }, 6000);
      }
    }, 30000);
  }
})();
