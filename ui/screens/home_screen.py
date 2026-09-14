from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.app import MDApp

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.md_bg_color = MDApp.get_running_app().theme_cls.backgroundColor
        
        # Caixa centralizada para os botões do menu
        layout = MDBoxLayout(
            orientation="vertical", 
            padding=40, 
            spacing=25, 
            size_hint=(0.7, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        # Título do App
        titulo = MDLabel(
            text="Meu Calendário & Tarefas", 
            halign="center", 
            bold=True
        )
        layout.add_widget(titulo)
        
        # Botão para ir às Tarefas
        btn_tasks = MDButton(
            MDButtonText(text="Gerenciar Tarefas"),
            style="elevated",
            size_hint_x=1,
            on_release=lambda x: self.change_screen("task_screen")
        )
        layout.add_widget(btn_tasks)
        
        # Botão para ir ao Calendário
        btn_calendar = MDButton(
            MDButtonText(text="Ver Calendário"),
            style="elevated",
            size_hint_x=1,
            on_release=lambda x: self.change_screen("calendar_screen")
        )
        layout.add_widget(btn_calendar)
        
        self.add_widget(layout)

    def change_screen(self, screen_name):
        """Muda para a tela desejada através do gerenciador principal."""
        MDApp.get_running_app().root.current = screen_name