from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.label import MDLabel
from kivy.uix.floatlayout import FloatLayout

from database.connection import create_tables
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.task_screen import TaskScreen
from ui.screens.habits_screen import HabitsScreen
from ui.screens.pomodoro_screen import PomodoroScreen
from ui.screens.home_dashboard_screen import HomeDashboardScreen
from ui.screens.week_screen import WeekScreen
from ui.screens.calendar_screen import CalendarScreen
from ui.screens.day_detail_screen import DayDetailScreen
from core.logger import get_logger

class Sidebar(MDBoxLayout):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        self.orientation = "vertical"
        self.size_hint_x = None
        self.width = dp(70)
        self.md_bg_color = (0.1, 0.1, 0.1, 1)
        
        self.add_nav("home", "home_dashboard")
        self.add_nav("view-dashboard", "dashboard")
        self.add_nav("calendar-month", "calendar_screen")
        self.add_nav("calendar-week", "week_screen")
        self.add_nav("fire", "habits_screen")
        self.add_nav("timer-outline", "pomodoro_screen")
        self.add_nav("plus-box", "task_screen")
        self.add_widget(MDLabel())

    def add_nav(self, icon, screen_name):
        btn = MDIconButton(icon=icon, theme_icon_color="Custom", icon_color=(0, 0.9, 0.46, 1))
        btn.bind(on_release=lambda x: setattr(self.sm, 'current', screen_name))
        self.add_widget(btn)

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        create_tables()
        
        root = FloatLayout()
        main_layout = MDBoxLayout(orientation="horizontal", md_bg_color=(0.07, 0.07, 0.07, 1))
        
        self.sm = MDScreenManager()
        self.sm.add_widget(HomeDashboardScreen(name="home_dashboard"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(CalendarScreen(name="calendar_screen"))
        self.sm.add_widget(DayDetailScreen(name="day_detail"))
        self.sm.add_widget(WeekScreen(name="week_screen"))
        self.sm.add_widget(TaskScreen(name="task_screen"))
        self.sm.add_widget(HabitsScreen(name="habits_screen"))
        self.sm.add_widget(PomodoroScreen(name="pomodoro_screen"))
        
        sidebar = Sidebar(self.sm)
        main_layout.add_widget(sidebar)
        main_layout.add_widget(self.sm)
        root.add_widget(main_layout)
        
        fab = MDFabButton(
            icon="plus", 
            md_bg_color=(0, 0.9, 0.46, 1), 
            pos_hint={"right": 0.95, "y": 0.05}
        )
        fab.bind(on_release=lambda x: setattr(self.sm, 'current', 'task_screen'))
        root.add_widget(fab)
        
        return root

if __name__ == "__main__":
    MainApp().run()