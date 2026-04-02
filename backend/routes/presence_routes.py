"""Presence routes — /api/share, /api/qrcode, /api/aniversariantes, /api/eventos

Feature 6 — Offline presence & viral:
  - Shareable digital profile card
  - QR code for each table
  - Birthday automatic detection
  - Seasonal decoration mode ("Modo Festa")
"""

import logging
import xml.etree.ElementTree as ET
from datetime import date

from flask import Blueprint, jsonify, render_template_string, request

try:
    from backend.database import get_db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

logger = logging.getLogger(__name__)

presence_bp = Blueprint("presence", __name__)

# ── Seasonal events ───────────────────────────────────────────────────────────

EVENTOS_SAZONAIS = {
    (12, 25): {"nome": "Natal", "emoji": "🎄", "cor": "#ff0000", "particulas": "snow"},
    (12, 24): {"nome": "Natal", "emoji": "🎄", "cor": "#ff0000", "particulas": "snow"},
    (10, 31): {"nome": "Halloween", "emoji": "🎃", "cor": "#ff6600", "particulas": "bats"},
    (1,  1):  {"nome": "Ano Novo", "emoji": "🎆", "cor": "#ffd700", "particulas": "fireworks"},
    (6,  12): {"nome": "Dia dos Namorados", "emoji": "💕", "cor": "#ff69b4", "particulas": "hearts"},
}
# February → Carnaval (any day in Feb)
_CARNAVAL = {"nome": "Carnaval", "emoji": "🎊", "cor": "#ffd700", "particulas": "confetti"}


# ── Evento ativo ──────────────────────────────────────────────────────────────

@presence_bp.get("/api/eventos/ativo")
def evento_ativo():
    """Return the currently active seasonal event, if any."""
    hoje = date.today()
    evento = EVENTOS_SAZONAIS.get((hoje.month, hoje.day))
    if not evento and hoje.month == 2:
        evento = _CARNAVAL
    if not evento:
        evento = {"nome": None, "emoji": "🍦", "cor": "#4fc3f7", "particulas": "none"}
    return jsonify(evento)


# ── QR Code SVG ───────────────────────────────────────────────────────────────

