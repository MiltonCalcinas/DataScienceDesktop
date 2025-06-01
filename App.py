import customtkinter as ctk
import sqlalchemy
import mysql.connector
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage 
import pandas as pd
import numpy as np
from frame_movil import MovableResizableFrame
import requests
import json
import config
import colores
import os
from PIL import Image, ImageTk
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from login import Login
import operator
import pandas.api.types as ptypes
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import  confusion_matrix, classification_report,roc_curve, auc, r2_score,mean_squared_error,root_mean_squared_error,mean_absolute_error,accuracy_score,f1_score,roc_auc_score,precision_score
import tkinter.font as tkFont
import csv
import colorsys 

def sesion_guardada():
    print("---Verificndo auth_token---")
    if os.path.exists("session.json"):
        print("Tiene sesion guardada")
        with open("session.json", "r") as f:
            session = json.load(f)

        token = session.get("auth_token")
        print("Tocken auth se sesion anterior:",token)
        if token:
            # Validamos el token con el backend
            print("validando el token")
            res = requests.get(config.VIEW_VERIFY_TOKEN, headers={
                "Authorization": f"Token {token}"
            })

            if res.status_code == 200:
                print("--- Servidor: ",res.json())
                print("Token validado(✅)")
                return True  # El token sigue siendo válido
    print("No tiene sesion guardada ")
    return False


def center_window(ventana):
    ventana.update_idletasks()  # Asegura que se obtienen dimensiones reales
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = 150
    ventana.geometry(f"+{x}+{y}")





def saving_config(modo,key="COLOR_MODE"):
    CONFIG_FILE = r"config.json"
    # Leer contenido actual
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[key] = modo

    # Guardar el archivo actualizado
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_setting(key="COLOR_MODE"):
    CONFIG_FILE = r"config.json"
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get(key, "DRACULA")
    return None

