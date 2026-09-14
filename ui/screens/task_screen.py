from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.app import MDApp

from database.repositories.task_repository import TaskRepository
from models.task_model import Task 

class TaskScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.prioridade_selecionada = "Normal"
        self.md_bg_color = MDApp.get_running_app().theme_cls.backgroundColor
        self.repo = TaskRepository() 

        # 1. Layout principal criado PRIMEIRO de tudo
        main_layout = MDBoxLayout(orientation="vertical", padding=20, spacing=20)
        
        # 2. Barra superior com o botão de voltar para a Home
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=10)
        btn_back = MDIconButton(
            icon="arrow-left",
            on_release=lambda x: setattr(MDApp.get_running_app().root, 'current', 'home')
        )
        top_bar.add_widget(btn_back)
        top_bar.add_widget(MDLabel(text="")) # Espaçador
        main_layout.add_widget(top_bar)
        
        titulo = MDLabel(text="Minhas Tarefas", halign="center", size_hint_y=None, height=40)
        main_layout.add_widget(titulo)
        
        scroll = MDScrollView()
        self.task_list_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=10)
        scroll.add_widget(self.task_list_layout)
        main_layout.add_widget(scroll)
        
        # Painel de formulário
        form_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=15)
        
        self.text_field = MDTextField(
            MDTextFieldHintText(text="Nova tarefa..."),
            mode="outlined"
        )
        form_layout.add_widget(self.text_field)
        
        self.category_field = MDTextField(
            MDTextFieldHintText(text="Categoria (Ex: Trabalho)"),
            mode="outlined"
        )
        form_layout.add_widget(self.category_field)
        
        label_prioridade = MDLabel(
            text="Selecione a Prioridade:",
            size_hint_y=None,
            height=20
        )
        form_layout.add_widget(label_prioridade)
        
        row_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=10)
        
        priority_box = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=5)
        
        self.btn_baixa = MDButton(MDButtonText(text="Baixa"), style="outlined", on_release=lambda x: self.set_priority("Baixa"))
        self.btn_normal = MDButton(MDButtonText(text="Normal"), style="tonal", on_release=lambda x: self.set_priority("Normal"))
        self.btn_alta = MDButton(MDButtonText(text="Alta"), style="outlined", on_release=lambda x: self.set_priority("Alta"))
        
        priority_box.add_widget(self.btn_baixa)
        priority_box.add_widget(self.btn_normal)
        priority_box.add_widget(self.btn_alta)
        
        row_layout.add_widget(priority_box)
        
        add_button = MDButton(
            MDButtonText(text="Adicionar"),
            style="elevated",
            on_release=self.add_new_task
        )
        row_layout.add_widget(add_button)
        
        form_layout.add_widget(row_layout)
        main_layout.add_widget(form_layout)
        
        self.add_widget(main_layout)

    def set_priority(self, prioridade):
        self.prioridade_selecionada = prioridade
        self.btn_baixa.style = "tonal" if prioridade == "Baixa" else "outlined"
        self.btn_normal.style = "tonal" if prioridade == "Normal" else "outlined"
        self.btn_alta.style = "tonal" if prioridade == "Alta" else "outlined"

    def on_enter(self):
        self.load_tasks()

    def load_tasks(self):
        self.task_list_layout.clear_widgets() 
        tarefas_do_banco = self.repo.get_all_tasks()
        
        for tarefa in tarefas_do_banco:
            linha_tarefa = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)
            
            icone = "checkbox-marked-circle" if tarefa.is_completed else "checkbox-blank-circle-outline"
            btn_status = MDIconButton(
                icon=icone,
                on_release=lambda instancia, t=tarefa: self.toggle_task(t) 
            )
            linha_tarefa.add_widget(btn_status)
            
            detalhes_texto = f"{tarefa.title}  |  [{tarefa.category}]  |  Prioridade: {tarefa.priority}"
            label_tarefa = MDLabel(text=detalhes_texto)
            linha_tarefa.add_widget(label_tarefa)
            
            btn_delete = MDIconButton(
                icon="trash-can-outline",
                on_release=lambda instancia, t=tarefa: self.delete_task(t)
            )
            linha_tarefa.add_widget(btn_delete)
            
            self.task_list_layout.add_widget(linha_tarefa)

    def add_new_task(self, instance):
        titulo = self.text_field.text.strip()
        categoria = self.category_field.text.strip()
        prioridade = self.prioridade_selecionada 
        
        if titulo != "":
            if not categoria:
                categoria = "Geral"
                
            self.text_field.text = ""
            self.category_field.text = ""
            self.set_priority("Normal")
            
            nova_tarefa = Task(title=titulo, category=categoria, priority=prioridade)
            self.repo.add_task(nova_tarefa)
            self.load_tasks()
            
    def toggle_task(self, tarefa):
        tarefa.is_completed = 0 if tarefa.is_completed else 1
        self.repo.update_task(tarefa)
        self.load_tasks()
        
    def delete_task(self, tarefa):
        self.repo.delete_task(tarefa.id)
        self.load_tasks()