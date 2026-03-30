"""
Loyalty (fidelidade) model.

Rules:
- Each order gives 10 points per item (quantidade).
- Every 100 points earns 1 resgate (free-item reward).
- Points are cumulative and never reset; resgates track how many have been granted.
"""

from backend.database import get_db

POINTS_PER_ITEM = 10
POINTS_PER_RESGATE = 100


def adicionar_pontos(user_id: int, quantidade: int) -> dict:
    """Add loyalty points for a new order and grant resgates if threshold met."""
    pontos_ganhos = quantidade * POINTS_PER_ITEM
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Upsert fidelidade row
            cursor.execute(
                """
                INSERT INTO fidelidade (user_id, pontos, resgates)
                VALUES (%s, %s, 0)
                ON CONFLICT (user_id) DO UPDATE
                  SET pontos     = fidelidade.pontos + EXCLUDED.pontos,
                      updated_at = CURRENT_TIMESTAMP
                RETURNING pontos, resgates
                """,
                (user_id, pontos_ganhos),
            )
            row = cursor.fetchone()
            pontos_total = row["pontos"]
            resgates_atual = row["resgates"]

            # Grant resgates for every 100-point threshold crossed
            resgates_devidos = pontos_total // POINTS_PER_RESGATE
            if resgates_devidos > resgates_atual:
                cursor.execute(
                    "UPDATE fidelidade SET resgates = %s WHERE user_id = %s RETURNING pontos, resgates",
                    (resgates_devidos, user_id),
                )
                row = cursor.fetchone()

            return dict(row)


def obter_pontos(user_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, pontos, resgates, updated_at FROM fidelidade WHERE user_id = %s",
                (user_id,),
            )
            return cursor.fetchone()


def resgatar(user_id: int) -> dict:
    """
    Redeem one reward.  Requires at least POINTS_PER_RESGATE points available
    (pontos - resgates_usados * POINTS_PER_RESGATE >= POINTS_PER_RESGATE).
    Returns updated fidelidade row or raises ValueError.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT pontos, resgates FROM fidelidade WHERE user_id = %s FOR UPDATE",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Usuário não possui pontos de fidelidade.")

            pontos = row["pontos"]
            resgates = row["resgates"]
            pontos_disponiveis = pontos - resgates * POINTS_PER_RESGATE

            if pontos_disponiveis < POINTS_PER_RESGATE:
                raise ValueError(
                    f"Pontos insuficientes. Você tem {pontos_disponiveis} pontos disponíveis "
                    f"(necessário: {POINTS_PER_RESGATE})."
                )

            cursor.execute(
                """
                UPDATE fidelidade
                SET resgates = resgates + 1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                RETURNING pontos, resgates, updated_at
                """,
                (user_id,),
            )
            return dict(cursor.fetchone())
