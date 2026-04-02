/**
 * chatbot-widget.js — Floating chat assistant for Gelateria Pro
 * XSS-safe: uses textContent for all user-provided content.
 */

(function () {
  'use strict';

  const API_URL = window.API_URL || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:5000'
      : ''
  );

  // ── Styles ─────────────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    #chat-bubble {
      position: fixed; bottom: 24px; right: 24px;
      width: 52px; height: 52px; border-radius: 50%;
      background: #00ff41; color: #000;
      border: none; cursor: pointer;
      font-size: 1.4em; z-index: 9000;
      box-shadow: 0 4px 16px rgba(0,255,65,0.4);
      transition: transform 0.2s;
    }
    #chat-bubble:hover { transform: scale(1.1); }
    #chat-panel {
      display: none;
      position: fixed; bottom: 88px; right: 24px;
      width: 320px; max-height: 480px;
      background: #111; border: 1px solid #2a2a2a;
      border-radius: 12px; z-index: 9001;
      flex-direction: column;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    #chat-panel.open { display: flex; }
    #chat-header {
      padding: 12px 16px;
      background: #1a1a1a;
      border-bottom: 1px solid #2a2a2a;
      border-radius: 12px 12px 0 0;
      color: #00ff41; font-weight: 600; font-size: 0.95em;
      display: flex; justify-content: space-between; align-items: center;
    }
    #chat-close-btn {
      background: none; border: none; color: #888;
      cursor: pointer; font-size: 1.1em;
    }
    #chat-messages {
      flex: 1; overflow-y: auto;
      padding: 12px; display: flex;
      flex-direction: column; gap: 8px;
    }
    .chat-msg {
      max-width: 80%; padding: 8px 12px;
      border-radius: 12px; font-size: 0.88em;
      line-height: 1.4; word-break: break-word;
    }
    .chat-msg.bot {
      background: #1a1a1a; color: #e0e0e0;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .chat-msg.user {
      background: rgba(0,255,65,0.15); color: #00ff41;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }
    .chat-msg.typing { color: #666; font-style: italic; }
    #chat-input-row {
      display: flex; gap: 6px;
      padding: 10px; border-top: 1px solid #2a2a2a;
    }
    #chat-input {
      flex: 1; padding: 8px 10px;
      background: #1a1a1a; border: 1px solid #2a2a2a;
      border-radius: 8px; color: #e0e0e0;
      font-size: 0.88em; outline: none;
    }
    #chat-input:focus { border-color: #00ff41; }
    #chat-send {
      padding: 8px 12px; background: #00ff41;
      border: none; border-radius: 8px;
      color: #000; font-weight: 700;
      cursor: pointer; font-size: 0.85em;
    }
    #chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
  `;
  document.head.appendChild(style);

  // ── DOM ───────────────────────────────────────────────────────────────────
  const bubble = document.createElement('button');
  bubble.id = 'chat-bubble';
  bubble.textContent = '🍦';
  bubble.title = 'Chat com assistente';

  const panel = document.createElement('div');
  panel.id = 'chat-panel';
  panel.innerHTML = `
    <div id="chat-header">
      <span>🍦 Assistente Gelateria</span>
      <button id="chat-close-btn" title="Fechar">✕</button>
    </div>
    <div id="chat-messages"></div>
    <div id="chat-input-row">
      <input id="chat-input" type="text" placeholder="Digite sua mensagem…" autocomplete="off" />
      <button id="chat-send">➤</button>
    </div>
  `;

  document.body.appendChild(bubble);
  document.body.appendChild(panel);

  const messagesEl = document.getElementById('chat-messages');
  const inputEl = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');

  // ── Helpers ───────────────────────────────────────────────────────────────
  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.textContent = text;  // XSS-safe: textContent not innerHTML
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  function showTyping() {
    return addMessage('Digitando…', 'bot typing');
  }

  // ── Events ────────────────────────────────────────────────────────────────
  bubble.addEventListener('click', () => {
    panel.classList.toggle('open');
    if (panel.classList.contains('open') && messagesEl.childElementCount === 0) {
      addMessage('Olá! 🍦 Sou o assistente da Gelateria Pro. Como posso te ajudar?', 'bot');
    }
    if (panel.classList.contains('open')) inputEl.focus();
  });

  document.getElementById('chat-close-btn').addEventListener('click', () => {
    panel.classList.remove('open');
  });

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    inputEl.value = '';
    sendBtn.disabled = true;

    const typingEl = showTyping();

    try {
      const res = await fetch(`${API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      typingEl.remove();
      addMessage(data.response || 'Desculpe, não entendi.', 'bot');
    } catch (_) {
      typingEl.remove();
      addMessage('Erro de conexão. Tente novamente.', 'bot');
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });
})();
