from database.connection import get_connection
from models.task_model import Task

class TaskRepository:
    def __init__(self):
        self.table_name = "tasks"

    def add_task(self, task: Task):
        """Salva uma nova tarefa no banco de dados."""
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"""
            INSERT INTO {self.table_name} (title, description, is_completed, priority, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            task.title, 
            task.description, 
            task.is_completed,
            task.priority,
            task.category, 
            task.created_at
        ))
        
        conn.commit()
        conn.close()

    def get_all_tasks(self):
        """Busca todas as tarefas cadastradas no banco de dados."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT id, title, description, is_completed, priority, category, created_at 
            FROM {self.table_name}
        """)
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task_obj = Task(
                id=row[0],
                title=row[1],
                description=row[2],
                is_completed=row[3],
                priority=row[4],
                category=row[5],
                created_at=row[6]
            )
            tasks.append(task_obj)
            
        return tasks

    def update_task(self, task: Task):
        """Atualiza os dados de uma tarefa existente."""
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"""
            UPDATE {self.table_name}
            SET title = ?, description = ?, is_completed = ?, priority = ?, category = ?
            WHERE id = ?
        """
        cursor.execute(sql, (
            task.title,
            task.description,
            task.is_completed,
            task.priority,
            task.category,
            task.id
        ))
        
        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        """Apaga uma tarefa do banco pelo ID."""
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"DELETE FROM {self.table_name} WHERE id = ?"
        cursor.execute(sql, (task_id,))
        
        conn.commit()
        conn.close()