from datetime import datetime

class Task:
    def __init__(self, title, description=None, is_completed=0, priority="Normal", category="Geral", is_routine=0, due_date=None, due_time=None, recurrence=None, last_completed_date=None, id=None, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.is_completed = is_completed
        self.priority = priority
        self.category = category
        self.is_routine = is_routine
        self.due_date = due_date
        self.due_time = due_time
        self.recurrence = recurrence
        self.last_completed_date = last_completed_date
        self.created_at = created_at or datetime.now()

    def get_formatted_time(self):
        if self.due_time is not None:
            try:
                m_int = int(self.due_time)
                return f"{m_int // 60:02d}:{m_int % 60:02d}"
            except:
                return str(self.due_time)
        return "Sem horário"