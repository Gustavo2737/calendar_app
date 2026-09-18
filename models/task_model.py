from datetime import datetime

class Task:
    def __init__(self, title, is_completed=0, is_routine=0, due_date=None, due_time=None, recurrence_type=None, recurrence_data=None, last_completed_date=None, id=None):
        self.id = id
        self.title = title
        self.is_completed = is_completed
        self.is_routine = is_routine
        self.due_date = due_date
        self.due_time = due_time # Minutos
        self.recurrence_type = recurrence_type # 'weekly', 'monthly'
        self.recurrence_data = recurrence_data # 'Seg, Qua', '15'
        self.last_completed_date = last_completed_date

    def get_formatted_time(self):
        if self.due_time is not None:
            return f"{self.due_time // 60:02d}:{self.due_time % 60:02d}"
        return "Dia Inteiro"  