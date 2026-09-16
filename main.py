from kivy.core.window import Window
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel

from database.connection import create_tables
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.week_screen import WeekScreen
from ui.screens.task_screen import TaskScreen
from ui.screens.calendar_screen import CalendarScreen
from ui.screens.day_detail_screen import DayDetailScreen
from core.logger import get_logger

logger = get_logger("MainApp")

class Sidebar(MDBoxLayout):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        self.orientation = "vertical"
        self.size_hint_x = None
        self.width = dp(70)
        self.md_bg_color = (0.10, 0.10, 0.10, 1)
        self.padding = [dp(10), dp(20), dp(10), dp(20)]
        self.spacing = dp(20)
        
        Window.bind(mouse_pos=self.on_mouse_pos)
        
        self.btn_home = self.create_nav_item("view-dashboard", "Meu Dia", "dashboard")
        self.btn_week = self.create_nav_item("view-week", "Minha Semana", "week_screen")
        self.btn_tasks = self.create_nav_item("plus-box", "Cadastrar", "task_screen")
        self.btn_cal = self.create_nav_item("calendar-month", "Calendário", "calendar_screen")
        self.add_widget(MDLabel())
        
    def create_nav_item(self, icon, text, screen_name):
        box = MDBoxLayout(orientation="horizontal", spacing=dp(15), size_hint_y=None, height=dp(50))
        btn_icon = MDIconButton(icon=icon, on_release=lambda x: setattr(self.sm, 'current', screen_name))
        btn_icon.theme_icon_color = "Custom"
        btn_icon.icon_color = (0.0, 0.9, 0.46, 1)
        lbl_text = MDLabel(text=text, bold=True, opacity=0)
        box.add_widget(btn_icon)
        box.add_widget(lbl_text)
        self.add_widget(box)
        return lbl_text
        
    def on_mouse_pos(self, window, pos):
        if self.collide_point(*pos):
            if self.width != dp(200):
                Animation(width=dp(200), duration=0.15, t='out_quad').start(self)
                for lbl in [self.btn_home, self.btn_week, self.btn_tasks, self.btn_cal]:
                    Animation(opacity=1, duration=0.15).start(lbl)
        else:
            if self.width != dp(70):
                Animation(width=dp(70), duration=0.15, t='out_quad').start(self)
                for lbl in [self.btn_home, self.btn_week, self.btn_tasks, self.btn_cal]:
                    Animation(opacity=0, duration=0.1).start(lbl)

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        
        create_tables()
        
        root = MDBoxLayout(orientation="horizontal", md_bg_color=(0.07, 0.07, 0.07, 1))
        
        self.sm = MDScreenManager()
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(WeekScreen(name="week_screen"))
        self.sm.add_widget(TaskScreen(name="task_screen"))
        self.sm.add_widget(CalendarScreen(name="calendar_screen"))
        self.sm.add_widget(DayDetailScreen(name="day_detail")) # TELA NOVA REGISTRADA
        
        sidebar = Sidebar(self.sm)
        root.add_widget(sidebar)
        root.add_widget(self.sm)
        
        return root

if __name__ == "__main__":
    MainApp().run()