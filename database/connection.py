import sqlite3

def get_connection():
    return sqlite3.connect("app_database.db")

def create_tables():
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
            due_date TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # (Nova coluna due_date adicionada acima)
    
    conn.commit()
    conn.close()
    print("Banco de dados atualizado e inicializado com sucesso!")