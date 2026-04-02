/**
 * onboarding.js — Interactive 5-step first-time user tutorial.
 * Uses spotlight (dark overlay) to highlight page elements.
 * Saved in localStorage — never shown twice.
 * Usage: <script src="js/onboarding.js"></script>
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'gp_onboarding_done';

  // Skip if already done
  if (localStorage.getItem(STORAGE_KEY) === '1') return;
  // Skip on auth page
  if (window.location.pathname.includes('auth.html')) return;

  const STEPS = [
    {
      title: '🍦 Bem-vindo à Gelateria Pro!',
      text: 'O sistema de gestão mais saboroso do Brasil. Vamos te mostrar os principais recursos em 5 passos.',
      selector: null, // Center modal, no spotlight
    },
    {
      title: '🗂️ Explore o Cardápio',
      text: 'Navegue pelos sabores disponíveis, preços e informações nutricionais diretamente aqui.',
      selector: '.nb-link[href="dashboard.html"]',
    },
    {
      title: '📦 Faça seu Primeiro Pedido',
      text: 'Use o terminal ou o dashboard para registrar pedidos em tempo real.',
      selector: '.nb-link[href="index.html"]',
    },
    {
      title: '💎 Ganhe Pontos & Badges',
      text: 'A cada pedido e check-in diário você acumula pontos e sobe de nível. Mantenha sua sequência!',
      selector: '#nb-streak, #nb-points',
    },
    {
      title: '🚀 Pronto para começar!',
      text: 'Você já sabe o essencial. Explore, divirta-se e qualquer dúvida o Gelinho está aqui para ajudar!',
      selector: null,
    },
  ];

  let currentStep = 0;

  // Inject styles
  const style = document.createElement('style');
  style.textContent = `
    #gp-onboarding-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.72);
      z-index: 8000;
      pointer-events: all;
    }
    #gp-onboarding-spotlight {
      position: absolute;
      border-radius: 10px;
      box-shadow: 0 0 0 9999px rgba(0,0,0,0.72);
      pointer-events: none;
      transition: all .35s cubic-bezier(.4,0,.2,1);
    }
    #gp-onboarding-card {
      position: fixed;
      bottom: 32px;
      left: 50%;
      transform: translateX(-50%);
      background: #1e2939;
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 20px;
      padding: 28px 32px;
      max-width: 420px;
      width: calc(100% - 40px);
      color: #fff;
      z-index: 8001;
      box-shadow: 0 20px 60px rgba(0,0,0,0.6);
      animation: gpOBIn .35s cubic-bezier(.175,.885,.32,1.275) forwards;
    }
    #gp-onboarding-card h2 { font-size: 20px; font-weight: 700; margin-bottom: 10px; }
    #gp-onboarding-card p  { font-size: 15px; color: #aaa; line-height: 1.5; margin-bottom: 20px; }
    .gp-ob-footer { display: flex; align-items: center; justify-content: space-between; }
    .gp-ob-dots { display: flex; gap: 6px; }
    .gp-ob-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: rgba(255,255,255,0.2);
      transition: background .2s;
    }
    .gp-ob-dot.active { background: #4fc3f7; }
    .gp-ob-btns { display: flex; gap: 10px; }
    .gp-ob-btn {
      padding: 10px 20px;
      border-radius: 10px;
      border: none;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity .2s;
    }
    .gp-ob-btn:hover { opacity: .85; }
    .gp-ob-btn.primary { background: #4fc3f7; color: #0d1117; }
    .gp-ob-btn.skip    { background: rgba(255,255,255,0.08); color: #aaa; }
    @keyframes gpOBIn {
      from { opacity: 0; transform: translateX(-50%) translateY(20px); }
      to   { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
  `;
  document.head.appendChild(style);

  // Build DOM
  const overlay = document.createElement('div');
  overlay.id = 'gp-onboarding-overlay';

  const spotlight = document.createElement('div');
  spotlight.id = 'gp-onboarding-spotlight';
  overlay.appendChild(spotlight);

  const card = document.createElement('div');
  card.id = 'gp-onboarding-card';
  document.body.appendChild(overlay);
  document.body.appendChild(card);

  function renderStep(i) {
    const step = STEPS[i];

    // Spotlight
    if (step.selector) {
      const el = document.querySelector(step.selector);
      if (el) {
        const rect = el.getBoundingClientRect();
        const pad = 8;
        Object.assign(spotlight.style, {
          left:   `${rect.left - pad}px`,
          top:    `${rect.top - pad}px`,
          width:  `${rect.width + pad * 2}px`,
          height: `${rect.height + pad * 2}px`,
          display: 'block',
        });
      } else {
        spotlight.style.display = 'none';
      }
    } else {
      spotlight.style.display = 'none';
    }

    // Dots
    const dots = STEPS.map((_, idx) =>
      `<span class="gp-ob-dot ${idx === i ? 'active' : ''}"></span>`
    ).join('');

    const isLast = i === STEPS.length - 1;

    card.innerHTML = `
      <h2>${step.title}</h2>
      <p>${step.text}</p>
      <div class="gp-ob-footer">
        <div class="gp-ob-dots">${dots}</div>
        <div class="gp-ob-btns">
          <button class="gp-ob-btn skip" id="gp-ob-skip">Pular</button>
          <button class="gp-ob-btn primary" id="gp-ob-next">
            ${isLast ? 'Começar! 🚀' : 'Próximo →'}
          </button>
        </div>
      </div>
    `;

    document.getElementById('gp-ob-skip').addEventListener('click', finish);
    document.getElementById('gp-ob-next').addEventListener('click', () => {
      if (i < STEPS.length - 1) {
        currentStep++;
        renderStep(currentStep);
      } else {
        finish();
      }
    });
  }

  function finish() {
    localStorage.setItem(STORAGE_KEY, '1');
    overlay.remove();
    card.remove();
  }

  // Start when DOM is ready
  function init() {
    renderStep(0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    setTimeout(init, 800); // slight delay for page render
  }
})();
