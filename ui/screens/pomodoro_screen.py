from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Line
from kivy.core.audio import SoundLoader
from datetime import datetime
from core.logger import get_logger
from database.connection import get_connection

try:
    from plyer import notification
except ImportError:
    notification = None

logger = get_logger("PomodoroModule")

# Paleta de Cores Padrão (Alto Contraste)
COLORS = {
    'BG': (0.07, 0.07, 0.07, 1),           # #121212
    'CARD': (0.12, 0.12, 0.12, 1),       # #1E1E1E
    'TEXT': (1, 1, 1, 1),                # #FFFFFF
    'LABEL': (0.69, 0.69, 0.69, 1),      # #B0B0B0
    'FOCUS': (0, 0.9, 0.46, 1),          # #00E676 (Verde Menta)
    'SHORT': (0, 0.69, 1, 1),            # #00B0FF (Azul Claro)
    'LONG': (1, 0.67, 0, 1),             # #FFAB00 (Laranja)
    'BTN_NORMAL': (0.05, 0.05, 0.05, 1), # Preto / Fundo Escuro
    'TEXT_DARK': (0, 0, 0, 1)            # #000000 (Preto para fundo verde)
}

# ==================== TELA 3: TIMER EM EXECUÇÃO ====================
class CircularTimer(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.percent = 100
        self.line_color = COLORS['FOCUS']
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.18, 0.18, 0.18, 1)
            Line(circle=(self.center_x, self.center_y, dp(120)), width=dp(10))
            Color(*self.line_color)
            angle = 360 * (self.percent / 100)
            if angle > 0:
                Line(circle=(self.center_x, self.center_y, dp(120), 0, angle), width=dp(10))

    def update_state(self, percent, color):
        self.percent = max(0, min(100, percent))
        self.line_color = color
        self.update_canvas()

    def pulse_animation(self):
        try:
            anim = Animation(percent=self.percent - 2, duration=0.5) + Animation(percent=self.percent + 2, duration=0.5)
            anim.repeat = True
            anim.start(self)
        except Exception:
            pass

    def stop_animation(self):
        try:
            Animation.cancel_all(self)
        except Exception:
            pass


