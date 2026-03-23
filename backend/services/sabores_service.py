from typing import Any

from psycopg2 import IntegrityError

from database import get_connection


def listar_sabores() -> list[dict[str, Any]]:
    """Return all flavors ordered by name."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, preco, disponivel FROM sabores ORDER BY nome")
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def buscar_sabores(termo: str) -> list[dict[str, Any]]:
    """Return flavors whose name contains *termo* (case-insensitive)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, preco, disponivel FROM sabores "
                "WHERE nome ILIKE %s ORDER BY nome",
                (f"%{termo}%",),
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def adicionar_sabor(nome: str, preco: float) -> dict[str, Any] | None:
    """Insert a new flavor and initialise a stock entry.

    Returns the created sabor dict, or ``None`` if the name already exists.

    Raises:
        ValueError: if *preco* is not positive.
    """
    if preco <= 0:
        raise ValueError("O preço deve ser maior que zero.")
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO sabores (nome, preco) VALUES (%s, %s) RETURNING id, nome, preco",
                    (nome, float(preco)),
                )
                sabor = dict(cur.fetchone())
                cur.execute(
                    "INSERT INTO estoque (sabor_id, quantidade) VALUES (%s, 0)",
                    (sabor["id"],),
                )
                conn.commit()
            except IntegrityError:
                return None
    return sabor


def remover_sabor(sabor_id: int) -> dict[str, Any] | None:
    """Delete a flavor by id. Returns the deleted row or ``None`` if not found."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM sabores WHERE id = %s RETURNING nome",
                (int(sabor_id),),
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row) if row else None
