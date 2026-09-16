import calendar
from datetime import datetime
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.app import MDApp

class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.07, 0.07, 0.07, 1)
        
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        
        main_layout = MDBoxLayout(orientation="vertical", padding=40, spacing=15)
        
        top_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=10)
        
        nav_layout = MDBoxLayout(orientation="horizontal", spacing=10)
        btn_prev = MDIconButton(icon="chevron-left", on_release=self.prev_month, theme_icon_color="Custom", icon_color=(0.0, 0.9, 0.46, 1))
        nav_layout.add_widget(btn_prev)
        
        self.label_month_year = MDLabel(text="", halign="center", bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        nav_layout.add_widget(self.label_month_year)
        
        btn_next = MDIconButton(icon="chevron-right", on_release=self.next_month, theme_icon_color="Custom", icon_color=(0.0, 0.9, 0.46, 1))
        nav_layout.add_widget(btn_next)
        
        top_layout.add_widget(nav_layout)
        main_layout.add_widget(top_layout)
        
        days_header = MDGridLayout(cols=7, size_hint_y=None, height=dp(35), spacing=5)
        week_days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for d in week_days:
            days_header.add_widget(MDLabel(text=d, halign="center", bold=True, theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
        main_layout.add_widget(days_header)
        
        self.calendar_grid = MDGridLayout(cols=7, spacing=5, adaptive_height=True)
        main_layout.add_widget(self.calendar_grid)
        main_layout.add_widget(MDLabel())
        
        self.add_widget(main_layout)
        self.build_calendar()

    def build_calendar(self):
        self.calendar_grid.clear_widgets()
        month_names = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.label_month_year.text = f"{month_names[self.month]} / {self.year}"
        
        cal = calendar.monthcalendar(self.year, self.month)
        for week in cal:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(MDLabel(size_hint_y=None, height=dp(45)))
                else:
                    btn_day = MDButton(
                        MDButtonText(text=str(day)),
                        style="text", size_hint=(1, None), height=dp(45),
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
        data_formatada = f"{self.year}-{self.month:02d}-{day:02d}"
        app = MDApp.get_running_app()
        detail_screen = app.sm.get_screen("day_detail")
        detail_screen.carregar_data(data_formatada)
        app.sm.current = "day_detail"