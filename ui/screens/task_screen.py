import calendar
from datetime import datetime, timedelta
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.app import MDApp
from database.connection import get_connection
from core.logger import get_logger

logger = get_logger("TaskScreen")

class TaskScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_routine_days = set()
        self.day_buttons = {}
        
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.selected_date = now.strftime('%Y-%m-%d')
        
        self.selected_hour = now.hour
        self.selected_minute = (now.minute // 5) * 5
        
        root_layout = MDBoxLayout(orientation="vertical", padding=dp(30), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        root_layout.add_widget(MDLabel(
            text="Cadastro de Nova Atividade / Rotina", 
            font_style="Headline", 
            bold=True, 
            size_hint_y=None, 
            height=dp(40), 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1)
        ))
        
        scroll = MDScrollView()
        
        self.form_layout = MDBoxLayout(
            orientation="vertical", 
            adaptive_height=True, 
            spacing=dp(18),
            size_hint_x=None,
            width=dp(600),
            pos_hint={"center_x": 0.5}
        )
        
        # Seção 1: Informações Principais
        sec1 = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(20), spacing=dp(12), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(14)])
        sec1.add_widget(MDLabel(text="Título da Atividade", bold=True, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)))
        
        self.title_input = MDTextField(hint_text="Ex: Estudar Matemática, Ir à academia...", mode="outlined")
        sec1.add_widget(self.title_input)
        self.form_layout.add_widget(sec1)
        
        # Seção 2: Tipo de Compromisso (Interruptor)
        sec2 = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(20), spacing=dp(12), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(14)])
        sec2.add_widget(MDLabel(text="Tipo de Compromisso", bold=True, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)))
        
        switch_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(15))
        self.routine_switch = MDSwitch()
        self.routine_switch.bind(active=self.on_routine_switch_active)
        switch_box.add_widget(self.routine_switch)
        switch_box.add_widget(MDLabel(text="Ativar Rotina Semanal Recorrente", theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        sec2.add_widget(switch_box)
        self.form_layout.add_widget(sec2)
        
        # Seção 3: Calendário Visual Integrado
        self.sec_date = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(20), spacing=dp(12), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(14)])
        
        date_header_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(35))
        date_header_box.add_widget(MDLabel(text="Data do Compromisso", bold=True, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)))
        self.lbl_current_date_selection = MDLabel(text=f"Selecionado: {self.selected_date}", halign="right", theme_text_color="Custom", text_color=(0.8, 0.8, 0.8, 1), role="small")
        date_header_box.add_widget(self.lbl_current_date_selection)
        self.sec_date.add_widget(date_header_box)
        
        nav_month_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_prev_m = MDIconButton(icon="chevron-left", theme_icon_color="Custom", icon_color=(0, 0.9, 0.46, 1))
        btn_prev_m.bind(on_release=lambda x: self.change_month(-1))
        nav_month_box.add_widget(btn_prev_m)
        
        self.lbl_month_year = MDLabel(text="", halign="center", bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        nav_month_box.add_widget(self.lbl_month_year)
        
        btn_next_m = MDIconButton(icon="chevron-right", theme_icon_color="Custom", icon_color=(0, 0.9, 0.46, 1))
        btn_next_m.bind(on_release=lambda x: self.change_month(1))
        nav_month_box.add_widget(btn_next_m)
        self.sec_date.add_widget(nav_month_box)
        
        days_header_grid = MDGridLayout(cols=7, size_hint_y=None, height=dp(30), spacing=dp(4))
        for d_name in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]:
            days_header_grid.add_widget(MDLabel(text=d_name, halign="center", bold=True, theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), role="small"))
        self.sec_date.add_widget(days_header_grid)
        
        self.calendar_grid = MDGridLayout(cols=7, adaptive_height=True, spacing=dp(6))
        self.sec_date.add_widget(self.calendar_grid)
        
        self.form_layout.add_widget(self.sec_date)
        self.build_mini_calendar()
        
        # Seção 4: Horário
        sec4 = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(20), spacing=dp(12), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(14)])
        sec4.add_widget(MDLabel(text="Horário do Compromisso", bold=True, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)))
        
        time_display_box = MDCard(orientation="horizontal", size_hint_y=None, height=dp(55), padding=dp(15), spacing=dp(15), md_bg_color=(0.17, 0.17, 0.17, 1), radius=[dp(10)])
        time_display_box.bind(on_release=self.open_time_picker_popup)
        time_display_box.add_widget(MDIconButton(icon="clock-outline", theme_icon_color="Custom", icon_color=(0, 0.9, 0.46, 1)))
        self.lbl_time_display = MDLabel(text=f"Horário selecionado: {self.selected_hour:02d}:{self.selected_minute:02d}", bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        time_display_box.add_widget(self.lbl_time_display)
        sec4.add_widget(time_display_box)
        self.form_layout.add_widget(sec4)
        
        # Seção 5: Seleção de Dias da Semana (Rotina) - Alto Contraste Aplicado
        self.sec_days = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(20), spacing=dp(12), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(14)])
        self.sec_days.add_widget(MDLabel(text="Dias da Semana da Rotina (Clique para Selecionar)", bold=True, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)))
        
        days_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(8))
        self.dias_mapeamento = {"Dom": "Domingo", "Seg": "Segunda-feira", "Ter": "Terça-feira", "Qua": "Quarta-feira", "Qui": "Quinta-feira", "Sex": "Sexta-feira", "Sáb": "Sábado"}
        
        for d_key in ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]:
            # Estado inicial inativo: outlined, fundo preto/escuro, texto verde menta
            btn = MDButton(
                MDButtonText(text=d_key, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1)), 
                style="outlined", 
                radius=[dp(15)]
            )
            btn.md_bg_color = (0.12, 0.12, 0.12, 1)
            btn.bind(on_release=lambda x, dk=d_key: self.toggle_day(dk))
            self.day_buttons[d_key] = btn
            days_box.add_widget(btn)
            
        self.sec_days.add_widget(days_box)
        
        # Botão Salvar (Com texto preto e fundo verde conforme padrão de alto contraste)
        btn_save = MDButton(
            MDButtonText(text="Salvar Atividade", theme_text_color="Custom", text_color=(0, 0, 0, 1)), 
            style="filled", 
            md_bg_color=(0, 0.9, 0.46, 1), 
            size_hint_y=None, 
            height=dp(50)
        )
        btn_save.bind(on_release=self.save_task)
        self.form_layout.add_widget(btn_save)
        
        scroll.add_widget(self.form_layout)
        root_layout.add_widget(scroll)
        self.add_widget(root_layout)

    def build_mini_calendar(self):
        self.calendar_grid.clear_widgets()
        month_names = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_month_year.text = f"{month_names[self.month]} {self.year}"
        
        cal = calendar.monthcalendar(self.year, self.month)
        for week in cal:
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(MDLabel(size_hint_y=None, height=dp(40)))
                else:
                    date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                    is_selected = (date_str == self.selected_date)
                    
                    btn = MDButton(
                        MDButtonText(text=str(day)), 
                        style="filled" if is_selected else "text", 
                        size_hint=(None, None), 
                        size=(dp(45), dp(40))
                    )
                    btn.pos_hint = {"center_x": 0.5}
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
        self.build_mini_calendar()

    def select_date(self, date_str):
        self.selected_date = date_str
        self.lbl_current_date_selection.text = f"Selecionado: {date_str}"
        self.build_mini_calendar()

    def open_time_picker_popup(self, *args):
        content = MDBoxLayout(orientation="vertical", padding=dp(25), spacing=dp(20), md_bg_color=(0.1, 0.1, 0.1, 1), size_hint_y=None, adaptive_height=True, size_hint_x=None, width=dp(380), pos_hint={"center_x": 0.5})
        content.add_widget(MDLabel(text="Selecionar Horário Preciso", bold=True, halign="center", theme_text_color="Custom", text_color=(1,1,1,1), size_hint_y=None, height=dp(30)))
        
        popup = Popup(title="Horário", size_hint=(None, None), size=(dp(420), dp(320)), content=content)
        
        self.time_preview_lbl = MDLabel(text=f"{self.selected_hour:02d}:{self.selected_minute:02d}", font_style="Headline", bold=True, halign="center", theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1), size_hint_y=None, height=dp(50))
        content.add_widget(self.time_preview_lbl)
        
        controls_box = MDBoxLayout(orientation="horizontal", spacing=dp(20), size_hint_y=None, height=dp(70), pos_hint={"center_x": 0.5})
        
        h_box = MDBoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None, height=dp(70))
        h_box.add_widget(MDLabel(text="Hora", halign="center", theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), role="small", size_hint_y=None, height=dp(20)))
        h_ctrl = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(45))
        
        btn_h_sub = MDButton(MDButtonText(text="-"), style="outlined", size_hint=(None, None), size=(dp(45), dp(45)))
        btn_h_sub.bind(on_release=lambda x: self.adjust_hour(-1))
        
        self.lbl_h_val = MDLabel(text=f"{self.selected_hour:02d}", halign="center", bold=True, theme_text_color="Custom", text_color=(1,1,1,1))
        
        btn_h_add = MDButton(MDButtonText(text="+"), style="filled", md_bg_color=(0, 0.9, 0.46, 1), size_hint=(None, None), size=(dp(45), dp(45)))
        btn_h_add.bind(on_release=lambda x: self.adjust_hour(1))
        
        h_ctrl.add_widget(btn_h_sub)
        h_ctrl.add_widget(self.lbl_h_val)
        h_ctrl.add_widget(btn_h_add)
        h_box.add_widget(h_ctrl)
        
        m_box = MDBoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None, height=dp(70))
        m_box.add_widget(MDLabel(text="Minuto Exato", halign="center", theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), role="small", size_hint_y=None, height=dp(20)))
        m_ctrl = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(45))
        
        btn_m_sub = MDButton(MDButtonText(text="-"), style="outlined", size_hint=(None, None), size=(dp(45), dp(45)))
        btn_m_sub.bind(on_release=lambda x: self.adjust_minute(-1))
        
        self.lbl_m_val = MDLabel(text=f"{self.selected_minute:02d}", halign="center", bold=True, theme_text_color="Custom", text_color=(1,1,1,1))
        
        btn_m_add = MDButton(MDButtonText(text="+"), style="filled", md_bg_color=(0, 0.9, 0.46, 1), size_hint=(None, None), size=(dp(45), dp(45)))
        btn_m_add.bind(on_release=lambda x: self.adjust_minute(1))
        
        m_ctrl.clear_widgets()
        m_ctrl.add_widget(btn_m_sub)
        m_ctrl.add_widget(self.lbl_m_val)
        m_ctrl.add_widget(btn_m_add)
        
        m_box.add_widget(m_ctrl)
        
        controls_box.add_widget(h_box)
        controls_box.add_widget(m_box)
        content.add_widget(controls_box)
        
        btn_confirm = MDButton(MDButtonText(text="Confirmar Horário", theme_text_color="Custom", text_color=(0, 0, 0, 1)), style="filled", md_bg_color=(0, 0.9, 0.46, 1), size_hint_y=None, height=dp(45))
        btn_confirm.bind(on_release=lambda x: [
            setattr(self.lbl_time_display, 'text', f"Horário selecionado: {self.selected_hour:02d}:{self.selected_minute:02d}"),
            popup.dismiss()
        ])
        content.add_widget(btn_confirm)
        
        popup.open()

    def adjust_hour(self, delta):
        self.selected_hour = (self.selected_hour + delta) % 24
        if hasattr(self, 'lbl_h_val') and self.lbl_h_val:
            self.lbl_h_val.text = f"{self.selected_hour:02d}"
        if hasattr(self, 'time_preview_lbl') and self.time_preview_lbl:
            self.time_preview_lbl.text = f"{self.selected_hour:02d}:{self.selected_minute:02d}"

    def adjust_minute(self, delta):
        self.selected_minute = (self.selected_minute + delta) % 60
        if hasattr(self, 'lbl_m_val') and self.lbl_m_val:
            self.lbl_m_val.text = f"{self.selected_minute:02d}"
        if hasattr(self, 'time_preview_lbl') and self.time_preview_lbl:
            self.time_preview_lbl.text = f"{self.selected_hour:02d}:{self.selected_minute:02d}"

    def on_routine_switch_active(self, switch, value):
        if value:
            if self.sec_date in self.form_layout.children:
                self.form_layout.remove_widget(self.sec_date)
            if self.sec_days not in self.form_layout.children:
                self.form_layout.add_widget(self.sec_days)
        else:
            if self.sec_days in self.form_layout.children:
                self.form_layout.remove_widget(self.sec_days)
            if self.sec_date not in self.form_layout.children:
                self.form_layout.add_widget(self.sec_date)
            self.selected_routine_days.clear()
            for d, btn in self.day_buttons.items():
                btn.style = "outlined"
                btn.md_bg_color = (0.12, 0.12, 0.12, 1)
                if btn.children and hasattr(btn.children[0], 'text_color'):
                    btn.children[0].text_color = (0, 0.9, 0.46, 1)

    def toggle_day(self, day_key):
        full_name = self.dias_mapeamento[day_key]
        btn = self.day_buttons[day_key]
        
        if full_name in self.selected_routine_days:
            self.selected_routine_days.remove(full_name)
            btn.style = "outlined"
            btn.md_bg_color = (0.12, 0.12, 0.12, 1)
            if btn.children and hasattr(btn.children[0], 'text_color'):
                btn.children[0].text_color = (0, 0.9, 0.46, 1)
        else:
            self.selected_routine_days.add(full_name)
            btn.style = "filled"
            btn.md_bg_color = (0, 0.9, 0.46, 1)
            if btn.children and hasattr(btn.children[0], 'text_color'):
                btn.children[0].text_color = (0, 0, 0, 1)

    def save_task(self, *args):
        title = self.title_input.text.strip()
        if not title:
            return
            
        is_routine = 1 if self.routine_switch.active else 0
        due_date = self.selected_date if not is_routine else None
        due_time = (self.selected_hour * 60) + self.selected_minute
        
        recurrence_data = ", ".join(self.selected_routine_days) if is_routine and self.selected_routine_days else None
        
        try:
            conn = get_connection()
            conn.execute("""
                INSERT INTO tasks (title, is_routine, due_date, due_time, recurrence_data, is_completed)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (title, is_routine, due_date, due_time, recurrence_data))
            conn.commit()
            conn.close()
            
            # Limpeza segura
            self.title_input.text = ""
            self.selected_routine_days.clear()
            for d, btn in self.day_buttons.items():
                btn.style = "outlined"
                btn.md_bg_color = (0.12, 0.12, 0.12, 1)
                if btn.children and hasattr(btn.children[0], 'text_color'):
                    btn.children[0].text_color = (0, 0.9, 0.46, 1)
            self.routine_switch.active = False
            
            # Vai para o dashboard
            app = MDApp.get_running_app()
            if app and hasattr(app, 'sm'):
                app.sm.current = "dashboard"
        except Exception as e:
            logger.error(f"Erro ao salvar tarefa: {e}")