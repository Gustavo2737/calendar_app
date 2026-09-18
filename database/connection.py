import sqlite3
from core.logger import get_logger

logger = get_logger("Database")

def get_connection():
    return sqlite3.connect("app_database.db")

def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tabela principal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                is_routine INTEGER DEFAULT 0,
                due_date TEXT,
                due_time INTEGER, 
                end_time INTEGER,
                recurrence_type TEXT, 
                recurrence_data TEXT, 
                last_completed_date TEXT,
                project_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migração automática para garantir colunas em bancos existentes
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        missing_cols = {
            "recurrence_type": "TEXT",
            "recurrence_data": "TEXT",
            "end_time": "INTEGER",
            "project_id": "INTEGER",
            "last_completed_date": "TEXT",
            "is_routine": "INTEGER DEFAULT 0"
        }
        
        for col_name, col_type in missing_cols.items():
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
                logger.info(f"Coluna {col_name} adicionada com sucesso à tabela tasks.")

        # Outras tabelas do ecossistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                streak INTEGER DEFAULT 0,
                last_done TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'A Fazer'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                duration_minutes INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Schema do banco de dados inicializado e validado.")
    except Exception as e:
        logger.critical(f"Falha crítica no banco de dados: {e}")