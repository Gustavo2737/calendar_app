from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.app import MDApp

class HomeDashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        root.add_widget(MDLabel(
            text="Painel Geral (Dashboard)", 
            font_style="Headline", 
            bold=True, 
            size_hint_y=None, 
            height=dp(40), 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1)
        ))
        
        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(15))
        
        content.add_widget(self.create_menu_card("Tarefas de Hoje & Progresso", "Gerencie suas atividades diárias e acompanhe seu progresso", "dashboard"))
        content.add_widget(self.create_menu_card("Minha Semana & Calendário", "Visualize sua agenda e compromissos dos próximos dias", "week_screen"))
        content.add_widget(self.create_menu_card("Rastreador de Hábitos", "Acompanhe sequências diárias e mantenha seus hábitos", "habits_screen"))
        content.add_widget(self.create_menu_card("Pomodoro / Foco", "Timer de alta produtividade para estudos e trabalho", "pomodoro_screen"))
        content.add_widget(self.create_menu_card("Novo Registro (Atividade / Rotina)", "Cadastre novos eventos ou rotinas semanais", "task_screen"))
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def create_menu_card(self, title, subtitle, target_screen):
        card = MDCard(
            orientation="vertical", 
            size_hint_y=None, 
            height=dp(90), 
            padding=dp(15), 
            spacing=dp(5), 
            md_bg_color=(0.12, 0.12, 0.12, 1), 
            radius=[dp(12)]
        )
        card.bind(on_release=lambda x: setattr(MDApp.get_running_app().sm, 'current', target_screen))
        
        card.add_widget(MDLabel(text=title, bold=True, font_style="Title", role="medium", theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)))
        card.add_widget(MDLabel(text=subtitle, theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), role="small"))
        return card