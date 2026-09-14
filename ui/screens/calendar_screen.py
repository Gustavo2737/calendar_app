import calendar
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.app import MDApp

class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.md_bg_color = MDApp.get_running_app().theme_cls.backgroundColor
        
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        
        main_layout = MDBoxLayout(orientation="vertical", padding=20, spacing=15)
        
        # --- TOPO: BOTÃO VOLTAR E TÍTULO DO MÊS ---
        top_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)
        
        btn_back = MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self.go_home()
        )
        top_layout.add_widget(btn_back)
        
        # Navegação de Meses
        nav_layout = MDBoxLayout(orientation="horizontal", spacing=10)
        btn_prev = MDIconButton(icon="chevron-left", on_release=self.prev_month)
        nav_layout.add_widget(btn_prev)
        
        self.label_month_year = MDLabel(text="", halign="center", bold=True)
        nav_layout.add_widget(self.label_month_year)
        
        btn_next = MDIconButton(icon="chevron-right", on_release=self.next_month)
        nav_layout.add_widget(btn_next)
        
        top_layout.add_widget(nav_layout)
        main_layout.add_widget(top_layout)
        
        # --- CABEÇALHO DOS DIAS DA SEMANA ---
        days_header = MDGridLayout(cols=7, size_hint_y=None, height=35, spacing=5)
        week_days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for d in week_days:
            days_header.add_widget(MDLabel(text=d, halign="center", bold=True))
        main_layout.add_widget(days_header)
        
        # --- GRADE DINÂMICA DOS DIAS (Com altura de linha fixa para alinhar perfeitamente) ---
        self.calendar_grid = MDGridLayout(
            cols=7, 
            spacing=5,
            row_default_height=45,  # Garante altura uniforme nas linhas
            row_force_default=True
        )
        main_layout.add_widget(self.calendar_grid)
        
        self.add_widget(main_layout)
        self.build_calendar()

    def build_calendar(self):
        """Calcula os dias e desenha a grade perfeitamente alinhada."""
        self.calendar_grid.clear_widgets()
        
        month_names = [
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        self.label_month_year.text = f"{month_names[self.month]} / {self.year}"
        
        cal = calendar.monthcalendar(self.year, self.month)
        
        for week in cal:
            for day in week:
                if day == 0:
                    # Espaço vazio uniforme
                    self.calendar_grid.add_widget(MDLabel(text="", size_hint_y=None, height=45))
                else:
                    btn_day = MDButton(
                        MDButtonText(text=str(day)),
                        style="outlined",
                        size_hint=(1, None),
                        height=45,
                        on_release=lambda x, d=day: self.select_day(d)
                    )
                    self.calendar_grid.add_widget(btn_day)

    def prev_month(self, instance):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.build_calendar()

    def next_month(self, instance):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.build_calendar()

    def select_day(self, day):
        print(f"Você clicou no dia: {day}/{self.month}/{self.year}")

    def go_home(self):
        MDApp.get_running_app().root.current = "home"