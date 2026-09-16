from datetime import datetime
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.app import MDApp

from database.repositories.task_repository import TaskRepository
from core.logger import get_logger

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

logger = get_logger("DashboardScreen")

def show_gamified_toast(message):
    """Exibe um popup motivacional customizado estilo SmartFit"""
    layout = BoxLayout(orientation="vertical", padding=dp(20))
    layout.add_widget(Label(text="✅", font_size=dp(40), size_hint_y=None, height=dp(60)))
    layout.add_widget(Label(text=message, bold=True, font_size=dp(18), halign="center"))
    
    popup = Popup(title="", separator_height=0, content=layout, size_hint=(0.7, 0.3), background_color=(0, 0.7, 0.4, 0.9))
    popup.open()
    Clock.schedule_once(lambda dt: popup.dismiss(), 2.5) # Fecha sozinho após 2.5s

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = TaskRepository()
        self.hoje_data = datetime.now().strftime("%Y-%m-%d")
        dias_map = {"Sun": "Dom", "Mon": "Seg", "Tue": "Ter", "Wed": "Qua", "Thu": "Qui", "Fri": "Sex", "Sat": "Sáb"}
        self.dia_str = dias_map.get(datetime.now().strftime("%a"), "Seg")

        main_layout = MDBoxLayout(orientation="vertical", padding=40, spacing=20)
        main_layout.md_bg_color = (0.07, 0.07, 0.07, 1)
        
        # HEADERS E BOTÃO DE CONCLUIR TODAS
        header_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        self.titulo = MDLabel(text=f"Hoje ({datetime.now().strftime('%d/%m')})", font_style="Headline", role="medium", bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        
        btn_concluir_todas = MDButton(MDButtonText(text="Concluir Todas", bold=True), style="filled", on_release=self.concluir_todas_hoje, radius=[dp(8)])
        btn_concluir_todas.theme_bg_color = "Custom"
        btn_concluir_todas.md_bg_color = (0.0, 0.9, 0.46, 1)
        
        header_layout.add_widget(self.titulo)
        header_layout.add_widget(btn_concluir_todas)
        main_layout.add_widget(header_layout)
        
        # BARRA DE PROGRESSO GAMIFICADA (À PROVA DE FALHAS DE VERSÃO)
        self.progress_lbl = MDLabel(text="Progresso: 0/0", size_hint_y=None, height=dp(20), theme_text_color="Custom", text_color=(0.8, 0.8, 0.8, 1), bold=True)
        
        # Fundo da barra (Cinza escuro)
        self.progress_bg = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(8), md_bg_color=(0.2, 0.2, 0.2, 1), radius=[dp(4)])
        # Preenchimento da barra (Verde Menta). Começa com size_hint_x = 0
        self.progress_fill = MDBoxLayout(size_hint_x=0, md_bg_color=(0.0, 0.9, 0.46, 1), radius=[dp(4)])
        self.progress_bg.add_widget(self.progress_fill)
        
        # O espaço restante da barra para manter a proporção visual correta
        self.progress_empty = MDBoxLayout(size_hint_x=1, md_bg_color=(0,0,0,0))
        self.progress_bg.add_widget(self.progress_empty)

        main_layout.add_widget(self.progress_lbl)
        main_layout.add_widget(self.progress_bg)
        
        # LISTA DE TAREFAS ROLÁVEL
        scroll = MDScrollView()
        self.task_list = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=15)
        scroll.add_widget(self.task_list)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def on_enter(self):
        self.load_daily_tasks()
        if PLYER_AVAILABLE:
            try:
                notification.notify(title="Planner", message="Confira suas atividades para hoje!", timeout=3)
            except:
                pass

    def load_daily_tasks(self):
        try:
            self.task_list.clear_widgets()
            tarefas = self.repo.get_all_tasks() 
            
            total_hoje = 0
            concluidas_hoje = 0
            
            for t in tarefas:
                e_hoje = (not t.is_routine and t.due_date == self.hoje_data)
                e_rotina_hoje = False
                if t.is_routine and t.recurrence:
                    if self.dia_str in [d.strip() for d in t.recurrence.split(",")]:
                        e_rotina_hoje = True
                
                if e_hoje or e_rotina_hoje:
                    total_hoje += 1
                    esta_concluida = (t.last_completed_date == self.hoje_data) if t.is_routine else bool(t.is_completed)
                    if esta_concluida: concluidas_hoje += 1

                    card = MDCard(
                        orientation="horizontal", size_hint_y=None, height=dp(80), padding=15, spacing=15,
                        style="elevated", md_bg_color=(0.11, 0.11, 0.11, 1), radius=[dp(12)]
                    )
                    
                    chk = MDCheckbox(active=esta_concluida, size_hint=(None, None), size=(dp(48), dp(48)))
                    chk.bind(active=lambda inst, val, task=t: self.toggle_status(task, val))
                    
                    textos = MDBoxLayout(orientation="vertical")
                    
                    # Feedback visual imediato
                    if esta_concluida:
                        lbl_title = MDLabel(text=f"[s]{t.title}[/s]", bold=True, markup=True, theme_text_color="Custom", text_color=(0.4, 0.4, 0.4, 1))
                    else:
                        lbl_title = MDLabel(text=t.title, bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
                        
                    lbl_sub = MDLabel(text=f"Horário: {t.get_formatted_time()}", theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), role="small")
                    
                    textos.add_widget(lbl_title)
                    textos.add_widget(lbl_sub)
                    card.add_widget(chk)
                    card.add_widget(textos)
                    self.task_list.add_widget(card)
                    
            # Atualiza barra de progresso (Mecânica Gamificada Segura)
            if total_hoje > 0:
                perc = concluidas_hoje / total_hoje
                self.progress_fill.size_hint_x = perc
                self.progress_empty.size_hint_x = 1 - perc
                
                if perc == 1.0:
                    self.progress_lbl.text = f"🏆 Dia 100% Concluído! Parabéns! ({concluidas_hoje}/{total_hoje})"
                    self.progress_lbl.text_color = (0.0, 0.9, 0.46, 1)
                else:
                    self.progress_lbl.text = f"Progresso: {concluidas_hoje}/{total_hoje} atividades"
                    self.progress_lbl.text_color = (0.8, 0.8, 0.8, 1)
            else:
                self.progress_fill.size_hint_x = 0
                self.progress_empty.size_hint_x = 1
                self.progress_lbl.text = "Sem atividades hoje."
                self.task_list.add_widget(MDLabel(text="Nenhuma atividade para hoje. Aproveite!", halign="center", theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=dp(60)))

        except Exception as e:
            logger.error(f"Erro carregar dashboard: {e}")

    def toggle_status(self, task, is_active):
        try:
            if task.is_routine:
                task.last_completed_date = self.hoje_data if is_active else None
            else:
                task.is_completed = 1 if is_active else 0
                
            self.repo.update_task(task)
            self.load_daily_tasks()
            
            if is_active:
                show_gamified_toast("Boa! Atividade concluída com sucesso!")
        except Exception as e:
            logger.error(f"Erro status: {e}")

    def concluir_todas_hoje(self, *args):
        try:
            tarefas = self.repo.get_all_tasks()
            mudou = False
            for t in tarefas:
                e_hoje = (not t.is_routine and t.due_date == self.hoje_data)
                e_rotina = (t.is_routine and t.recurrence and self.dia_str in [d.strip() for d in t.recurrence.split(",")])
                if e_hoje or e_rotina:
                    if t.is_routine: t.last_completed_date = self.hoje_data
                    else: t.is_completed = 1
                    self.repo.update_task(t)
                    mudou = True
            
            self.load_daily_tasks()
            if mudou:
                show_gamified_toast("Incrível! Você finalizou todas as tarefas de hoje!")
        except Exception as e:
            logger.error(f"Erro concluir todas: {e}")