class App(ctk.CTk):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        
        self.mode=load_setting(key="COLOR_MODE")
        self.color = colores.ColorDataFrame().get_colores(self.mode)
        self.configure(fg_color=self.color.COLOR_FONDO_APP)
        self.model_info_list = []
        self.contador_modelos = 0
        self.url_csv = None
        self.url_excel = None
        self.df = None
        self.y = None
        self.tipo_problema = None
        self.result_statistics = []
        self.graph_widgets = {}
        self.table_name_list = []
        self.load_font_system() 
        self.crear_interfaz()
        
        # Variables de control
        self.notas_guardadas = {}  # Diccionario para almacenar notas por número
        
        # Inicia sesión
        sesion = sesion_guardada()
        if sesion:
            with open("session.json", "r") as f:
                s = json.load(f)
            self.auth_token = s.get("auth_token")
            self.get_table_name_list()
            self.try_load_data_from_mysql()
        else:
            print("Abriendo login")
            login = Login(self,self.mode)  # le pasas la ventana padre
            login.grab_set()     # hace modal (no permite usar otras ventanas)
            self.wait_window(login)  # bloquea hasta que login se cierre
            
            if not hasattr(self,'auth_token'):
                self.destroy()
                return  
            
            if not login.is_new_user:
                self.get_table_name_list()
                self.try_load_data_from_mysql()
            else:
                self.create_pop_load_data()
        
        
        self.mainloop()
               
            
    def get_table_name_list(self):
        if hasattr(self, 'auth_token'):
            print("Sí tiene el atributo 'auth_token'")
        else:
            print("No tiene el atributo 'auth_token'")
            return
        

        headers = {
            "Authorization": f"Token {self.auth_token}"
        }

        res = requests.get(config.VIEW_TABLE_NAME_LIST, headers=headers)

        if res.status_code == 200:
            tablas = res.json()
            for tabla in tablas:
                print(f"Nombre: {tabla['table_name']}, BD: {tabla['db_name']}, Fecha: {tabla['created_at']}")
                self.table_name_list.append(tabla['table_name'])
                self.db_name= tabla["db_name"]

        else:
            print("Error al obtener tablas:", res.status_code)
       


    def try_load_data_from_mysql(self):
        if hasattr(self, 'auth_token'):
            print("Sí tiene el atributo 'auth_token'")
        else:
            print("No tiene el atributo 'auth_token'")
            return
        print("Token en App: ",self.auth_token)
        headers = {
            "Authorization": f"Token {self.auth_token}"
        }
        
        res = requests.get(
            url=config.VIEW_LAST_TABLE,
            headers=headers
        )
        print(config.VIEW_LAST_TABLE)
        if res.status_code == 200:
            print("---Servidor:", res.json())

            self.table_name = res.json()["table_name"]
            self.db_name = res.json()["db_name"]
            print("--Conectandose a mysql para obtener la tabla")
            engine = config.VAR_CONEXION + self.db_name
            try:
                self.df = pd.read_sql(f"SELECT * FROM {self.table_name}", engine)
                self.show_tree_viewport()
            
            except sqlalchemy.exc.OperationalError as e:
                print("Error al conectar con la base de datos o al consultar la tabla:")
                print(str(e))
                self.create_pop_load_data()  # Muestra ventana para cargar datos manualmente

            except Exception as e:
                print("Ocurrió un error inesperado:")
                print(str(e))
                self.create_pop_load_data()

        else:
            print(res.json())
            print("No hay tabla guardada en mysql")    
            self.create_pop_load_data()

    def create_pop_load_data(self):
        pop_load_data = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        pop_load_data.resizable(False, False)

        # Mostrar en primer  plano
        pop_load_data.transient(self)
        pop_load_data.lift()
        pop_load_data.focus_force()
        pop_load_data.grab_set()
        pop_load_data.update()

        #centrar ventana
        center_window(pop_load_data)
        
        ctk.CTkLabel(pop_load_data,text="Selecciona la Fuente")
        options = ["Archivo CSV",
                    "Archivo Excel",
                    "MySQL",
                    "PostgreSQL",
                    "SQLServer"]
        btn_list =[]

        for i, tipo in enumerate(options):
            btn = ctk.CTkButton(pop_load_data,
                        text=tipo,
                        command=lambda t=tipo: self.__ventana_conexion(t,pop_load_data),
                        fg_color=self.color.COLOR_RELLENO_WIDGET
                        )
            btn.grid(row=i+1, column=0, padx=20, pady=10)
            btn_list.append(btn)


    def crear_interfaz(self):
        self.title("Data Science")
        self.geometry("750x600")
        self.minsize(750,600)

        self.__style_for_tabla()

        self.crear_sidebar()
        #----             añadir penstañas a la interfaz       ----#
        self.crear_notebook()
        self.crear_procesar()
        self.crear_entrenamiento()
        self.crear_dashboard()

    def crear_sidebar(self):
        menu = ctk.CTkFrame(self)
        menu.pack(side="top",fill="x",expand=False,padx=10)
        menu.configure(fg_color=self.color.COLOR_FONDO_APP)
    
        img_task = ctk.CTkImage(light_image=Image.open(r"iconos\ico_task.png"),size=(20,20))
        btn_task= ctk.CTkButton(menu,
                                image=img_task,
                                text="",
                                width=20,
                                command=self.__form_task,
                                fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_task.grid(row=0,column=0,padx=(0,10))

        img_setting = ctk.CTkImage(light_image=Image.open(r"iconos\ico_setting.png"),size=(20,20))
        btn_setting= ctk.CTkButton(menu,
                                image=img_setting,
                                text="",
                                width=20,
                                fg_color=self.color.COLOR_RELLENO_WIDGET,
                                command=self.__form_setting)
        btn_setting.grid(row=0,column=1)


    def crear_notebook(self):
        """         CON ESTE CODIGO CREA EL NOTEBOOK Y LAS PESTAÑAS (LUEGO AÑADO LOS OBJETOS,ETC)        """
        self.notebook = ctk.CTkTabview(self,
                                       border_color=self.color.COLOR_BORDE_WIDGET,
                                       border_width=3)
        self.notebook.pack(fill="both",expand=True,padx=10,pady=10)
        self.notebook.configure(fg_color=self.color.COLOR_FONDO_APP)

        self.tab1 = self.notebook.add("Procesar")
        self.tab2 = self.notebook.add("Entrenamiento")
        self.tab3 = self.notebook.add("Dashboard")


    def __filtrar(self):
        self.pop_filter = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        self.pop_filter.title("Filtros")
        self.pop_filter.resizable(False, False) 
        self.pop_filter.transient(self)
        self.pop_filter.lift()
        self.pop_filter.focus_force()
        self.pop_filter.grab_set()
        self.pop_filter.update()
        center_window(self.pop_filter)

        self.filter_row = 0
        self.filter_widgets = []  # para almacenar widgets por fila

        self.scroll_frame = ctk.CTkScrollableFrame(self.pop_filter, width=540, height=300)
        self.scroll_frame.grid(row=0, column=0,columnspan=3, padx=10, pady=10)
        self.scroll_frame.configure(fg_color=self.color.COLOR_FONDO_APP)

        self.add_variable_filter()

        ctk.CTkButton(self.pop_filter, text="+", width=50,
                    command=self.add_variable_filter,
                    fg_color=self.color.COLOR_RELLENO_WIDGET).grid(row=1, column=0, padx=(0, 20), pady=(0, 10))

        ctk.CTkButton(self.pop_filter, text="Filtrar", command=self.exe_filter,
                      fg_color=self.color.COLOR_RELLENO_WIDGET).grid(row=2, column=0, padx=(0, 20), pady=(0, 20))
        
        ctk.CTkButton(self.pop_filter, text="Filtrar y Guardar", command=lambda :self.exe_filter(save=True),
                      fg_color=self.color.COLOR_RELLENO_WIDGET).grid(row=2, column=1, padx=(0, 20), pady=(0, 20))
        
        ctk.CTkButton(self.pop_filter, text="Descartar Filtros", command=self.descartar_filtro,
                      fg_color=self.color.COLOR_RELLENO_WIDGET).grid(row=2, column=2, padx=(0, 20), pady=(0, 20))
    
    def descartar_filtro(self):
        self.pop_filter.destroy()
        self.show_tree_viewport()


    def add_variable_filter(self):
        fila = self.filter_row

        # Combobox para seleccionar columna
        cbo_columna = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns),button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_columna.grid(row=fila, column=0, padx=20, pady=(10 if fila == 0 else 5))

        # Combobox para seleccionar operador (se actualizará dinámicamente)
        cbo_operador = ctk.CTkComboBox(self.scroll_frame, values=["="],button_color=self.color.COLOR_RELLENO_WIDGET)  # placeholder inicial
        cbo_operador.grid(row=fila, column=1, padx=20, pady=(10 if fila == 0 else 5))

        # Entry para escribir el valor
        entry_valor = ctk.CTkEntry(self.scroll_frame)
        entry_valor.grid(row=fila, column=2, padx=20, pady=(10 if fila == 0 else 5))

        # Evento al cambiar columna → actualiza operadores disponibles
        def actualizar_operadores(opcion):
            tipo = self.df[opcion].dtype
            if pd.api.types.is_numeric_dtype(tipo):
                operadores = [">", "<", "==", ">=", "<=","No NaN"]
            elif self.df[opcion].dtype == 'object':
                operadores = ["==", "!=", "contiene","comienza por", "termina por","está en","No NaN","No vacios"]
            elif ptypes.is_datetime64_any_dtype(self.df[opcion]):
                operadores = [">", "<", "==", ">=", "<=","por día","por mes","por año","No NaT"]
            
            cbo_operador.configure(values=operadores,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_operador.set(operadores[0])  # seleccionar por defecto el primero

        cbo_columna.configure(command=actualizar_operadores,button_color=self.color.COLOR_RELLENO_WIDGET)

        # Agregamos widgets a la lista de control
        self.filter_widgets.append((cbo_columna, cbo_operador, entry_valor))
        self.filter_row += 1


    def exe_filter(self,save=False):

        operadores_num = {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '==': operator.eq,
            '!=': operator.ne,
        }
        self.df_filtrado = self.df.copy()
        for cbo_col, cbo_op, entry_val in self.filter_widgets:
            col = cbo_col.get()
            op = cbo_op.get()
            val = entry_val.get()

            if col not in self.df_filtrado.columns:
                messagebox.showwarning("Columna No existente",f"La columna {col}no existe. Filtro Cancelado")
                print("Columna No existente",f"La columna {col}no existe. Filtro Cancelado")
                return
            
            
            if col == "" or op == "" or val == "":
                    continue  # saltar si está vacío
            tipo = self.df_filtrado[col].dtype
            if pd.api.types.is_numeric_dtype(tipo):
                try:
                    val_num = float(val)
                    if op == "No NaN":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].notna()] 
                    elif op in operadores_num:
                        
                        self.df_filtrado = self.df_filtrado[operadores_num[op](self.df_filtrado[col], val_num)]
                    else:
                        messagebox.showerror("Operador No valido",f"Se ha seleccionado {op} que no es valido para{col}. Filtro Cancelado")
                        print("Operador No valido",f"Se ha seleccionado {op} que no es valido para{col}. Filtro Cancelado")
                        return
                except ValueError:
                    messagebox.showerror("Error", f"'{val}' no es un número válido para la columna '{col}'.Filtro Cancelado")
                    print("Error", f"'{val}' no es un número válido para la columna '{col}'.Filtro Cancelado")
                    return
            elif self.df_filtrado[col].dtype == 'object':
                try:
                    if op == "==":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col]== val]
                    elif op == "!=":                        
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col]!= val]
                    elif op == "comienza por":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].str.startswith(val)]
                    elif op == "termina por":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].str.endswith(val)]
                    elif op == "contiene":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].str.contains(val)]
                    elif op == "está en":
                        list_val = [ valor.replace(" ","") for valor in val.split(",")]
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].isin(list_val)]
                    elif op == "No NaN": 
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].notna()] 
                    elif op == "No vacios":
                        self.df_filtrado = self.df_filtrado[ self.df_filtrado[col] != ""] 
                    else:
                        messagebox.showerror("Operador No valido",f"Se ha seleccionado {op} que no es valido para{col}. Filtro Cancelado")
                        print("Operador No valido",f"Se ha seleccionado {op} que no es valido para{col}. Filtro Cancelado")
                        return
                except Exception as ex:
                    messagebox.showerror("Error",f"Eror al filtrar columna Object.{col} .Filtro Cancelado")
                    print("Error",f"Eror al filtrar columna Object.{col}")
                    return
            elif ptypes.is_datetime64_any_dtype(self.df_filtrado[col]):
                try:
                    if op == "==":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col]==  pd.to_datetime(val)]
                    elif op == "!=":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col]!=pd.to_datetime(val)]
                    elif op == "<" or "<=" or ">" or ">=":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col]< val]
                    elif op == "por día":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].dt.day == int(val)]
                    elif op == "por mes":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].dt.month == int(val)]
                    elif op == "por año":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].dt.year == int(val)]
                    elif op == "No NaT":
                        self.df_filtrado = self.df_filtrado[self.df_filtrado[col].notna()]
                    else:
                        messagebox.showerror("Operador No valido",f"Se ha seleccionado {op} que no es valido para{col}. Filtro Cancelado")
                        print("Operador No valido",f"Se ha seleccionado {op} que no es valido para{col}. Filtro Cancelado")
                        return 
                except Exception as ex:
                    messagebox.showerror("Error",f"Eror al filtrar columna Datetime.{col}.Filtro Cancelado")
                    print("Error",f"Eror al filtrar columna Object.{col}.Filtro Cancelado")
                    return
            else:
                messagebox.showinfo("Tipo","El tipo de la columna no es numérica,object u datetime. Filtro Cancelado",col)
                print("Tipo","El tipo de la columna no es numérica,object u datetime. Filtro Cancelado")
                return
        self.show_tree_viewport(copia=True)
        msg_save = ""
        if save:
            self.df = self.df_filtrado
            msg_save = " y guardado."

        self.pop_filter.destroy()
        messagebox.showinfo("Filtrado",f"Filtrado {msg_save} correctamente")

    def top_level_params_ANO(self,metodo):
        
        if metodo == "-- Ninguna": 
            self.cbo_ANO.set("A. No Superivosado")
            return
        top = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        top.title(f"Configurar {metodo}")
        top.geometry("400x400")
        top.resizable(False, False)
        # centrar venana
        top.update()
        center_window(top)
        # Poner en primer plano con foco
        top.transient(self)
        top.lift()
        top.focus_force()
        top.grab_set()

        # Selección de columnas
        lbl_cols = ctk.CTkLabel(top, text="Selecciona columnas:",text_color=self.color.COLOR_LETRA_NORMAL)
        lbl_cols.pack(pady=5)

        columnas = list(self.df.head(10).select_dtypes(include="number").columns)
        selected_cols = []

        for col in columnas:
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(top, text=col, variable=var,text_color=self.color.COLOR_LETRA_NORMAL)
            chk.pack(anchor="w", padx=10,pady=10)
            selected_cols.append((col, var))

        n_clusters_entry = None
        n_components_entry = None
        # Hiperparámetros
        print(metodo)
        if metodo == "KMeans":
            ctk.CTkLabel(top, text="Número de clusters:",text_color=self.color.COLOR_LETRA_NORMAL).pack(pady=5)
            n_clusters_entry = ctk.CTkEntry(top, placeholder_text="Ej. 3")
            n_clusters_entry.pack(pady=5)

        elif metodo == "PCA":
            ctk.CTkLabel(top, text="Número de componentes:").pack(pady=5)
            n_components_entry = ctk.CTkEntry(top, placeholder_text="Ej. 2")
            n_components_entry.pack(pady=5)

        # Botón de aplicar
        def aplicar():
            columnas_seleccionadas = [col for col, var in selected_cols if var.get()]
            if metodo == "KMeans":
                n_clusters = int(n_clusters_entry.get())
                print(f"KMeans con columnas {columnas_seleccionadas} y {n_clusters} clusters")
                
                # Llama aquí a tu función de KMeans con esos parámetros
                df_select = self.df[columnas_seleccionadas]
                modelo_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                self.df['cluster'] = modelo_kmeans.fit_predict(df_select)
                print("Clustering completado. Nuevas etiquetas guardadas en 'cluster'.")
                

            elif metodo == "PCA":
                n_components = int(n_components_entry.get())
                print(f"PCA con columnas {columnas_seleccionadas} y {n_components} componentes")
                # Llama aquí a tu función de PCA con esos parámetros
                df_select = self.df[columnas_seleccionadas]
                pca = PCA(n_components=n_components)
                componentes = pca.fit_transform(df_select)

                # Guardar cada componente como nueva columna
                for i in range(n_components):
                    self.df[f'COMP_{i+1}'] = componentes[:, i]

                print(f"PCA completado. Se añadieron {n_components} componentes como columnas.")
            self.show_tree_viewport()
            self.cbo_ANO.set("A. No Superivosado")
            top.destroy()

        ctk.CTkButton(top, text="Aplicar", command=aplicar).pack(pady=10)

    def __convert_data_type(self):
        self.filas_conversion = []
        
        values=[
            "Texto a Número (int)",
            "Texto a Número (float)",
            "Texto a Fecha (datatime)",
            "Texto a Categoría",
            "Número a Texto",
            "Fecha a Texto",
            "Número (float) a Número (int)",
            "Número (int) a Número (float)",
        ]
        self.pop_conversion = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        self.pop_conversion.title("Convertir Tipo de Datos")
        self.pop_conversion.resizable(False, False)
        self.pop_conversion.transient(self)
        self.pop_conversion.lift()
        self.pop_conversion.focus_force()
        self.pop_conversion.grab_set()

        #centrar ventana
        self.pop_conversion.update()
        center_window(self.pop_conversion)

        # Crear un marco desplazable
        self.scroll_frame = ctk.CTkScrollableFrame(self.pop_conversion, width=485, height=300)
        self.scroll_frame.configure(fg_color=self.color.COLOR_FONDO_APP)
        self.scroll_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Guardar una lista para agregar nuevas filas dinámicamente
        self.conversion_row = 1

        # Fila inicial
        variable_conversion = ctk.CTkComboBox(self.scroll_frame, values=values,button_color=self.color.COLOR_RELLENO_WIDGET)
        variable_conversion.grid(row=0, column=0, padx=(20, 20), pady=(20, 20))

        variable_column = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns),button_color=self.color.COLOR_RELLENO_WIDGET)
        variable_column.grid(row=0, column=1, padx=(0, 20), pady=(20, 20))

        if self.mode == "LIGHT":
            color_texto=self.color.COLOR_LETRA_NORMAL
        else:
            color_texto=self.color.COLOR_LETRA_BOTON
        chk_column = ctk.CTkCheckBox(self.scroll_frame, text="Misma columna", border_color=self.color.COLOR_BORDE_WIDGET, text_color=color_texto)
        chk_column.grid(row=0, column=2, padx=(0, 20), pady=(20, 20))
        
        # Guardar los widgets en una lista
        self.filas_conversion.append((variable_conversion, variable_column, chk_column))
        
        self.btn_add_variables = ctk.CTkButton(self.pop_conversion,
                                          text="+",
                                          width=50,
                                          command=lambda:self.add_variable_conversion(values),
                                          fg_color=self.color.COLOR_RELLENO_WIDGET
                                          )
        self.btn_add_variables.grid(row=1,column=0,pady=(0,10))

        self.btn_conversion = ctk.CTkButton(self.pop_conversion,
                                  text="Convertir Tipo",
                                  command=self.__conversion,
                                  fg_color=self.color.COLOR_RELLENO_WIDGET
                                  )
        self.btn_conversion.grid(row=1,column=1,pady=(0,10))

    def add_variable_conversion(self,values):
        fila = self.conversion_row

        variable_conversion = ctk.CTkComboBox(self.scroll_frame, values=values,button_color=self.color.COLOR_RELLENO_WIDGET)
        variable_conversion.grid(row=fila, column=0, padx=(20, 20), pady=(0, 20))
        variable_column = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns),button_color=self.color.COLOR_RELLENO_WIDGET)
        variable_column.grid(row=fila, column=1, padx=(0, 20), pady=(0, 20))
        chk_column = ctk.CTkCheckBox(self.scroll_frame, text="Misma columna",fg_color=self.color.COLOR_RELLENO_WIDGET)
        chk_column.grid(row=fila, column=2, padx=(0, 20), pady=(0, 20))

        # Guardar los widgets en una lista
        self.filas_conversion.append((variable_conversion, variable_column, chk_column))

        self.conversion_row += 1
    def __conversion(self):
      
        for i, (variable_conversion, variable_column, chk_column) in enumerate(self.filas_conversion):
            tipo_conversion = variable_conversion.get()
            columna = variable_column.get()
            usar_misma = chk_column.get()
            print(f"Fila {i+1}:")
            print(f"  Tipo conversión: {tipo_conversion}")
            print(f"  Columna: {columna}")
            print(f"  ¿Misma columna?: {'Sí' if usar_misma else 'No'}")
            try:
                nueva_columna = columna if usar_misma else f"{columna}_convertido"

                if tipo_conversion == "Texto a Número (int)":
                    self.df[nueva_columna] = pd.to_numeric(self.df[columna], errors="coerce").astype("Int64")
                elif tipo_conversion == "Texto a Número (float)":
                    self.df[nueva_columna] = pd.to_numeric(self.df[columna], errors="coerce")
                elif tipo_conversion == "Texto a Fecha (datatime)":
                    self.df[nueva_columna] = pd.to_datetime(self.df[columna], errors="coerce")
                elif tipo_conversion == "Texto a Categoría":
                    self.df[nueva_columna] = self.df[columna].astype("category")
                elif tipo_conversion == "Número a Texto":
                    self.df[nueva_columna] = self.df[columna].astype(str)
                elif tipo_conversion == "Fecha a Texto":
                    self.df[nueva_columna] = self.df[columna].astype(str)
                elif tipo_conversion == "Número (float) a Número (int)":
                    self.df[nueva_columna] = self.df[columna].astype("Int64")
                elif tipo_conversion == "Número (int) a Número (float)":
                    self.df[nueva_columna] = self.df[columna].astype(float)
                else:
                    messagebox.showwarning("Conversión no implementada", f"La conversión '{tipo_conversion}' no está implementada.")
                    print(f"⚠ Conversión no implementada: {tipo_conversion}")
                    continue

                print(f"✔ Conversión realizada: {columna} → {nueva_columna} ({tipo_conversion})")

            except Exception as e:
                print(f"❌ Error al convertir la columna '{columna}': {e}")
                messagebox.showerror("Error de conversión", f"No se pudo convertir la columna '{columna}':\n{e}")

        self.show_tree_viewport()


    def __calculate_statistics(self):
        values=[
                "media",
                "mediana",
                "desviacion_estandar",
                "varianza",
                "minimo",
                "maximo"
            ]
        self.popup_statistics = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        self.popup_statistics.title("Estadísticas")
        self.popup_statistics.resizable(False,False)

        # centrar ventana
        self.popup_statistics.update()
        center_window(self.popup_statistics)

        self.popup_statistics.transient(self)
        self.popup_statistics.lift()
        self.popup_statistics.focus_force()
        self.popup_statistics.grab_set()

        # Guardar una lista para agregar nuevas filas dinámicamente
        self.statistics_row = 1
        
        self.statistics_combos = []  # ← Aquí guardaremos los ComboBox        

        # Crear un marco desplazable
        self.scroll_frame = ctk.CTkScrollableFrame(self.popup_statistics, width=340, height=300)
        self.scroll_frame.configure(fg_color=self.color.COLOR_FONDO_APP)
        self.scroll_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Añadir el primer par de ComboBox con referencias
        cbo_stat = ctk.CTkComboBox(self.scroll_frame, values=values,button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_stat.grid(row=0, column=0, padx=(20, 20), pady=(20, 20))

        cbo_var = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns),button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_var.grid(row=0, column=1, padx=(0, 20), pady=(20, 20))

        self.statistics_combos.append((cbo_stat, cbo_var))
        
        self.btn_add_variables = ctk.CTkButton(self.popup_statistics,
                                          text="+",
                                          width=50,
                                          command=lambda:self.add_variable_statistics(values),fg_color=self.color.COLOR_RELLENO_WIDGET)
        self.btn_add_variables.grid(row=2,column=0,pady=(0,10))

        self.btn_statistics = ctk.CTkButton(self.popup_statistics,
                                  text="Calcular",
                                  command=self.__statistics,fg_color=self.color.COLOR_RELLENO_WIDGET)
        self.btn_statistics.grid(row=2,column=1,pady=(0,10))

    def add_variable_statistics(self, values):
        fila = self.statistics_row
        
        cbo_stat = ctk.CTkComboBox(self.scroll_frame, values=values,button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_stat.grid(row=fila, column=0, padx=(20, 20), pady=(0, 20))

        cbo_var = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns),button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_var.grid(row=fila, column=1, padx=(0, 20), pady=(0, 20))

        self.statistics_combos.append((cbo_stat, cbo_var))  # ← Guardamos los nuevos ComboBox
        
        self.statistics_row += 1

    def __statistics(self):

        statistics = {
            "media": np.mean,
            "mediana": np.median,
            "desviacion_estandar": np.std,
            "varianza": np.var,
            "minimo": np.min,
            "maximo": np.max
        }

        resultados = []
        #self.result_statistics.clear()  # Limpia resultados anteriores

        for cbo_stat, cbo_var in self.statistics_combos:
            stat_name = cbo_stat.get()
            var_name = cbo_var.get()

            if stat_name and var_name:
                try:
                    funcion = statistics[stat_name]
                    valor = funcion(self.df[var_name])
                    resultado = {
                        "variable": var_name,
                        "estadistica": stat_name,
                        "valor": float(valor)
                    }
                    self.result_statistics.append(resultado)
                    resultados.append(f"{stat_name.title()} de '{var_name}': {valor:.4f}")

                except Exception as e:
                    resultados.append(f"Error con '{var_name}': {str(e)}")
                
                    

        # Mostrar resultados en un nuevo popup
        self.__show_result_popup(resultados)

    def __show_result_popup(self, resultados):
        self.popup_statistics.destroy()
        popup_resultados = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        popup_resultados.title("Resultados de Estadísticas")
        popup_resultados.geometry("400x300")

        #centarr ventana
        popup_resultados.update()
        center_window(popup_resultados)

        popup_resultados.transient(self)
        popup_resultados.lift()
        popup_resultados.focus_force()
        

        txt_resultados = ctk.CTkTextbox(popup_resultados, wrap="word")
        txt_resultados.pack(expand=True, fill="both", padx=20, pady=20)

        texto = "\n".join(resultados)
        txt_resultados.insert("1.0", texto)
        txt_resultados.configure(state="disabled")


    def mostrar_historial_estadisticas(self):
        if not self.result_statistics:
            messagebox.showinfo("Historial", "No hay estadísticas calculadas todavía.")
            return

        popup = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        popup.title("Historial de Estadísticas")
        popup.geometry("400x300")

        texto = "\n".join(
            f"{r['estadistica'].title()} de '{r['variable']}': {r['valor']:.4f}"
            for r in self.result_statistics
        )

        text_widget = ctk.CTkTextbox(popup, wrap="word")
        text_widget.insert("1.0", texto)
        text_widget.configure(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=20, pady=20)

    def _generate_graph(self):
        if self.df is None:
            print("Todavía no se han Cargado Datos")
            messagebox.showerror("Error","No se han cargado los datos")
            return
        
        self.popup_generate_graph = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        self.popup_generate_graph.title("Generar Gráfico")
        self.popup_generate_graph.resizable(False,False)

        #centar ventana
        self.popup_generate_graph.update()
        center_window(self.popup_generate_graph)
        
        self.generate_grafics_row = 2

        # Crear un marco desplazable
        self.scroll_frame = ctk.CTkScrollableFrame(self.popup_generate_graph, width=570, height=300)
        self.scroll_frame.configure(fg_color=self.color.COLOR_FONDO_APP)
        self.scroll_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.popup_generate_graph.transient(self)
        self.popup_generate_graph.lift()
        self.popup_generate_graph.focus_force() 
        self.popup_generate_graph.grab_set() # bloque ventana principal
        values = [
                    "Barra",
                    "Tarta",
                    "Linea",
                    "Dispersión",
                    "Bigote",
                    "Bigote por categoría"
                    ]

        ctk.CTkComboBox(self.scroll_frame,
                                            values=values,
                                            command=lambda valor, fila=0: self._type_graph(valor,0)
                                            ,button_color=self.color.COLOR_RELLENO_WIDGET
        ).grid(row=0,column=0,padx=(20,20),pady=(10,20))

        self.btn_add_variables = ctk.CTkButton(self.popup_generate_graph,
                                          text="+",
                                          width=50,
                                          command=lambda:self.add_variable(values),fg_color=self.color.COLOR_RELLENO_WIDGET)
        self.btn_add_variables.grid(row=1,column=0,padx=20,pady=(0,10))



    def _type_graph(self, valor, fila):
        # Elimina widgets previos en esa fila
        if fila in self.graph_widgets:
            # Conserva el combobox del tipo de gráfico (columna 0)
            nuevo_widget_fila = [self.graph_widgets[fila][0]]
            
            # Elimina los widgets adicionales si existen
            for widget in self.graph_widgets[fila][1:]:
                widget.destroy()
            
            self.graph_widgets[fila] = nuevo_widget_fila

        # Construye los nuevos widgets según el tipo
        widgets = []
        if valor in ["Barra", "Tarta"]:
            cbo_variable = ctk.CTkComboBox(self.scroll_frame,
                                        values=list(self.df.select_dtypes(include="object").columns)
                                        ,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_variable.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            btn = ctk.CTkButton(self.scroll_frame,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor, categoria=cbo_variable.get()),
                                fg_color=self.color.COLOR_RELLENO_WIDGET)
            btn.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            widgets.extend([cbo_variable, btn])

        elif valor in ["Linea", "Dispersión"]:
            cbo_x = ctk.CTkComboBox(self.scroll_frame,
                                    values=list(self.df.select_dtypes(include="number").columns)
                                    ,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_y = ctk.CTkComboBox(self.scroll_frame,
                                    values=list(self.df.select_dtypes(include="number").columns)
                                    ,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_x.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            cbo_y.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            btn = ctk.CTkButton(self.scroll_frame,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor, x=cbo_x.get(), y=cbo_y.get()),
                                fg_color=self.color.COLOR_RELLENO_WIDGET)
            btn.grid(row=fila, column=3, pady=(10, 20), padx=(0, 20))
            widgets.extend([cbo_x, cbo_y, btn])

        elif valor == "Bigote":
            cbo_var = ctk.CTkComboBox(self.scroll_frame,
                                    values=list(self.df.select_dtypes(include="number").columns)
                                    ,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_var.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            btn = ctk.CTkButton(self.scroll_frame,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor, va=cbo_var.get()),
                                fg_color=self.color.COLOR_RELLENO_WIDGET)
            btn.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            widgets.extend([cbo_var, btn])

        elif valor == "Bigote por categoría":
            cbo_num = ctk.CTkComboBox(self.scroll_frame,
                                    values=list(self.df.select_dtypes(include="number").columns)
                                    ,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_cat = ctk.CTkComboBox(self.scroll_frame,
                                    values=list(self.df.select_dtypes(include="object").columns)
                                    ,button_color=self.color.COLOR_RELLENO_WIDGET)
            cbo_num.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            cbo_cat.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            btn = ctk.CTkButton(self.scroll_frame,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor,
                                                                va=cbo_num.get(),
                                                                categoria=cbo_cat.get()),
                                fg_color=self.color.COLOR_RELLENO_WIDGET)
            btn.grid(row=fila, column=3, pady=(10, 20), padx=(0, 20))
            widgets.extend([cbo_num, cbo_cat, btn])

        self.graph_widgets[fila] = widgets
        

    def add_variable(self, values):
        fila = self.generate_grafics_row
        
        # Combo de tipo de gráfico
        cbo_tipo = ctk.CTkComboBox(self.scroll_frame,
                                values=values,
                                command=lambda valor, fila=fila: self._type_graph(valor, fila))
        cbo_tipo.grid(row=fila, column=0, padx=(20, 20), pady=(10, 20))
        
        self.graph_widgets[fila] = [cbo_tipo]
        
        self.generate_grafics_row +=1

    def _add_graph(self, tipo, **variable):
        if tipo == "Barra":
            fig, ax = plt.subplots()
            height = self.df[variable["categoria"]].value_counts().values
            x = self.df[variable["categoria"]].value_counts().index
            ax.bar(x, height)
            ax.set_title(f"Distribución {variable['categoria']}")
            plt.show()

        elif tipo == "Tarta":
            fig, ax = plt.subplots()
            x = self.df[variable["categoria"]].value_counts(normalize=True).values
            labels = self.df[variable["categoria"]].value_counts(normalize=True).index
            ax.pie(x, labels=labels)
            ax.set_title(f"Distribución {variable['categoria']}")
            plt.show()

        elif tipo == "Linea":
            fig, ax = plt.subplots()
            ax.plot(self.df[variable["x"]], self.df[variable["y"]])
            ax.set_title(f"Gráfico de {variable['y']}")
            plt.show()

        elif tipo == "Dispersión":
            fig, ax = plt.subplots()
            ax.scatter(self.df[variable["x"]], self.df[variable["y"]])
            ax.set_title(f"Gráfico de {variable['y']}")
            plt.show()

        elif tipo == "Bigote":
            fig, ax = plt.subplots()
            ax.boxplot(self.df[variable["va"]].dropna())
            ax.set_title(f"Gráfico de Bigote de {variable['va']}")
            plt.show()

        elif tipo == "Bigote por categoría":
            fig, ax = plt.subplots()
            grouped_data = self.df.groupby(variable["categoria"])[variable["va"]]
            data = [group.dropna().values for _, group in grouped_data]
            ax.boxplot(data, labels=grouped_data.groups.keys())
            ax.set_title(f"Bigote de {variable['va']} por {variable['categoria']}")
            plt.show()
        else:
            messagebox.showwarning("No existe","El tipo de gráficos seleccionado no existe")


    def __select_columns(self):
        popup_choose_columns = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        popup_choose_columns.title("Elige las columnas")
        popup_choose_columns.resizable(False,False)

        #centarr ventana
        popup_choose_columns.update()
        center_window(popup_choose_columns)

        popup_choose_columns.transient(self)
        popup_choose_columns.lift()
        popup_choose_columns.focus_force()
        popup_choose_columns.grab_set()
        

        group_check = {}
        for i,col in enumerate(self.df.columns):
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(
                                popup_choose_columns,
                                text=col,
                                variable=var
                                )
            chk.pack(anchor="w",pady=5,padx=20)
            group_check[col] = var

        print("Group checkbox de Transformar variables",group_check)
        btn_choose_columns= ctk.CTkButton(popup_choose_columns,
                                        text="Seleccionar",
                                        command=lambda:self.__save_columns(group_check,popup_choose_columns))
        btn_choose_columns.pack(anchor="w",pady=(5,10),padx=20)

    def __save_columns(self,group_check,popup_choose_columns):
        cols =  [ col for col,var in group_check.items() if var.get()]
        self.df = self.df[cols]
        self.show_tree_viewport()
        popup_choose_columns.destroy()

    def __transform_variables(self,function):
        print("--evento click Transformar Variable :",function)
        math_functions = {
                'ln': np.log,
                'log10':np.log10,
                'sqrt':np.sqrt,
                'exp': np.exp,
                'square':np.square,
                'abs':np.abs,
            }
        
        if math_functions.get(function,None) is None:
            return
        else:

            popup_choose_columns = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
            popup_choose_columns.title(f"Calcular {function}")
            popup_choose_columns.resizable(False,False)
            
            #centrar ventana
            popup_choose_columns.update()
            center_window(popup_choose_columns)

                    # Poner en primer plano con foco
            popup_choose_columns.transient(self)
            popup_choose_columns.focus_force()
            popup_choose_columns.lift()
            popup_choose_columns.grab_set()

            group_check = {}
            columns_number = self.df.select_dtypes(include='number').columns
            for i,col in enumerate(columns_number):
                var = ctk.BooleanVar()
                chk = ctk.CTkCheckBox(
                                    popup_choose_columns,
                                    text=col,
                                    variable=var
                                    )
                chk.pack(anchor="w",pady=5,padx=20)
                group_check[col] = var

            print("Group checkbox de Transformar variables",group_check)
            btn_choose_columns= ctk.CTkButton(popup_choose_columns,
                                            text="Seleccionar",
                                            command=lambda:self.__transfrom(group_check,
                                                                               function,
                                                                               math_functions,
                                                                               popup_choose_columns))
            btn_choose_columns.pack(anchor="w",pady=5,padx=20)

    def __transfrom(self,group_check,function,math_functions,popup_choose_columns):
        try:
            print("-- on click columnas elegidas:")
            cols =  [ col for col,var in group_check.items() if var.get()]   
            cols_func = [f"{function}_{col}" for col in cols]
            print(cols)
            self.df[cols_func]= math_functions[function](self.df[cols])
            self.show_tree_viewport()
            popup_choose_columns.destroy()

        except Exception as ex:
            messagebox.showerror("Campos Invalidos para la Transformación", ex)

    def post_table_name(self,table_name):
        
        url = config.VIEW_SAVE_TABLE_NAME
        headers = {
            "Authorization": f"Token {self.auth_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "table_name": table_name,
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                print("✅ Tabla guardada con éxito:", response.json())
                self.db_name = response.json()['db_name']
                return response.json()
            else:
                print(f"❌ Error al guardar tabla: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print("❌ Error de conexión al guardar tabla:", str(e))
            return None


    def importar_from_csv(self,encoding,sep,table_name):
        
        if self.url_csv is None or encoding == "" or sep == "":
            messagebox.showerror("Campos Invalidos para la Transformación", "Por favor, completa todos los campos obligatorios.")
            return
        
        if table_name in self.table_name_list:
            messagebox.showerror("Tabla ya existe","Por favor, utilice otro nombre de tabla, esta tabla ya existe")
            return
        else:
            print("--- añadiendo tabla_name---")
            self.table_name_list.append(table_name)
            print("---saving table name")
            self.post_table_name(table_name)
            self.table_name = table_name


        try:
            print("--- Mostrando tabla csv")
            self.df = pd.read_csv(self.url_csv,sep=sep,encoding=encoding)
            self.guardar_en_bbdd()
            self.show_tree_viewport()
        except Exception as ex:
            print("Error al importar CSV",ex)
            messagebox.showerror(
                title="Error al Importar CSV",
                message=ex
            )
        self.form.destroy()

    def importar_from_excel(self,sheet_name,table_name):
        
        if self.url_excel is None or sheet_name=="" :
            messagebox.showwarning("Campos requeridos", "Por favor, Seleciona el archivo Excel con los datos y establece la Hoja.")
            return
        
        
        if table_name in self.table_name_list:
            messagebox.showerror("Tabla ya existe","Por favor, utilice otro nombre de tabla, esta tabla ya existe")
            return
        else:
            print("--- post guardar nombre de tabla---")
            self.table_name_list.append(table_name)
            self.post_table_name(table_name)
            self.table_name = table_name
        print("--- solicitar post excel")
        print("--datos: ",self.url_excel)
        print("Nombre hoja:",sheet_name)

        try:
            self.df = pd.read_excel(self.url_excel,sheet_name=sheet_name)
            self.guardar_en_bbdd()
            self.show_tree_viewport()
            
        except Exception as ex:
            print("Error al importar Excel:",ex)
            messagebox.showerror(
                title="Error importar Excel",
                message=ex
            )
        self.form.destroy()

    def importar_from_bbdd(self,**kwargs):
        for value in kwargs.values():
            if value == "" or value == None:
                messagebox.showwarning("Campos requeridos","Por favor, Completa los paramtros de la conexion.")
                return

        table_name = kwargs["nombre_tabla"]
        if table_name in self.table_name_list:
            messagebox.showerror("Tabla ya existe","Por favor, utilice otro nombre de tabla, esta tabla ya existe")
            return
        else:

            print("--- post guardar nombre de tabla---")
            self.table_name_list.append(table_name)
            self.post_table_name(table_name)
            self.table_name = table_name

        sgbd_ = kwargs["SGBD"]
        nombre_tabla =  kwargs["nombre_tabla"]
        usuario = kwargs["usuario_db"]
        password = kwargs["password_db"]
        db = kwargs["db"]
        host = kwargs["host"]
        puerto = kwargs["puerto"]
        consulta = kwargs["consulta"]
        vars_conexion = {
            "MySQL": lambda user, password, db, host, port: f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}",
            "PostgreSQL": lambda user, password, db, host, port: f"postgresql://{user}:{password}@{host}:{port}/{db}",
            "SQLServer": lambda user, password, db, host, port: f"mssql+pyodbc://{user}:{password}@{host},{port}/{db}?driver=ODBC+Driver+17+for+SQL+Server",
        }
        try:
            str_engine = vars_conexion[sgbd_](usuario, password, db,host,puerto)
            print("engine",str_engine)
            engine = sqlalchemy.create_engine(str_engine)
            self.df = pd.read_sql(consulta,engine)
            self.guardar_en_bbdd()
            self.show_tree_viewport()
            
        except Exception as ex:
            print(f"Error Importar mediante Conexion con bbdd {sgbd_}",ex) 
            messagebox.showerror(
                title="Error Conexion",
                message=ex
            )          
        finally:
            if engine is not None:
                engine.dispose()

                
            
        self.form.destroy()
                

    def __guardar_url_csv(self,txt_file):
        
        self.url_csv = filedialog.askopenfilename(
            title="Selecciona CSV con datos",
            filetypes=[("Archivo CSV","*.csv")]
        )
        if self.url_csv is not None:
            archivo = os.path.basename(self.url_csv)
            txt_file.configure(state="normal")
            txt_file.insert(0,archivo)
            txt_file.configure(state="disabled")

    def __guardar_url_excel(self,txt_file):
         
        self.url_excel = filedialog.askopenfilename(
            title="Selecciona Excel con datos",
            filetypes=[("Archivo Excel","*.xlsx *.xls")]
        )

        if self.url_excel is not None:
            archivo = os.path.basename(self.url_excel)
            txt_file.configure(state="normal")
            txt_file.insert(0,archivo)
            txt_file.configure(state="disabled")

    def __ventana_conexion(self,tipo_bbdd,padre = None):
        print("--- La fuente de datos seleccionada es :",tipo_bbdd)
        
        if tipo_bbdd == "-- Ninguna":
            return
        
        if padre is not None:
            padre.destroy()
        
        self.form = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        
        self.form.title("Obtención de Datos")
        
        self.form.transient(self)
        self.form.lift()
        self.form.focus_force() 
        self.form.grab_set() # bloque ventana principal
    
        if tipo_bbdd == "Archivo Excel":
            
            lbl_file = ctk.CTkLabel(self.form,text="Seleccionar Excel")
            lbl_file.grid(row=0,column=0,padx=(50,20),pady=(20,10),sticky="e")
            txt_file = ctk.CTkEntry(self.form)
            txt_file.grid(row=0,column=1,padx=(0,10),pady=(20,10))
            btn_file = ctk.CTkButton(self.form,
                                     text="⬅",
                                     width=20,
                                     command=lambda: self.__guardar_url_excel(txt_file))
            btn_file.grid(row=0,column=2,padx=(0,20),pady=(20,10))

            lbl_sheet_name = ctk.CTkLabel(self.form,text="Hoja")
            lbl_sheet_name.grid(row=1,column=0,padx=(50,20),pady=(10,20))

            txt_sheet_name = ctk.CTkEntry(self.form)
            txt_sheet_name.grid(row=1,column=1,padx=(0,10),pady=(10,20))

            lbl_table_name = ctk.CTkLabel(self.form,text="Nombre tabla")
            lbl_table_name.grid(row=2,column=0,padx=(50,20),pady=(10,20))

            txt_table_name = ctk.CTkEntry(self.form)
            txt_table_name.grid(row=2,column=1,padx=(0,10),pady=(10,20)) 

            btn_enviar = ctk.CTkButton(self.form,
                                       text="Enviar",
                                       command=lambda:self.importar_from_excel(
                                            txt_sheet_name.get(),
                                            txt_table_name.get())
                                            )
            btn_enviar.grid(row=3,column=0,columnspan=2,pady=(10,20))

        
        elif tipo_bbdd.strip() == "Archivo CSV":
            
  
            lbl_file = ctk.CTkLabel(self.form,text="CSV")
            lbl_file.grid(row=0,column=0,padx=(50,20),pady=(20,10),sticky="e")
            txt_file = ctk.CTkEntry(self.form)
            txt_file.configure(state="disabled")

            txt_file.grid(row=0,column=1,padx=(0,50),pady=(20,10))
            btn_file = ctk.CTkButton(self.form,
                                     text="⬅",
                                     width=20,
                                     command=lambda: self.__guardar_url_csv(txt_file))
            btn_file.grid(row=0,column=2,pady=(20,10),padx=(0,10))
            lbl_encoding = ctk.CTkLabel(self.form,text="encoding")
            lbl_encoding.grid(row=1,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_encoding = ctk.CTkEntry(self.form)
            txt_encoding.grid(row=1,column=1,padx=(0,50),pady=(10,10))
            lbl_sep = ctk.CTkLabel(self.form,text="sep")
            lbl_sep.grid(row=2,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_sep = ctk.CTkEntry(self.form)
            txt_sep.grid(row=2,column=1,padx=(0,50),pady=(10,10))
            
            lbl_table_name = ctk.CTkLabel(self.form,text="Nombre tabla")
            lbl_table_name.grid(row=3,column=0,padx=(50,20),pady=(10,10))

            txt_table_name = ctk.CTkEntry(self.form)
            txt_table_name.grid(row=3,column=1,padx=(0,50),pady=(10,10)) 
            
            btn_enviar = ctk.CTkButton(self.form,
                                       text="Enviar",
                                       command=lambda: self.importar_from_csv(
                                                                        txt_encoding.get(),
                                                                        txt_sep.get(),
                                                                        txt_table_name.get())
                                                            )
            
            btn_enviar.grid(row=4,column=1,pady=(10,10),padx=(0,50))

        elif tipo_bbdd in ["MySQL","PostgreSQL","SQLServer"] :  
            print(tipo_bbdd)
            lbl_user = ctk.CTkLabel(self.form,text="Usuario")
            lbl_user.grid(row=0,column=0,padx=(50,20),pady=(20,10),sticky="e")
            txt_user = ctk.CTkEntry(self.form)
            txt_user.grid(row=0,column=1,padx=(0,50),pady=(20,10))

            lbl_password = ctk.CTkLabel(self.form,text="Contraseña")
            lbl_password.grid(row=1,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_password = ctk.CTkEntry(self.form)
            txt_password.grid(row=1,column=1,padx=(0,50),pady=(10,10))

            lbl_db = ctk.CTkLabel(self.form,text="Base de Datos")
            lbl_db.grid(row=2,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_db = ctk.CTkEntry(self.form)
            txt_db.grid(row=2,column=1,padx=(0,50),pady=(10,10))

            lbl_host = ctk.CTkLabel(self.form,text="Host")
            lbl_host.grid(row=3,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_host = ctk.CTkEntry(self.form)
            txt_host.grid(row=3,column=1,padx=(0,50),pady=(10,10))

            lbl_puerto = ctk.CTkLabel(self.form,text="Puerto")
            lbl_puerto.grid(row=4,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_puerto = ctk.CTkEntry(self.form)
            txt_puerto.grid(row=4,column=1,padx=(0,50),pady=(10,10))

            lbl_consulta = ctk.CTkLabel(self.form,text="Consulta")
            lbl_consulta.grid(row=5,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_consulta = ctk.CTkEntry(self.form)
            txt_consulta.grid(row=5,column=1,padx=(0,50),pady=(10,10))

            lbl_nombre_tabla = ctk.CTkLabel(self.form,text="Nombrar Tabla")
            lbl_nombre_tabla.grid(row=6,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_nombre_tabla = ctk.CTkEntry(self.form)
            txt_nombre_tabla.grid(row=6,column=1,padx=(0,50),pady=(10,10))

            btn_enviar = ctk.CTkButton(self.form,
                                       text="Enviar",
                                       command=lambda: self.importar_from_bbdd(
                                           nombre_tabla = txt_nombre_tabla.get(),
                                           usuario_db=txt_user.get(),
                                           password_db=txt_password.get(),
                                           host=txt_host.get(),
                                           db=txt_db.get(),
                                           consulta=txt_consulta.get(),
                                           puerto =txt_puerto.get(),
                                           SGBD = tipo_bbdd
                                       )
                                       )
            
            btn_enviar.grid(row=7,column=0,columnspan=2,pady=(10,20))
        

    def crear_procesar(self):
        header_padre = ctk.CTkFrame(self.tab1,
                                    fg_color=self.color.COLOR_FONDO_FRAME,
                                    corner_radius=10,
                                    border_color=self.color.COLOR_BORDE_WIDGET,
                                    border_width=2,
                                    )
        header_padre.pack(side="top",padx=20,pady=(20,10),fill="x")
        header_hijo = ctk.CTkFrame(header_padre,
                                   fg_color=self.color.COLOR_FONDO_FRAME,
                                   corner_radius=10,
                                   border_color=self.color.COLOR_BORDE_WIDGET)
        header_hijo.pack(padx=10,pady=10,fill="both")

        # FILA 1 :  CARGAR DATOS, ELEGIR COLUMNAS, TRANSFORMAR VARIABLES, GENERAR GRÁFICOS, VARIABLE DEPENDIENTE

        cbo_cargar_datos = ctk.CTkComboBox(header_hijo,
                                            values=[
                                               "Archivo CSV",
                                               "Archivo Excel",
                                               "MySQL",
                                               "PostgreSQL",
                                               "SQLServer",
                                               "-- Ninguna"
                                           ],
                                           command=self.__ventana_conexion,
                                           button_color=self.color.COLOR_RELLENO_WIDGET,
                                           border_color=self.color.COLOR_BORDE_WIDGET,
                                           state="readonly")
        cbo_cargar_datos.set("Fuente de Datos")
        cbo_cargar_datos.grid(row=0,column=0,padx=(10,5),sticky="nsew",pady=(0,10))

        self.btn_elegir_columnas = ctk.CTkButton(header_hijo,
                                                 text="Elegir Columnas",
                                                 command=self.__select_columns,
                                                 fg_color=self.color.COLOR_RELLENO_WIDGET
                                                 )
        self.btn_elegir_columnas.grid(row=0,column=1,padx=(5,5),sticky="nsew",pady=(0,10))

        cbo_transform_variables = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "ln",
                                          "log10",
                                          "sqrt",# raiz cuadrada
                                          "exp",
                                          "square",
                                          "abs",
                                          "-- Ninguna"
                                           ],
                                           command= self.__transform_variables,
                                           button_color=self.color.COLOR_RELLENO_WIDGET,
                                           state="readonly")
        cbo_transform_variables.grid(row=0,column=2,padx=(5,5),sticky="nsew",pady=(0,10))
        cbo_transform_variables.set("Transformar Variables")

        btn_generate_graph = ctk.CTkButton(header_hijo,
                                           text="Generar Gráfico",
                                           command=self._generate_graph,
                                                 fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_generate_graph.grid(row=0,column=3,padx=(5,5),sticky="nsew",pady=(0,10))

        self.cbo_variable_dependiente = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Columna1",
                                          "Columna2",
                                          "Columna3",
                                          "-- Ninguna"
                                           ],
                                           button_color=self.color.COLOR_RELLENO_WIDGET,
                                           command=self.variable_dependiente,
                                           state="readonly")
        self.cbo_variable_dependiente.grid(row=0,column=4,padx=(5,10),sticky="nsew",pady=(0,10))
        self.cbo_variable_dependiente.set("Variable Dependiente")

        for col in range(5):  # Tienes 5 elementos
            header_hijo.grid_columnconfigure(col, weight=1)
        header_hijo.grid_rowconfigure(1, weight=1)

        # FILA 2: FILTRO , CONVERTIR TIPO, A.N.S., CALCULAR ESTÁDISTICAS,  APLICAR (CAMBIOS)

        btn_filtro = ctk.CTkButton(header_hijo,
                                   text="Filtrar",
                                   command=self.__filtrar,
                                                 fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_filtro.grid(row=1,column=0,padx=(10,5),sticky="nsew")


        btn_convert_data_type = ctk.CTkButton(header_hijo,
                                              text="Convertir Tipo Datos",
                                              command=self.__convert_data_type,
                                                 fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_convert_data_type.grid(row=1,column=1,padx=(5,5),sticky="nsew")
        
        self.cbo_ANO = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "PCA",
                                          "KMeans",
                                          "-- Ninguna"
                                           ],
                                           command=self.top_level_params_ANO,
                                           button_color=self.color.COLOR_RELLENO_WIDGET,
                                           state="readonly")
        self.cbo_ANO.grid(row=1,column=2,padx=(5,5),sticky="nsew")
        self.cbo_ANO.set("A. No Superivosado")
        
        
        btn_calculate_statistics = ctk.CTkButton(header_hijo,
                                                 text="Estadísticas",
                                                 command= self.__calculate_statistics,
                                                 fg_color=self.color.COLOR_RELLENO_WIDGET
                                        )
        btn_calculate_statistics.grid(row=1,column=3,padx=(5,5),sticky="nsew")
        

        btn_aplicar = ctk.CTkButton(header_hijo,
                                    command=self.guardar_en_bbdd,
                                    text="Aplicar",
                                    fg_color = self.color.COLOR_RELLENO_WIDGET
                                    )
        btn_aplicar.grid(row=1,column=4,padx=(5,10),sticky="nsew")

        frame_tabla = ctk.CTkFrame(self.tab1,height=400,fg_color=self.color.COLOR_FONDO_FRAME)
        frame_tabla.pack(fill="x",side="top",pady=(10,20),padx=20)
        
        scroll_x = ttk.Scrollbar(frame_tabla,orient="horizontal")
        scroll_x.pack(side="bottom",fill="x")     


        
        """ ------------obteniendo los datos---------------"""
        

        self.tree = ttk.Treeview(frame_tabla,
                            xscrollcommand=scroll_x.set ,
                           
                            show="headings")
        
        scroll_x.config(command=self.tree.xview)
        self.tree.pack(padx=20, pady=20, fill="both", expand=True)
    
    def variable_dependiente(self,value):
        if self.df is None:
            messagebox.showerror("Error","No ha importado tabla")
            return
        if value not in self.df.columns:
            messagebox.showerror("Error","Variable no presente en la tabla")
            return
        self.y = value
        
        pop = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        pop.title("Tipo Problema")
        pop.resizable(False, False)
        pop.transient(self)
        pop.lift()
        pop.focus_force()
        pop.grab_set()
        pop.update()
        ctk.CTkLabel(pop,text="Selecciona El tipo de Problema").grid(row=0,padx=20,pady=10)
        cbo =ctk.CTkComboBox(pop,values=["Regresion","Clasificacion"],command=self.establecer_problema,state="readonly")
        cbo.grid(row=1,padx=20,pady=10)
        cbo.set("Regresion")
        
        

    def establecer_problema(self,value):
        if value not in ["Regresion","Clasificacion"]:
            messagebox.showerror("Error","Valor no válido. Debe ser Regresion o Clasificacion. ")
        else:
            self.tipo_problema =value
            self.set_options()

    def show_tree_viewport(self,copia=False):
        print("--- Renderizando tabla df")
        if copia:
            df = self.df_filtrado
        else:
            df = self.df
        df.info()


        # tree 
        self.tree["columns"] = list(df.columns)
        self.cbo_variable_dependiente.configure(values=list(df.columns))

        # encambezado (cols)
        for col in df.columns:
            self.tree.heading(col,text=col.capitalize())
            self.tree.column(col, anchor="center")
        
        #limpiar filas
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar datos (50 primeras filas)
        for vector in df.values[:50]:
            self.tree.insert("","end",values=tuple(vector))
        # actualizaciones
        self.cbo_var_y.configure(values=list(self.df.columns)+[""])
        self.cbo_var_x.configure(values=list(self.df.columns)+[""])

    def crear_entrenamiento(self):
        header_padre = ctk.CTkFrame(self.tab2,fg_color=self.color.COLOR_FONDO_FRAME,corner_radius=10, border_width=2, border_color=self.color.COLOR_BORDE_WIDGET)
        header_padre.pack(side="top",padx=20,pady=(20,10),fill="x")

        header_hijo = ctk.CTkFrame(header_padre,fg_color=self.color.COLOR_FONDO_FRAME,corner_radius=10)
        header_hijo.pack(fill="both",padx=10,pady=10)

        # Dentro de crear_entrenamiento()
        header_hijo.grid_columnconfigure(0, weight=3)  # 30%
        header_hijo.grid_columnconfigure(1, weight=1)  # 10%
        header_hijo.grid_columnconfigure(2, weight=4)  # 40%
        header_hijo.grid_columnconfigure(3, weight=2)  # 20%





        self.cbo_modelo = ctk.CTkComboBox(header_hijo,
                                     values=[
                                            'Linear Regression',
                                            'Random Forest Regressor',
                                            'Decision Tree Regressor',
                                            'Svm Regressor',
                                            'Knn Regressor',
                                            'Random Forest Classifier',
                                            'Decision Tree Classifier',
                                            'Svm Classifier',
                                            'Knn Classifier',
                                            'Naive Bayes',
                                     ],
                                     button_color=self.color.COLOR_RELLENO_WIDGET,
                                     state="readonly"
                                     )
        self.cbo_modelo.grid(row=0,column=0,padx=(10,5),pady=(0,10),sticky="snew")
        self.cbo_modelo.set("Modelo")
        def habilitar(value):
            if value not in ["Grid Search CV","Randomized Search CV"]:
                self.area_params.configure(state="normal")
                self.area_params.delete("1.0", "end")
                
                self.area_params.configure(state="disabled")

                self.spin_cv.configure(state="normal")
                self.spin_cv.set(0)
                self.spin_cv.configure(state="disabled")

            else:
                
                self.spin_cv.configure(state="readonly")
                self.spin_cv.set("cv")
                self.area_params.configure(state="normal")

        cbo_type_search = ctk.CTkComboBox(header_hijo,
                                            values=[
                                                "-- Ninguna",
                                                "Grid Search CV",
                                                "Randomized Search CV"
                                            ],
                                     button_color=self.color.COLOR_RELLENO_WIDGET,
                                     border_color=self.color.COLOR_BORDE_WIDGET,
                                     command=habilitar,
                                     state="readonly")
        cbo_type_search.set("Tipo Busqueda")
        
        cbo_type_search.grid(row=1,column=0,padx=(10,5),sticky="snew")
        self.spin_cv = ctk.CTkComboBox(header_hijo,
                                       values=["3"]+ [str(i) for i in range(5, 21, 5)],
                                        button_color=self.color.COLOR_RELLENO_WIDGET,
                                        border_color=self.color.COLOR_BORDE_WIDGET
                                        )

        self.spin_cv.grid(row=0, column=1, padx=5, pady=(0,10), sticky="snew")
        self.spin_cv.set("cv")
        self.spin_cv.configure(state="disabled")
        self.cbo_scoring = ctk.CTkComboBox(header_hijo,
                                  values=[
                                      "MSE",
                                      "RMSE",
                                      "MEA",
                                      "R²",
                                      "Accuracy",
                                      "f1",
                                      "ROC AUC",
                                      "Precisión"
                                  ],
                                  button_color=self.color.COLOR_RELLENO_WIDGET,
                                  border_color=self.color.COLOR_BORDE_WIDGET,
                                  state="readonly")
        self.cbo_scoring.set("Scoring")
        self.cbo_scoring.grid(row=1,column=1,padx=5,sticky="snew")
        self.area_params = ctk.CTkTextbox(header_hijo, height=80)
        self.area_params.insert("0.0", "Establecer Hiperparámetros (como diccionario {})")
        self.area_params.configure(state="disabled")
        self.area_params.grid(row=0,rowspan=2,column=2,padx=(5,5),sticky="snew")

        frame_btn = ctk.CTkFrame(header_hijo,fg_color=self.color.COLOR_FONDO_FRAME)
        frame_btn.grid(row=0,rowspan=2,column=3,sticky="snew")
        
        btn_entrenar = ctk.CTkButton(frame_btn,
                                     text="Entrenar",
                                     fg_color=self.color.COLOR_RELLENO_WIDGET,
                                     command=lambda: self.train_model(
                                    type_search=cbo_type_search.get(),
                                   )
        )
        btn_entrenar.pack(fill="x",expand=True,side="left")
        
        self.frame_modelos = ctk.CTkFrame(self.tab2,
                                    height=400,
                                    fg_color=self.color.COLOR_FONDO_FRAME)
        self.frame_modelos.pack(fill="x",side="top",pady=(10,20),padx=20)
        btn_historial = ctk.CTkButton(self.frame_modelos,
                                      text="Mostrar Estidisticos",
                                      command=self.mostrar_historial_estadisticas,
                                      fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_historial.grid(row=0,column=0,padx=10,pady=10,sticky="snew")


    def crear_dashboard(self):
        # Frame principal
        header_padre = ctk.CTkFrame(self.tab3, fg_color=self.color.COLOR_FONDO_FRAME, corner_radius=20)
        header_padre.pack(fill="x")

        # Frame secundario
        header_hijo = ctk.CTkFrame(header_padre, fg_color=self.color.COLOR_FONDO_FRAME, corner_radius=20)
        header_hijo.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configurar la expansión de filas y columnas
        header_padre.grid_columnconfigure(0, weight=1)  # Expande la columna 0 de header_padre

        #header_hijo.grid_rowconfigure(0, weight=1)  # Expande la fila 0 de header_hijo
        header_hijo.grid_columnconfigure(0, weight=1,minsize=200)  # Expande la columna 0 de header_hijo
        header_hijo.grid_columnconfigure(1, weight=1,minsize=250)  # Expande la columna 1 de header_hijo
        header_hijo.grid_columnconfigure(2,weight=1,minsize=300)
        header_hijo.grid_columnconfigure(3,weight=1,minsize=120)

        # Frame de imagen
        frame_img = tk.LabelFrame(header_hijo, text="Opciones Imagen", relief="flat", background=self.color.COLOR_FONDO_FRAME)
        frame_img.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        frame_img.grid_columnconfigure(0, weight=1)
        frame_img.grid_columnconfigure(1, weight=1)
        
        self.cbo_editar_imagen = ctk.CTkComboBox(frame_img,
                                          button_color=self.color.COLOR_RELLENO_WIDGET,
                                          values=[],
                                          state="readonly",
                                          command=lambda v: self.seleccionar_elemento("imagen", v)
                                          )
        self.cbo_editar_imagen.set("Elegir Imagen")
        self.cbo_editar_imagen.grid(row=0, column=0, padx=5, pady=(5,10), sticky="nsew")

        btn_crear_imagen = ctk.CTkButton(frame_img, text="Cargar", command=self.crear_imagen,
                                   fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_crear_imagen.grid(row=0, column=1, padx=5, pady=(5, 10), sticky="nsew")

        btn_cambiar_imagen = ctk.CTkButton(frame_img, text="Cambiar", command=self.cambiar_imagen,
                                   fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_cambiar_imagen.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="nsew")

        btn_borrar_imagen = ctk.CTkButton(frame_img, text="Eliminar", command=self.eliminar_imagen,
                                   fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_borrar_imagen.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="nsew")

        # Frame de fuente
        frame_fuente = tk.LabelFrame(header_hijo, text="Opciones Texto", relief="flat", background=self.color.COLOR_FONDO_FRAME)
        frame_fuente.grid(row=0, column=1, padx=(0, 5), sticky="nsew")
        frame_fuente.grid_columnconfigure(0,weight=1)
        frame_fuente.grid_columnconfigure(1,weight=1)
        frame_fuente.grid_columnconfigure(2,weight=1)

        btn_crear_texto= ctk.CTkButton(frame_fuente, 
                                   text="Nuevo",
                                   fg_color=self.color.COLOR_RELLENO_WIDGET,
                                   command=self.crear_textbox)
        btn_crear_texto.grid(row=0, column=0, padx=5, pady=(5,10), sticky="nsew")
        
        self.cbo_editar_texto = ctk.CTkComboBox(frame_fuente,
                                          button_color=self.color.COLOR_RELLENO_WIDGET,
                                          values=[],
                                          state="readonly",
                                          command=lambda v: self.seleccionar_elemento("texto", v)
                                          )
        self.cbo_editar_texto.set("Elegir Texto")
        self.cbo_editar_texto.grid(row=0, column=1, padx=5, pady=(5,10), sticky="nsew")
        self.is_bold = False
        self.is_italic = False
        self.is_underline = False

        btn_borrar_texto= ctk.CTkButton(frame_fuente, 
                                   text="Eliminar",
                                   fg_color=self.color.COLOR_RELLENO_WIDGET,
                                   command=self.eliminar_textbox)
        btn_borrar_texto.grid(row=0, column=2, padx=5, pady=(5,10), sticky="nsew")

        
        fuente_subframe = ctk.CTkFrame(frame_fuente, fg_color=self.color.COLOR_FONDO_FRAME)
        fuente_subframe.grid(padx=5, pady=(0,10), row=1, column=0, sticky="nsew")
        fuente_subframe.grid_columnconfigure(0,weight=1)
        fuente_subframe.grid_columnconfigure(1,weight=1)
        fuente_subframe.grid_columnconfigure(2,weight=1)

        self.btn_negrita = ctk.CTkButton(fuente_subframe, text="N", font=("Arial", 12, "bold"), width=10,
                                    fg_color=self.color.COLOR_RELLENO_WIDGET,
                                    command=self.toggle_bold)
        self.btn_negrita.grid(padx=0, pady=0,row=1, column=0)

        self.btn_cursiva = ctk.CTkButton(fuente_subframe, text="C", font=("Arial", 12, "italic"), width=10,
                                    fg_color=self.color.COLOR_RELLENO_WIDGET,
                                    command=self.toggle_italic)
        self.btn_cursiva.grid(padx=0, pady=0,row=1, column=1)

        self.btn_subrayado = ctk.CTkButton(fuente_subframe, text="S", font=("Arial", 12, "underline"), width=10,
                                      fg_color=self.color.COLOR_RELLENO_WIDGET,
                                      command=self.toggle_underline)
        self.btn_subrayado.grid(padx=0, pady=0,row=1, column=2)

        self.cbo_fuente = ctk.CTkComboBox(frame_fuente, values=self.fuentes_disponibles,
                                     button_color=self.color.COLOR_RELLENO_WIDGET,
                                     command=self.call_update_font)
        self.cbo_fuente.grid(row=1, column=1, padx=5, pady=(0, 10),sticky="nsew")
        lista_size = [ "12", "14", "16", "18", "20", "24", "28", "32", "36", "40", "44", "48", "60"]
        self.cbo_size = ctk.CTkComboBox(frame_fuente, values=lista_size, width=100,
                                   button_color=self.color.COLOR_RELLENO_WIDGET,
                                   command=self.call_update_font)
        self.cbo_size.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="nsew")

        #self.btn_fuente_aplicar =ctk.CTkButton(frame_fuente,text="Aplicar Fuente")
        

        # Frame de configuración de gráfico
        frame_configurar_grafico = tk.LabelFrame(header_hijo, text="Opciones Gráficos", relief="flat", background=self.color.COLOR_FONDO_FRAME)
        frame_configurar_grafico.grid(row=0, column=2, padx=(0, 5),sticky="nsew")
        frame_configurar_grafico.grid_columnconfigure(0,weight=1)
        frame_configurar_grafico.grid_columnconfigure(1,weight=1)
        frame_configurar_grafico.grid_columnconfigure(2,weight=1)

        self.cbo_editar_grafico = ctk.CTkComboBox(frame_configurar_grafico,
                                          button_color=self.color.COLOR_RELLENO_WIDGET,
                                          values=[],
                                          state="readonly",
                                          command=lambda v: self.seleccionar_elemento("grafico", v)
                                          )
        self.cbo_editar_grafico.set("Elegir Grafico")
        self.cbo_editar_grafico.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky="nsew")

        btn_borrar_grafico= ctk.CTkButton(frame_configurar_grafico, 
                                   text="Eliminar",
                                   fg_color=self.color.COLOR_RELLENO_WIDGET,
                                   command=self.eliminar_grafico)
        btn_borrar_grafico.grid(row=0, column=2, padx=5, pady=(5,10), sticky="nsew")

        cbo_relleno = ctk.CTkComboBox(frame_configurar_grafico,button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_relleno.grid(row=1, column=0, padx=5, sticky="nsew")

        cbo_contorno = ctk.CTkComboBox(frame_configurar_grafico,button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_contorno.grid(row=1, column=1, padx=5, sticky="nsew")

        cbo_efectos = ctk.CTkComboBox(frame_configurar_grafico,button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_efectos.grid(row=1, column=2, padx=5, sticky="nsew")

        # Frame de impresión
        frame_guardar = tk.LabelFrame(header_hijo, text="Opciones Hoja", relief="flat", background=self.color.COLOR_FONDO_FRAME)
        frame_guardar.grid(row=0, column=3, padx=(0, 10), sticky="nsew")
        
        
        colores_lista = ["Blanco", "Gris claro", "Azul muy claro", "SunGlow", "Burnt Siena", "Cardinal", "Chocolate Cosmos", "Lapiz Lazuli", "Beige"]
        cbo_fondo = ctk.CTkComboBox(frame_guardar, values=colores_lista,
                                    button_color=self.color.COLOR_RELLENO_WIDGET,
                                    command=self.cambiar_fondo_hoja)
        cbo_fondo.set("Elegir Fondo")
        cbo_fondo.pack(padx=5, pady=(5, 10), fill="x")

        btn_add_txt= ctk.CTkButton(frame_guardar, 
                                   text="Guardar",
                                   fg_color=self.color.COLOR_RELLENO_WIDGET,
                                   command=self.guardar_hoja_csv)
        btn_add_txt.pack(fill="x",expand=True, padx=5,pady=(0, 10))
        
         # Frame principal (panel)
        panel = ctk.CTkFrame(self.tab3, fg_color=self.color.COLOR_FONDO_FRAME)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabview (dashboard) en el panel, 
        self.dashboard = ctk.CTkTabview(panel,fg_color=self.color.COLOR_FONDO_FRAME)
        self.dashboard.pack(side="left", fill="both", expand=True)

        # Menú lateral (panel_graficos) a la derecha
        menu_lateral = ctk.CTkTabview(panel,fg_color=self.color.COLOR_FONDO_FRAME)
        menu_lateral.pack(side="right", fill="y", padx=(10, 0), pady=10)

        hoja_grafico = menu_lateral.add("Gráficos")
        hoja_formato = menu_lateral.add("Formato")

        panel_graficos = ctk.CTkFrame(hoja_grafico, fg_color=self.color.COLOR_FONDO_FRAME)
        panel_graficos.pack(fill="both",  pady=10, expand=True)

        panel_formato = ctk.CTkFrame(hoja_formato,fg_color=self.color.COLOR_FONDO_FRAME)
        panel_formato.pack(fill="both", expand=True)

        cuadro_iconos = ctk.CTkFrame(panel_graficos,fg_color=self.color.COLOR_RELLENO_WIDGET)
        cuadro_iconos.pack(pady=(0,20))

        cuadro_variables = ctk.CTkFrame(panel_graficos,fg_color=self.color.COLOR_RELLENO_WIDGET)
        cuadro_variables.pack(fill="both",expand=True)

        # Agregar las hojas al dashboard y frames (contenido blanco)
        self.hojas = {}
        self.hojas_frame = {}

        for i in range(1,4):
            self.hojas[f"hoja{i}"] = self.dashboard.add(f"Hoja {i}")
            
            self.hojas_frame[f"hoja{i}_frame"] =  ctk.CTkFrame(self.hojas[f"hoja{i}"],
                                                                fg_color="#ffffff",
                                                                border_width=2,
                                                                border_color=self.color.COLOR_BORDE_WIDGET)
            
            self.hojas_frame[f"hoja{i}_frame"].grid(row=0, column=0, sticky="nsew")
            self.hojas[f"hoja{i}"].grid_rowconfigure(0, weight=1) # Asegura que la fila 0 de hoja-i se expanda
            self.hojas[f"hoja{i}"].grid_columnconfigure(0, weight=1)  # Asegura que la columna 0 de hoja-i se expanda

        ruta_iconos = os.listdir(r'iconos\plots')
        print("--- iconos")
        pill_images =[]
        my_ctk_images  =[]
        for nombre_ico in ruta_iconos:
            ruta_ico =os.path.join( r"iconos\plots", nombre_ico)
            pil_image = Image.open(ruta_ico)
            pill_images.append(pil_image)
            my_ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(30,30)) 
            my_ctk_images.append(my_ctk_image)


        # Agregar Iconos de Gráficos

        tipos_graficos = ["Barra", "Tarta", "Linea", "Dispersión", "Bigote", "Bigote por categoría","Densidad","Histograma"]

        btn_graficos = {}
        for i, tipo in enumerate(tipos_graficos):
            btn_graficos[f"btn_{i+1}"] = ctk.CTkButton(
                cuadro_iconos,
                text="",
                image=my_ctk_images[i],
                width=10, height=10,
                command=lambda t=tipo: self.crear_grafico(t)
            )

        contador = 0
        for row in range(2):
            for col in range(4):
                if f"btn_{contador+1}" in btn_graficos:
                    btn_graficos[f"btn_{contador+1}"].grid(row=row, column=col, padx=5, pady=5)
                contador += 1

        #  Agregar seleccion de Variables
        lbl_var_y = ctk.CTkLabel(cuadro_variables,text="Eje y",text_color=self.color.COLOR_LETRA_BOTON)
        lbl_var_y.pack()
        self.cbo_var_y = ctk.CTkComboBox(cuadro_variables,values=["Col 1","Col 2"],state="readonly")
        self.cbo_var_y.pack()
        lbl_var_x = ctk.CTkLabel(cuadro_variables,text="Eje x",text_color=self.color.COLOR_LETRA_BOTON)
        lbl_var_x.pack()
        self.cbo_var_x = ctk.CTkComboBox(cuadro_variables,values=["Col 1","Col 2"],state="readonly")
        self.cbo_var_x.pack(pady=(0,10))

        # Agregar componentes de ajustes del gráfico
        self.ajustes_graficos = {}
        ajustes_nombre = ["Size","Width","Height","Redondear","Relleno","Color"]
        # Dentro de tu clase, crea un diccionario para guardar ajustes por objeto
        self.valores_ajustes = {
            "texto": {},
            "grafico": {},
            "imagen": {}
        }

        for i in range(len(ajustes_nombre)):
            nombre = ajustes_nombre[i]

            self.ajustes_graficos[f"lbl_{nombre}"] = ctk.CTkLabel(panel_formato, text=nombre)
            self.ajustes_graficos[f"lbl_{nombre}"].grid(row=i, column=0)

            self.ajustes_graficos[f"sld_{nombre}"] = ctk.CTkSlider(panel_formato, from_=-100, to=100,
                                                            command=lambda valor, ajuste=nombre: self.aplicar_formato(valor, ajuste))
            self.ajustes_graficos[f"sld_{nombre}"].grid(row=i, column=1)

        self.frames_movil_text_box = {}
        self.frames_movil_graficos = {}
        self.frames_movil_imagen = {}
        self.num_cuadro_texto = 1
        self.num_grafico =1
        self.num_imagen = 1

    # def set_texto(self):
    #     """         llamar al pichar boton aplicar    """
    #     weight = "bold" if self.is_bold else "normal"
    #     slant = "italic" if self.is_italic else "roman"
    #     underline = True if self.is_underline else False
    #     fuente = self.cbo_fuente.get()
    #     size= int(self.cbo_size.get()) 
    #     font = ctk.CTkFont(family=fuente, size=size, weight=weight, slant=slant, underline=underline)
    #     value = self.cbo_editar.get()  
    #     frame = self.frames_movil_text_box[value]
    #     textbox = frame.winfo_children()[0]  # si solo hay 1 hijo, será el CTkTextbox

    #     textbox.configure(font=font)
    def load_font_system(self):
        #self.fuentes_disponibles = list(tkFont.families())
        #self.fuentes_disponibles.sort()
        fuentes_populares = [
            "Arial", "Calibri", "Cambria", "Comic Sans MS", "Consolas",
            "Courier New", "Georgia", "Helvetica", "Lucida Console", "Segoe UI",
            "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        self.fuentes_disponibles =fuentes_populares

    def update_font(self):      # aplica sobre el objeto seleccionado en self.cbo_editar_texto
        
        weight = "bold" if self.is_bold else "normal"
        slant = "italic" if self.is_italic else "roman"
        underline = True if self.is_underline else False
        fuente = self.cbo_fuente.get()
        size=int(self.cbo_size.get())
        font = ctk.CTkFont(family=fuente, size=size, weight=weight, slant=slant, underline=underline)
        value = self.cbo_editar_texto.get()
        frame = self.frames_movil_text_box[value]
        textbox = frame.winfo_children()[0]  # si solo hay 1 hijo, será el CTkTextbox

        textbox.configure(font=font)

    def call_update_font(self,value):
        self.update_font()

    def seleccionar_elemento(self, tipo, value):
        if tipo == "texto":
            self.cbo_editar_grafico.set("")
            self.cbo_editar_imagen.set("")
            self.clean_menu_editar(value)
            self.actualizar_sliders(tipo,value)
        elif tipo == "grafico":
            self.cbo_editar_texto.set("")
            self.cbo_editar_imagen.set("")
            self.actualizar_sliders(tipo,value)

        elif tipo == "imagen":
            self.cbo_editar_texto.set("")
            self.cbo_editar_grafico.set("")
            self.actualizar_sliders(tipo,value)

    def clean_menu_editar(self,value):
        """     reinicia a valores perdeterminados el cbo fuente , cbo size , negrita, cursiva, subrrayado"""
        name_txt =self.cbo_editar_texto.get()
        textbox = self.frames_movil_text_box[name_txt].winfo_children()[0]
        fuente = textbox.cget("font")
        
        family = fuente.cget("family")
        tamaño = fuente.cget("size")
        negrita = fuente.cget("weight") == "bold"
        cursiva = fuente.cget("slant") == "italic"
        subrayado = fuente.cget("underline")
        
        self.cbo_fuente.set(family)
        self.cbo_size.set(tamaño)
        self.is_bold = negrita
        self.is_italic = cursiva
        self.is_underline = subrayado
    

    def toggle_bold(self):
        self.is_bold = not self.is_bold
        self.update_font()

    def toggle_italic(self):
        self.is_italic = not self.is_italic
        self.update_font()

    def toggle_underline(self):
        self.is_underline = not self.is_underline
        self.update_font()

    def crear_textbox(self):
        hoja = self.dashboard.get().lower().replace(" ", "")
        hojas_frame_ = self.hojas_frame[f"{hoja}_frame"]
        
        frame_movil = MovableResizableFrame(hojas_frame_,600,80)
        self.frames_movil_text_box[f"Cuadro Texto {self.num_cuadro_texto}"] = frame_movil
        values = [f"Cuadro Texto {self.num_cuadro_texto}"] + list(self.cbo_editar_texto.cget("values"))
        self.cbo_editar_texto.configure(values=values)
        self.num_cuadro_texto+=1
        frame_movil.place(x=100, y=100)
        frame_movil.pack_propagate(False)

        text_box = ctk.CTkTextbox(frame_movil )
        text_box.pack(fill="both", expand=True,padx=10, pady=10)

    def eliminar_textbox(self):
        name_txt = self.cbo_editar_texto.get()  # Obtiene el nombre del textbox seleccionado
        if name_txt in self.frames_movil_text_box:
            frame = self.frames_movil_text_box[name_txt]
            frame.destroy()  # Destruye el frame contenedor (y por ende el textbox)
            del self.frames_movil_text_box[name_txt]  # Elimina la referencia del diccionario

            # Actualiza el combobox para remover el nombre eliminado
            values = list(self.cbo_editar_texto.cget("values"))
            if name_txt in values:
                values.remove(name_txt)
                self.cbo_editar_texto.configure(values=values)
                self.cbo_editar_texto.set('')  # Limpia la selección actual

    def crear_grafico(self, tipo_grafico):
        # Obtener variables seleccionadas (asegúrate que estos atributos existen en tu clase)
        var_x = self.cbo_var_x.get() if hasattr(self, "cbo_var_x") else None
        var_y = self.cbo_var_y.get() if hasattr(self, "cbo_var_y") else None
        
        

        # Control básico si no se seleccionan variables
        
        if (var_y =='' or var_x =='') and tipo_grafico in ['Barra','Linea','Dispersión','Bigote por categoría']:
            messagebox.showerror("Error", f"Grafica {tipo_grafico} necesita de los 2 ejes.")
            return
        elif  var_y =='' and tipo_grafico == "Tarta":
            messagebox.showerror("Error", f"Grafica {tipo_grafico} necesita Eje Y.")
            return
        elif  var_x in self.df.columns.to_list() and (tipo_grafico == "Tarta" or tipo_grafico == 'Bigote'):
            messagebox.showerror("Error", f"Grafica {tipo_grafico} No usa El Eje X.")
            return
        else:
            fig, ax = plt.subplots()
            ax.set_facecolor('none')
            fig.patch.set_facecolor('none')
            try:
                if tipo_grafico == "Barra":
                    # Ejemplo: barras de la variable Y agrupadas por X
                    grouped = self.df.groupby(var_x)[var_y].mean()
                    grouped.plot(kind='bar', ax=ax)
                    ax.set_title("Gráfico de Barras")
                elif tipo_grafico == "Tarta":
                    # Pie con distribución de variable X
                    counts = self.df[var_y].value_counts()
                    ax.pie(counts, labels=counts.index, autopct="%1.1f%%")
                    ax.set_title("Gráfico de Tarta")
                elif tipo_grafico == "Linea":
                    ax.plot(self.df[var_x], self.df[var_y])
                    ax.set_title("Gráfico de Línea")
                elif tipo_grafico == "Dispersión":
                    ax.scatter(self.df[var_x], self.df[var_y])
                    ax.set_title("Gráfico de Dispersión")
                elif tipo_grafico == "Bigote":
                    ax.boxplot(self.df[var_y].dropna())
                    ax.set_title("Gráfico de Caja (Bigote)")
                elif tipo_grafico == "Bigote por categoría":
                    categories = self.df[var_x].unique()
                    data = [self.df[self.df[var_x] == cat][var_y].dropna() for cat in categories]
                    ax.boxplot(data, labels=categories)
                    ax.set_title("Bigote por Categoría")
            except Exception as e:
                messagebox.showerror("Error",f"Error:\n{str(e)}")
                return
        hoja = self.dashboard.get().lower().replace(" ", "")
        hojas_frame_ = self.hojas_frame[f"{hoja}_frame"]
        

        nombre  =f"Gráfico {self.num_grafico}"
        frame_movil = MovableResizableFrame(hojas_frame_,300,300)
        frame_movil.figure = fig
        self.frames_movil_graficos[nombre]=frame_movil
        values = [nombre] + list(self.cbo_editar_grafico.cget("values"))
        self.cbo_editar_grafico.configure(values=values)
        self.num_grafico+=1
        frame_movil.place(x=100, y=100)
        frame_movil.pack_propagate(False)

        self.canvas = FigureCanvasTkAgg(fig, master=frame_movil)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def eliminar_grafico(self):
        name_grafico = self.cbo_editar_grafico.get()  # Obtiene el nombre del gráfico seleccionado
        if name_grafico in self.frames_movil_graficos:
            frame = self.frames_movil_graficos[name_grafico]
            frame.destroy()  # Elimina el contenedor del gráfico
            del self.frames_movil_graficos[name_grafico]  # Borra del diccionario

            # Actualiza el combobox para remover el nombre eliminado
            values = list(self.cbo_editar_grafico.cget("values"))
            if name_grafico in values:
                values.remove(name_grafico)
                self.cbo_editar_grafico.configure(values=values)
                self.cbo_editar_grafico.set('')  # Limpia la selección actual
                
    def crear_imagen(self):
        ruta = self.buscar_imagen()
        if not ruta:
            return

        hoja = self.dashboard.get().lower().replace(" ", "")
        hojas_frame_ = self.hojas_frame[f"{hoja}_frame"]

        frame_movil = MovableResizableFrame(hojas_frame_, 300, 300)
        nombre_imagen = f"Imagen {self.num_imagen}"
        self.frames_movil_imagen[nombre_imagen] = frame_movil

        values = [nombre_imagen] + list(self.cbo_editar_imagen.cget("values"))
        self.cbo_editar_imagen.configure(values=values)
        self.cbo_editar_imagen.set(nombre_imagen)
        self.num_imagen += 1

        frame_movil.place(x=100, y=100)
        frame_movil.pack_propagate(False)

        imagen_pil = Image.open(ruta)
        frame_movil.imagen_original = imagen_pil

        imagen_pil.thumbnail((200, 200))
        img = ctk.CTkImage(light_image=imagen_pil, size=imagen_pil.size)

        label_imagen = ctk.CTkLabel(frame_movil, image=img, text="")
        label_imagen.image = img
        label_imagen.pack(expand=True)

        frame_movil.label_imagen = label_imagen
        frame_movil.ruta = ruta
        
    def cambiar_imagen(self):
        nombre = self.cbo_editar_imagen.get()
        if nombre not in self.frames_movil_imagen:
            return

        ruta = self.buscar_imagen()
        if not ruta:
            return

        frame = self.frames_movil_imagen[nombre]
        for widget in frame.winfo_children():
            widget.destroy()

        imagen_pil = Image.open(ruta)
        imagen_pil.thumbnail((280, 280))
        img = ImageTk.PhotoImage(imagen_pil)

        label_imagen = ctk.CTkLabel(frame, image=img, text="")
        label_imagen.image = img
        label_imagen.pack(expand=True)

        frame.ruta = ruta

    def eliminar_imagen(self):
        nombre = self.cbo_editar_imagen.get()
        if nombre in self.frames_movil_imagen:
            frame = self.frames_movil_imagen[nombre]
            frame.destroy()
            del self.frames_movil_imagen[nombre]

            # Actualiza el combobox
            values = list(self.cbo_editar_imagen.cget("values"))
            if nombre in values:
                values.remove(nombre)
                self.cbo_editar_imagen.configure(values=values)
                self.cbo_editar_imagen.set('')
    
    def cambiar_fondo_hoja(self, opcion):
        # Asocia opciones a colores
        colores = {
            "Blanco": "#ffffff",  # Blanco
            "Gris claro": "#f0f0f0",  # Gris claro
            "Azul muy claro": "#e6f7ff",   # Azul muy claro
            "SunGlow":"#FFC857",
            "Burnt Siena":"#E9724C",
            "Cardinal":"#C5283D",
            "Chocolate Cosmos":"#481D24",
            "Lapiz Lazuli":"#255F85",
            "Beige":"#F3FAE1",
        }

        color_fondo = colores.get(opcion)
        if not color_fondo:
            return

        hoja = self.dashboard.get().lower().replace(" ", "")
        frame_hoja = self.hojas_frame.get(f"{hoja}_frame")
        
        if frame_hoja:
            frame_hoja.configure(fg_color=color_fondo)
        else:
            messagebox.showerror("Error", "No se pudo encontrar la hoja actual.")
    
    def guardar_hoja_csv(self):
        hoja = self.dashboard.get().lower().replace(" ", "")
        frame_hoja = self.hojas_frame.get(f"{hoja}_frame")

        if not frame_hoja:
            messagebox.showerror("Error", "No se encontró la hoja actual.")
            return

        datos = []

        # 🔤 Textos
        for nombre, frame in self.frames_movil_text_box.items():
            if frame.master == frame_hoja:
                textbox = frame.winfo_children()[0]
                contenido = textbox.get("0.0", "end-1c")
                datos.append(["Texto", nombre, contenido])

        # 📈 Gráficos
        for nombre, frame in self.frames_movil_graficos.items():
            if frame.master == frame_hoja:
                # Intenta identificar el tipo de gráfico desde el título del eje
                fig = self.canvas.figure
                title = fig.axes[0].get_title() if fig.axes else "Gráfico"
                datos.append(["Gráfico", nombre, f"Tipo: {title}"])

        # 🖼️ Imágenes
        for nombre, frame in self.frames_movil_imagen.items():
            if frame.master == frame_hoja:
                ruta = getattr(frame, "ruta", "Desconocida")
                datos.append(["Imagen", nombre, f"Ruta: {ruta}"])

        if not datos:
            messagebox.showerror("Error", "No hay elementos en esta hoja.")
            return

        # 📝 Guardar en CSV
        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv")],
                                                    title="Guardar hoja como CSV")

        if not ruta_archivo:
            return  # Cancelado por el usuario

        with open(ruta_archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tipo", "Nombre", "Contenido"])
            writer.writerows(datos)

        messagebox.showinfo("Guardado", f"Hoja guardada en {ruta_archivo}")

    def actualizar_sliders(self, tipo, seleccionado):
        print(self.valores_ajustes)
        
        # Obtener ajustes guardados (o dict vacío si no hay)
        ajustes = self.valores_ajustes[tipo].get(seleccionado, {})
        
        # Lista de todos los ajustes que manejas
        lista_ajustes = ["Size", "Width", "Height", "Redondear", "Relleno", "Color"]

        for ajuste in lista_ajustes:
            valor = ajustes.get(ajuste, 0)
            slider = self.ajustes_graficos.get(f"sld_{ajuste}")
            if slider:
                original_command = slider._command
                slider.configure(command=None)
                slider.set(valor)
                slider.configure(command=original_command)



    def aplicar_formato(self, valor, ajuste):
        valor = int(valor)

        seleccionado = self.cbo_editar_texto.get()
        tipo = "texto"
        if not seleccionado:
            seleccionado = self.cbo_editar_grafico.get()
            tipo = "grafico"
        if not seleccionado:
            seleccionado = self.cbo_editar_imagen.get()
            tipo = "imagen"
        if not seleccionado:
            return
        
         # Guardar el valor del slider para este objeto y ajuste
        if seleccionado not in self.valores_ajustes[tipo]:
            self.valores_ajustes[tipo][seleccionado] = {}
        self.valores_ajustes[tipo][seleccionado][ajuste] = valor

        if tipo == "texto":
            frame = self.frames_movil_text_box.get(seleccionado)
            base_height = 200
            base_width = 400
        elif tipo == "grafico":
            frame = self.frames_movil_graficos.get(seleccionado)
            base = 300
        elif tipo == "imagen":
            frame = self.frames_movil_imagen.get(seleccionado)
            base = 300
        else:
            return

        if not frame:
            print("No has seleccionado Elemento")
            return
        # Aplica cambios según el ajuste
        
        if ajuste == "Size":
            
            
            if tipo == "grafico" or tipo == "imagen":
                new_size = base + valor # base + valor
                frame.configure(width=new_size, height=new_size)
                frame.place_configure(width=new_size, height=new_size)
            if tipo == "texto":
                new_heigth = base_height + valor
                new_width = base_width + valor 
                frame.configure(width=new_width, height=new_heigth)
                frame.place_configure(width=new_width, height=new_heigth)
            
            
            slider = self.ajustes_graficos["sld_Width"]
            # Guardar y quitar el command
            original_command = slider._command
            slider.configure(command=None)
            # Actualizar sin disparar la función
            slider.set(valor)
            # Volver a poner el command
            slider.configure(command=original_command)

            slider = self.ajustes_graficos["sld_Height"]
            original_command = slider._command
            slider.configure(command=None)
            slider.set(valor)
            slider.configure(command=original_command)

            if tipo == "imagen":
                # Redimensionar la imagen original para que encaje en el nuevo tamaño
                imagen_resized = frame.imagen_original.copy()
                imagen_resized.thumbnail((new_size, new_size))

                img = ctk.CTkImage(light_image=imagen_resized, size=imagen_resized.size)
                frame.label_imagen.configure(image=img)
                frame.label_imagen.image = img

        elif ajuste == "Width":

            current_height = frame.winfo_height()
           
            width_new = (base_width if tipo=="texto" else base) + valor
            
            frame.configure(width=width_new)
            frame.place_configure(width=width_new, height=current_height)


        elif ajuste == "Height":
            current_width = frame.winfo_width()

            heigth_new = (base_height if tipo=="texto" else base) + valor
            frame.configure(height=heigth_new)
            frame.place_configure(width=current_width, height=heigth_new)

        elif ajuste == "Redondear":
            valor = valor+100
            # Asume que el frame tiene atributo corner_radius si es CTkFrame personalizado
            if hasattr(frame, 'configure'):
                try:
                    frame.configure(corner_radius=int(valor / 10))
                except:
                    pass  # algunos widgets pueden no soportar esto

        elif ajuste == "Relleno":
            valor =valor+100
            # Valor entre 0 y 200
            h = min(valor * 1.8, 360)  # Escalar a [0, 360]
            
            # Convertir HSV → RGB
            r, g, b = colorsys.hsv_to_rgb(h / 360, 1.0, 1.0)

            # Si el valor es mayor a 180, mezclamos hacia blanco
            if valor > 180:
                t = (valor - 180) / 20  # de 0 a 1
                r = r * (1 - t) + 1 * t
                g = g * (1 - t) + 1 * t
                b = b * (1 - t) + 1 * t

            # RGB → HEX
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            # Aplica el color al frame    
            if tipo == "grafico":
                try:
                    if hasattr(frame, "figure"):
                        fig = frame.figure
                        if fig.axes:
                            ax = fig.axes[0]
                            fig.patch.set_facecolor(hex_color)
                            ax.set_facecolor(hex_color)
                            fig.canvas.draw()
                            fig.canvas.get_tk_widget().update()
                            print(f"[INFO] Fondo del gráfico '{seleccionado}' cambiado a {hex_color}")
                        else:
                            print(f"[ERROR] El gráfico '{seleccionado}' no tiene ejes.")
                    else:
                        print(f"[ERROR] El frame '{seleccionado}' no tiene atributo 'figure'")
                except Exception as e:
                    print(f"[ERROR] No se pudo actualizar fondo del gráfico '{seleccionado}':", e)

            else:
                # Aplicar color de fondo a widgets normales (texto, imagen, etc.)
                try:
                    frame.configure(fg_color=hex_color)
                except Exception:
                    pass
                for hijo in frame.winfo_children():
                    try:
                        hijo.configure(fg_color=hex_color)
                    except Exception:
                        pass

        elif ajuste == "Color":
            valor = valor+100
            h = min(valor * 1.8, 360)  # Escalar a [0, 360] (matiz)

            # HSV → RGB
            r, g, b = colorsys.hsv_to_rgb(h / 360, 1.0, 1.0)

            # Si el valor es mayor a 180, mezclar hacia negro
            if valor > 180:
                t = (valor - 180) / 20  # de 0 a 1
                t = min(t, 1.0)  # limitar por seguridad
                r = r * (1 - t)
                g = g * (1 - t)
                b = b * (1 - t)

            # RGB → HEX
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

            # Aplicar el color según el tipo
            if tipo == "texto":
                try:
                    for hijo in frame.winfo_children():
                        hijo.configure(fg=hex_color)
                except Exception:
                    pass

            elif tipo == "grafico":
                try:
                    if hasattr(frame, "figure"):
                        fig = frame.figure
                        if fig.axes:
                            ax = fig.axes[0]

                            # Cambiar colores del título, etiquetas y ejes
                            ax.title.set_color(hex_color)
                            ax.xaxis.label.set_color(hex_color)
                            ax.yaxis.label.set_color(hex_color)
                            ax.tick_params(axis='x', colors=hex_color)
                            ax.tick_params(axis='y', colors=hex_color)

                            # Cambiar colores de etiquetas de ticks
                            for label in ax.get_xticklabels():
                                label.set_color(hex_color)
                            for label in ax.get_yticklabels():
                                label.set_color(hex_color)

                            fig.canvas.draw()
                            fig.canvas.get_tk_widget().update()
                            print(f"[INFO] Color del gráfico '{seleccionado}' actualizado a {hex_color}")
                        else:
                            print(f"[ERROR] El gráfico '{seleccionado}' no tiene ejes.")
                    else:
                        print(f"[ERROR] El frame '{seleccionado}' no tiene figura asociada.")
                except Exception as e:
                    print(f"[ERROR] No se pudo actualizar color del gráfico '{seleccionado}':", e)

            elif tipo == "imagen":
                pass

    def __form_setting(self):
        popup_setting = ctk.CTkToplevel(self,
                                        fg_color=self.color.COLOR_FONDO_FRAME,
                                        )
        
                #centrar ventana
        popup_setting.update()
        center_window(popup_setting)

                # Poner en primer plano con foco
        popup_setting.transient(self)
        popup_setting.focus_force()
        popup_setting.lift()
        popup_setting.grab_set()
        
        ctk.CTkLabel(popup_setting,
                     text="Mi Tabla",
                     text_color=self.color.COLOR_LETRA_NORMAL
                     ).grid(row=1,column=0,padx=10,pady=10)
        
        cbo_set_table=ctk.CTkComboBox(popup_setting,
                        values=self.table_name_list,
                        state="readonly",
                        button_color=self.color.COLOR_RELLENO_WIDGET
                        )
        cbo_set_table.grid(row=1,column=1,padx=10,pady=10)
        
        ctk.CTkLabel(popup_setting,
                     text="Color Fondo",
                     text_color=self.color.COLOR_LETRA_NORMAL,
                     ).grid(row=2,column=0,padx=10,pady=10)
        
        df_color = colores.ColorDataFrame()
        lista_colores = df_color.get_list_color()
        cbo_color_fondo = ctk.CTkComboBox(popup_setting,
                        values=lista_colores,
                        state="readonly",
                        button_color=self.color.COLOR_RELLENO_WIDGET)
        cbo_color_fondo.grid(row=2,column=1,padx=10,pady=10)

        def cerrar():
            popup_setting.destroy()

        ctk.CTkButton(popup_setting,
                      text="Cancelar",
                      command=cerrar,
                      ).grid(row=3,column=0,padx=10,pady=10)
        ctk.CTkButton(popup_setting,
                      text="Aplicar",
                      command=lambda:self.actualizar_interfaz(
                          cbo_color_fondo.get(),
                          cbo_set_table.get(),
                          popup_setting
                      ),
                      ).grid(row=3,column=1,padx=10,pady=10)
        

    def actualizar_interfaz(self,color_mode,tabla_actual,popup):    
        if self.mode != color_mode and color_mode!='':
            saving_config(color_mode,"COLOR_MODE")
            self.mode = color_mode

        
        if tabla_actual != self.table_name  and tabla_actual !='':
            self.table_name = tabla_actual
            saving_config(tabla_actual,"TABLA_NAME")
            self.importar_from_bbdd
            engine = config.VAR_CONEXION + self.db_name
            try:
                self.df = pd.read_sql(f"SELECT * FROM {self.table_name}", engine)
                self.show_tree_viewport()
                
            except sqlalchemy.exc.OperationalError as e:
                messagebox.showerror("Error",f"Error al conectar con la base de datos o al consultar la tabla:{e}")
                print("Error al conectar con la base de datos o al consultar la tabla:")
                print(str(e))

        popup.destroy()


    def __form_task(self):
        popup_task = ctk.CTkToplevel(self, fg_color=self.color.COLOR_FONDO_FRAME)
        popup_task.title("Notas")
        popup_task.geometry("270x290")
        popup_task.resizable(False, False)

        popup_task.update()
        center_window(popup_task)

        popup_task.transient(self)
        popup_task.focus_force()
        popup_task.lift()
        popup_task.grab_set()

        # Configurar columnas simétricas
        for i in range(4):
            popup_task.grid_columnconfigure(i, weight=1)

        # Frame principal con scroll
        scroll_frame = ctk.CTkScrollableFrame(popup_task,
                                            fg_color=self.color.COLOR_FONDO_APP)
        scroll_frame.grid(row=1, column=0, rowspan=4, columnspan=4, padx=10, pady=10)

        self.botones_nota = []
        self.max_botones_nota = 12
        self.botones_por_fila_nota = 3

        def abrir_ventana_nota(id_nota):
            nota_window = ctk.CTkToplevel(popup_task)
            nota_window.title(f"Nota {id_nota}")
            nota_window.geometry("300x300")
            nota_window.resizable(False, False)
            nota_window.update()
            center_window(nota_window)

            # Ventana modal y en foco
            nota_window.transient(self)
            nota_window.grab_set()
            nota_window.lift()
            nota_window.focus_force()

            textbox = ctk.CTkTextbox(nota_window, width=280, height=200)
            textbox.pack(padx=10, pady=(10, 5), expand=True, fill="both")
            textbox.focus_set()
            # Si ya existe contenido, cargarlo
            if id_nota in self.notas_guardadas:
                textbox.insert("0.0", self.notas_guardadas[id_nota])

            btn_frame = ctk.CTkFrame(nota_window, fg_color="transparent")
            btn_frame.pack(pady=10)

            def guardar():
                contenido = textbox.get("0.0", "end").strip()
                self.notas_guardadas[id_nota] = contenido
                nota_window.destroy()

            def cancelar():
                nota_window.destroy()

            btn_guardar = ctk.CTkButton(btn_frame, text="Guardar", command=guardar, width=100)
            btn_cancelar = ctk.CTkButton(btn_frame, text="Cancelar", command=cancelar, width=100)
            btn_guardar.grid(row=0, column=0, padx=5)
            btn_cancelar.grid(row=0, column=1, padx=5)

        def añadir_boton():
            if len(self.botones_nota) >= self.max_botones_nota:
                return

            fila = len(self.botones_nota) // self.botones_por_fila_nota
            columna = len(self.botones_nota) % self.botones_por_fila_nota
            indice = len(self.botones_nota) + 1

            nuevo_boton = ctk.CTkButton(scroll_frame,
                                        text=f"Nota {indice}",
                                        width=55,
                                        fg_color=self.color.COLOR_RELLENO_WIDGET,
                                        command=lambda i=indice: abrir_ventana_nota(i))
            nuevo_boton.grid(row=fila, column=columna, padx=10, pady=10)
            self.botones_nota.append(nuevo_boton)

        def cerrar():
            popup_task.destroy()

        boton_agregar = ctk.CTkButton(popup_task, text="+", width=40, height=40,
                                    command=añadir_boton,
                                    fg_color=self.color.COLOR_RELLENO_WIDGET)
        boton_agregar.grid(row=5, column=1, pady=10, padx=10)

        boton_cerrar = ctk.CTkButton(popup_task, text="Cerrar", width=40, height=40,
                                    command=cerrar,
                                    fg_color=self.color.COLOR_RELLENO_WIDGET)
        boton_cerrar.grid(row=5, column=2, pady=10, padx=10)

        

        # Luego recorres notas_guardadas
        for i in range(1, len(self.notas_guardadas) + 1):
            añadir_boton()  # Esto crea el botón nuevamente y lo vincula con abrir_ventana_nota(i)
            

        

    def set_options(self):
        tipo = self.df[self.y].dtype
        if self.tipo_problema == "Regresion":
            self.cbo_modelo.configure(values=[
                                            'Linear Regression',
                                            'Random Forest Regressor',
                                            'Decision Tree Regressor',
                                            'Svm Regressor',
                                            'Knn Regressor',
                                            
            ])
            self.cbo_scoring.configure(values=[
                                      "MSE",
                                      "RMSE",
                                      "MEA",
                                      "R²",
            ])
        elif self.tipo_problema=="Clasificacion":
            self.cbo_modelo.configure(values=[
                                            'Logistic Regression',
                                            'Random Forest Classifier',
                                            'Decision Tree Classifier',
                                            'Svm Classifier',
                                            'Knn Classifier',
                                            'Naive Bayes',
            ])
            self.cbo_scoring.configure(values=[
                                      "Accuracy",
                                      "f1",
                                      "ROC AUC",
                                      "Precisión"
            ])
        else:
            print("Vtipo de variable no válida")
    def train_model(self,type_search):
        mapear_modelos = {
            'Linear Regression':"linear_regression",
            'Random Forest Regressor':"random_forest_regressor",
            'Decision Tree Regressor':"decision_tree_regressor",
            'Svm Regressor':"svm_regressor",
            'Knn Regressor':"knn_regressor",
            'Logistic Regression':"logistic_regression",
            'Random Forest Classifier':"random_forest_classifier",
            'Decision Tree Classifier':"decision_tree_classifier",
            'Svm Classifier':"svm_classifier",
            'Knn Classifier':"knn_classifier",
            'Naive Bayes':"naive_bayes",
        }

        function_models = {
            # Regresores
            "linear_regression": LinearRegression,
            "random_forest_regressor": RandomForestRegressor,
            "decision_tree_regressor": DecisionTreeRegressor,
            "svm_regressor": SVR,
            "knn_regressor": KNeighborsRegressor,
            "logistic_regression": LogisticRegression,
            "random_forest_classifier": RandomForestClassifier,
            "decision_tree_classifier": DecisionTreeClassifier,
            "svm_classifier": SVC,
            "knn_classifier": KNeighborsClassifier,
            "naive_bayes": GaussianNB,
        }
        if self.y == None:
            messagebox.showwarning(
                "Variable Dependiente",
                "No has seleccionado ninguna variable dependiente"
            )
            print("Variable Dependiente","No has seleccionado ninguna variable dependiente")
            return
        
        select_model = self.cbo_modelo.get()
        if select_model not in list(mapear_modelos.keys()):
            messagebox.showwarning("Modelo no válido",f"El modelo seleccionado no es válido.Valor = {select_model}")
            print("Modelo no válido",f"El modelo seleccionado no es válido.Valor = {select_model}")
            return
        
        name_model = mapear_modelos.get(select_model)
        model = function_models.get(name_model)
        model = model()

        if self.tipo_problema not in ["Regresion","Clasificacion"]:
             messagebox.showerror("Tipo Problema",f"No has seleccionado un tipo válido: '{self.tipo_problema}'")

        
        scoring = self.cbo_scoring.get()
        if self.tipo_problema == "Regresion" and scoring not in ["MSE", "RMSE", "MEA", "R²"]:
            messagebox.showerror("Scoring",f"No has seleccionado scoring válido para el Regresor: '{scoring}'")
            print("Scoring",f"No has seleccionado scoring válido: '{scoring}'")
            return
        elif self.tipo_problema == "Clasificacion" and scoring not in ["Accuracy", "f1", "ROC AUC", "Precisión"]:
            messagebox.showerror("Scoring",f"No has seleccionado scoring válido: para el Clasificador '{scoring}'")
            print("Scoring",f"No has seleccionado scoring válido: '{scoring}'")
            return
        else:
            print("Scoring",f"Scoring válido: '{scoring}'")

        X = self.df.drop(columns=[self.y])
        y = self.df[self.y]

        print("Shape de X:", X.shape)
        print("Shape de y:", y.shape)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        # Determinar el nombre de la métrica y calcularla
        nombre_metrica = self.cbo_scoring.get()
        if type_search not in ["Randomized Search CV","Grid Search CV"]:
            print("SIN busqueda de hiperparametros")
            try:


                print("Entrenando modelo sin hiperparametros")
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_train = model.predict(X_train)

                if nombre_metrica == "MSE":
                    rendimiento = mean_squared_error(y_test, y_pred)
                    rendimiento_train = mean_squared_error(y_train, y_pred_train)
                elif nombre_metrica == "RMSE":
                    rendimiento = root_mean_squared_error(y_test, y_pred)
                    rendimiento_train = root_mean_squared_error(y_train, y_pred_train)
                elif nombre_metrica == "MEA":
                    rendimiento = mean_absolute_error(y_test, y_pred)
                    rendimiento_train = mean_absolute_error(y_train, y_pred_train)
                elif nombre_metrica == "R²":
                    rendimiento = r2_score(y_test, y_pred)
                    rendimiento_train = r2_score(y_train, y_pred_train)
                elif nombre_metrica == "Accuracy":
                    rendimiento = accuracy_score(y_test, y_pred)
                    rendimiento_train = accuracy_score(y_train, y_pred_train)
                elif nombre_metrica == "f1":
                    rendimiento = f1_score(y_test, y_pred, average="weighted")
                    rendimiento_train = f1_score(y_train, y_pred_train,average='weighted')
                elif nombre_metrica == "ROC AUC":
                    try:
                        rendimiento = roc_auc_score(y_test, model.predict_proba(X_test), multi_class="ovr")
                        rendimiento_train = roc_auc_score(y_train, model.predict_proba(X_train), multi_class="ovr")
                    except:
                        rendimiento = "No disponible (predict_proba no soportado)"
                elif nombre_metrica == "Precisión":
                    rendimiento = precision_score(y_test, y_pred, average="weighted")
                    rendimiento_train = precision_score(y_train, y_pred_train, average="weighted")
                else:
                    rendimiento = "Métrica desconocida"

                # Crear nombre del botón y ventana
                nombre = f"Modelo {self.contador_modelos} : {select_model}"
                predictoras = list(self.df.columns)
                predictoras.remove(self.y)
                info = f"""Modelo: {select_model}
                           \nVariable Dependiente: {self.y}
                           \nVariables Predictoras: {",".join(predictoras)}
                           \n{nombre_metrica.capitalize()+" (en train"}: {round(rendimiento_train, 4) if isinstance(rendimiento_train, (float, int)) else rendimiento_train}
                           \n{nombre_metrica.capitalize()+" (en test)"}: {round(rendimiento, 4) if isinstance(rendimiento, (float, int)) else rendimiento}"""
                self.agregar_btn_modelo_entrenado(nombre, info)
                self.contador_modelos += 1
                print("rendimiento_train",rendimiento_train)
                print("Rendimiento:",rendimiento)

            except Exception as ex:
                messagebox.showerror("Error",ex)
                print(ex)
                return

        # VERIFICA QUE LOS VALORES CV Y PARAMS SEAN CORRECTOS
        if  type_search in ["Grid Search CV","Randomized Search CV"]:
        
            scoring = {
                "MSE": "neg_mean_squared_error",
                "RMSE": "neg_root_mean_squared_error",
                "MAE": "neg_mean_absolute_error",
                "R²": "r2",
                "Accuracy": "accuracy",
                "f1": "f1",
                "ROC AUC": "roc_auc",
                "Precisión": "precision"
            }.get(self.cbo_scoring.get())

            cv_str = self.spin_cv.get()
            try:
                cv = int(cv_str)
            except ValueError:
                messagebox.showerror("CV", f"El valor de Validación Cruzada no es válido. Debe ser un número entero. Se obtuvo '{cv_str}'")
                return
            
            import ast
            try:
                texto = self.area_params.get("1.0", "end-1c").strip()
                if not texto :
                    messagebox.showerror("Hiperparametros",f"No puede esatar vacio los hiperparamtros. Se obtuvo {texto}")
                    print("Hiperparametros",f"No puede esatar vacio los hiperparamtros {texto}")
                    return
                print("Hiperparametros:")
                print(texto)
                params = ast.literal_eval(texto)
                
            except Exception as e:
                messagebox.showerror("Error de parámetros", f"El formato de los hiperparámetros no es válido:\n{e}")
                print("Error de parámetros", f"El formato de los hiperparámetros no es válido:\n{e}")
                return
            

            if type_search == "Grid Search CV":
                print("Entrenando GridSearhCV")
                search = GridSearchCV(
                    estimator =model,
                    param_grid=params,
                    scoring=scoring,
                    cv = cv,
                    n_jobs=-1
                )
                search.fit(X_train,y_train)

                y_pred = search.best_estimator_.predict(X_test)
                if self.tipo_problema == "Regresion":
                    rendimiento = mean_squared_error(y_true=y_test,y_pred=y_pred)
                elif self.tipo_problema == "Clasificacion":
                    rendimiento  = accuracy_score(y_true=y_test,y_pred=y_pred)
                else:
                    rendimiento = "Desconocido"
                    
                print("Rendimiento del mejor(Grid):",rendimiento)
                # Crear nombre del botón y ventana
                nombre = f"Modelo {self.contador_modelos} : {select_model}"
                predictoras = list(self.df.columns)
                predictoras.remove(self.y)
                info = f"""Modelo: {select_model}
                           \nVariable Dependiente: {self.y}
                           \nVariables Predictoras: {",".join(predictoras)}
                           \n{nombre_metrica.capitalize() +"(en test)"}: {round(rendimiento, 4) if isinstance(rendimiento, (float, int)) else rendimiento}
                           \nTipo Busqueda: {type_search}
                           \nCV: {cv}
                           \nMejores parametros: {search.best_params_}
                           \nScore del Mejor Estimador (en validación): {-round(search.best_score_,4)}"""
                self.agregar_btn_modelo_entrenado(nombre, info)
                self.contador_modelos += 1

            elif type_search =="Randomized Search CV":
                print("Entrenando RandomizedSearchCV")
                search = RandomizedSearchCV(
                    estimator=model,
                    param_distributions=params,
                    cv=cv,
                    scoring=scoring,
                    n_jobs=-1,
                    random_state=42
                )
                search.fit(X_train,y_train)
                y_pred = search.best_estimator_.predict(X_test)
                rendimiento = mean_squared_error(y_true=y_test,y_pred=y_pred)
                print("Rendimiento del mejor (Randomized):",rendimiento)
                                # Crear nombre del botón y ventana
                nombre = f"Modelo {self.contador_modelos} : {select_model}"
                predictoras = list(self.df.columns)
                predictoras.remove(self.y)
                info = f"""Modelo: {select_model}
                           \nVariable Dependiente: {self.y}
                           \nVariables Predictoras: {",".join(predictoras)}
                           \n{nombre_metrica.capitalize()} +"(en test)": {round(rendimiento, 4) if isinstance(rendimiento, (float, int)) else rendimiento}
                           \nTipo Busqueda: {type_search}
                           \nCV: {cv}
                           \nMejores parametros: {search.best_params_}
                           \nScore del Mejor Estimador (en validación): {-search.best_score_}"""
                self.agregar_btn_modelo_entrenado(nombre, info)
                self.contador_modelos += 1

            
    def agregar_btn_modelo_entrenado(self, nombre_modelo, info_texto):
        if not hasattr(self, 'modelo_count'):
            self.modelo_count = len(self.frame_modelos.grid_slaves())

        fila = self.modelo_count // 5
        columna = self.modelo_count % 5

        # frame = ctk.CTkFrame(self.frame_modelos)
        # frame.grid(row=fila, column=columna, padx=10, pady=10)

        btn_info = ctk.CTkButton(self.frame_modelos, text=nombre_modelo,
                                command=lambda: self.mostrar_info_modelo(nombre_modelo, info_texto),
                                fg_color=self.color.COLOR_RELLENO_WIDGET)
        btn_info.grid(row=fila,column=columna,padx=10,pady=10,sticky="snew")

        # Asegurar que la columna se expanda proporcionalmente
        #self.frame_modelos.grid_columnconfigure(columna, weight=1)

        self.modelo_count += 1

    def mostrar_info_modelo(self, nombre, info):
        ventana = ctk.CTkToplevel(self,fg_color=self.color.COLOR_FONDO_FRAME)
        ventana.title(nombre)
        ventana.resizable(False,False)
        #ventana.geometry("300x200")
        ventana.transient(self)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()
        ventana.update()
        
        label = ctk.CTkLabel(ventana, text=info, justify="left", padx=10, pady=10)
        label.pack(fill="both", expand=True)
        

    def calcular_metricas(modelo,X_test,y_test,tipo_modelo):
        y_pred = modelo.predict(X_test)
        print("calculadon metrica.............................................")

        if tipo_modelo == "regresion":
            mse = round(mean_squared_error(y_test, y_pred),4)
            rmse = round(np.sqrt(mse),4)
            r2 = round(r2_score(y_test, y_pred),4)
            return {"mse":mse,"rmse":rmse,"R^2": r2},200
        elif tipo_modelo == "clasificacion":
            y_scores = modelo.predict_proba(X_test)[:,1]
            report = classification_report(y_true= y_test,y_pred=y_pred)
            print(report)
            matriz_confusion = confusion_matrix(y_true=y_test,y_pred=y_pred).tolist()
            print(matriz_confusion)
            fpr,tpr,_ = roc_curve(y_test,y_scores)
            auc_score = round(auc(fpr,tpr),4)
            return {"report":report,"matriz_confusion":matriz_confusion,"auc_score": auc_score},200
        else:
            return {"error":"No se ha encontrado el modelo elegido"},400




    def guardar_en_bbdd(self):
        print("--- Guardar cambios----")
        if self.df is None:
            messagebox.showinfo("No hay tabla","Debe cargar una tabla para guardarla en bbdd")
        nombre_tabla = self.table_name
        try:
             
            url_engine = f"mysql+mysqlconnector://cliente:cliente1234@localhost/"
            print("url engine:", url_engine)


            engine_root = sqlalchemy.create_engine(url_engine)
            db_name = self.db_name
            with engine_root.connect() as conn:
                conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

            engine = sqlalchemy.create_engine(f"{url_engine}{db_name}")
            print("exportando a MySQL la tabla", nombre_tabla)
            self.df.to_sql(name=nombre_tabla, con=engine, if_exists='replace', index=False)

            print(f"DataFrame guardado en la base de datos '{db_name}'")
            print("Saliendo de funcion datos> crear_db_clientes()")
            messagebox.showinfo(
                title="Exito",
                message="Cambios Aplicados correctamente"
            )
        except Exception as ex:
            print(ex)
            messagebox.showerror(
                title="Error",
                message=ex
            )

    def buscar_imagen(self):
        return filedialog.askopenfilename(
            title="Selecciona Imagen (png,jpg,etc)",
            filetypes=[("Archivos de Imagen","*.png *.jpg *.jpeg *.gif")]
        )


    def __style_for_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")  # o "clam" para otro look moderno

        # Estilo general de la tabla
        style.configure("Treeview",
                        background=self.color.COLOR_FONDO_FRAME,     # fondo de las filas
                        foreground=self.color.COLOR_LETRA_NORMAL,        # color del texto
                        rowheight=30,               # altura de filas
                        fieldbackground="#88001f",  # fondo cuando la tabla tiene focus
                        bordercolor="#cccccc", 
                        borderwidth=1)

        # Estilo cuando seleccionas una fila
        style.map("Treeview",
                background=[("selected", self.color.COLOR_BORDE_WIDGET),("active", "#acacac")],    # color de fondo al seleccionar
                foreground=[("selected", self.color.COLOR_LETRA_NORMAL),("active", "black")])      # color de texto al seleccionar

        # Estilo de los encabezados (columnas)
        style.configure("Treeview.Heading",
                        background=self.color.COLOR_RELLENO_WIDGET,
                        foreground= self.color.COLOR_BORDE_WIDGET,
                        padding=(10, 10),
                        font=("Arial", 10, "bold"))



    

