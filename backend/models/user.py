import hashlib
import os
import secrets

from backend.database import get_db

_SCRYPT_N = 2 ** 14  # CPU/memory cost (16 384 rounds)
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_BYTES = 16


def _hash_password(password: str) -> str:
    """Return a stored hash string using scrypt: <hex-salt>$<hex-hash>"""
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
    )
    return salt.hex() + "$" + digest.hex()


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plaintext password against a stored scrypt hash (salt$hash)."""
    try:
        salt_hex, digest_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, Exception):
        return False
    expected = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
    )
    return secrets.compare_digest(expected, bytes.fromhex(digest_hex))


def criar_usuario(name: str, email: str, password: str):
    """Insert a new user and return the row (without password_hash)."""
    password_hash = _hash_password(password)
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, level, total_points, created_at
                """,
                (name, email, password_hash),
            )
            return cur.fetchone()


def buscar_usuario_por_email(email: str):
    """Return the full user row including password_hash, or None."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE email = %s AND deleted_at IS NULL",
                (email,),
            )
            return cur.fetchone()


def autenticar_usuario(email: str, password: str):
    """Return (user_row_without_hash, None) on success or (None, error_msg) on failure."""
    user = buscar_usuario_por_email(email)
    if not user:
        return None, "Credenciais inválidas."
    if not _verify_password(password, user["password_hash"]):
        return None, "Credenciais inválidas."
    safe = {k: v for k, v in dict(user).items() if k != "password_hash"}
    return safe, None
