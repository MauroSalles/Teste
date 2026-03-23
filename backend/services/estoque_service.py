from typing import Any

from database import get_connection


def listar_estoque() -> list[dict[str, Any]]:
    """Return stock levels for all flavors."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.nome, e.quantidade, s.preco
                FROM estoque e
                JOIN sabores s ON e.sabor_id = s.id
                ORDER BY s.nome
                """
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def atualizar_estoque(
    sabor_nome: str, quantidade: int
) -> tuple[dict[str, Any] | None, str | None]:
    """Set the stock quantity for a flavor by name.

    Returns ``(result_dict, None)`` on success or ``(None, error_message)``
    on failure.

    Raises:
        ValueError: if *quantidade* is negative.
    """
    if quantidade < 0:
        raise ValueError("A quantidade não pode ser negativa.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM sabores WHERE LOWER(nome) = LOWER(%s)",
                (sabor_nome,),
            )
            sabor = cur.fetchone()
            if not sabor:
                return None, "Sabor não encontrado"

            cur.execute(
                "UPDATE estoque SET quantidade = %s, atualizado_em = NOW() "
                "WHERE sabor_id = %s RETURNING quantidade",
                (int(quantidade), sabor["id"]),
            )
            updated = cur.fetchone()
        conn.commit()
    return {"quantidade": updated["quantidade"]}, None
