"""User model — registration, login, and profile queries."""

import logging
import bcrypt
from backend.database import get_db

logger = logging.getLogger(__name__)


def criar_usuario(nome: str, email: str, senha: str, role: str = "user") -> dict | None:
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id, nome, email, role, criado_em
                """,
                (nome, email, hashed, role),
            )
            return cur.fetchone()


def buscar_usuario_por_email(email: str) -> dict | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, senha_hash, role FROM usuarios WHERE email = %s",
                (email,),
            )
            return cur.fetchone()


def buscar_usuario_por_id(user_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, role, criado_em FROM usuarios WHERE id = %s",
                (user_id,),
            )
            return cur.fetchone()


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha_plain.encode(), senha_hash.encode())


def listar_usuarios() -> list:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, role, criado_em FROM usuarios ORDER BY criado_em DESC"
            )
            return cur.fetchall()
