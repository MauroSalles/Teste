/**
 * navbar.js — Global navigation component injected into all pages.
 * Shows: streak 🔥, points 💎, user name, notification badge.
 * Usage: <script src="js/navbar.js"></script> in <head>
 */

(function () {
  'use strict';

  const API = '';

  // Inject CSS
  const style = document.createElement('style');
  style.textContent = `
    #gp-navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
      background: rgba(13, 17, 23, 0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      display: flex;
      align-items: center;
      padding: 0 20px;
      height: 56px;
      gap: 8px;
    }
    #gp-navbar .nb-logo {
      font-size: 22px;
      font-weight: 800;
      color: #4fc3f7;
      text-decoration: none;
      flex-shrink: 0;
    }
    #gp-navbar .nb-links {
      display: flex;
      gap: 4px;
      flex: 1;
      justify-content: center;
      flex-wrap: wrap;
    }
    #gp-navbar .nb-link {
      color: #aaa;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
      padding: 6px 10px;
      border-radius: 8px;
      transition: color .2s, background .2s;
    }
    #gp-navbar .nb-link:hover { color: #fff; background: rgba(255,255,255,0.08); }
    #gp-navbar .nb-link.active { color: #4fc3f7; }
    #gp-navbar .nb-stats {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }
    #gp-navbar .nb-stat {
      font-size: 13px;
      font-weight: 700;
      color: #fff;
    }
    #gp-navbar .nb-badge {
      position: relative;
      cursor: pointer;
    }
    #gp-navbar .nb-badge-dot {
      position: absolute;
      top: -4px;
      right: -4px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ef4444;
      display: none;
    }
    #gp-navbar .nb-user {
      font-size: 13px;
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
    #gp-navbar .nb-login {
      font-size: 13px;
      color: #4fc3f7;
      text-decoration: none;
      font-weight: 600;
    }
    body { padding-top: 56px !important; }
    @media (max-width: 600px) {
      #gp-navbar .nb-links { display: none; }
    }
  `;
  document.head.appendChild(style);

  // Build navbar HTML
  function buildNavbar() {
    const nav = document.createElement('nav');
    nav.id = 'gp-navbar';

    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const links = [
      { href: 'index.html',     label: 'Terminal' },
      { href: 'dashboard.html', label: 'Dashboard' },
      { href: 'feed.html',      label: 'Feed' },
      { href: 'landing.html',   label: 'Início' },
    ];

    const linksHtml = links.map(l =>
      `<a class="nb-link ${currentPage === l.href ? 'active' : ''}" href="${l.href}">${l.label}</a>`
    ).join('');

    nav.innerHTML = `
      <a class="nb-logo" href="landing.html">🍦 Gelateria</a>
      <div class="nb-links">${linksHtml}</div>
      <div class="nb-stats">
        <span class="nb-stat" id="nb-streak" title="Streak atual"></span>
        <span class="nb-stat" id="nb-points" title="Pontos"></span>
        <span class="nb-badge" id="nb-notif" title="Notificações">
          🔔<span class="nb-badge-dot" id="nb-badge-dot"></span>
        </span>
        <span class="nb-user" id="nb-user"></span>
      </div>
    `;

    document.body.insertBefore(nav, document.body.firstChild);
  }

  // Load user stats from API
  async function loadStats() {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (!token || !userStr) {
      document.getElementById('nb-user').innerHTML = `<a class="nb-login" href="auth.html">Entrar</a>`;
      return;
    }

    const user = JSON.parse(userStr);
    document.getElementById('nb-user').textContent = user.name ? user.name.split(' ')[0] : 'Eu';

    try {
      const r = await fetch(`${API}/api/daily/streak/${user.id}`);
      if (r.ok) {
        const d = await r.json();
        if (d.streak > 0) {
          document.getElementById('nb-streak').textContent = `🔥 ${d.streak}`;
        }
      }
    } catch (_) {}

    try {
      const r = await fetch(`${API}/api/fidelidade/${user.id}`);
      if (r.ok) {
        const d = await r.json();
        if (d.pontos != null) {
          document.getElementById('nb-points').textContent = `💎 ${d.pontos}`;
        }
      }
    } catch (_) {}
  }

  // Expose badge toggling for other modules
  window.gpNavbar = {
    showNotificationBadge() {
      const dot = document.getElementById('nb-badge-dot');
      if (dot) dot.style.display = 'block';
    },
    hideNotificationBadge() {
      const dot = document.getElementById('nb-badge-dot');
      if (dot) dot.style.display = 'none';
    },
  };

  // Init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { buildNavbar(); loadStats(); });
  } else {
    buildNavbar();
    loadStats();
  }
})();
