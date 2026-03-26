from backend.database import get_db


# ── Cash register ─────────────────────────────────────────────────────────────

def abrir_caixa(valor_abertura=0.0):
    """Open a new cash register session. Automatically closes any existing open sessions first."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Auto-close any session left open from a previous day
            cursor.execute(
                """
                UPDATE caixa
                SET status = 'fechado', data_fechamento = CURRENT_TIMESTAMP
                WHERE status = 'aberto'
                """
            )
            cursor.execute(
                "INSERT INTO caixa (valor_abertura, status) VALUES (%s, 'aberto') RETURNING *",
                (float(valor_abertura),),
            )
            return cursor.fetchone()


def fechar_caixa(valor_fechamento):
    """Close the currently open cash register session."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE caixa
                SET status = 'fechado',
                    data_fechamento = CURRENT_TIMESTAMP,
                    valor_fechamento = %s
                WHERE status = 'aberto'
                RETURNING *
                """,
                (float(valor_fechamento),),
            )
            return cursor.fetchone()


def caixa_atual():
    """Return the currently open cash register session, if any."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM caixa WHERE status = 'aberto' ORDER BY id DESC LIMIT 1")
            return cursor.fetchone()


def registrar_despesa(descricao, valor, caixa_id=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO despesas (caixa_id, descricao, valor) VALUES (%s, %s, %s) RETURNING *",
                (caixa_id, descricao, float(valor)),
            )
            return cursor.fetchone()


def listar_despesas(caixa_id=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            if caixa_id:
                cursor.execute(
                    "SELECT * FROM despesas WHERE caixa_id = %s ORDER BY data DESC",
                    (caixa_id,),
                )
            else:
                cursor.execute("SELECT * FROM despesas ORDER BY data DESC LIMIT 50")
            return cursor.fetchall()


# ── Financial analytics ───────────────────────────────────────────────────────

def kpis_gerais():
    """Return aggregate KPIs from existing orders data."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(p.id)                                              AS total_pedidos,
                    COALESCE(SUM(p.quantidade * s.preco), 0)                 AS faturamento_total,
                    COALESCE(AVG(p.quantidade * s.preco), 0)                 AS ticket_medio,
                    COALESCE(SUM(p.quantidade * s.preco)
                        FILTER (WHERE p.data >= CURRENT_DATE), 0)            AS faturamento_hoje,
                    COUNT(p.id) FILTER (WHERE p.data >= CURRENT_DATE)        AS pedidos_hoje,
                    COALESCE(SUM(p.quantidade * s.preco)
                        FILTER (WHERE p.data >= DATE_TRUNC('month', CURRENT_DATE)), 0)
                                                                             AS faturamento_mes
                FROM pedidos p
                JOIN sabores s ON s.id = p.sabor_id
                """
            )
            return cursor.fetchone()


def top_sabores(limite=5):
    """Return the top-selling flavors by number of units sold."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    s.id,
                    s.nome,
                    s.preco,
                    COALESCE(SUM(p.quantidade), 0)         AS unidades_vendidas,
                    COALESCE(SUM(p.quantidade * s.preco), 0) AS faturamento
                FROM sabores s
                LEFT JOIN pedidos p ON p.sabor_id = s.id
                GROUP BY s.id, s.nome, s.preco
                ORDER BY unidades_vendidas DESC
                LIMIT %s
                """,
                (limite,),
            )
            return cursor.fetchall()


def faturamento_por_periodo(inicio, fim):
    """Return daily revenue between two dates."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    DATE(p.data)                              AS dia,
                    COUNT(p.id)                               AS pedidos,
                    SUM(p.quantidade)                         AS unidades,
                    COALESCE(SUM(p.quantidade * s.preco), 0)  AS faturamento
                FROM pedidos p
                JOIN sabores s ON s.id = p.sabor_id
                WHERE DATE(p.data) BETWEEN %s AND %s
                GROUP BY dia
                ORDER BY dia
                """,
                (inicio, fim),
            )
            return cursor.fetchall()


def despesas_caixa_atual():
    """Return total expenses for the currently open cash session."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COALESCE(SUM(d.valor), 0) AS total_despesas
                FROM despesas d
                JOIN caixa c ON c.id = d.caixa_id
                WHERE c.status = 'aberto'
                """
            )
            return cursor.fetchone()
