from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.app import MDApp

from database.repositories.task_repository import TaskRepository
from models.task_model import Task 
from core.logger import get_logger

logger = get_logger("TaskScreen")

class TaskScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = TaskRepository() 
        self.dias_selecionados = []
        self.raw_minutes = None
        self.is_routine_mode = False 
        self.temp_hour = None
        self.time_popup = None

        main_layout = MDBoxLayout(orientation="vertical", padding=40, spacing=25)
        main_layout.md_bg_color = (0.07, 0.07, 0.07, 1) # #121212
        
        main_layout.add_widget(MDLabel(text="Cadastrar Nova Atividade", font_style="Headline", role="small", bold=True, size_hint_y=None, height=dp(40), theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        
        self.text_field = MDTextField(MDTextFieldHintText(text="O que você precisa fazer? *"), mode="outlined")
        main_layout.add_widget(self.text_field)
        
        # TOGGLE VISUALMENTE DESTACADO
        toggle_card = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=15, padding=[15, 5, 15, 5], md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
        self.lbl_mode = MDLabel(text="MODO: Evento Único", bold=True, theme_text_color="Custom", text_color=(0.0, 0.9, 0.46, 1))
        self.switch_mode = MDSwitch(active=False)
        self.switch_mode.bind(active=self.on_switch_mode)
        toggle_card.add_widget(self.lbl_mode)
        toggle_card.add_widget(self.switch_mode)
        main_layout.add_widget(toggle_card)
        
        self.dynamic_container = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=15)
        
        # CONTAINER: EVENTO ÚNICO
        self.event_box = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=15)
        self.date_field = MDTextField(MDTextFieldHintText(text="Data Específica (Selecione no ícone)"), mode="outlined", readonly=True, size_hint_x=0.8)
        btn_date = MDIconButton(icon="calendar", on_release=self.open_date_picker, theme_icon_color="Custom", icon_color=(0.0, 0.9, 0.46, 1))
        self.event_box.add_widget(self.date_field)
        self.event_box.add_widget(btn_date)
        
        # CONTAINER: ROTINA SEMANAL
        self.routine_box = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=10)
        self.routine_box.add_widget(MDLabel(text="Dias da Repetição Semanal:", size_hint_y=None, height=dp(20), theme_text_color="Custom", text_color=(0.8, 0.8, 0.8, 1)))
        row_dias = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=5)
        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        self.botoes_dias = {}
        for d in dias:
            btn = MDButton(MDButtonText(text=d), style="outlined", on_release=self.toggle_dia, radius=[dp(8)])
            self.botoes_dias[btn] = d
            row_dias.add_widget(btn)
        self.routine_box.add_widget(row_dias)
        
        # CONTAINER: HORÁRIO (Comum a ambos)
        self.time_box = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=15)
        self.time_field = MDTextField(MDTextFieldHintText(text="Horário (Opcional)"), mode="outlined", readonly=True, size_hint_x=0.8)
        btn_time = MDIconButton(icon="clock-outline", on_release=self.open_time_picker_hours, theme_icon_color="Custom", icon_color=(0.0, 0.9, 0.46, 1))
        self.time_box.add_widget(self.time_field)
        self.time_box.add_widget(btn_time)
        
        self.dynamic_container.add_widget(self.event_box)
        self.dynamic_container.add_widget(self.time_box)
        main_layout.add_widget(self.dynamic_container)
        
        self.lbl_feedback = MDLabel(text="", theme_text_color="Error", size_hint_y=None, height=dp(20))
        main_layout.add_widget(self.lbl_feedback)
        
        # BOTÃO SALVAR COM DESTAQUE
        btn_salvar = MDButton(MDButtonText(text="SALVAR ATIVIDADE", bold=True), style="filled", on_release=self.add_new_task, size_hint_x=1, size_hint_y=None, height=dp(55), radius=[dp(12)])
        btn_salvar.theme_bg_color = "Custom"
        btn_salvar.md_bg_color = (0.0, 0.8, 0.4, 1)
        
        main_layout.add_widget(MDLabel()) 
        main_layout.add_widget(btn_salvar)
        self.add_widget(main_layout)

    def on_switch_mode(self, instance, active):
        self.is_routine_mode = active
        self.dynamic_container.clear_widgets()
        if active:
            self.lbl_mode.text = "MODO: Rotina Semanal"
            self.dynamic_container.add_widget(self.routine_box)
        else:
            self.lbl_mode.text = "MODO: Evento Único"
            self.dynamic_container.add_widget(self.event_box)
        self.dynamic_container.add_widget(self.time_box)

    def toggle_dia(self, instance):
        dia = self.botoes_dias[instance]
        if dia in self.dias_selecionados:
            self.dias_selecionados.remove(dia)
            instance.style = "outlined"
            instance.md_bg_color = (0.15, 0.15, 0.15, 1)
        else:
            self.dias_selecionados.append(dia)
            instance.style = "filled"
            instance.md_bg_color = (0.0, 0.9, 0.46, 1)

    def open_date_picker(self, *args):
        try:
            dialog = MDModalDatePicker()
            dialog.bind(on_ok=lambda inst: self.set_date_field(inst))
            dialog.open()
        except Exception as e:
            logger.error(f"Erro DatePicker: {e}")

    def set_date_field(self, instance_dialog):
        self.date_field.text = instance_dialog.get_date()[0].strftime("%Y-%m-%d")
        instance_dialog.dismiss()

    def open_time_picker_hours(self, *args):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(text="Selecione a Hora", size_hint_y=None, height=dp(30), bold=True))
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        self.time_popup = Popup(title="", separator_height=0, content=layout, size_hint=(0.85, 0.75), background_color=(0.12, 0.12, 0.12, 1))
        for h in range(24): # 00:00 a 23:00
            btn = Button(text=f"{h:02d}", size_hint_y=None, height=dp(50), background_color=(0, 0.7, 0.4, 1))
            btn.bind(on_release=lambda x, hs=h: self.select_hour_and_proceed(hs))
            grid.add_widget(btn)
            
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        btn_cancel = Button(text="Limpar / Cancelar", size_hint_y=None, height=dp(45), background_color=(0.3, 0.3, 0.3, 1))
        btn_cancel.bind(on_release=self.clear_time)
        layout.add_widget(btn_cancel)
        self.time_popup.open()

    def clear_time(self, *args):
        self.time_field.text = ""
        self.raw_minutes = None
        self.time_popup.dismiss()

    def select_hour_and_proceed(self, hour_int):
        self.temp_hour = hour_int
        self.time_popup.dismiss()
        self.open_time_picker_minutes()

    def open_time_picker_minutes(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(text=f"Hora: {self.temp_hour:02d} - Minutos", size_hint_y=None, height=dp(30), bold=True))
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        self.time_popup = Popup(title="", separator_height=0, content=layout, size_hint=(0.85, 0.75), background_color=(0.12, 0.12, 0.12, 1))
        for m in range(0, 60, 5): # De 5 em 5 minutos
            btn = Button(text=f"{m:02d}", size_hint_y=None, height=dp(50), background_color=(0, 0.7, 0.4, 1))
            btn.bind(on_release=lambda x, mi=m: self.finalize_time(mi))
            grid.add_widget(btn)
            
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        btn_cancel = Button(text="Voltar", size_hint_y=None, height=dp(45), background_color=(0.3, 0.3, 0.3, 1))
        btn_cancel.bind(on_release=self.time_popup.dismiss)
        layout.add_widget(btn_cancel)
        self.time_popup.open()

    def finalize_time(self, minute_int):
        self.time_field.text = f"{self.temp_hour:02d}:{minute_int:02d}"
        self.raw_minutes = (self.temp_hour * 60) + minute_int
        self.time_popup.dismiss()

    def add_new_task(self, instance):
        titulo = self.text_field.text.strip()
        if not titulo:
            self.lbl_feedback.text = "Atenção: O título não pode estar vazio!"
            return
        
        self.lbl_feedback.text = ""
        is_routine = 1 if self.is_routine_mode else 0
        data = None
        rotina = None
        
        if self.is_routine_mode:
            if not self.dias_selecionados:
                self.lbl_feedback.text = "Selecione ao menos um dia para a rotina."
                return
            rotina = ", ".join(self.dias_selecionados)
        else:
            data = self.date_field.text.strip()
            if not data:
                self.lbl_feedback.text = "Selecione uma data para o evento."
                return

        try:
            self.repo.add_task(Task(title=titulo, is_routine=is_routine, due_date=data, due_time=self.raw_minutes, recurrence=rotina))
            # Reset UI
            self.text_field.text = ""
            self.date_field.text = ""
            self.time_field.text = ""
            self.raw_minutes = None
            self.dias_selecionados.clear()
            for b in self.botoes_dias.keys():
                b.style = "outlined"
                b.md_bg_color = (0.15, 0.15, 0.15, 1)
            MDApp.get_running_app().sm.current = "dashboard"
        except Exception as e:
            logger.error(f"Erro Salvar: {e}")