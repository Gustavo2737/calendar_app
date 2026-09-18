from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.app import MDApp
from kivy.metrics import dp
from database.connection import get_connection
from core.logger import get_logger
from datetime import datetime

logger = get_logger("DashboardScreen")

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        header_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        header_box.add_widget(MDLabel(
            text="Minhas Atividades e Rotinas", 
            font_style="Headline", 
            bold=True, 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1)
        ))
        
        btn_add = MDButton(MDButtonText(text="+ Nova Atividade"), style="filled", md_bg_color=(0, 0.9, 0.46, 1))
        btn_add.bind(on_release=self.go_to_task_screen)
        header_box.add_widget(btn_add)
        layout.add_widget(header_box)
        
        scroll = MDScrollView()
        self.tasks_list_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12))
        scroll.add_widget(self.tasks_list_layout)
        
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self, *args):
        self.load_data()

    def load_data(self):
        self.tasks_list_layout.clear_widgets()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, is_routine, due_date, due_time, recurrence_data, is_completed FROM tasks ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                empty_card = MDCard(
                    orientation="vertical", 
                    size_hint_y=None, 
                    height=dp(80), 
                    padding=dp(20), 
                    md_bg_color=(0.12, 0.12, 0.12, 1), 
                    radius=[dp(12)]
                )
                empty_card.add_widget(MDLabel(
                    text="Nenhuma atividade cadastrada ainda.", 
                    halign="center", 
                    theme_text_color="Custom", 
                    text_color=(0.7, 0.7, 0.7, 1)
                ))
                self.tasks_list_layout.add_widget(empty_card)
                return

            for row in rows:
                task_id, title, is_routine, due_date, due_time, recurrence_data, is_completed = row
                
                card = MDCard(
                    orientation="horizontal", 
                    size_hint_y=None, 
                    height=dp(70), 
                    padding=dp(15), 
                    spacing=dp(15), 
                    md_bg_color=(0.12, 0.12, 0.12, 1), 
                    radius=[dp(12)]
                )
                
                info_box = MDBoxLayout(orientation="vertical", spacing=dp(4))
                info_box.add_widget(MDLabel(
                    text=title, 
                    bold=True, 
                    theme_text_color="Custom", 
                    text_color=(1, 1, 1, 1)
                ))
                
                if is_routine:
                    detalhe_txt = f"Rotina Semanal: {recurrence_data if recurrence_data else 'Não especificado'}"
                else:
                    time_str = "Dia Inteiro"
                    if due_time is not None and str(due_time).strip() != "":
                        try:
                            t_int = int(float(str(due_time)))
                            time_str = f"{t_int//60:02d}:{t_int%60:02d}"
                        except Exception:
                            time_str = str(due_time)
                    detalhe_txt = f"Data: {due_date} às {time_str}"
                
                info_box.add_widget(MDLabel(
                    text=detalhe_txt, 
                    theme_text_color="Custom", 
                    text_color=(0.7, 0.7, 0.7, 1), 
                    role="small"
                ))
                
                card.add_widget(info_box)
                
                btn_delete = MDIconButton(
                    icon="delete-outline", 
                    theme_icon_color="Custom", 
                    icon_color=(0.9, 0.3, 0.3, 1)
                )
                btn_delete.bind(on_release=lambda x, tid=task_id: self.delete_task(tid))
                card.add_widget(btn_delete)
                
                self.tasks_list_layout.add_widget(card)
                
        except Exception as e:
            logger.error(f"Erro ao carregar rotinas/tarefas: {e}")

    def delete_task(self, task_id):
        try:
            conn = get_connection()
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            self.load_data()
        except Exception as e:
            logger.error(f"Erro ao excluir tarefa {task_id}: {e}")

    def go_to_task_screen(self, *args):
        app = MDApp.get_running_app()
        if app and hasattr(app, 'sm'):
            # Tenta os nomes mais comuns de telas de cadastro para evitar crash
            for screen_name in ["task", "task_screen", "cadastro", "new_task"]:
                if screen_name in app.sm.screen_names:
                    app.sm.current = screen_name
                    return
            # Fallback seguro
            app.sm.current = "task"