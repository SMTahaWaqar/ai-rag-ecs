import os
import psycopg

def dsn() -> str:
    return os.environ.get("DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag")

def connect():
    return psycopg.connect(dsn())