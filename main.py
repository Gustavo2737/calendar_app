from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from database.connection import create_tables
from ui.screens.home_screen import HomeScreen
from ui.screens.task_screen import TaskScreen
from ui.screens.calendar_screen import CalendarScreen

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        
        # Gerenciador de telas central do app
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(TaskScreen(name="task_screen"))
        sm.add_widget(CalendarScreen(name="calendar_screen"))
        
        return sm

    def on_start(self):
        create_tables()
        print("App iniciado e banco de dados pronto!")

if __name__ == "__main__":
    MainApp().run()