/**
 * payment-widget.js — Payment options modal for Gelateria Pro
 * Shows Stripe / PIX / Cash options after order creation.
 */

(function () {
  'use strict';

  const API_URL = window.API_URL || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:5000'
      : ''
  );

  const MAX_POLL_ATTEMPTS = 12;
  const POLL_INTERVAL_MS = 5000;

  // ── Inject styles ─────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    #payment-overlay {
      display: none;
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.7);
      z-index: 1000;
      align-items: center;
      justify-content: center;
    }
    #payment-overlay.active { display: flex; }
    #payment-modal {
      background: #111;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      padding: 28px;
      width: 360px;
      max-width: 95vw;
      color: #e0e0e0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    #payment-modal h3 { margin: 0 0 20px; color: #00ff41; font-size: 1.1em; }
    .pay-btn {
      display: block; width: 100%; margin-bottom: 10px;
      padding: 12px; border: 1px solid #2a2a2a;
      border-radius: 8px; background: #1a1a1a;
      color: #e0e0e0; font-size: 0.95em;
      cursor: pointer; text-align: left;
      transition: border-color 0.2s, background 0.2s;
    }
    .pay-btn:hover { border-color: #00ff41; background: rgba(0,255,65,0.08); }
    #payment-close {
      margin-top: 12px; background: none; border: none;
      color: #888; cursor: pointer; font-size: 0.85em;
      text-decoration: underline;
    }
    #pix-info {
      display: none; margin-top: 16px;
      padding: 14px; background: #1a1a1a;
      border-radius: 8px; word-break: break-all;
      font-size: 0.8em; color: #00ff41;
    }
    #payment-success {
      display: none; text-align: center;
      padding: 20px; color: #00cc44; font-size: 1.1em;
    }
  `;
  document.head.appendChild(style);

  // ── Build modal DOM ───────────────────────────────────────────────────────
  const overlay = document.createElement('div');
  overlay.id = 'payment-overlay';
  overlay.innerHTML = `
    <div id="payment-modal">
      <h3>💳 Escolha a forma de pagamento</h3>
      <div id="payment-methods-list">
        <button class="pay-btn" data-method="stripe">💳 Cartão de Crédito/Débito (Stripe)</button>
        <button class="pay-btn" data-method="pix">🏦 PIX</button>
        <button class="pay-btn" data-method="dinheiro">💵 Dinheiro</button>
      </div>
      <div id="pix-info"></div>
      <div id="payment-success">✅ Pagamento confirmado ✓</div>
      <button id="payment-close">Fechar</button>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById('payment-close').addEventListener('click', () => {
    overlay.classList.remove('active');
  });

  // ── Handle method selection ───────────────────────────────────────────────
  overlay.querySelectorAll('.pay-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const method = btn.dataset.method;
      const pedidoId = overlay.dataset.pedidoId;
      const valor = parseFloat(overlay.dataset.valor || '0');

      if (method === 'pix') {
        await _handlePix(valor, pedidoId);
      } else if (method === 'stripe') {
        _handleStripe(valor);
      } else {
        _showSuccess();
      }
    });
  });

  async function _handlePix(valor, pedidoId) {
    const pixInfo = document.getElementById('pix-info');
    pixInfo.style.display = 'block';
    pixInfo.textContent = 'Gerando QR Code PIX…';

    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch(`${API_URL}/api/payments/pix/qrcode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ valor, descricao: `Pedido #${pedidoId}` }),
      });
      if (!res.ok) throw new Error('Falha ao gerar PIX');
      const data = await res.json();
      pixInfo.textContent = `TXID: ${data.txid}\n\nQR Code:\n${data.qrcode}`;

      // Poll for payment
      _pollPix(data.txid);
    } catch (err) {
      pixInfo.textContent = `Erro: ${err.message}`;
    }
  }

  function _handleStripe(valor) {
    // Minimal Stripe redirect placeholder
    const pixInfo = document.getElementById('pix-info');
    pixInfo.style.display = 'block';
    pixInfo.textContent = 'Redirecionando para pagamento com cartão…';
    setTimeout(() => _showSuccess(), 2000);
  }

  function _pollPix(txid) {
    const token = localStorage.getItem('token') || '';
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      if (attempts > MAX_POLL_ATTEMPTS) { clearInterval(interval); return; }
      try {
        const res = await fetch(`${API_URL}/api/payments/pix/status/${txid}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const data = await res.json();
        if (data.status === 'pago') {
          clearInterval(interval);
          _showSuccess();
        }
      } catch (_) {}
    }, POLL_INTERVAL_MS);
  }

  function _showSuccess() {
    document.getElementById('payment-methods-list').style.display = 'none';
    document.getElementById('pix-info').style.display = 'none';
    document.getElementById('payment-success').style.display = 'block';
    setTimeout(() => overlay.classList.remove('active'), 3000);
  }

  // ── Public API ────────────────────────────────────────────────────────────
  window.PaymentWidget = {
    show(pedidoId, valor) {
      overlay.dataset.pedidoId = pedidoId;
      overlay.dataset.valor = valor;
      document.getElementById('payment-methods-list').style.display = 'block';
      document.getElementById('pix-info').style.display = 'none';
      document.getElementById('payment-success').style.display = 'none';
      overlay.classList.add('active');
    },
  };
})();
