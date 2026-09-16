from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
from database.repositories.task_repository import TaskRepository

class DayDetailScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = TaskRepository()
        self.data_alvo = ""

        self.main_layout = MDBoxLayout(orientation="vertical", padding=40, spacing=20)
        self.main_layout.md_bg_color = (0.07, 0.07, 0.07, 1)
        
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=10)
        btn_back = MDIconButton(icon="arrow-left", on_release=lambda x: setattr(MDApp.get_running_app().sm, 'current', 'calendar_screen'), theme_icon_color="Custom", icon_color=(0.0, 0.9, 0.46, 1))
        self.titulo = MDLabel(text="Detalhes", font_style="Headline", role="small", bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.titulo)
        self.main_layout.add_widget(top_bar)
        
        scroll = MDScrollView()
        self.task_list = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=15)
        scroll.add_widget(self.task_list)
        self.main_layout.add_widget(scroll)
        self.add_widget(self.main_layout)

    def carregar_data(self, data_str):
        self.data_alvo = data_str
        self.titulo.text = f"Agenda: {data_str}"
        self.atualizar_lista()

    def atualizar_lista(self):
        self.task_list.clear_widgets()
        tarefas = self.repo.get_tasks_by_date(self.data_alvo)
        
        if not tarefas:
            self.task_list.add_widget(MDLabel(text="Nenhum evento único para esta data.", halign="center", theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=dp(60)))
            return
            
        for t in tarefas:
            card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(80), padding=15, spacing=15, style="elevated", md_bg_color=(0.11, 0.11, 0.11, 1), radius=[dp(12)])
            chk = MDCheckbox(active=bool(t.is_completed), size_hint=(None, None), size=(dp(48), dp(48)))
            chk.bind(active=lambda inst, val, task=t: self.toggle_status(task, val))
            
            textos = MDBoxLayout(orientation="vertical")
            display = f"[s]{t.title}[/s]" if t.is_completed else t.title
            textos.add_widget(MDLabel(text=display, bold=True, markup=True, theme_text_color="Custom", text_color=(1, 1, 1, 1) if not t.is_completed else (0.5, 0.5, 0.5, 1)))
            textos.add_widget(MDLabel(text=f"Horário: {t.get_formatted_time()}", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), role="small"))
            
            card.add_widget(chk)
            card.add_widget(textos)
            self.task_list.add_widget(card)

    def toggle_status(self, task, is_active):
        task.is_completed = 1 if is_active else 0
        self.repo.update_task(task)
        self.atualizar_lista()