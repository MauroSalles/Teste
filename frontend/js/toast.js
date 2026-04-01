/**
 * toast.js — Elegant in-app toast notification system.
 * Types: success (green), error (red), info (blue), achievement (gold + confetti).
 * Stackable up to 3. Auto-dismiss in 4s with progress bar.
 * Usage: gpToast.show({ type, message })
 *        gpToast.success('Pedido realizado!')
 *        gpToast.error('Algo deu errado')
 *        gpToast.info('Nova mensagem')
 *        gpToast.achievement('Badge conquistado! 🏆')
 */

(function () {
  'use strict';

  // Inject styles
  const style = document.createElement('style');
  style.textContent = `
    #gp-toast-container {
      position: fixed;
      top: 68px;
      right: 16px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }
    .gp-toast {
      pointer-events: all;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: #1e2939;
      border-radius: 14px;
      padding: 14px 16px 10px;
      min-width: 280px;
      max-width: 360px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
      border-left: 4px solid #4fc3f7;
      animation: gpSlideIn .3s cubic-bezier(.175,.885,.32,1.275) forwards;
      position: relative;
      overflow: hidden;
    }
    .gp-toast.leaving {
      animation: gpSlideOut .25s ease-in forwards;
    }
    .gp-toast.success { border-left-color: #22c55e; }
    .gp-toast.error   { border-left-color: #ef4444; }
    .gp-toast.info    { border-left-color: #4fc3f7; }
    .gp-toast.achievement { border-left-color: #ffd700; background: #1e1a08; }
    .gp-toast-icon { font-size: 22px; flex-shrink: 0; margin-top: 1px; }
    .gp-toast-body { flex: 1; }
    .gp-toast-msg  { color: #fff; font-size: 14px; font-weight: 500; line-height: 1.4; }
    .gp-toast-close {
      background: none;
      border: none;
      color: #666;
      font-size: 16px;
      cursor: pointer;
      padding: 0 2px;
      flex-shrink: 0;
    }
    .gp-toast-close:hover { color: #fff; }
    .gp-toast-progress {
      position: absolute;
      bottom: 0;
      left: 0;
      height: 3px;
      background: rgba(255,255,255,0.25);
      animation: gpProgress 4s linear forwards;
    }
    .gp-toast.achievement .gp-confetti {
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 100%;
      pointer-events: none;
      overflow: hidden;
    }
    .gp-confetti-piece {
      position: absolute;
      width: 6px;
      height: 6px;
      border-radius: 1px;
      animation: gpConfettiFall 1s ease-in forwards;
    }
    @keyframes gpSlideIn {
      from { opacity: 0; transform: translateX(110%); }
      to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes gpSlideOut {
      from { opacity: 1; transform: translateX(0); max-height: 200px; margin-bottom: 0; }
      to   { opacity: 0; transform: translateX(110%); max-height: 0; padding: 0; margin-bottom: -10px; }
    }
    @keyframes gpProgress {
      from { width: 100%; }
      to   { width: 0%; }
    }
    @keyframes gpConfettiFall {
      0%   { transform: translateY(-10px) rotate(0deg); opacity: 1; }
      100% { transform: translateY(60px) rotate(360deg); opacity: 0; }
    }
  `;
  document.head.appendChild(style);

  // Create container
  let container;
  function getContainer() {
    if (!container) {
      container = document.createElement('div');
      container.id = 'gp-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  const ICONS = {
    success:     '✅',
    error:       '❌',
    info:        'ℹ️',
    achievement: '🏆',
  };

  const MAX_TOASTS = 3;
  let active = 0;

  function createConfetti(el) {
    const colors = ['#ffd700', '#ff6b6b', '#4fc3f7', '#22c55e', '#a78bfa'];
    const wrapper = document.createElement('div');
    wrapper.className = 'gp-confetti';
    for (let i = 0; i < 12; i++) {
      const piece = document.createElement('div');
      piece.className = 'gp-confetti-piece';
      piece.style.left = `${Math.random() * 100}%`;
      piece.style.background = colors[Math.floor(Math.random() * colors.length)];
      piece.style.animationDelay = `${Math.random() * 0.4}s`;
      wrapper.appendChild(piece);
    }
    el.appendChild(wrapper);
  }

  function show({ type = 'info', message = '', duration = 4000 } = {}) {
    if (active >= MAX_TOASTS) return;
    active++;

    const c = getContainer();
    const toast = document.createElement('div');
    toast.className = `gp-toast ${type}`;

    toast.innerHTML = `
      <span class="gp-toast-icon">${ICONS[type] || 'ℹ️'}</span>
      <div class="gp-toast-body"><p class="gp-toast-msg">${message}</p></div>
      <button class="gp-toast-close" aria-label="Fechar">✕</button>
      <div class="gp-toast-progress"></div>
    `;

    if (type === 'achievement') createConfetti(toast);

    c.appendChild(toast);

    // Close on button click
    toast.querySelector('.gp-toast-close').addEventListener('click', () => dismiss(toast));

    // Auto-dismiss
    const timer = setTimeout(() => dismiss(toast), duration);
    toast._timer = timer;

    return toast;
  }

  function dismiss(toast) {
    clearTimeout(toast._timer);
    toast.classList.add('leaving');
    toast.addEventListener('animationend', () => {
      toast.remove();
      active = Math.max(0, active - 1);
    }, { once: true });
  }

  // Public API
  window.gpToast = {
    show,
    success:     (msg) => show({ type: 'success',     message: msg }),
    error:       (msg) => show({ type: 'error',       message: msg }),
    info:        (msg) => show({ type: 'info',        message: msg }),
    achievement: (msg) => show({ type: 'achievement', message: msg }),
  };
})();
