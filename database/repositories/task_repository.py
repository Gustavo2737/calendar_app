from database.connection import get_connection
from models.task_model import Task
from core.logger import get_logger

logger = get_logger("TaskRepository")

class TaskRepository:
    def __init__(self):
        self.table_name = "tasks"

    def _row_to_task(self, row):
        return Task(id=row[0], title=row[1], description=row[2], is_completed=row[3], priority=row[4], category=row[5], is_routine=row[6], due_date=row[7], due_time=row[8], recurrence=row[9], last_completed_date=row[10], created_at=row[11])

    def add_task(self, task: Task):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table_name} (title, description, is_completed, priority, category, is_routine, due_date, due_time, recurrence, last_completed_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (task.title, task.description, task.is_completed, task.priority, task.category, task.is_routine, task.due_date, task.due_time, task.recurrence, task.last_completed_date, task.created_at))
            conn.commit()
            conn.close()
            logger.info(f"Tarefa salva: {task.title}")
        except Exception as e:
            logger.error(f"Erro Insert: {e}")
            raise

    def get_all_tasks(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, title, description, is_completed, priority, category, is_routine, due_date, due_time, recurrence, last_completed_date, created_at FROM {self.table_name}")
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_task(row) for row in rows]
        except Exception as e:
            logger.error(f"Erro Select All: {e}")
            return []

    def get_tasks_by_date(self, date_str: str):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE due_date = ?", (date_str,))
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_task(row) for row in rows]
        except Exception as e:
            logger.error(f"Erro Select Date: {e}")
            return []

    def update_task(self, task: Task):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {self.table_name} SET title=?, is_completed=?, is_routine=?, due_date=?, due_time=?, recurrence=?, last_completed_date=? WHERE id=?",
                (task.title, task.is_completed, task.is_routine, task.due_date, task.due_time, task.recurrence, task.last_completed_date, task.id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro Update: {e}")