import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            database=os.environ.get("DB_NAME", "gelateria"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", ""),
            port=os.environ.get("DB_PORT", 5432),
            cursor_factory=RealDictCursor,
        )
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(os.path.dirname(__file__), "../database/schema.sql"), "r") as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    conn.close()
