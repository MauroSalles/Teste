"""Feedback model — customer satisfaction ratings and comments."""

from backend.database import get_db


def registrar_feedback(nome: str, email: str, mensagem: str, nota: int):
    """Insert a feedback record and return the new row."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO feedback (nome, email, mensagem, nota)
                VALUES (%s, %s, %s, %s)
                RETURNING id, nome, email, mensagem, nota, criado_em
                """,
                (nome, email, mensagem, nota),
            )
            return cursor.fetchone()


def listar_feedbacks(limit: int = 50):
    """Return the most recent feedback records, newest first."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, mensagem, nota, criado_em FROM feedback ORDER BY criado_em DESC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()


def media_nota() -> float:
    """Return the average rating across all feedback, or 0.0 if none."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT AVG(nota)::FLOAT FROM feedback")
            row = cursor.fetchone()
            if row and row["avg"] is not None:
                return round(row["avg"], 2)
            return 0.0
