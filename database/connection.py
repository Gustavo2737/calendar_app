import sqlite3
from core.logger import get_logger

logger = get_logger("DatabaseConnection")

def get_connection():
    try:
        return sqlite3.connect("app_database.db")
    except Exception as e:
        logger.error(f"Erro SQLite: {e}")
        raise

def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                is_completed INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'Normal',
                category TEXT DEFAULT 'Geral',
                is_routine INTEGER DEFAULT 0,
                due_date TEXT,
                due_time INTEGER,
                recurrence TEXT,
                last_completed_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migração segura
        for col, col_type in [("is_routine", "INTEGER DEFAULT 0"), ("due_date", "TEXT"), ("due_time", "INTEGER"), ("recurrence", "TEXT"), ("last_completed_date", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()
        logger.info("Tabelas sincronizadas.")
    except Exception as e:
        logger.critical(f"Falha ao criar tabelas: {e}")