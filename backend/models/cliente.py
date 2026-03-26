from backend.database import get_db

_TIER_THRESHOLDS = [
    (500, "Ouro"),
    (200, "Prata"),
    (0,   "Bronze"),
]


def _calcular_tier(pontos: int) -> str:
    for threshold, tier in _TIER_THRESHOLDS:
        if pontos >= threshold:
            return tier
    return "Bronze"


def listar_clientes():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM clientes ORDER BY nome"
            )
            return cursor.fetchall()


def adicionar_cliente(nome, email=None, telefone=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO clientes (nome, email, telefone)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (nome, email or None, telefone or None),
            )
            return cursor.fetchone()


def buscar_cliente_por_id(cliente_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
            return cursor.fetchone()


def buscar_cliente_por_nome(nome):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM clientes WHERE LOWER(nome) LIKE LOWER(%s) ORDER BY nome",
                (f"%{nome}%",),
            )
            return cursor.fetchall()


def adicionar_pontos(cliente_id, pontos):
    """Add loyalty points to a customer and recalculate their tier."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + %s WHERE id = %s RETURNING *",
                (pontos, cliente_id),
            )
            cliente = cursor.fetchone()
            if not cliente:
                return None
            novo_tier = _calcular_tier(int(cliente["pontos_fidelidade"]))
            cursor.execute(
                "UPDATE clientes SET tier = %s WHERE id = %s RETURNING *",
                (novo_tier, cliente_id),
            )
            return cursor.fetchone()


def segmentacao_clientes():
    """Return customers grouped by tier with aggregate spend data."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.tier,
                    COUNT(c.id)                                    AS total_clientes,
                    COALESCE(SUM(c.pontos_fidelidade), 0)          AS total_pontos
                FROM clientes c
                GROUP BY c.tier
                ORDER BY total_pontos DESC
                """
            )
            return cursor.fetchall()


def top_clientes(limite=5):
    """Return the top customers by loyalty points."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, email, pontos_fidelidade, tier FROM clientes ORDER BY pontos_fidelidade DESC LIMIT %s",
                (limite,),
            )
            return cursor.fetchall()
