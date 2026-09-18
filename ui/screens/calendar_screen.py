from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivy.metrics import dp
from database.connection import get_connection
from core.logger import get_logger
import calendar
from datetime import datetime

logger = get_logger("CalendarScreen")

class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.selected_date = now.strftime('%Y-%m-%d')
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        # Container centralizado com tupla de tamanho correta (largura, altura)
        cal_container = MDBoxLayout(
            orientation="vertical", 
            size_hint=(None, None), 
            size=(dp(420), dp(350)), 
            pos_hint={"center_x": 0.5},
            spacing=dp(10)
        )
        
        # Cabeçalho do Mês
        header_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_prev = MDIconButton(icon="chevron-left", theme_icon_color="Custom", icon_color=(0, 0.9, 0.46, 1))
        btn_prev.bind(on_release=lambda x: self.change_month(-1))
        header_box.add_widget(btn_prev)
        
        self.lbl_month_year = MDLabel(text="", halign="center", bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        header_box.add_widget(self.lbl_month_year)
        
        btn_next = MDIconButton(icon="chevron-right", theme_icon_color="Custom", icon_color=(0, 0.9, 0.46, 1))
        btn_next.bind(on_release=lambda x: self.change_month(1))
        header_box.add_widget(btn_next)
        
        cal_container.add_widget(header_box)
        
        # Dias da semana cabeçalho
        days_header = MDGridLayout(cols=7, size_hint_y=None, height=dp(30), spacing=dp(4))
        for d_name in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]:
            days_header.add_widget(MDLabel(text=d_name, halign="center", bold=True, theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), role="small"))
        cal_container.add_widget(days_header)
        
        # Grade do Calendário
        self.calendar_grid = MDGridLayout(cols=7, size_hint=(None, None), size=(dp(420), dp(240)), spacing=dp(6))
        cal_container.add_widget(self.calendar_grid)
        
        layout.add_widget(cal_container)
        
        # Seção de Atividades do Dia Selecionado
        layout.add_widget(MDLabel(text="Atividades do Dia Selecionado", bold=True, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1), size_hint_y=None, height=dp(30)))
        
        scroll = MDScrollView()
        self.tasks_list_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(10))
        scroll.add_widget(self.tasks_list_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.build_calendar()

    def on_enter(self, *args):
        self.build_calendar()
        self.load_tasks_for_selected_date()

    def build_calendar(self):
        self.calendar_grid.clear_widgets()
        month_names = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_month_year.text = f"{month_names[self.month]} {self.year}"
        
        cal = calendar.monthcalendar(self.year, self.month)
        for week in cal:
            for day in week:
                if day == 0:
                    empty_cell = MDBoxLayout(size_hint=(None, None), size=(dp(54), dp(36)))
                    self.calendar_grid.add_widget(empty_cell)
                else:
                    date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                    is_selected = (date_str == self.selected_date)
                    
                    btn = MDButton(
                        MDButtonText(text=str(day)), 
                        style="filled" if is_selected else "text", 
                        size_hint=(None, None), 
                        size=(dp(54), dp(36))
                    )
                    btn.pos_hint = {"center_x": 0.5, "center_y": 0.5}
                    btn.md_bg_color = (0, 0.9, 0.46, 1) if is_selected else (0.17, 0.17, 0.17, 1)
                    btn.bind(on_release=lambda x, ds=date_str: self.select_date(ds))
                    self.calendar_grid.add_widget(btn)

    def change_month(self, delta):
        self.month += delta
        if self.month > 12:
            self.month = 1
            self.year += 1
        elif self.month < 1:
            self.month = 12
            self.year -= 1
        self.build_calendar()

    def select_date(self, date_str):
        self.selected_date = date_str
        self.build_calendar()
        self.load_tasks_for_selected_date()

    def load_tasks_for_selected_date(self):
        self.tasks_list_layout.clear_widgets()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, due_time, is_routine FROM tasks WHERE is_routine = 0 AND due_date = ?", (self.selected_date,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                card = MDCard(orientation="vertical", size_hint_y=None, height=dp(60), padding=dp(15), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(10)])
                card.add_widget(MDLabel(text="Nenhuma atividade para esta data.", halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                self.tasks_list_layout.add_widget(card)
                return
                
            for row in rows:
                task_id, title, due_time, is_routine = row
                
                time_str = "Dia Inteiro"
                if due_time is not None and str(due_time).strip() != "":
                    try:
                        t_int = int(float(str(due_time)))
                        time_str = f"{t_int//60:02d}:{t_int%60:02d}"
                    except Exception:
                        time_str = str(due_time)
                
                card = MDCard(orientation="vertical", size_hint_y=None, height=dp(65), padding=dp(15), spacing=dp(5), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(10)])
                card.add_widget(MDLabel(text=title, bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1)))
                card.add_widget(MDLabel(text=f"Horário: {time_str}", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), role="small"))
                
                self.tasks_list_layout.add_widget(card)
        except Exception as e:
            logger.error(f"Erro ao carregar tarefas do calendário: {e}")