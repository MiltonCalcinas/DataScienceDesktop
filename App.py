import customtkinter as ctk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage 
import pandas as pd
import numpy as np
from frame_movil import MovableResizableFrame
import requests
import json
import config
import os
from PIL import Image

class App(ctk.CTk):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.url_csv = None
        self.url_csv = None
        


        self.crear_interfaz()

    def crear_interfaz(self):
        self.title("Crear Pestañaas")
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
        menu.pack(side="top",fill="x",expand=True,padx=10)
        
 
        img_task = ctk.CTkImage(light_image=Image.open(r"iconos\ico_task.png"),size=(20,20))
        btn_task= ctk.CTkButton(menu,
                                image=img_task,
                                text="",
                                width=20,
                                command=self.__form_task)
        btn_task.grid(row=0,column=0,padx=(0,10))

        img_setting = ctk.CTkImage(light_image=Image.open(r"iconos\ico_setting.png"),size=(20,20))
        btn_setting= ctk.CTkButton(menu,
                                image=img_setting,
                                text="",
                                width=20)
        btn_setting.grid(row=0,column=1)


    def crear_notebook(self):
        """         CON ESTE CODIGO CREA EL NOTEBOOK Y LAS PESTAÑAS (LUEGO AÑADO LOS OBJETOS,ETC)        """
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both",expand=True,padx=10,pady=10)
        
        self.tab1 = self.notebook.add("Procesar")
        self.tab2 = self.notebook.add("Entrenamiento")
        self.tab3 = self.notebook.add("Dashboard")


    def __solicitud_post_csv(self,encoding,sep):
        
        if self.url_csv is None or encoding == "" or sep == "":
            messagebox.showwarning("Campos requeridos", "Por favor, completa todos los campos obligatorios.")
            return
        
        print("--- solicitar post csv")
        print("--datos: ",self.url_csv,encoding,sep)
        with open(self.url_csv,"rb") as f:
            files = {'file': f}
            data = {
                "fuente": "csv",
                "encoding": encoding,
                "sep" : sep,
                
            }
            try:
                response = requests.post(
                    config.VIEW_CARGAR_DATOS,
                    data= data,
                    files=files

                )
                if response.ok :
                    print("✅",response.json())
                    self.form.destroy()
                else:
                    print("❌ Error",response.text)
            except Exception as ex:
                print("❌ Excepción",ex)


        


    def __solicitud_post_excel(self):

        if self.url_excel is None :
            messagebox.showwarning("Campos requeridos", "Por favor, Seleciona el archivo Excel con los datos.")
            return
        
        print("--- solicitar post csv")
        print("--datos: ",self.url_csv)
        
        with open(self.url_excel,"rb") as f:
            files = {'file': f}
            data = {
                "fuente": "excel",
                
            }
            try:
                response = requests.post(
                    config.VIEW_CARGAR_DATOS,
                    data= data,
                    files=files

                )
                if response.ok :
                    print("✅",response.json())
                    self.form.destroy()
                else:
                    print("❌ Error",response.text)
            except Exception as ex:
                print("❌ Excepción",ex)

    def __solicitud_post_conexion_db(self,**kwargs):
        for value in kwargs.values():
            if value == "" or value == None:
                messagebox.showwarning("Campos requeridos","Por favor, Completa los paramtros de la conexion.")
                return

        
        data = {
            "fuente": "SGBD",
            "SGBD":kwargs["SGBD"],
            "nombre_tabla": kwargs["nombre_tabla"],
            "usuario_db": kwargs["usuario_db"],
            "password_db": kwargs["password_db"],
            "db": kwargs["db"],
            "host": kwargs["host"],
            "puerto": kwargs["puerto"],
            "consulta": kwargs["consulta"]
        }

        print("--- Enviando credenciales para que el servidor obtenga la tabla")
        

        try:
            response = requests.post(
                config.VIEW_CARGAR_DATOS,
                data=json.dumps(data),
                headers= {'Content-Type': 'application/json'}
            )
            if response.ok:
                print("✅", response.json())
                self.form.destroy()
            else:
                print("❌ Error", response.text)
                
        except Exception as ex:
            print("❌ Excepción", ex)

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

        

    def __ventana_conexion(self,tipo_bbdd):
        print("--- La fuente de datos seleccionada es :",tipo_bbdd)
        
        if tipo_bbdd == "-- Ninguna":
            return
        
        self.form = ctk.CTkToplevel(self)
        
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
            btn_enviar = ctk.CTkButton(self.form,
                                       text="Enviar",
                                       command=self.__solicitud_post_excel)
            btn_enviar.grid(row=1,column=0,columnspan=2,pady=(10,20))
        
        elif tipo_bbdd.strip() == "Archivo CSV":
            
            self.form.geometry("370x200")

            lbl_file = ctk.CTkLabel(self.form,text="CSV")
            lbl_file.grid(row=0,column=0,padx=(50,20),pady=(20,10),sticky="e")
            txt_file = ctk.CTkEntry(self.form)
            txt_file.configure(state="disabled")

            txt_file.grid(row=0,column=1,padx=(0,10),pady=(20,10))
            btn_file = ctk.CTkButton(self.form,
                                     text="⬅",
                                     width=20,
                                     command=lambda: self.__guardar_url_csv(txt_file))
            btn_file.grid(row=0,column=2,pady=(20,10))
            lbl_encoding = ctk.CTkLabel(self.form,text="encoding")
            lbl_encoding.grid(row=1,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_encoding = ctk.CTkEntry(self.form)
            txt_encoding.grid(row=1,column=1,padx=(0,50),pady=(10,10))
            lbl_sep = ctk.CTkLabel(self.form,text="sep")
            lbl_sep.grid(row=2,column=0,padx=(50,20),pady=(10,10),sticky="e")
            txt_sep = ctk.CTkEntry(self.form)
            txt_sep.grid(row=2,column=1,padx=(0,50),pady=(10,10))
            btn_enviar = ctk.CTkButton(self.form,
                                       text="Enviar",
                                       command=lambda: self.__solicitud_post_csv(
                                                                                 txt_encoding.get(),
                                                                                 txt_sep.get()))
            
            btn_enviar.grid(row=3,column=0,pady=(10,20),columnspan=2)

        elif tipo_bbdd in ["MySQL","PostgreSQL","SQLServer"] :  
            
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
                                       command=lambda: self.__solicitud_post_conexion_db(
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
        header_padre = ctk.CTkFrame(self.tab1,fg_color="#96fba4",corner_radius=20)
        header_padre.pack(side="top",padx=20,pady=(20,10),fill="x")
        header_hijo = ctk.CTkFrame(header_padre,fg_color="#96fbd0",corner_radius=20)
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
                                           command=self.__ventana_conexion)
        cbo_cargar_datos.set("Fuente de Datos")
        cbo_cargar_datos.grid(row=0,column=0,padx=(10,5),sticky="nsew",pady=(0,10))

        cbo_elegir_columnas = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Columna1",
                                          "Columna2",
                                          "Columna3",
                                          "-- Ninguna"
                                           ])
        cbo_elegir_columnas.grid(row=0,column=1,padx=(5,5),sticky="nsew",pady=(0,10))
        cbo_elegir_columnas.set("Elegir Columnas")

        cbo_transformar_variables = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "ln",
                                          "log10",
                                          "sqrt",# raiz cuadrada
                                          "exp",
                                          "square",
                                          "abs",
                                          "-- Ninguna"
                                           ])
        cbo_transformar_variables.grid(row=0,column=2,padx=(5,5),sticky="nsew",pady=(0,10))
        cbo_transformar_variables.set("Transformar Variables")

        cbo_generar_graficos = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Bar",
                                          "Pie",
                                          "Line",
                                          "Area",
                                          "Box",
                                          "Box by Category",
                                               "-- Ninguna"
                                           ])
        cbo_generar_graficos.grid(row=0,column=3,padx=(5,5),sticky="nsew",pady=(0,10))
        cbo_generar_graficos.set("Generar Gráficos")

        cbo_variable_dependiente = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Columna1",
                                          "Columna2",
                                          "Columna3",
                                          "-- Ninguna"
                                           ])
        cbo_variable_dependiente.grid(row=0,column=4,padx=(5,10),sticky="nsew",pady=(0,10))
        cbo_variable_dependiente.set("Variable Dependiente")

        for col in range(5):  # Tienes 5 elementos
            header_hijo.grid_columnconfigure(col, weight=1)
        header_hijo.grid_rowconfigure(1, weight=1)

        # FILA 2: FILTRO , CONVERTIR TIPO, A.N.S., CALCULAR ESTÁDISTICAS,  APLICAR (CAMBIOS)

        txt_filtro = ctk.CTkEntry(header_hijo,placeholder_text="Filtro:")
        txt_filtro.grid(row=1,column=0,padx=(10,5),sticky="nsew")
        cbo_convertir_tipo = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Texto a Número (int)",
                                          "Texto a Número (float)",
                                          "Texto a Fecha (datatime)",
                                          "Texto a Categoría",
                                          "Número a Texto",
                                          "Fecha a Texto",
                                          "-- Ninguna"
                                           ])
        cbo_convertir_tipo.grid(row=1,column=1,padx=(5,5),sticky="nsew")
        cbo_convertir_tipo.set("Convertir Tipo de Datos")
        
        cbo_ANO = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "PCA",
                                          "Kmeans",
                                          "Linkage",
                                          "-- Ninguna"
                                           ])
        cbo_ANO.grid(row=1,column=2,padx=(5,5),sticky="nsew")
        cbo_ANO.set("A. No Superivosado")
        
        cbo_calcular_estadisticas = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Medi",
                                          "Mediana",
                                          "Desviacion Estandar",
                                          "Varianza",
                                          "Mínimo",
                                          "Máximo",
                                          "-- Ninguna"
                                           ])
        cbo_calcular_estadisticas.grid(row=1,column=3,padx=(5,5),sticky="nsew")
        cbo_calcular_estadisticas.set("Estadísticas")

        btn_aplicar = ctk.CTkButton(header_hijo,command=self.aplicar_cambios,text="Aplicar")
        btn_aplicar.grid(row=1,column=4,padx=(5,10),sticky="nsew")

        frame_tabla = ctk.CTkFrame(self.tab1,height=400,fg_color="#96fba4")
        frame_tabla.pack(fill="x",side="top",pady=(10,20),padx=20)
        
        scroll_x = ttk.Scrollbar(frame_tabla,orient="horizontal")
        scroll_x.pack(side="bottom",fill="x")     


        
        """ ------------obteniendo los datos---------------"""
        df = pd.read_csv("datos.csv",sep=",")

        tree = ttk.Treeview(frame_tabla,xscrollcommand=scroll_x.set ,columns=tuple(df.columns), show="headings")
        scroll_x.config(command=tree.xview)

        for col in df.columns:
            tree.heading(col,text=col.capitalize())

        tree.pack(padx=20, pady=20, fill="both", expand=True)

        # Insertar datos
        for vector in df.values:
            tree.insert("","end",values=tuple(vector))


    def crear_entrenamiento(self):
        header_padre = ctk.CTkFrame(self.tab2,fg_color="#ad96fb")
        header_padre.pack(side="top",padx=20,pady=(20,10),fill="x")

        header_hijo = ctk.CTkFrame(header_padre)
        header_hijo.pack(fill="both",padx=10,pady=10)

    # Configurar el grid para que se expanda
        header_hijo.grid_rowconfigure((0,1), weight=1)  # filas 0 y 1
        header_hijo.grid_columnconfigure((0,1,2), weight=1)  # columnas 0 y 1
        header_hijo.grid_columnconfigure(2,weight=1,minsize=50)
        cbo_modelo = ctk.CTkComboBox(header_hijo,
                                     values=[
                                            'Linear Regression',
                                            'Random Forest Regressor',
                                            'Decision Tree Regressor',
                                            'Svm Regressor',
                                            'Knn Regressor',
                                            'Logistic Regression',
                                            'Random Forest Classifier',
                                            'Decision Tree Classifier',
                                            'Svm Classifier',
                                            'Knn Classifier',
                                            'Naive Bayes',
                                     ])
        cbo_modelo.grid(row=0,column=0,padx=(10,5),pady=(0,10),sticky="snew")

        cbo_tipo_busqueda = ctk.CTkComboBox(header_hijo,
                                            values=[
                                                "Grid Search CV",
                                                "Randomized Search CV"
                                            ])
        cbo_tipo_busqueda.grid(row=1,column=0,padx=(10,5),sticky="snew")

        area_params = ctk.CTkEntry(header_hijo,height=40,placeholder_text="Establecer Hiperparámetros (con diccionario {})")
        area_params.grid(row=0,rowspan=2,column=1,columnspan=2,padx=(5,10),sticky="snew")

        frame_btn = ctk.CTkFrame(header_hijo)
        frame_btn.grid(row=0,rowspan=2,column=3,sticky="snew")
        btn_entrenar = ctk.CTkButton(frame_btn,
                                     text="Entrenar",
                                     command=self.__enviar_datos_entrenamiento)
        btn_entrenar.pack(fill="x",expand=True,side="left")

        frame_tabla = ctk.CTkFrame(self.tab2,height=400,fg_color="#ad96fb")
        frame_tabla.pack(fill="x",side="top",pady=(10,20),padx=20)

    def crear_dashboard(self):
        # Frame principal
        header_padre = ctk.CTkFrame(self.tab3, fg_color="#d30000", corner_radius=20)
        header_padre.pack(fill="x")

        # Frame secundario
        header_hijo = ctk.CTkFrame(header_padre, fg_color="#ffa5a5", corner_radius=20)
        header_hijo.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configurar la expansión de filas y columnas
        #header_padre.grid_rowconfigure(0, weight=1)  # Expande la fila 0 de header_padre
        header_padre.grid_columnconfigure(0, weight=1)  # Expande la columna 0 de header_padre

        #header_hijo.grid_rowconfigure(0, weight=1)  # Expande la fila 0 de header_hijo
        header_hijo.grid_columnconfigure(0, weight=1,minsize=100)  # Expande la columna 0 de header_hijo
        header_hijo.grid_columnconfigure(1, weight=1,minsize=200)  # Expande la columna 1 de header_hijo
        header_hijo.grid_columnconfigure(2,weight=1,minsize=300)
        header_hijo.grid_columnconfigure(3,weight=1,minsize=100)

        # Frame de imagen
        frame_img = ctk.CTkFrame(header_hijo)
        frame_img.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        cbo_fondo = ctk.CTkComboBox(frame_img, values=["Opción 1", "Opción 2", "Opción 3"])
        cbo_fondo.pack(pady=(0, 10), fill="x")

        btn_imagen = ctk.CTkButton(frame_img, text="Cargar Imagen", command=self.buscar_imagen)
        btn_imagen.pack(pady=(0, 10), fill="x")

        # Frame de fuente
        frame_fuente = ctk.CTkFrame(header_hijo, corner_radius=10, border_width=2, border_color="#8888aa")
        frame_fuente.grid(row=0, column=1, padx=(0, 10), sticky="nsew")
        frame_fuente.grid_columnconfigure(0,weight=1)
        frame_fuente.grid_columnconfigure(1,weight=1)
        frame_fuente.grid_columnconfigure(2,weight=1)
        frame_fuente.grid_columnconfigure(3,weight=1)

        cbo_fuente = ctk.CTkComboBox(frame_fuente, values=["Arial", "Times New Roman"])
        cbo_fuente.grid(row=0, column=0, columnspan=3, pady=(0, 10),sticky="nsew")

        cbo_size = ctk.CTkComboBox(frame_fuente, values=[str(i) for i in range(10, 25)], width=100)
        cbo_size.grid(row=0, column=3, pady=(0, 10), sticky="nsew")

        btn_negrita = ctk.CTkButton(frame_fuente, text="N", font=("Arial", 12, "bold"), width=10)
        btn_negrita.grid(row=1, column=0)

        btn_cursiva = ctk.CTkButton(frame_fuente, text="C", font=("Arial", 12, "italic"), width=10)
        btn_cursiva.grid(row=1, column=1)

        btn_subrayado = ctk.CTkButton(frame_fuente, text="S", font=("Arial", 12, "underline"), width=10)
        btn_subrayado.grid(row=1, column=2)

        # Frame de configuración de gráfico
        frame_configurar_grafico = ctk.CTkFrame(header_hijo, corner_radius=10, border_width=2, border_color="#8888aa")
        frame_configurar_grafico.grid(row=0, column=2, padx=(0, 10),sticky="nsew")
        frame_configurar_grafico.grid_columnconfigure(0,weight=1)
        frame_configurar_grafico.grid_columnconfigure(1,weight=1)
        frame_configurar_grafico.grid_columnconfigure(2,weight=1)

        cbo_relleno = ctk.CTkComboBox(frame_configurar_grafico)
        cbo_relleno.grid(row=1, column=0, sticky="nsew")

        cbo_contorno = ctk.CTkComboBox(frame_configurar_grafico)
        cbo_contorno.grid(row=1, column=1, sticky="nsew")

        cbo_efectos = ctk.CTkComboBox(frame_configurar_grafico)
        cbo_efectos.grid(row=1, column=2, sticky="nsew")

        # Frame de impresión
        frame_imprimir = ctk.CTkFrame(header_hijo)
        frame_imprimir.grid(row=0, column=3, padx=(0, 10), sticky="nsew")

        btn_vertical = ctk.CTkButton(frame_imprimir, text="Ver Vertical")
        btn_vertical.pack(fill="x", pady=(0, 10))

        btn_imprimir = ctk.CTkButton(frame_imprimir, text="Imprimir como PDF")
        btn_imprimir.pack(fill="x")

        
         # Frame principal (panel)
        panel = ctk.CTkFrame(self.tab3, fg_color="#e90078")
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabview (dashboard) en el panel, 
        self.dashboard = ctk.CTkTabview(panel)
        self.dashboard.pack(side="left", fill="both", expand=True)

        # Menú lateral (panel_graficos) a la derecha
        menu_lateral = ctk.CTkTabview(panel,fg_color="#ff9eb4")
        menu_lateral.pack(side="right", fill="y", padx=(10, 0), pady=10)

        hoja_grafico = menu_lateral.add("Gráficos")
        hoja_formato = menu_lateral.add("Formato")

        panel_graficos = ctk.CTkFrame(hoja_grafico, fg_color="#e96a00")
        panel_graficos.pack(fill="both",  pady=10,expand=True)

        panel_formato = ctk.CTkFrame(hoja_formato,fg_color="#e96a00")
        panel_formato.pack(fill="both",expand=True)

        cuadro_iconos = ctk.CTkFrame(panel_graficos,fg_color="#88001f")
        cuadro_iconos.pack(pady=(0,20))

        cuadro_variables = ctk.CTkFrame(panel_graficos,fg_color="#88001f")
        cuadro_variables.pack(fill="both",expand=True)

        # Agregar las hojas al dashboard y frames (contenido blanco)
        self.hojas = {}
        self.hojas_frame = {}

        for i in range(1,4):
            self.hojas[f"hoja{i}"] = self.dashboard.add(f"Hoja {i}")
            
            self.hojas_frame[f"hoja{i}_frame"] =  ctk.CTkFrame(self.hojas[f"hoja{i}"], fg_color="#ffffff")
            self.hojas_frame[f"hoja{i}_frame"].grid(row=0, column=0, sticky="nsew")
        
            self.hojas[f"hoja{i}"].grid_rowconfigure(0, weight=1) # Asegura que la fila 0 de hoja-i se expanda
            self.hojas[f"hoja{i}"].grid_columnconfigure(0, weight=1)  # Asegura que la columna 0 de hoja-i se expanda


        # # Contenido dentro del frame

        # Agregar más elementos al menú lateral (panel_graficos)
        
        ico_barra = PhotoImage(file=r"iconos\ico_barra.png")

        from PIL import Image  # Necesitarás Pillow instalado

        # Cargar imagen con PIL
        pil_image = Image.open(r"iconos\ico_barra.png")

        # Crear un CTkImage
        my_ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(30,30)) 

        # Agregar Iconos de Gráficos
        btn_graficos = {}
        for i in range(8):
            btn_graficos[f"btn_{i+1}"] = ctk.CTkButton(cuadro_iconos,
                                                    text="",
                                                    image=my_ctk_image,
                                                    width=10,height=10,
                                                    command=self.crear_objeto)
    
        contador = 0
        for row in range(2):
            for col in range(4):
                btn_graficos[f"btn_{contador+1}"].grid(row=row,column=col,padx=5,pady=5)
                contador+=1

        #  Agregar seleccion de Variables
        lbl_var_y = ctk.CTkLabel(cuadro_variables,text="Eje y")
        lbl_var_y.pack()
        cbo_var_y = ctk.CTkComboBox(cuadro_variables,values=["Col 1","Col 2"])
        cbo_var_y.pack()
        lbl_var_x = ctk.CTkLabel(cuadro_variables,text="Eje x")
        lbl_var_x.pack()
        cbo_var_x = ctk.CTkComboBox(cuadro_variables,values=["Col 1","Col 2"])
        cbo_var_x.pack()

        # Agregar componentes de ajustes del gráfico
        ajustes_graficos = {}
        ajustes_nombre = ["Size","Width","Height","Border","Redondear","Relleno","Sombra"]
        for i in range(len(ajustes_nombre)):

            ajustes_graficos[f"lbl_{ajustes_nombre[i]}"] = ctk.CTkLabel(panel_formato,text=ajustes_nombre[i])
            ajustes_graficos[f"lbl_{ajustes_nombre[i]}"].grid(row=i,column=0)

            ajustes_graficos[f"sld_{ajustes_nombre[i]}"] = ctk.CTkSlider(panel_formato)
            ajustes_graficos[f"sld_{ajustes_nombre[i]}"].grid(row=i,column=1)

    def __form_task(self):
        
        if not hasattr(self,'form_task') or not self.form.winfo_exists():
            self.form_task()
            self.title("Crea Una Tarea")
            # lbl_title = 
            # txt_title=

            # lbl_description
            # lbl_description

            # txt_description
            # txt_description

            # lbl_name
            # lbl_name

            # txt_name
            # txt_name
            

            # lbl_db
            # lbl_db

            # txt_db
            # txt_db

            # important
            
            # btn_anotar
            # btn_anotar

    def crear_objeto(self):
        hoja = self.dashboard.get().lower().replace(" ","")
        hojas_frame_ = self.hojas_frame[f"{hoja}_frame"]
        frame_movil = MovableResizableFrame(hojas_frame_)
        frame_movil.place(x=100,y=100)

    def aplicar_cambios(self):
        pass
    def buscar_imagen(self):
        cbo_imagen = filedialog.askopenfilename(
            title="Selecciona Imagen (png,jpg,etc)",
            filetypes=("Archivos de Imagen","*.png *.jpg *.jpeg *.gif")
        )


    def __style_for_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")  # o "clam" para otro look moderno

        # Estilo general de la tabla
        style.configure("Treeview",
                        background="#f58cc2",     # fondo de las filas
                        foreground="black",        # color del texto
                        rowheight=30,               # altura de filas
                        fieldbackground="#88001f",  # fondo cuando la tabla tiene focus
                        bordercolor="#cccccc", 
                        borderwidth=1)

        # Estilo cuando seleccionas una fila
        style.map("Treeview",
                background=[("selected", "#1abc9c")],    # color de fondo al seleccionar
                foreground=[("selected", "white")])      # color de texto al seleccionar

        # Estilo de los encabezados (columnas)
        style.configure("Treeview.Heading",
                        background="#3498db",
                        foreground="white",
                        padding=(10, 10),
                        font=("Arial", 10, "bold"))
        
    def __enviar_datos_entrenamiento(self):
        pass