class TimerActiveScreen(MDScreen):
    def __init__(self, main_controller, **kwargs):
        super().__init__(**kwargs)
        self.main = main_controller
        self.timer_event = None
        self.is_running = False
        self.current_phase = 'FOCUS'
        self.cycles_completed = 0
        self.sessions_today = 0
        self.time_left = 25 * 60
        self.profile_data = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15), md_bg_color=COLORS['BG'])
        
        # Top Bar
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_back = MDIconButton(icon="arrow-left", theme_icon_color="Custom", icon_color=COLORS['TEXT'])
        btn_back.bind(on_release=lambda x: self.main.go_to_screen("timers_list"))
        self.lbl_timer_title = MDLabel(text="Timer Ativo", bold=True, font_style="Title", theme_text_color="Custom", text_color=COLORS['TEXT'])
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.lbl_timer_title)
        layout.add_widget(top_bar)
        
        # Tarefa associada
        self.lbl_task_active = MDLabel(text="Nenhuma rotina associada", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small", size_hint_y=None, height=dp(20))
        layout.add_widget(self.lbl_task_active)
        
        # Fase Atual e Contadores
        self.lbl_phase = MDLabel(text="FASE: FOCO", bold=True, halign="center", theme_text_color="Custom", text_color=COLORS['FOCUS'], size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_phase)
        
        counters_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(30), pos_hint={"center_x": 0.5})
        self.lbl_cycles = MDLabel(text="Ciclo: 1/4", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small")
        self.lbl_sessions = MDLabel(text="Sessões hoje: 0", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small")
        counters_box.add_widget(self.lbl_cycles)
        counters_box.add_widget(self.lbl_sessions)
        layout.add_widget(counters_box)
        
        # Anel Circular centralizado em destaque
        timer_box = MDBoxLayout(orientation="vertical", size_hint=(1, 1))
        self.circular_timer = CircularTimer(size_hint=(1, 1))
        self.lbl_timer = MDLabel(text="25:00", font_size=sp(64), bold=True, halign="center", theme_text_color="Custom", text_color=COLORS['TEXT'], pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.circular_timer.add_widget(self.lbl_timer)
        timer_box.add_widget(self.circular_timer)
        layout.add_widget(timer_box)
        
        # Botões de Controle
        controls_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(65), spacing=dp(25), pos_hint={"center_x": 0.5}, adaptive_width=True)
        
        self.btn_reset = MDIconButton(icon="reload", theme_icon_color="Custom", icon_color=COLORS['FOCUS'])
        self.btn_reset.bind(on_release=self.reset_timer)
        
        self.btn_play = MDButton(MDButtonText(text="▶ INICIAR", theme_text_color="Custom", text_color=COLORS['FOCUS']), style="outlined", md_bg_color=COLORS['BTN_NORMAL'], size_hint_x=None, width=dp(180), size_hint_y=None, height=dp(50))
        self.btn_play.bind(on_release=self.toggle_timer)
        
        self.btn_skip = MDIconButton(icon="skip-next", theme_icon_color="Custom", icon_color=COLORS['FOCUS'])
        self.btn_skip.bind(on_release=self.skip_phase)
        
        controls_box.add_widget(self.btn_reset)
        controls_box.add_widget(self.btn_play)
        controls_box.add_widget(self.btn_skip)
        layout.add_widget(controls_box)
        
        self.add_widget(layout)

    def load_profile(self, profile_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id, name, focus_time, short_pause, long_pause, cycles_before_long_pause, auto_start_next_cycle, task_id FROM pomodoro_profiles WHERE id = ?", (profile_id,))
            row = c.fetchone()
            conn.close()
            if row:
                self.profile_data = {
                    'id': row[0], 'name': row[1], 'focus': row[2], 'short': row[3], 'long': row[4],
                    'cycles': row[5], 'auto': bool(row[6]), 'task_id': row[7]
                }
                self.lbl_timer_title.text = self.profile_data['name']
                self.current_phase = 'FOCUS'
                self.cycles_completed = 0
                self.time_left = self.profile_data['focus'] * 60
                
                if self.profile_data['task_id']:
                    t_conn = get_connection()
                    t_c = t_conn.cursor()
                    t_c.execute("SELECT title FROM tasks WHERE id = ?", (self.profile_data['task_id'],))
                    t_row = t_c.fetchone()
                    t_conn.close()
                    if t_row:
                        self.lbl_task_active.text = f"Focando na rotina: {t_row[0]}"
                    else:
                        self.lbl_task_active.text = "Nenhuma rotina associada"
                else:
                    self.lbl_task_active.text = "Nenhuma rotina associada"
                
                self.load_sessions_count()
                self.update_ui_state()
                logger.info(f"Perfil carregado no timer ativo: {self.profile_data['name']}")
        except Exception as e:
            logger.error(f"Erro ao carregar perfil no timer ativo: {e}")

    def load_sessions_count(self):
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM pomodoro_sessions WHERE date(start_time) = ? AND completed = 1 AND type = 'FOCUS'", (today_str,))
            res = c.fetchone()
            self.sessions_today = res[0] if res else 0
            conn.close()
            self.lbl_sessions.text = f"Sessões hoje: {self.sessions_today}"
        except Exception as e:
            logger.error(f"Erro ao contar sessões: {e}")

    def get_current_duration(self):
        if not self.profile_data: return 25
        if self.current_phase == 'FOCUS':
            return self.profile_data['focus']
        elif self.current_phase == 'SHORT':
            return self.profile_data['short']
        elif self.current_phase == 'LONG':
            return self.profile_data['long']
        return 5

    def update_ui_state(self):
        col = COLORS['FOCUS'] if self.current_phase == 'FOCUS' else (COLORS['SHORT'] if self.current_phase == 'SHORT' else COLORS['LONG'])
        phase_labels = {
            'FOCUS': 'FASE: FOCO',
            'SHORT': 'FASE: PAUSA CURTA',
            'LONG': 'FASE: PAUSA LONGA'
        }
        self.lbl_phase.text = phase_labels.get(self.current_phase, 'FASE: FOCO')
        self.lbl_phase.text_color = col
        
        if not self.is_running:
            self.btn_play.md_bg_color = COLORS['BTN_NORMAL']
            self.btn_play.style = "outlined"
            self.btn_play.children[0].text_color = COLORS['FOCUS']
        else:
            self.btn_play.md_bg_color = COLORS['LONG']
            self.btn_play.style = "filled"
            self.btn_play.children[0].text_color = COLORS['TEXT_DARK']

        max_c = self.profile_data['cycles'] if self.profile_data else 4
        self.lbl_cycles.text = f"Ciclo: {self.cycles_completed + 1}/{max_c}"
        
        dur = self.get_current_duration() * 60
        pct = (self.time_left / dur) * 100 if dur > 0 else 100
        self.circular_timer.update_state(pct, col)

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def toggle_timer(self, *args):
        if not self.is_running:
            try:
                self.is_running = True
                self.btn_play.children[0].text = "⏸ PAUSAR"
                self.btn_play.md_bg_color = COLORS['LONG']
                self.btn_play.style = "filled"
                self.btn_play.children[0].text_color = COLORS['TEXT_DARK']
                self.session_start = datetime.now()
                self.timer_event = Clock.schedule_interval(self.tick, 1)
                self.circular_timer.pulse_animation()
                self.main.show_snackbar("Sessão iniciada!")
                logger.info(f"Timer iniciado na fase {self.current_phase}")
            except Exception as e:
                logger.error(f"Erro ao iniciar timer: {e}")
        else:
            self.is_running = False
            self.btn_play.children[0].text = "▶ RETOMAR"
            self.btn_play.md_bg_color = COLORS['BTN_NORMAL']
            self.btn_play.style = "outlined"
            self.btn_play.children[0].text_color = COLORS['FOCUS']
            if self.timer_event:
                self.timer_event.cancel()
            self.circular_timer.stop_animation()
            self.main.show_snackbar("Sessão pausada.")
            logger.info("Timer pausado.")

    def tick(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            self.lbl_timer.text = self.format_time(self.time_left)
            dur = self.get_current_duration() * 60
            pct = (self.time_left / dur) * 100 if dur > 0 else 100
            col = COLORS['FOCUS'] if self.current_phase == 'FOCUS' else (COLORS['SHORT'] if self.current_phase == 'SHORT' else COLORS['LONG'])
            self.circular_timer.update_state(pct, col)
        else:
            self.finish_phase()

    def skip_phase(self, *args):
        if self.timer_event: self.timer_event.cancel()
        self.circular_timer.stop_animation()
        self.finish_phase(skipped=True)

    def reset_timer(self, *args):
        if self.timer_event: self.timer_event.cancel()
        self.circular_timer.stop_animation()
        self.is_running = False
        self.btn_play.children[0].text = "▶ INICIAR"
        self.btn_play.md_bg_color = COLORS['BTN_NORMAL']
        self.btn_play.style = "outlined"
        self.btn_play.children[0].text_color = COLORS['FOCUS']
        self.time_left = self.get_current_duration() * 60
        self.lbl_timer.text = self.format_time(self.time_left)
        self.update_ui_state()
        logger.info("Timer reiniciado.")

    def finish_phase(self, skipped=False):
        self.is_running = False
        if self.timer_event: self.timer_event.cancel()
        self.circular_timer.stop_animation()
        
        try:
            end_t = datetime.now()
            dur_min = self.get_current_duration()
            if dur_min > 0 and hasattr(self, 'session_start') and self.profile_data:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""INSERT INTO pomodoro_sessions 
                             (task_id, profile_id, start_time, end_time, duration, type, completed) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (self.profile_data.get('task_id'), self.profile_data['id'],
                           self.session_start.strftime("%Y-%m-%d %H:%M:%S"),
                           end_t.strftime("%Y-%m-%d %H:%M:%S"),
                           dur_min, self.current_phase, 1 if not skipped else 0))
                conn.commit()
                conn.close()
                logger.info(f"Sessão registrada no SQLite: {self.current_phase} ({dur_min} min)")
        except Exception as e:
            logger.error(f"Erro ao salvar sessão: {e}")

        # Reproduzir som de aviso agradável e enviar notificação escrita ao concluir
        if not skipped:
            try:
                sound = SoundLoader.load('assets/notification.wav')
                if sound:
                    sound.play()
            except Exception as e:
                logger.error(f"Erro ao reproduzir som de notificação: {e}")

            try:
                phase_label_txt = "Foco" if self.current_phase == 'FOCUS' else ("Pausa Curta" if self.current_phase == 'SHORT' else "Pausa Longa")
                notif_msg = f"Ciclo de {phase_label_txt} concluído com sucesso!"
                
                if notification:
                    notification.notify(
                        title="Pomodoro Concluído",
                        message=notif_msg,
                        app_name="App de Produtividade",
                        timeout=5
                    )
            except Exception as e:
                logger.error(f"Erro ao enviar notificação escrita do sistema: {e}")

        if self.current_phase == 'FOCUS':
            self.cycles_completed += 1
            self.sessions_today += 1
            self.load_sessions_count()
            
            max_cycles = self.profile_data['cycles'] if self.profile_data else 4
            
            if self.cycles_completed >= max_cycles:
                self.current_phase = 'LONG'
                self.cycles_completed = 0
                self.main.show_snackbar("Ciclo completo! Iniciando Pausa Longa.")
            else:
                self.current_phase = 'SHORT'
                self.main.show_snackbar("Foco concluído! Iniciando Pausa Curta.")
        else:
            self.current_phase = 'FOCUS'
            self.main.show_snackbar("Pausa concluída! Retorne ao foco.")

        self.btn_play.children[0].text = "▶ INICIAR"
        self.btn_play.md_bg_color = COLORS['BTN_NORMAL']
        self.btn_play.style = "outlined"
        self.btn_play.children[0].text_color = COLORS['FOCUS']
        self.time_left = self.get_current_duration() * 60
        self.lbl_timer.text = self.format_time(self.time_left)
        self.update_ui_state()

        if self.profile_data and self.profile_data.get('auto', False):
            self.toggle_timer()


# ==================== TELA 2: CRIAR / EDITAR TIMER ====================
class TimerFormScreen(MDScreen):
    def __init__(self, main_controller, **kwargs):
        super().__init__(**kwargs)
        self.main = main_controller
        self.editing_id = None
        self.selected_task_id = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12), md_bg_color=COLORS['BG'])
        
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_back = MDIconButton(icon="arrow-left", theme_icon_color="Custom", icon_color=COLORS['TEXT'])
        btn_back.bind(on_release=lambda x: self.main.go_to_screen("timers_list"))
        self.lbl_form_title = MDLabel(text="Criar Novo Timer", bold=True, font_style="Title", theme_text_color="Custom", text_color=COLORS['TEXT'])
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.lbl_form_title)
        layout.add_widget(top_bar)
        
        scroll = MDScrollView()
        form_box = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(10), padding=dp(5))
        
        def add_labeled_field(label_text, field_widget):
            lbl = MDLabel(text=label_text, theme_text_color="Custom", text_color=COLORS['LABEL'], role="small", size_hint_y=None, height=dp(18))
            form_box.add_widget(lbl)
            form_box.add_widget(field_widget)

        self.input_name = MDTextField(mode="outlined", hint_text="Ex: Estudo Pesado")
        add_labeled_field("Nome do Timer", self.input_name)
        
        presets_label = MDLabel(text="Presets rápidos de Foco (min):", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small", size_hint_y=None, height=dp(18))
        form_box.add_widget(presets_label)
        
        presets_box = MDBoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(35))
        for p_val in [15, 25, 30, 45, 60, 90]:
            btn_p = MDButton(MDButtonText(text=f"{p_val}m"), style="outlined", size_hint_x=None, width=dp(45))
            btn_p.bind(on_release=lambda x, val=p_val: setattr(self.input_focus, 'text', str(val)))
            presets_box.add_widget(btn_p)
        form_box.add_widget(presets_box)
        
        self.input_focus = MDTextField(mode="outlined", hint_text="25", input_filter='int', text="25")
        add_labeled_field("Tempo de Foco (minutos)", self.input_focus)
        
        self.input_short = MDTextField(mode="outlined", hint_text="5", input_filter='int', text="5")
        add_labeled_field("Pausa Curta (minutos)", self.input_short)
        
        self.input_long = MDTextField(mode="outlined", hint_text="15", input_filter='int', text="15")
        add_labeled_field("Pausa Longa (minutos)", self.input_long)
        
        self.input_cycles = MDTextField(mode="outlined", hint_text="4", input_filter='int', text="4")
        add_labeled_field("Ciclos antes da Pausa Longa", self.input_cycles)
        
        lbl_auto = MDLabel(text="Iniciar próximo ciclo automaticamente", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small", size_hint_y=None, height=dp(18))
        form_box.add_widget(lbl_auto)
        
        auto_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        auto_box.add_widget(MDLabel(text="Habilitar início automático", theme_text_color="Custom", text_color=COLORS['TEXT']))
        self.switch_auto = MDSwitch(active=False)
        auto_box.add_widget(self.switch_auto)
        form_box.add_widget(auto_box)
        
        lbl_task = MDLabel(text="Associar a uma Tarefa (Opcional)", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small", size_hint_y=None, height=dp(18))
        form_box.add_widget(lbl_task)
        
        self.btn_select_task = MDButton(MDButtonText(text="Selecionar Tarefa de Rotina"), style="outlined", size_hint_x=1)
        self.btn_select_task.bind(on_release=self.open_routine_picker)
        form_box.add_widget(self.btn_select_task)
        
        scroll.add_widget(form_box)
        layout.add_widget(scroll)
        
        actions_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_cancel = MDButton(MDButtonText(text="Cancelar", theme_text_color="Custom", text_color=COLORS['LABEL']), style="text", size_hint_x=1, on_release=lambda x: self.main.go_to_screen("timers_list"))
        btn_save = MDButton(MDButtonText(text="Salvar Timer", theme_text_color="Custom", text_color=COLORS['TEXT_DARK']), style="filled", md_bg_color=COLORS['FOCUS'], size_hint_x=1, on_release=self.save_timer)
        actions_box.add_widget(btn_cancel)
        actions_box.add_widget(btn_save)
        layout.add_widget(actions_box)
        
        self.add_widget(layout)

    def open_routine_picker(self, *args):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            if not c.fetchone():
                self.main.show_snackbar("Nenhuma tabela de tarefas encontrada.")
                conn.close()
                return
            
            c.execute("PRAGMA table_info(tasks)")
            cols = [col[1] for col in c.fetchall()]
            
            routines = []
            if 'is_routine' in cols:
                c.execute("SELECT id, title FROM tasks WHERE is_routine = 1")
                routines = c.fetchall()
            else:
                c.execute("SELECT id, title FROM tasks")
                routines = c.fetchall()
            
            conn.close()

            content = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(220))
            btn_none = MDButton(MDButtonText(text="Nenhuma Rotina Associada"), style="outlined", size_hint_x=1)
            btn_none.bind(on_release=lambda x: self.pick_task(None, "Nenhuma Rotina"))
            content.add_widget(btn_none)

            if not routines:
                lbl_empty = MDLabel(text="Nenhuma tarefa de rotina encontrada. Crie uma rotina na aba 'Cadastrar'.", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL'])
                content.add_widget(lbl_empty)
            else:
                for tid, ttitle in routines:
                    btn_t = MDButton(MDButtonText(text=ttitle), style="text", size_hint_x=1)
                    btn_t.bind(on_release=lambda x, id=tid, title=ttitle: self.pick_task(id, title))
                    content.add_widget(btn_t)

            self.task_picker_dialog = MDDialog(
                MDDialogHeadlineText(text="Selecionar Tarefa de Rotina", halign="center"),
                MDDialogContentContainer(content, orientation="vertical"),
                MDDialogButtonContainer(
                    MDButton(MDButtonText(text="Fechar"), style="text", on_release=lambda x: self.task_picker_dialog.dismiss()),
                    spacing="8dp"
                )
            )
            self.task_picker_dialog.open()
        except Exception as e:
            logger.error(f"Erro ao buscar tarefas de rotina: {e}")
            self.main.show_snackbar("Erro ao carregar tarefas de rotina.")

    def pick_task(self, task_id, task_title):
        self.selected_task_id = task_id
        self.btn_select_task.children[0].text = f"Rotina: {task_title}"
        if self.task_picker_dialog:
            self.task_picker_dialog.dismiss()
        self.main.show_snackbar(f"Rotina associada: {task_title}")

    def load_profile_for_edit(self, profile_id):
        self.editing_id = profile_id
        self.lbl_form_title.text = "Editar Timer"
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT name, focus_time, short_pause, long_pause, cycles_before_long_pause, auto_start_next_cycle, task_id FROM pomodoro_profiles WHERE id = ?", (profile_id,))
            row = c.fetchone()
            conn.close()
            if row:
                self.input_name.text = row[0]
                self.input_focus.text = str(row[1])
                self.input_short.text = str(row[2])
                self.input_long.text = str(row[3])
                self.input_cycles.text = str(row[4])
                self.switch_auto.active = bool(row[5])
                self.selected_task_id = row[6]
                if self.selected_task_id:
                    t_conn = get_connection()
                    t_c = t_conn.cursor()
                    t_c.execute("SELECT title FROM tasks WHERE id = ?", (self.selected_task_id,))
                    t_row = t_c.fetchone()
                    t_conn.close()
                    if t_row:
                        self.btn_select_task.children[0].text = f"Rotina: {t_row[0]}"
        except Exception as e:
            logger.error(f"Erro ao carregar perfil para edição: {e}")

    def clear_form(self):
        self.editing_id = None
        self.lbl_form_title.text = "Criar Novo Timer"
        self.input_name.text = ""
        self.input_focus.text = "25"
        self.input_short.text = "5"
        self.input_long.text = "15"
        self.input_cycles.text = "4"
        self.switch_auto.active = False
        self.selected_task_id = None
        self.btn_select_task.children[0].text = "Selecionar Tarefa de Rotina"

    def save_timer(self, *args):
        try:
            name = self.input_name.text.strip()
            focus_str = self.input_focus.text.strip()
            short_str = self.input_short.text.strip()
            long_str = self.input_long.text.strip()
            cycles_str = self.input_cycles.text.strip()

            if not name:
                self.main.show_snackbar("O nome do timer não pode estar vazio!")
                return
            
            if not focus_str.isdigit() or not short_str.isdigit() or not long_str.isdigit() or not cycles_str.isdigit():
                self.main.show_snackbar("Preencha todos os campos numéricos com valores válidos!")
                return

            focus = int(focus_str)
            short_p = int(short_str)
            long_p = int(long_str)
            cycles = int(cycles_str)
            auto = 1 if self.switch_auto.active else 0

            if focus <= 0 or short_p <= 0 or long_p <= 0 or cycles <= 0:
                self.main.show_snackbar("Todos os tempos e ciclos devem ser números positivos maiores que zero!")
                return

            conn = get_connection()
            c = conn.cursor()
            if self.editing_id:
                c.execute("""UPDATE pomodoro_profiles SET name=?, focus_time=?, short_pause=?, long_pause=?, 
                             cycles_before_long_pause=?, auto_start_next_cycle=?, task_id=? WHERE id=?""",
                          (name, focus, short_p, long_p, cycles, auto, self.selected_task_id, self.editing_id))
                logger.info(f"Timer editado com sucesso: ID {self.editing_id}")
            else:
                c.execute("""INSERT INTO pomodoro_profiles 
                             (name, focus_time, short_pause, long_pause, cycles_before_long_pause, auto_start_next_cycle, task_id) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (name, focus, short_p, long_p, cycles, auto, self.selected_task_id))
                logger.info(f"Novo timer criado com sucesso: {name}")
            conn.commit()
            conn.close()

            self.main.show_snackbar("Timer salvo com sucesso!")
            self.main.go_to_screen("timers_list")
        except Exception as e:
            logger.error(f"Erro ao salvar timer: {e}")
            self.main.show_snackbar("Erro ao salvar timer. Verifique os valores informados.")


# ==================== TELA 1: MEUS TIMERS ====================
class TimersListScreen(MDScreen):
    def __init__(self, main_controller, **kwargs):
        super().__init__(**kwargs)
        self.main = main_controller
        self.build_ui()

    def on_enter(self, *args):
        self.load_timers()

    def build_ui(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=COLORS['BG'])
        
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        top_bar.add_widget(MDLabel(text="Meus Timers de Foco", bold=True, font_style="Headline", theme_text_color="Custom", text_color=COLORS['TEXT']))
        layout.add_widget(top_bar)
        
        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12))
        scroll.add_widget(self.list_box)
        layout.add_widget(scroll)
        
        btn_create = MDButton(
            MDButtonText(text="+ Novo Timer", theme_text_color="Custom", text_color=COLORS['TEXT_DARK']),
            style="filled",
            md_bg_color=COLORS['FOCUS'],
            size_hint_y=None,
            height=dp(50),
            pos_hint={"center_x": 0.5}
        )
        btn_create.bind(on_release=lambda x: self.main.open_form_create())
        layout.add_widget(btn_create)
        
        self.add_widget(layout)

    def load_timers(self):
        self.list_box.clear_widgets()
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id, name, focus_time, short_pause, cycles_before_long_pause FROM pomodoro_profiles")
            rows = c.fetchall()
            conn.close()

            if not rows:
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(90), padding=dp(20), md_bg_color=COLORS['CARD'], radius=[dp(12)])
                empty_card.add_widget(MDLabel(text="Nenhum timer criado ainda.\nClique em + Novo Timer para começar!", halign="center", theme_text_color="Custom", text_color=COLORS['LABEL']))
                self.list_box.add_widget(empty_card)
                return

            for row in rows:
                p_id, name, focus, short_p, cycles = row
                
                card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(90), padding=dp(15), spacing=dp(10), md_bg_color=COLORS['CARD'], radius=[dp(12)])
                
                info = MDBoxLayout(orientation="vertical", spacing=dp(2))
                info.add_widget(MDLabel(text=name, bold=True, theme_text_color="Custom", text_color=COLORS['TEXT']))
                info.add_widget(MDLabel(text=f"Foco: {focus} min | Pausa Curta: {short_p}m", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small"))
                info.add_widget(MDLabel(text=f"Ciclos antes da pausa longa: {cycles}", theme_text_color="Custom", text_color=COLORS['LABEL'], role="small"))
                card.add_widget(info)
                
                actions = MDBoxLayout(orientation="horizontal", adaptive_width=True, spacing=dp(5), pos_hint={"center_y": 0.5})
                
                btn_start = MDButton(MDButtonText(text="Iniciar", theme_text_color="Custom", text_color=COLORS['TEXT_DARK']), style="filled", md_bg_color=COLORS['FOCUS'], size_hint_x=None, width=dp(80), size_hint_y=None, height=dp(36))
                btn_start.bind(on_release=lambda x, pid=p_id: self.main.start_timer_with_profile(pid))
                
                btn_edit = MDIconButton(icon="pencil-outline", theme_icon_color="Custom", icon_color=COLORS['LABEL'])
                btn_edit.bind(on_release=lambda x, pid=p_id: self.main.open_form_edit(pid))
                
                btn_del = MDIconButton(icon="delete-outline", theme_icon_color="Custom", icon_color=(0.9, 0.3, 0.3, 1))
                btn_del.bind(on_release=lambda x, pid=p_id: self.delete_timer(pid))
                
                actions.add_widget(btn_start)
                actions.add_widget(btn_edit)
                actions.add_widget(btn_del)
                
                card.add_widget(actions)
                self.list_box.add_widget(card)
        except Exception as e:
            logger.error(f"Erro ao listar timers: {e}")

    def delete_timer(self, profile_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM pomodoro_profiles WHERE id = ?", (profile_id,))
            conn.commit()
            conn.close()
            self.main.show_snackbar("Timer excluído com sucesso!")
            self.load_timers()
            logger.info(f"Perfil Pomodoro excluído: ID {profile_id}")
        except Exception as e:
            logger.error(f"Erro ao excluir timer: {e}")
            self.main.show_snackbar("Erro ao excluir timer.")


# ==================== MÓDULO PRINCIPAL POMODORO SCREEN ====================
class PomodoroScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_db()
        
        self.manager_internal = MDScreenManager()
        
        self.screen_list = TimersListScreen(self, name="timers_list")
        self.screen_form = TimerFormScreen(self, name="timer_form")
        self.screen_active = TimerActiveScreen(self, name="timer_active")
        
        self.manager_internal.add_widget(self.screen_list)
        self.manager_internal.add_widget(self.screen_form)
        self.manager_internal.add_widget(self.screen_active)
        
        self.add_widget(self.manager_internal)

    def init_db(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            
            c.execute('''CREATE TABLE IF NOT EXISTS pomodoro_profiles 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, focus_time INTEGER, short_pause INTEGER, long_pause INTEGER, cycles_before_long_pause INTEGER, auto_start_next_cycle INTEGER, task_id INTEGER)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS pomodoro_sessions 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, profile_id INTEGER, start_time TEXT, end_time TEXT, duration INTEGER, type TEXT, completed INTEGER)''')

            c.execute("PRAGMA table_info(pomodoro_profiles)")
            p_cols = [col[1] for col in c.fetchall()]
            if 'task_id' not in p_cols:
                c.execute("ALTER TABLE pomodoro_profiles ADD COLUMN task_id INTEGER")

            c.execute("SELECT COUNT(*) FROM pomodoro_profiles")
            if c.fetchone()[0] == 0:
                defaults = [
                    ("Clássico", 25, 5, 15, 4, 0),
                    ("Estudo Pesado", 50, 10, 20, 3, 1),
                    ("Leitura Leve", 15, 3, 10, 5, 0)
                ]
                c.executemany("INSERT INTO pomodoro_profiles (name, focus_time, short_pause, long_pause, cycles_before_long_pause, auto_start_next_cycle) VALUES (?, ?, ?, ?, ?, ?)", defaults)

            conn.commit()
            conn.close()
            logger.info("Banco de dados Pomodoro inicializado e validado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados Pomodoro: {e}")

    def go_to_screen(self, screen_name):
        self.manager_internal.current = screen_name

    def open_form_create(self):
        self.screen_form.clear_form()
        self.manager_internal.current = "timer_form"

    def open_form_edit(self, profile_id):
        self.screen_form.load_profile_for_edit(profile_id)
        self.manager_internal.current = "timer_form"

    def start_timer_with_profile(self, profile_id):
        self.screen_active.load_profile(profile_id)
        self.manager_internal.current = "timer_active"

    def show_snackbar(self, text):
        try:
            MDSnackbar(
                MDSnackbarText(text=text),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8
            ).open()
        except Exception as e:
            logger.error(f"Erro ao exibir snackbar: {e}")