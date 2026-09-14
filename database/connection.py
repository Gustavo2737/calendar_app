import sqlite3

def get_connection():
    """Cria e retorna uma conexão com o arquivo do banco de dados."""
    return sqlite3.connect("app_database.db")

def create_tables():
    """Cria as tabelas necessárias e garante as colunas novas se já existirem."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de tarefas atualizada com priority e category
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            is_completed INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'Normal',
            category TEXT DEFAULT 'Geral',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Bloco de segurança para bancos antigos que já foram criados sem essas colunas
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Normal'")
    except sqlite3.OperationalError:
        pass # A coluna já existe, então apenas ignoramos o erro
        
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'Geral'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("Banco de dados atualizado e inicializado com sucesso!")