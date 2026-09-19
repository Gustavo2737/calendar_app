from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp, sp
from datetime import datetime, timedelta
from core.logger import get_logger
from database.connection import get_connection

logger = get_logger("WeekScreen")

# Paleta de Cores Padrão (Alto Contraste)
COLORS = {
    'BG': (0.07, 0.07, 0.07, 1),           # #121212
    'CARD': (0.12, 0.12, 0.12, 1),       # #1E1E1E
    'TEXT': (1, 1, 1, 1),                # #FFFFFF
    'LABEL': (0.69, 0.69, 0.69, 1),      # #B0B0B0
    'FOCUS': (0, 0.9, 0.46, 1),          # #00E676 (Verde Menta)
    'BTN_NORMAL': (0.12, 0.12, 0.12, 1), # Fundo escuro / preto
    'TEXT_DARK': (0, 0, 0, 1)            # Preto para fundo verde
}

class WeekScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_day = "Seg"
        self.days = [
            ("Seg", "Segunda-feira"),
            ("Ter", "Terça-feira"),
            ("Qua", "Quarta-feira"),
            ("Qui", "Quinta-feira"),
            ("Sex", "Sexta-feira"),
            ("Sáb", "Sábado"),
            ("Dom", "Domingo")
        ]
        self.day_map_full = {
            "Seg": "segunda",
            "Ter": "terça",
            "Qua": "quarta",
            "Qui": "quinta",
            "Sex": "sexta",
            "Sáb": "sábado",
            "Dom": "domingo"
        }
        self.build_ui()

    def on_enter(self, *args):
        self.load_routines()

    def build_ui(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=COLORS['BG'])
        
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        top_bar.add_widget(MDLabel(
            text="Minha Semana (Rotinas)",
            bold=True,
            font_style="Headline",
            theme_text_color="Custom",
            text_color=COLORS['TEXT']
        ))
        layout.add_widget(top_bar)
        
        days_scroll = MDScrollView(size_hint_y=None, height=dp(50), do_scroll_y=False)
        self.days_box = MDBoxLayout(orientation="horizontal", spacing=dp(10), adaptive_width=True)
        
        self.day_buttons = {}
        for short_name, full_name in self.days:
            is_selected = (short_name == self.selected_day)
            
            bg_col = COLORS['FOCUS'] if is_selected else COLORS['BTN_NORMAL']
            txt_col = COLORS['TEXT_DARK'] if is_selected else COLORS['FOCUS']
            
            btn = MDButton(
                MDButtonText(text=short_name, theme_text_color="Custom", text_color=txt_col),
                style="filled" if is_selected else "outlined",
                md_bg_color=bg_col,
                size_hint_x=None,
                width=dp(70),
                size_hint_y=None,
                height=dp(42)
            )
            btn.bind(on_release=lambda x, s=short_name: self.select_day(s))
            self.day_buttons[short_name] = btn
            self.days_box.add_widget(btn)
            
        days_scroll.add_widget(self.days_box)
        layout.add_widget(days_scroll)
        
        routines_scroll = MDScrollView()
        self.routines_list_box = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12))
        routines_scroll.add_widget(self.routines_list_box)
        layout.add_widget(routines_scroll)
        
        self.add_widget(layout)

    def select_day(self, day_short):
        self.selected_day = day_short
        logger.info(f"Dia selecionado na WeekScreen: {day_short}")
        
        for short_name, btn in self.day_buttons.items():
            is_selected = (short_name == day_short)
            if is_selected:
                btn.md_bg_color = COLORS['FOCUS']
                btn.style = "filled"
                if btn.children and hasattr(btn.children[0], 'text_color'):
                    btn.children[0].text_color = COLORS['TEXT_DARK']
            else:
                btn.md_bg_color = COLORS['BTN_NORMAL']
                btn.style = "outlined"
                if btn.children and hasattr(btn.children[0], 'text_color'):
                    btn.children[0].text_color = COLORS['FOCUS']
                    
        self.load_routines()

    def calculate_time_remaining(self, target_day_str):
        try:
            now = datetime.now()
            days_order = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
            
            target_idx = -1
            for idx, d in enumerate(days_order):
                if d in target_day_str.lower():
                    target_idx = idx
                    break
            
            if target_idx == -1:
                return "🕒 Horário regular"
                
            current_idx = now.weekday()
            days_diff = (target_idx - current_idx) % 7
            if days_diff == 0:
                days_diff = 7
                
            future_time = now + timedelta(days=days_diff)
            delta = future_time - now
            d_val = delta.days
            h_val = delta.seconds // 3600
            m_val = (delta.seconds % 3600) // 60
            
            return f"🕒 Faltam {d_val}d {h_val}h {m_val}min"
        except Exception:
            return "🕒 Calculando..."

    def load_routines(self):
        self.routines_list_box.clear_widgets()
        try:
            conn = get_connection()
            c = conn.cursor()
            
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            if not c.fetchone():
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(90), padding=dp(20), md_bg_color=COLORS['CARD'], radius=[dp(12)])
                empty_card.add_widget(MDLabel(text="Nenhuma rotina cadastrada.", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL']))
                self.routines_list_box.add_widget(empty_card)
                conn.close()
                return

            c.execute("SELECT * FROM tasks")
            col_names = [description[0] for description in c.description]
            rows = c.fetchall()
            conn.close()

            if not rows:
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(90), padding=dp(20), md_bg_color=COLORS['CARD'], radius=[dp(12)])
                empty_card.add_widget(MDLabel(text="Nenhuma rotina encontrada no banco de dados.", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL']))
                self.routines_list_box.add_widget(empty_card)
                return

            target_keyword = self.day_map_full.get(self.selected_day, "").lower()
            filtered_rows = []

            for row in rows:
                task = dict(zip(col_names, row))
                
                # Juntar o conteúdo de todas as colunas de texto para garantir que encontre o dia cadastrado onde quer que ele esteja salvo
                combined_text = " ".join([str(val) for val in task.values() if val is not None]).lower()
                
                # Verificar se o dia correspondente (ex: 'segunda') está presente no registro da tarefa
                if target_keyword in combined_text or self.selected_day.lower() in combined_text:
                    filtered_rows.append(task)

            # Fallback opcional: Se nenhuma rotina tiver o dia explícito gravado mas for rotina, exibe para não sumir
            if not filtered_rows:
                for row in rows:
                    task = dict(zip(col_names, row))
                    if task.get('is_routine') == 1 or task.get('is_routine') == '1':
                        # Se não tem dia especificado ou se o usuário quiser ver todas as rotinas em todas as abas caso não tenham filtro estrito
                        pass

            if not filtered_rows:
                full_name_display = self.days[[d[0] for d in self.days].index(self.selected_day)][1]
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(90), padding=dp(20), md_bg_color=COLORS['CARD'], radius=[dp(12)])
                empty_card.add_widget(MDLabel(text=f"Nenhuma rotina encontrada para {full_name_display}.", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL']))
                self.routines_list_box.add_widget(empty_card)
                return

            for task in filtered_rows:
                title = task.get('title', task.get('name', 'Sem título'))
                desc = task.get('description', '')
                time_info = task.get('time_info', task.get('days', task.get('day_of_week', task.get('date', ''))))
                
                full_name_display = self.days[[d[0] for d in self.days].index(self.selected_day)][1]
                display_schedule = f"Dia: {full_name_display}" + (f" | Horário: {time_info}" if time_info else "")
                time_remaining = self.calculate_time_remaining(full_name_display)

                card = MDCard(orientation="vertical", size_hint_y=None, height=dp(115), padding=dp(15), spacing=dp(5), md_bg_color=COLORS['CARD'], radius=[dp(12)])
                
                card.add_widget(MDLabel(text=title, bold=True, theme_text_color="Custom", text_color=COLORS['TEXT']))
                card.add_widget(MDLabel(text=display_schedule, theme_text_color="Custom", text_color=COLORS['LABEL'], role="small"))
                card.add_widget(MDLabel(text=time_remaining, theme_text_color="Custom", text_color=COLORS['FOCUS'], role="small", bold=True))
                
                self.routines_list_box.add_widget(card)
                
        except Exception as e:
            logger.error(f"Erro ao carregar rotinas na WeekScreen: {e}")