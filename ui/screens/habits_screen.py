from datetime import datetime, timedelta
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from database.connection import get_connection
from core.logger import get_logger

logger = get_logger("HabitsScreen")

class HabitsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hoje_str = datetime.now().strftime("%Y-%m-%d")
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        layout.add_widget(MDLabel(
            text="Rastreador de Hábitos", 
            font_style="Headline", 
            bold=True, 
            size_hint_y=None, 
            height=dp(50), 
            theme_text_color="Custom", 
            text_color=(1,1,1,1)
        ))
        
        input_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60), spacing=dp(10))
        self.habit_input = MDTextField(hint_text="Novo Hábito (Ex: Beber 2L de água)", mode="outlined")
        btn_add = MDButton(MDButtonText(text="Adicionar"), style="filled", md_bg_color=(0, 0.9, 0.46, 1), on_release=self.add_habit)
        input_box.add_widget(self.habit_input)
        input_box.add_widget(btn_add)
        layout.add_widget(input_box)
        
        scroll = MDScrollView()
        self.habits_list = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(10))
        scroll.add_widget(self.habits_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def on_enter(self):
        self.load_habits()

    def add_habit(self, *args):
        name = self.habit_input.text.strip()
        if not name:
            return
        try:
            conn = get_connection()
            conn.execute("INSERT INTO habits (name, streak, last_done) VALUES (?, 0, NULL)", (name,))
            conn.commit()
            conn.close()
            self.habit_input.text = ""
            self.load_habits()
            MDSnackbar(MDSnackbarText(text="Hábito cadastrado com sucesso!"), md_bg_color=(0, 0.7, 0.3, 1)).open()
        except Exception as e:
            logger.error(f"Erro ao salvar hábito: {e}")

    def load_habits(self):
        self.habits_list.clear_widgets()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, streak, last_done FROM habits")
            rows = cur.fetchall()
            conn.close()
            
            if not rows:
                self.habits_list.add_widget(MDLabel(
                    text="Nenhum hábito cadastrado ainda.", 
                    halign="center", 
                    theme_text_color="Custom", 
                    text_color=(0.6, 0.6, 0.6, 1),
                    size_hint_y=None,
                    height=dp(50)
                ))
                return

            for hid, name, streak, last_done in rows:
                concluido_hoje = (last_done == self.hoje_str)
                
                card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(70), padding=dp(15), spacing=dp(15), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(10)])
                
                info_box = MDBoxLayout(orientation="vertical")
                info_box.add_widget(MDLabel(text=name, bold=True, theme_text_color="Custom", text_color=(1,1,1,1)))
                info_box.add_widget(MDLabel(text=f"Sequência atual: {streak} dias", theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1) if streak > 0 else (0.6,0.6,0.6,1), role="small"))
                
                btn_action = MDButton(
                    MDButtonText(text="Feito Hoje" if not concluido_hoje else "Concluído"), 
                    style="filled", 
                    md_bg_color=(0.2, 0.2, 0.2, 1) if concluido_hoje else (0, 0.9, 0.46, 1),
                    on_release=lambda x, h_id=hid, s=streak, ld=last_done: self.check_habit(h_id, s, ld)
                )
                
                card.add_widget(info_box)
                card.add_widget(btn_action)
                self.habits_list.add_widget(card)
        except Exception as e:
            logger.error(f"Erro ao carregar hábitos: {e}")

    def check_habit(self, habit_id, current_streak, last_done):
        if last_done == self.hoje_str:
            return
            
        ontem_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        new_streak = (current_streak + 1) if (last_done == ontem_str or current_streak == 0) else 1
        
        try:
            conn = get_connection()
            conn.execute("UPDATE habits SET streak = ?, last_done = ? WHERE id = ?", (new_streak, self.hoje_str, habit_id))
            conn.commit()
            conn.close()
            self.load_habits()
            MDSnackbar(MDSnackbarText(text=f"Incrível! Sequência de {new_streak} dias!"), md_bg_color=(0, 0.9, 0.46, 1)).open()
        except Exception as e:
            logger.error(f"Erro ao atualizar hábito: {e}")