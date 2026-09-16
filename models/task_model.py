from datetime import datetime

class Task:
    # Adicionamos o due_date no construtor (padrão é None se a tarefa não tiver data)
    def __init__(self, title, description=None, is_completed=0, priority="Normal", category="Geral", due_date=None, id=None, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.is_completed = is_completed
        self.priority = priority
        self.category = category
        self.due_date = due_date  # Nova propriedade! Ex: "2026-09-16"
        self.created_at = created_at or datetime.now()

    def __repr__(self):
        status = "✅" if self.is_completed else "❌"
        data = f", Data: {self.due_date}" if self.due_date else ""
        return f"Task({self.id}, {self.title}, [{self.category}], Prioridade: {self.priority}{data}, {status})"  