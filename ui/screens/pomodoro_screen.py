from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer
from kivy.metrics import dp
from kivy.clock import Clock
from core.logger import get_logger

logger = get_logger("PomodoroScreen")

class PomodoroScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_left = 25 * 60  # 25 minutos padrão
        self.timer_event = None
        self.is_running = False
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(30), spacing=dp(20), md_bg_color=(0.07, 0.07, 0.07, 1), pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        layout.add_widget(MDLabel(text="Pomodoro Timer", font_style="Headline", bold=True, halign="center", theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        
        # Display do Timer
        timer_card = MDCard(orientation="vertical", size_hint=(None, None), size=(dp(300), dp(180)), padding=dp(20), pos_hint={"center_x": 0.5}, md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(20)])
        self.lbl_timer = MDLabel(text="25:00", font_style="Display", bold=True, halign="center", theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1), pos_hint={"center_y": 0.5})
        timer_card.add_widget(self.lbl_timer)
        layout.add_widget(timer_card)
        
        # Botões de Controle
        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(15), pos_hint={"center_x": 0.5}, adaptive_width=True)
        
        self.btn_start = MDButton(MDButtonText(text="Iniciar"), style="filled", md_bg_color=(0, 0.9, 0.46, 1))
        self.btn_start.bind(on_release=self.toggle_timer)
        btn_box.add_widget(self.btn_start)
        
        btn_reset = MDButton(MDButtonText(text="Reiniciar"), style="outlined")
        btn_reset.bind(on_release=self.reset_timer)
        btn_box.add_widget(btn_reset)
        
        layout.add_widget(btn_box)
        self.add_widget(layout)

    def toggle_timer(self, *args):
        if not self.is_running:
            self.is_running = True
            self.btn_start.children[0].text = "Pausar"
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        else:
            self.is_running = False
            self.btn_start.children[0].text = "Iniciar"
            if self.timer_event:
                self.timer_event.cancel()

    def update_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            mins = self.time_left // 60
            secs = self.time_left % 60
            self.lbl_timer.text = f"{mins:02d}:{secs:02d}"
        else:
            self.stop_timer_and_alert()

    def stop_timer_and_alert(self):
        if self.timer_event:
            self.timer_event.cancel()
        self.is_running = False
        self.btn_start.children[0].text = "Iniciar"
        self.time_left = 25 * 60
        self.lbl_timer.text = "25:00"
        
        # Exibe o aviso na tela quando o tempo acaba
        self.show_finished_dialog()

    def show_finished_dialog(self):
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Pomodoro Finalizado! 🎉",
                halign="center"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="filled",
                    on_release=lambda x: dialog.dismiss()
                ),
                spacing="8dp"
            )
        )
        dialog.open()

    def reset_timer(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
        self.is_running = False
        self.btn_start.children[0].text = "Iniciar"
        self.time_left = 25 * 60
        self.lbl_timer.text = "25:00"