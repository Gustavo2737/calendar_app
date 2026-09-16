from database.connection import get_connection
from models.task_model import Task

class TaskRepository:
    def __init__(self):
        self.table_name = "tasks"

    def add_task(self, task: Task):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Adicionamos o due_date no INSERT
        sql = f"""
            INSERT INTO {self.table_name} (title, description, is_completed, priority, category, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            task.title, 
            task.description, 
            task.is_completed,
            task.priority,
            task.category, 
            task.due_date, # Novo campo
            task.created_at
        ))
        
        conn.commit()
        conn.close()

    def get_all_tasks(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Adicionamos o due_date no SELECT (agora é o índice 6)
        cursor.execute(f"""
            SELECT id, title, description, is_completed, priority, category, due_date, created_at 
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
                due_date=row[6], # Novo campo mapeado
                created_at=row[7]
            )
            tasks.append(task_obj)
            
        return tasks

    def get_tasks_by_date(self, date_str: str):
        """Busca no banco apenas as tarefas agendadas para uma data específica (YYYY-MM-DD)."""
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"""
            SELECT id, title, description, is_completed, priority, category, due_date, created_at 
            FROM {self.table_name}
            WHERE due_date = ?
        """
        cursor.execute(sql, (date_str,))
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task_obj = Task(id=row[0], title=row[1], description=row[2], is_completed=row[3], 
                            priority=row[4], category=row[5], due_date=row[6], created_at=row[7])
            tasks.append(task_obj)
            
        return tasks

    def update_task(self, task: Task):
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"""
            UPDATE {self.table_name}
            SET title = ?, description = ?, is_completed = ?, priority = ?, category = ?, due_date = ?
            WHERE id = ?
        """
        cursor.execute(sql, (
            task.title, task.description, task.is_completed, 
            task.priority, task.category, task.due_date, task.id
        ))
        
        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"DELETE FROM {self.table_name} WHERE id = ?"
        cursor.execute(sql, (task_id,))
        
        conn.commit()
        conn.close()