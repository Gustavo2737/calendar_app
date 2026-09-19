from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.clock import Clock
from database.connection import get_connection
from core.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger("DashboardScreen")

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        header_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        header_box.add_widget(MDLabel(
            text="Atividades de Hoje", 
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
        Clock.schedule_once(self.load_data, 0.1)

    def get_time_left_str(self, is_routine, due_date, due_time, recurrence_data, now):
        try:
            if due_time is None or str(due_time).strip() == "": return ""
            t_int = int(float(str(due_time)))
            th, tm = t_int // 60, t_int % 60
        except: return ""

        if not is_routine:
            if not due_date: return ""
            try:
                target_dt = datetime.strptime(due_date, "%Y-%m-%d").replace(hour=th, minute=tm, second=0, microsecond=0)
            except: return ""
        else:
            dia_map = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sáb": 5, "dom": 6}
            if not recurrence_data: return ""
            today_idx = now.weekday()
            target_dts = []
            for d_name in dia_map:
                if d_name in recurrence_data.lower():
                    days_ahead = dia_map[d_name] - today_idx
                    if days_ahead < 0 or (days_ahead == 0 and (now.hour * 60 + now.minute) >= t_int):
                        days_ahead += 7
                    target_dts.append(now.replace(hour=th, minute=tm, second=0, microsecond=0) + timedelta(days=days_ahead))
            if not target_dts: return ""
            target_dt = min(target_dts)

        diff = target_dt - now
        if diff.total_seconds() < 0: return "⏳ Atrasado"
        days, rem = diff.days, diff.seconds
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        
        if days > 0: return f"⏳ {days}d {hours}h {minutes}min"
        elif hours > 0: return f"⏳ {hours}h {minutes}min"
        else: return f"⏳ {minutes}min"

    def load_data(self, dt=None):
        self.tasks_list_layout.clear_widgets()
        now = datetime.now()
        
        # Strings para identificar se a tarefa pertence ao dia atual
        hoje_data = now.strftime('%Y-%m-%d')
        hoje_str = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"][now.weekday()]
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, is_routine, due_date, due_time, recurrence_data, is_completed FROM tasks ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()
            
            has_tasks = False
            
            for row in rows:
                task_id, title, is_routine, due_date, due_time, recurrence_data, is_completed = row
                
                # FILTRO RIGOROSO: Pula a tarefa se não for de hoje
                if is_routine:
                    if not recurrence_data or hoje_str not in str(recurrence_data).lower():
                        continue
                else:
                    if due_date != hoje_data:
                        continue
                
                has_tasks = True
                
                time_str = "Dia Inteiro"
                if due_time is not None and str(due_time).strip() != "":
                    try:
                        t_int = int(float(str(due_time)))
                        time_str = f"{t_int//60:02d}:{t_int%60:02d}"
                    except Exception:
                        time_str = str(due_time)

                if is_routine:
                    detalhe_txt = f"Rotina: Hoje às {time_str}"
                else:
                    detalhe_txt = f"Data: Hoje às {time_str}"
                
                timer_txt = self.get_time_left_str(is_routine, due_date, due_time, recurrence_data, now)

                card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(95), padding=dp(15), spacing=dp(15), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
                
                info_box = MDBoxLayout(orientation="vertical", spacing=dp(2))
                info_box.add_widget(MDLabel(text=title, bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1)))
                info_box.add_widget(MDLabel(text=detalhe_txt, theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), role="small"))
                
                if timer_txt:
                    info_box.add_widget(MDLabel(text=timer_txt, theme_text_color="Custom", text_color=(0, 0.9, 0.46, 1), bold=True, role="small"))
                
                card.add_widget(info_box)
                
                btn_delete = MDIconButton(icon="delete-outline", theme_icon_color="Custom", icon_color=(0.9, 0.3, 0.3, 1))
                btn_delete.bind(on_release=lambda x, tid=task_id: self.delete_task(tid))
                card.add_widget(btn_delete)
                
                self.tasks_list_layout.add_widget(card)
                
            if not has_tasks:
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(80), padding=dp(20), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
                empty_card.add_widget(MDLabel(text="Você não possui atividades para hoje! 🎉", halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                self.tasks_list_layout.add_widget(empty_card)
                
        except Exception as e:
            logger.error(f"Erro ao carregar rotinas/tarefas: {e}")

    def delete_task(self, task_id):
        try:
            conn = get_connection()
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            Clock.schedule_once(self.load_data, 0)
        except Exception as e:
            logger.error(f"Erro ao excluir tarefa {task_id}: {e}")

    def go_to_task_screen(self, *args):
        app = MDApp.get_running_app()
        if app and hasattr(app, 'sm'):
            for screen_name in ["task", "task_screen", "cadastro", "new_task"]:
                if screen_name in app.sm.screen_names:
                    app.sm.current = screen_name
                    return
            app.sm.current = "task"