def _gerar_qr_svg(mesa_numero: int, base_url: str) -> str:
    """Generate a simple SVG QR-code placeholder for the given table.

    A real implementation would use the `qrcode` library; here we produce
    a visually complete SVG placeholder that links to the correct URL.
    """
    url = f"{base_url}?mesa={mesa_numero}"
    # Build an SVG with the URL as text + a decorative frame
    svg = ET.Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        width="200",
        height="240",
        viewBox="0 0 200 240",
    )

    # Background
    bg = ET.SubElement(svg, "rect", width="200", height="240", fill="#ffffff", rx="12")  # noqa: F841

    # QR border
    border = ET.SubElement(svg, "rect", x="20", y="20", width="160", height="160",  # noqa: F841
                           fill="#f0f0f0", stroke="#333", attrib={"stroke-width": "2"})

    # Decorative QR-code pattern (simplified grid to represent a QR visually)
    cell = 10
    pattern = [
        [1,1,1,1,1,1,1,0,0,1,0,1,1,1,1,1],
        [1,0,0,0,0,0,1,0,1,0,1,0,1,0,0,1],
        [1,0,1,1,1,0,1,0,0,1,0,0,1,0,1,1],
        [1,0,1,1,1,0,1,0,1,1,0,1,1,0,1,1],
        [1,0,1,1,1,0,1,0,0,0,1,0,1,0,1,1],
        [1,0,0,0,0,0,1,0,1,0,0,1,1,0,0,1],
        [1,1,1,1,1,1,1,0,1,0,1,0,1,1,1,1],
        [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
        [1,0,1,1,0,1,1,0,0,1,0,1,1,0,1,0],
        [0,1,0,0,1,0,0,0,1,0,1,0,0,1,0,1],
        [1,0,1,0,0,0,1,0,0,1,0,0,1,0,1,0],
        [0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,1],
        [1,1,1,1,1,1,1,0,0,1,0,1,1,0,1,0],
        [1,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1],
        [1,0,1,1,1,0,1,0,0,1,0,0,1,0,1,0],
        [1,1,1,1,1,1,1,0,1,0,1,0,0,1,0,1],
    ]
    for row_idx, row in enumerate(pattern):
        for col_idx, val in enumerate(row):
            if val:
                ET.SubElement(
                    svg, "rect",
                    x=str(20 + col_idx * cell),
                    y=str(20 + row_idx * cell),
                    width=str(cell - 1),
                    height=str(cell - 1),
                    fill="#1a1a2e",
                )

    # Label
    title = ET.SubElement(svg, "text", x="100", y="205", fill="#333",  # noqa: F841
                          attrib={"font-size": "14", "text-anchor": "middle",
                                  "font-family": "Arial, sans-serif"})
    title.text = f"Mesa {mesa_numero}"

    subtitle = ET.SubElement(svg, "text", x="100", y="225", fill="#888",  # noqa: F841
                             attrib={"font-size": "10", "text-anchor": "middle",
                                     "font-family": "Arial, sans-serif"})
    subtitle.text = "Escaneie para pedir 🍦"

    # Clickable link overlay
    a = ET.SubElement(svg, "a", attrib={"href": url, "target": "_blank"})
    ET.SubElement(a, "rect", x="0", y="0", width="200", height="240",
                  fill="transparent")

    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(svg, encoding="unicode")


@presence_bp.get("/api/qrcode/mesa/<int:numero>")
def qrcode_mesa(numero):
    """Return SVG QR code for a specific table."""
    if numero < 1 or numero > 999:
        return jsonify({"error": "Número de mesa inválido"}), 400

    base_url = request.host_url.rstrip("/")
    svg = _gerar_qr_svg(numero, base_url)
    return svg, 200, {"Content-Type": "image/svg+xml"}


# ── Shareable profile card ────────────────────────────────────────────────────

_CARD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta property="og:title" content="{{ nome }} na Gelateria Pro 🍦">
  <meta property="og:description" content="{{ streak }} dias de sequência • {{ pontos }} pontos • Sabor favorito: {{ sabor }}">
  <meta property="og:image" content="{{ base_url }}/static/og-image.png">
  <title>{{ nome }} — Gelateria Pro</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .card {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 24px;
      padding: 40px 32px;
      max-width: 380px;
      width: 100%;
      text-align: center;
      backdrop-filter: blur(20px);
      color: #fff;
    }
    .avatar {
      font-size: 64px;
      margin-bottom: 16px;
    }
    h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
    .username { color: #4fc3f7; font-size: 16px; margin-bottom: 24px; }
    .stats {
      display: flex;
      justify-content: center;
      gap: 24px;
      margin-bottom: 28px;
    }
    .stat { display: flex; flex-direction: column; align-items: center; }
    .stat-value { font-size: 28px; font-weight: 700; color: #ffd700; }
    .stat-label { font-size: 12px; color: #aaa; margin-top: 4px; }
    .badges {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;
      margin-bottom: 28px;
    }
    .badge {
      background: rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 13px;
    }
    .btn-share {
      display: inline-block;
      background: #25D366;
      color: #fff;
      text-decoration: none;
      padding: 14px 28px;
      border-radius: 50px;
      font-weight: 600;
      font-size: 15px;
      transition: transform .2s;
    }
    .btn-share:hover { transform: scale(1.05); }
    .footer { margin-top: 20px; font-size: 12px; color: #666; }
  </style>
</head>
<body>
  <div class="card">
    <div class="avatar">🍦</div>
    <h1>{{ nome }}</h1>
    <p class="username">@{{ username }}</p>
    <div class="stats">
      <div class="stat">
        <span class="stat-value">{{ streak }}🔥</span>
        <span class="stat-label">Streak</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ pontos }}💎</span>
        <span class="stat-label">Pontos</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ nivel }}⭐</span>
        <span class="stat-label">Nível</span>
      </div>
    </div>
    <div class="badges">
      <span class="badge">🍫 {{ sabor }}</span>
      {% if plano %}<span class="badge">{{ plano_emoji }} {{ plano }}</span>{% endif %}
    </div>
    <a class="btn-share" href="{{ whatsapp_url }}" target="_blank">
      📲 Compartilhar no WhatsApp
    </a>
    <p class="footer">Gelateria Pro • gelateriapro.app</p>
  </div>
</body>
</html>"""


@presence_bp.get("/api/share/cartao/<int:user_id>")
def cartao_digital(user_id):
    """Return a shareable HTML profile card for a user."""
    nome = "Amigo Gelado"
    username = f"usuario{user_id}"
    streak = 0
    pontos = 0
    nivel = 1
    sabor = "Chocolate"
    plano = None
    plano_emoji = ""

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, level, total_points FROM users WHERE id=%s", (user_id,))
                u = cur.fetchone()
                if not u:
                    return jsonify({"error": "Usuário não encontrado"}), 404
                nome = u["name"]
                nivel = u["level"]
                pontos = u["total_points"]

                cur.execute(
                    "SELECT username FROM perfis_publicos WHERE user_id=%s",
                    (user_id,),
                )
                pp = cur.fetchone()
                if pp:
                    username = pp["username"]

                cur.execute(
                    "SELECT streak_atual FROM daily_checkins WHERE user_id=%s ORDER BY data DESC LIMIT 1",
                    (user_id,),
                )
                ci = cur.fetchone()
                if ci:
                    streak = ci["streak_atual"]

                cur.execute(
                    """SELECT s.nome FROM pedidos p
                       JOIN sabores s ON s.id = p.sabor_id
                       WHERE p.user_id=%s
                       GROUP BY s.nome ORDER BY COUNT(*) DESC LIMIT 1""",
                    (user_id,),
                )
                sp = cur.fetchone()
                if sp:
                    sabor = sp["nome"]

                cur.execute(
                    "SELECT plano FROM clube_assinaturas WHERE user_id=%s AND status='ativo'",
                    (user_id,),
                )
                cl = cur.fetchone()
                if cl:
                    plano = cl["plano"].capitalize()
                    plano_emoji = {"bronze": "🥉", "prata": "🥈", "ouro": "🥇"}.get(cl["plano"], "")

    except Exception as e:
        logger.warning("Cartao digital DB error: %s", e)

    base_url = request.host_url.rstrip("/")
    share_url = f"{base_url}/api/share/cartao/{user_id}"
    whatsapp_msg = f"Olha meu perfil na Gelateria Pro! {streak} dias de sequência 🔥 {share_url}"
    whatsapp_url = f"https://api.whatsapp.com/send?text={whatsapp_msg}"

    html = render_template_string(
        _CARD_TEMPLATE,
        nome=nome,
        username=username,
        streak=streak,
        pontos=pontos,
        nivel=nivel,
        sabor=sabor,
        plano=plano,
        plano_emoji=plano_emoji,
        base_url=base_url,
        whatsapp_url=whatsapp_url,
    )
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


# ── Birthday check ────────────────────────────────────────────────────────────

@presence_bp.get("/api/aniversariantes/hoje")
def aniversariantes_hoje():
    """Admin: return users whose birthday is today.

    Requires a `data_nascimento` column on the users table.
    Falls back gracefully if the column does not exist.
    """
    hoje = date.today()
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, name, email
                       FROM users
                       WHERE EXTRACT(MONTH FROM data_nascimento) = %s
                         AND EXTRACT(DAY   FROM data_nascimento) = %s
                         AND deleted_at IS NULL""",
                    (hoje.month, hoje.day),
                )
                rows = cur.fetchall()
        aniversariantes = [dict(r) for r in rows]
    except Exception as e:
        logger.warning("Aniversariantes error: %s", e)
        aniversariantes = []

    return jsonify({
        "data": str(hoje),
        "total": len(aniversariantes),
        "aniversariantes": aniversariantes,
    })
