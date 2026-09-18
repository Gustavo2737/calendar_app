from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText
from kivy.metrics import dp
from database.connection import get_connection
from core.logger import get_logger

logger = get_logger("WeekScreen")

class WeekScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_day = "Segunda-feira"  # Padrão inicial
        self.day_buttons = {}
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        layout.add_widget(MDLabel(
            text="Minha Semana (Rotinas)", 
            font_style="Headline", 
            bold=True, 
            size_hint_y=None, 
            height=dp(40), 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1)
        ))
        
        # Barra de dias da semana
        days_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Mapeamento do botão curto para o nome completo ou abreviação salva
        self.dias_semana_map = {
            "Seg": ["Segunda", "Seg"],
            "Ter": ["Terça", "Ter"],
            "Qua": ["Quarta", "Qua"],
            "Qui": ["Quinta", "Qui"],
            "Sex": ["Sexta", "Sex"],
            "Sáb": ["Sábado", "Sáb"],
            "Dom": ["Domingo", "Dom"]
        }
        
        for d_short, termos in self.dias_semana_map.items():
            btn = MDButton(MDButtonText(text=d_short), style="outlined", radius=[dp(15)])
            btn.md_bg_color = (0.12, 0.12, 0.12, 1)
            btn.bind(on_release=lambda x, ds=d_short: self.filter_day(ds))
            self.day_buttons[d_short] = btn
            days_box.add_widget(btn)
            
        layout.add_widget(days_box)
        
        # Scroll para listar as rotinas do dia selecionado
        scroll = MDScrollView()
        self.routine_list_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12))
        scroll.add_widget(self.routine_list_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def on_enter(self, *args):
        self.filter_day("Seg")  # Exibe Segunda por padrão ao entrar

    def filter_day(self, day_short):
        self.selected_day = day_short
        
        # Atualiza a estética dos botões da semana
        for d, btn in self.day_buttons.items():
            if d == day_short:
                btn.style = "filled"
                btn.md_bg_color = (0, 0.9, 0.46, 1)
            else:
                btn.style = "outlined"
                btn.md_bg_color = (0.12, 0.12, 0.12, 1)
                
        self.load_routines_for_day(day_short)

    def load_routines_for_day(self, day_short):
        self.routine_list_layout.clear_widgets()
        termos_busca = self.dias_semana_map.get(day_short, [day_short])
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, is_routine, due_time, recurrence_data FROM tasks WHERE is_routine = 1")
            rows = cursor.fetchall()
            conn.close()
            
            # Filtra de forma flexível (verificando se algum termo de busca está presente na string de recorrência)
            match_rows = []
            for row in rows:
                task_id, title, is_routine, due_time, recurrence_data = row
                if recurrence_data:
                    rec_str = str(recurrence_data)
                    if any(termo.lower() in rec_str.lower() for termo in termos_busca):
                        match_rows.append(row)
            
            if not match_rows:
                empty_card = MDCard(
                    orientation="vertical", 
                    size_hint_y=None, 
                    height=dp(80), 
                    padding=dp(20), 
                    md_bg_color=(0.12, 0.12, 0.12, 1), 
                    radius=[dp(12)]
                )
                empty_card.add_widget(MDLabel(
                    text=f"Nenhuma rotina cadastrada para {day_short}.", 
                    halign="center", 
                    theme_text_color="Custom", 
                    text_color=(0.7, 0.7, 0.7, 1)
                ))
                self.routine_list_layout.add_widget(empty_card)
                return

            for row in match_rows:
                task_id, title, is_routine, due_time, recurrence_data = row
                
                card = MDCard(
                    orientation="vertical", 
                    size_hint_y=None, 
                    height=dp(65), 
                    padding=dp(15), 
                    spacing=dp(5), 
                    md_bg_color=(0.12, 0.12, 0.12, 1), 
                    radius=[dp(12)]
                )
                card.add_widget(MDLabel(
                    text=title, 
                    bold=True, 
                    theme_text_color="Custom", 
                    text_color=(1, 1, 1, 1)
                ))
                
                time_str = "Horário livre"
                if due_time is not None and str(due_time).strip() != "":
                    try:
                        t_int = int(float(str(due_time)))
                        time_str = f"Horário: {t_int//60:02d}:{t_int%60:02d}"
                    except Exception:
                        pass
                        
                card.add_widget(MDLabel(
                    text=f"Dias: {recurrence_data} | {time_str}", 
                    theme_text_color="Custom", 
                    text_color=(0.7, 0.7, 0.7, 1), 
                    role="small"
                ))
                
                self.routine_list_layout.add_widget(card)
                
        except Exception as e:
            logger.error(f"Erro ao carregar rotinas da semana: {e}")