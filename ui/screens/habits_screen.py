from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.metrics import dp
from kivy.clock import Clock
from database.connection import get_connection
from core.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger("HabitsScreen")

class HabitsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edit_dialog = None
        self.current_edit_id = None
        
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.07, 1))
        
        # Cabeçalho
        layout.add_widget(MDLabel(
            text="Rastreador de Hábitos", 
            font_style="Headline", 
            bold=True, 
            size_hint_y=None, 
            height=dp(40), 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1)
        ))
        
        # Painel de Cadastro com altura correta (dp(190)) e frases explicativas fixas acima de cada campo
        form_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(190), padding=dp(15), spacing=dp(10), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
        
        # 1. Campo Nome do Hábito com Rótulo Fixo Acima
        name_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(4))
        name_box.add_widget(MDLabel(text="📝 Nome do Hábito (ex: Ler 10 páginas, Beber água):", theme_text_color="Custom", text_color=(0.9, 0.9, 0.9, 1), role="small", size_hint_y=None, height=dp(20)))
        self.habit_input = MDTextField(mode="outlined", size_hint_y=None, height=dp(46))
        name_box.add_widget(self.habit_input)
        form_card.add_widget(name_box)
        
        # 2. Campo Categoria com Rótulo Fixo Acima
        cat_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(4))
        cat_box.add_widget(MDLabel(text="🏷️ Categoria ou Meta (ex: Estudos, Saúde, Fitness):", theme_text_color="Custom", text_color=(0.9, 0.9, 0.9, 1), role="small", size_hint_y=None, height=dp(20)))
        self.category_input = MDTextField(mode="outlined", size_hint_y=None, height=dp(46))
        cat_box.add_widget(self.category_input)
        form_card.add_widget(cat_box)
        
        layout.add_widget(form_card)
        
        btn_add = MDButton(
            MDButtonText(text="Adicionar Hábito"), 
            style="filled", 
            md_bg_color=(0, 0.9, 0.46, 1),
            size_hint_y=None,
            height=dp(45)
        )
        btn_add.bind(on_release=self.add_habit)
        layout.add_widget(btn_add)
        
        # Lista de Hábitos
        scroll = MDScrollView()
        self.habits_list_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12))
        scroll.add_widget(self.habits_list_layout)
        
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self, *args):
        Clock.schedule_once(self.load_habits, 0.1)

    def check_and_migrate_db(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS habits 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, streak INTEGER, last_completed TEXT)''')
        cursor.execute("PRAGMA table_info(habits)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'category' not in columns:
            cursor.execute("ALTER TABLE habits ADD COLUMN category TEXT DEFAULT 'Geral'")
        if 'streak' not in columns:
            cursor.execute("ALTER TABLE habits ADD COLUMN streak INTEGER DEFAULT 0")
        if 'last_completed' not in columns:
            cursor.execute("ALTER TABLE habits ADD COLUMN last_completed TEXT")

    def load_habits(self, dt=None):
        self.habits_list_layout.clear_widgets()
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            self.check_and_migrate_db(cursor)
            conn.commit()
            
            cursor.execute("SELECT id, name, category, streak, last_completed FROM habits ORDER BY id DESC")
            rows = cursor.fetchall()
            
            if not rows:
                empty_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(80), padding=dp(20), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
                empty_card.add_widget(MDLabel(text="Nenhum hábito cadastrado. Comece agora!", halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                self.habits_list_layout.add_widget(empty_card)
                conn.close()
                return

            for row in rows:
                habit_id, name, category, streak, last_completed = row
                
                if not category:
                    category = "Geral"
                
                if last_completed and last_completed != today_str and last_completed != yesterday_str:
                    streak = 0
                    cursor.execute("UPDATE habits SET streak = 0 WHERE id = ?", (habit_id,))
                    conn.commit()

                is_completed_today = (last_completed == today_str)

                card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(95), padding=dp(15), spacing=dp(10), md_bg_color=(0.12, 0.12, 0.12, 1), radius=[dp(12)])
                
                info_box = MDBoxLayout(orientation="vertical", spacing=dp(3))
                info_box.add_widget(MDLabel(text=name, bold=True, theme_text_color="Custom", text_color=(1, 1, 1, 1) if not is_completed_today else (0.6, 0.6, 0.6, 1)))
                info_box.add_widget(MDLabel(text=f"Categoria: {category}", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), role="small"))
                
                streak_text = f"🔥 Sequência: {streak} dias" if streak > 0 else "Inicie sua sequência hoje!"
                streak_color = (0, 0.9, 0.46, 1) if streak > 0 else (0.6, 0.6, 0.6, 1)
                info_box.add_widget(MDLabel(text=streak_text, theme_text_color="Custom", text_color=streak_color, role="small"))
                
                card.add_widget(info_box)
                
                actions_box = MDBoxLayout(orientation="horizontal", adaptive_width=True, spacing=dp(5), pos_hint={"center_y": 0.5})
                
                btn_done = MDIconButton(
                    icon="check-circle" if is_completed_today else "check-circle-outline",
                    theme_icon_color="Custom",
                    icon_color=(0, 0.9, 0.46, 1) if is_completed_today else (0.7, 0.7, 0.7, 1)
                )
                if not is_completed_today:
                    btn_done.bind(on_release=lambda x, hid=habit_id, s=streak: self.complete_habit(hid, s))
                
                btn_edit = MDIconButton(icon="pencil-outline", theme_icon_color="Custom", icon_color=(0.7, 0.7, 0.7, 1))
                btn_edit.bind(on_release=lambda x, hid=habit_id, n=name, c=category: self.show_edit_dialog(hid, n, c))
                
                btn_delete = MDIconButton(icon="delete-outline", theme_icon_color="Custom", icon_color=(0.9, 0.3, 0.3, 1))
                btn_delete.bind(on_release=lambda x, hid=habit_id: self.delete_habit(hid))
                
                actions_box.add_widget(btn_done)
                actions_box.add_widget(btn_edit)
                actions_box.add_widget(btn_delete)
                
                card.add_widget(actions_box)
                self.habits_list_layout.add_widget(card)
                
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao carregar hábitos: {e}")

    def add_habit(self, *args):
        name = self.habit_input.text.strip()
        category = self.category_input.text.strip()
        if not name:
            return
        if not category:
            category = "Geral"
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            self.check_and_migrate_db(cursor)
            cursor.execute("INSERT INTO habits (name, category, streak) VALUES (?, ?, 0)", (name, category))
            conn.commit()
            conn.close()
            
            self.habit_input.text = ""
            self.category_input.text = ""
            Clock.schedule_once(self.load_habits, 0.05)
        except Exception as e:
            logger.error(f"Erro ao adicionar hábito: {e}")

    def complete_habit(self, habit_id, current_streak):
        today_str = datetime.now().strftime("%Y-%m-%d")
        new_streak = current_streak + 1
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE habits SET streak = ?, last_completed = ? WHERE id = ?", (new_streak, today_str, habit_id))
            conn.commit()
            conn.close()
            Clock.schedule_once(self.load_habits, 0.05)
        except Exception as e:
            logger.error(f"Erro ao concluir hábito: {e}")

    def delete_habit(self, habit_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            conn.commit()
            conn.close()
            Clock.schedule_once(self.load_habits, 0.05)
        except Exception as e:
            logger.error(f"Erro ao deletar hábito: {e}")

    def show_edit_dialog(self, habit_id, current_name, current_category):
        self.current_edit_id = habit_id
        
        content_box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(120))
        self.edit_input = MDTextField(text=current_name, mode="outlined", hint_text="Nome do Hábito")
        self.edit_category = MDTextField(text=current_category, mode="outlined", hint_text="Categoria")
        content_box.add_widget(self.edit_input)
        content_box.add_widget(self.edit_category)
        
        self.edit_dialog = MDDialog(
            MDDialogHeadlineText(text="Editar Hábito", halign="left"),
            MDDialogContentContainer(content_box, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancelar"), style="text", on_release=self.close_edit_dialog),
                MDButton(MDButtonText(text="Salvar"), style="filled", md_bg_color=(0, 0.9, 0.46, 1), on_release=self.save_edit_habit),
                spacing="8dp"
            )
        )
        self.edit_dialog.open()

    def close_edit_dialog(self, *args):
        if self.edit_dialog:
            self.edit_dialog.dismiss()

    def save_edit_habit(self, *args):
        new_name = self.edit_input.text.strip()
        new_category = self.edit_category.text.strip()
        if not new_category:
            new_category = "Geral"
            
        if new_name and self.current_edit_id:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE habits SET name = ?, category = ? WHERE id = ?", (new_name, new_category, self.current_edit_id))
                conn.commit()
                conn.close()
                Clock.schedule_once(self.load_habits, 0.05)
            except Exception as e:
                logger.error(f"Erro ao editar hábito: {e}")
        self.close_edit_dialog()