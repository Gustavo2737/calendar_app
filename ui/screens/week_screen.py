from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDButton, MDButtonText
from database.repositories.task_repository import TaskRepository

class WeekScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = TaskRepository()
        self.dia_atual = "Seg"
        
        main_layout = MDBoxLayout(orientation="vertical", padding=40, spacing=20)
        main_layout.md_bg_color = (0.07, 0.07, 0.07, 1)
        
        main_layout.add_widget(MDLabel(text="Visão Semanal", font_style="Headline", role="medium", bold=True, size_hint_y=None, height=dp(40), theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        
        dias_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(55), spacing=5)
        self.dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        self.botoes = {}
        
        for d in self.dias:
            btn = MDButton(MDButtonText(text=d), style="filled" if d == "Seg" else "outlined", on_release=self.selecionar_dia, radius=[dp(8)])
            btn.theme_bg_color = "Custom"
            btn.md_bg_color = (0.0, 0.9, 0.46, 1) if d == "Seg" else (0.15, 0.15, 0.15, 1)
            self.botoes[btn] = d
            dias_layout.add_widget(btn)
            
        main_layout.add_widget(dias_layout)
        
        scroll = MDScrollView()
        self.task_list = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=15)
        scroll.add_widget(self.task_list)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def on_enter(self):
        self.atualizar_indicadores()
        self.carregar_rotinas()

    def atualizar_indicadores(self):
        tarefas = self.repo.get_all_tasks()
        dias_com_tarefa = set()
        for t in tarefas:
            if t.is_routine and t.recurrence:
                for d in t.recurrence.split(","):
                    dias_com_tarefa.add(d.strip())
                    
        for btn, dia_str in self.botoes.items():
            texto = dia_str
            if dia_str in dias_com_tarefa:
                texto += " •" # Indicador visual limpo
            btn.children[0].text = texto

    def selecionar_dia(self, btn_clicado):
        self.dia_atual = self.botoes[btn_clicado]
        for btn in self.botoes.keys():
            btn.style = "outlined"
            btn.md_bg_color = (0.15, 0.15, 0.15, 1)
        btn_clicado.style = "filled"
        btn_clicado.md_bg_color = (0.0, 0.9, 0.46, 1)
        self.carregar_rotinas()

    def carregar_rotinas(self):
        self.task_list.clear_widgets()
        tarefas = self.repo.get_all_tasks() 
        encontrou = False
        
        for t in tarefas:
            if t.is_routine and t.recurrence and self.dia_atual in [d.strip() for d in t.recurrence.split(",")]:
                encontrou = True
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
                
        if not encontrou:
            self.task_list.add_widget(MDLabel(text=f"Nenhuma rotina para {self.dia_atual}.", halign="center", theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=dp(60)))

    def toggle_status(self, task, is_active):
        task.is_completed = 1 if is_active else 0
        self.repo.update_task(task)
        self.carregar_rotinas()