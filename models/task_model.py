from datetime import datetime

class Task:
    def __init__(self, title, description=None, is_completed=0, priority="Normal", category="Geral", id=None, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.is_completed = is_completed
        self.priority = priority
        self.category = category
        self.created_at = created_at or datetime.now()

    def __repr__(self):
        status = "✅" if self.is_completed else "❌"
        return f"Task({self.id}, {self.title}, [{self.category}], Priority: {self.priority}, {status})"