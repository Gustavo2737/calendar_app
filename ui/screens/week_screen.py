from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText
from kivy.metrics import dp
from database.connection import get_connection
from core.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger("WeekScreen")

class WeekScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_day = "Segunda-feira"
        self.day_buttons = {}
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        layout.add_widget(MDLabel(text="Minha Semana (Rotinas)", font_style="Headline", bold=True, size_hint_y=None, height=dp(40), theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        
        days_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.dias_semana_map = {
            "Seg": ["Segunda", "Seg"], "Ter": ["Terça", "Ter"], "Qua": ["Quarta", "Qua"],
            "Qui": ["Quinta", "Qui"], "Sex": ["Sexta", "Sex"], "Sáb": ["Sábado", "Sáb"], "Dom": ["Domingo", "Dom"]
        }
        
        for d_short, termos in self.dias_semana_map.items():
            btn = MDButton(MDButtonText(text=d_short), style="outlined", radius=[dp(15)])
            btn.md_bg_color = (0.12, 0.12, 0.12, 1)
            btn.bind(on_release=lambda x, ds=d_short: self.filter_day(ds))
            self.day_buttons[d_short] = btn
            days_box.add_widget(btn)
            
        layout.add_widget(days_box)
        
        scroll = MDScrollView()
        self.routine_list_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12))
        scroll.add_widget(self.routine_list_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def on_enter(self, *args):
        self.filter_day("Seg")

    def get_time_left_str(self, is_routine, due_date, due_time, recurrence_data):
        try:
            if due_time is None or str(due_time).strip() == "": return ""
            t_int = int(float(str(due_time)))
            th, tm = t_int // 60, t_int % 60
        except: return ""

        now = datetime.now()
        dia_map = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sáb": 5, "dom": 6}
        if not recurrence_data: return ""
        
        today_idx = now.weekday()
        target_dts = []
        for d_name in dia_map:
            if d_name in recurrence_data.lower():
                days_ahead = dia_map[d_name] - today_idx
                if days_ahead < 0 or (days_ahead == 0 and (now.hour * 60 + now.minute) >= t_int):
                    days_ahead += 7
                target_dts.append(now.replace(hour=th, minute=tm, second=0, microsecond=0) + timedelta(days=days_ahead))
        
        if not target_dts: return ""
        target_dt = min(target_dts)

        diff = target_dt - now
        if diff.total_seconds() < 0: return "⏳ Atrasado"
        days, rem = diff.days, diff.seconds
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        
        if days > 0: return f"⏳ {days}d {hours}h {minutes}min"
        elif hours > 0: return f"⏳ {hours}h {minutes}min"
        else: return f"⏳ {minutes}min"

    def filter_day(self, day_short):
        self.selected_day = day_short
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
            
            match_rows = []
            for row in rows:
                if row[4]: 
                    if any(termo.lower() in str(row[4]).lower() for termo in termos_busca):
                        match_rows.append(row)
            
            if not match_rows:
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(80), padding=dp(20), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
                empty_card.add_widget(MDLabel(text=f"Nenhuma rotina cadastrada para {day_short}.", halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                self.routine_list_layout.add_widget(empty_card)
                return

            for row in match_rows:
                task_id, title, is_routine, due_time, recurrence_data = row
                
                time_str = "Horário livre"
                if due_time is not None and str(due_time).strip() != "":
                    try:
                        t_int = int(float(str(due_time)))
                        time_str = f"às {t_int//60:02d}:{t_int%60:02d}"
                    except Exception:
                        pass
                        
                timer_txt = self.get_time_left_str(is_routine, None, due_time, recurrence_data)

                card = MDCard(orientation="vertical", size_hint_y=None, height=dp(95), padding=dp(15), spacing=dp(5), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
                card.add_widget(MDLabel(text=title, bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1)))
                card.add_widget(MDLabel(text=f"Dias: {recurrence_data} {time_str}", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), role="small"))
                
                if timer_txt:
                    card.add_widget(MDLabel(text=timer_txt, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1), bold=True, role="small"))
                
                self.routine_list_layout.add_widget(card)
                
        except Exception as e:
            logger.error(f"Erro ao carregar rotinas da semana: {e}")