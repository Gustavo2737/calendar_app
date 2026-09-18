from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.app import MDApp
from database.connection import get_connection

class DayDetailScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        self.title_lbl = MDLabel(text="Detalhes do Dia", font_style="Headline", bold=True, size_hint_y=None, height=dp(40), theme_text_color="Custom", text_color=(1,1,1,1))
        layout.add_widget(self.title_lbl)
        
        btn_voltar = MDButton(MDButtonText(text="Voltar ao Calendário"), style="outlined", on_release=lambda x: setattr(MDApp.get_running_app().sm, 'current', 'calendar_screen'))
        layout.add_widget(btn_voltar)
        
        scroll = MDScrollView()
        self.task_list = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(10))
        scroll.add_widget(self.task_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def carregar_data(self, data_str):
        self.title_lbl.text = f"Atividades em {data_str}"
        self.task_list.clear_widgets()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT title, due_time FROM tasks WHERE due_date = ?", (data_str,))
            rows = cur.fetchall()
            conn.close()
            
            if not rows:
                self.task_list.add_widget(MDLabel(text="Nenhuma atividade neste dia.", theme_text_color="Custom", text_color=(0.6,0.6,0.6,1)))
                return
                
            for title, due_time in rows:
                t_str = f"{due_time//60:02d}:{due_time%60:02d}" if due_time is not None else "Dia Inteiro"
                card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(60), padding=dp(10), md_bg_color=(0.12,0.12,0.12,1), radius=[dp(8)])
                card.add_widget(MDLabel(text=f"{title} ({t_str})", theme_text_color="Custom", text_color=(1,1,1,1)))
                self.task_list.add_widget(card)
        except Exception as e:
            pass