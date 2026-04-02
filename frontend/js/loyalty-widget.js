/**
 * loyalty-widget.js — Loyalty points, tier, coupon validation and referral display.
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
    #loyalty-widget {
      background: #111;
      border: 1px solid #2a2a2a;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #e0e0e0;
    }
    #loyalty-widget h2 { font-size: 1.1em; color: #00ff41; margin-bottom: 14px; }
    .loyalty-row { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 16px; }
    .loyalty-stat {
      background: #1a1a1a; border-radius: 8px;
      padding: 12px 16px; min-width: 100px; text-align: center;
    }
    .loyalty-stat .ls-label { font-size: 0.75em; color: #888; text-transform: uppercase; margin-bottom: 4px; }
    .loyalty-stat .ls-value { font-size: 1.6em; font-weight: 700; color: #00ff41; }
    #coupon-form { display: flex; gap: 8px; margin-top: 12px; }
    #coupon-input {
      flex: 1; padding: 8px 12px;
      background: #1a1a1a; border: 1px solid #2a2a2a;
      border-radius: 8px; color: #e0e0e0; font-size: 0.9em;
    }
    #coupon-input:focus { outline: none; border-color: #00ff41; }
    #coupon-btn {
      padding: 8px 16px; background: #00ff41;
      border: none; border-radius: 8px;
      color: #000; font-weight: 700; cursor: pointer;
    }
    #coupon-result { margin-top: 8px; font-size: 0.88em; }
    #coupon-result.ok { color: #00cc44; }
    #coupon-result.err { color: #ff4444; }
    #referral-box {
      margin-top: 14px; background: #1a1a1a;
      border-radius: 8px; padding: 12px;
      display: flex; justify-content: space-between; align-items: center;
    }
    #referral-code { font-family: monospace; font-size: 1em; color: #00ff41; }
    #copy-referral-btn {
      padding: 5px 12px; background: #1a1a1a;
      border: 1px solid #2a2a2a; border-radius: 6px;
      color: #888; cursor: pointer; font-size: 0.8em;
    }
    #copy-referral-btn:hover { border-color: #00ff41; color: #00ff41; }
  `;
  document.head.appendChild(style);

  // ── Build widget ───────────────────────────────────────────────────────────
  const widget = document.createElement('div');
  widget.id = 'loyalty-widget';
  widget.innerHTML = `
    <h2>🌟 Fidelidade</h2>
    <div class="loyalty-row">
      <div class="loyalty-stat">
        <div class="ls-label">Pontos</div>
        <div class="ls-value" id="lw-points">—</div>
      </div>
      <div class="loyalty-stat">
        <div class="ls-label">Tier</div>
        <div class="ls-value" id="lw-tier">—</div>
      </div>
      <div class="loyalty-stat">
        <div class="ls-label">Resgates</div>
        <div class="ls-value" id="lw-resgates">—</div>
      </div>
    </div>
    <div>
      <strong style="font-size:0.85em;color:#888;">VALIDAR CUPOM</strong>
      <div id="coupon-form">
        <input id="coupon-input" type="text" placeholder="Código do cupom" />
        <button id="coupon-btn">Validar</button>
      </div>
      <div id="coupon-result"></div>
    </div>
    <div>
      <strong style="font-size:0.85em;color:#888;display:block;margin-top:14px;">SEU CÓDIGO DE REFERRAL</strong>
      <div id="referral-box">
        <span id="referral-code">—</span>
        <button id="copy-referral-btn">Copiar</button>
      </div>
    </div>
  `;

  // Insert before first section or main
  function mountWidget() {
    const main = document.querySelector('main') || document.body;
    const firstSection = main.querySelector('.section, .cards');
    if (firstSection) {
      main.insertBefore(widget, firstSection);
    } else {
      main.appendChild(widget);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountWidget);
  } else {
    mountWidget();
  }

  // ── Load data ──────────────────────────────────────────────────────────────
  async function loadLoyalty() {
    const token = localStorage.getItem('token') || '';
    const userId = localStorage.getItem('user_id') || '1';
    if (!token) return;

    try {
      const res = await fetch(`${API_URL}/api/loyalty/points/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        document.getElementById('lw-points').textContent = data.pontos ?? 0;
        document.getElementById('lw-resgates').textContent = data.resgates ?? 0;
      }
    } catch (_) {}

    try {
      const res = await fetch(`${API_URL}/api/loyalty/referral/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        document.getElementById('referral-code').textContent = data.code || '—';
        document.getElementById('lw-tier').textContent = `T${data.tier || 1}`;
      }
    } catch (_) {}
  }

  // ── Coupon validation ──────────────────────────────────────────────────────
  document.getElementById('coupon-btn').addEventListener('click', async () => {
    const code = document.getElementById('coupon-input').value.trim();
    const resultEl = document.getElementById('coupon-result');
    if (!code) return;

    const token = localStorage.getItem('token') || '';
    resultEl.textContent = 'Validando…';
    resultEl.className = '';

    try {
      const res = await fetch(`${API_URL}/api/loyalty/coupon/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ code, order_total: 50 }),
      });
      const data = await res.json();
      if (data.valid) {
        resultEl.textContent = `✅ Cupom válido! Desconto: R$ ${data.discount.toFixed(2)}`;
        resultEl.className = 'ok';
      } else {
        resultEl.textContent = `❌ ${data.error || 'Cupom inválido'}`;
        resultEl.className = 'err';
      }
    } catch (_) {
      resultEl.textContent = '❌ Erro de conexão';
      resultEl.className = 'err';
    }
  });

  // ── Copy referral ─────────────────────────────────────────────────────────
  document.getElementById('copy-referral-btn').addEventListener('click', () => {
    const code = document.getElementById('referral-code').textContent;
    if (code && code !== '—') {
      navigator.clipboard.writeText(code).catch(() => {});
      document.getElementById('copy-referral-btn').textContent = 'Copiado!';
      setTimeout(() => {
        document.getElementById('copy-referral-btn').textContent = 'Copiar';
      }, 2000);
    }
  });

  loadLoyalty();
})();
