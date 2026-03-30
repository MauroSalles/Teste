import hashlib
import os
import secrets

from backend.database import get_db


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False


def criar_usuario(name: str, email: str, password: str):
    password_hash = _hash_password(password)
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, level, total_points, created_at
                """,
                (name, email, password_hash),
            )
            return cursor.fetchone()


def buscar_usuario_por_email(email: str):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND deleted_at IS NULL",
                (email,),
            )
            return cursor.fetchone()


def buscar_usuario_por_id(user_id: int):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email, level, total_points, created_at FROM users WHERE id = %s AND deleted_at IS NULL",
                (user_id,),
            )
            return cursor.fetchone()


def autenticar_usuario(email: str, password: str):
    """Return user dict on success, None on failure."""
    user = buscar_usuario_por_email(email)
    if not user:
        return None
    if not _verify_password(password, user["password_hash"]):
        return None
    return user
