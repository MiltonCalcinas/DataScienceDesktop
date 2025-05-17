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
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def center_window(ventana):
    ventana.update_idletasks()  # Asegura que se obtienen dimensiones reales
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = 150
    ventana.geometry(f"+{x}+{y}")

class App(ctk.CTk):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)        
        self.url_csv = None
        self.url_csv = None
        self.df = None
        self.result_statistics = []
        self.graph_widgets = {}
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


    def __filtrar(self):
        self.pop_filter = ctk.CTkToplevel(self)
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

        scroll_frame = ctk.CTkScrollableFrame(self.pop_filter, width=600, height=300)
        scroll_frame.grid(row=0, column=0, padx=10, pady=10)
        self.scroll_frame = scroll_frame  # guardamos referencia

        self.add_variable_filter()

        ctk.CTkButton(self.pop_filter, text="+", width=50,
                    command=self.add_variable_filter).grid(row=1, column=0, padx=(0, 20), pady=(0, 20))

        ctk.CTkButton(self.pop_filter, text="Filtrar", command=self.exe_filter).grid(row=2, column=0, padx=(0, 20), pady=(0, 20))

    def add_variable_filter(self):
        fila = self.filter_row

        # Combobox para seleccionar columna
        cbo_columna = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns))
        cbo_columna.grid(row=fila, column=0, padx=20, pady=(10 if fila == 0 else 5))

        # Combobox para seleccionar operador (se actualizará dinámicamente)
        cbo_operador = ctk.CTkComboBox(self.scroll_frame, values=["="])  # placeholder inicial
        cbo_operador.grid(row=fila, column=1, padx=20, pady=(10 if fila == 0 else 5))

        # Entry para escribir el valor
        entry_valor = ctk.CTkEntry(self.scroll_frame)
        entry_valor.grid(row=fila, column=2, padx=20, pady=(10 if fila == 0 else 5))

        # Evento al cambiar columna → actualiza operadores disponibles
        def actualizar_operadores(opcion):
            tipo = self.df[opcion].dtype
            if pd.api.types.is_numeric_dtype(tipo):
                operadores = [">", "<", "=", ">=", "<="]
            else:
                operadores = ["=", "!=", "comienza por", "termina por"]
            cbo_operador.configure(values=operadores)
            cbo_operador.set(operadores[0])  # seleccionar por defecto el primero

        cbo_columna.configure(command=actualizar_operadores)

        # Agregamos widgets a la lista de control
        self.filter_widgets.append((cbo_columna, cbo_operador, entry_valor))
        self.filter_row += 1


    def exe_filter(self):
        try:
            condiciones = []

            for cbo_col, cbo_op, entry_val in self.filter_widgets:
                col = cbo_col.get()
                op = cbo_op.get()
                val = entry_val.get()

                if col == "" or op == "" or val == "":
                    continue  # saltar si está vacío

                tipo = self.df[col].dtype

                if pd.api.types.is_numeric_dtype(tipo):
                    try:
                        val_num = float(val)
                        condiciones.append(f"`{col}` {op} {val_num}")
                    except ValueError:
                        messagebox.showerror("Error", f"'{val}' no es un número válido para la columna '{col}'")
                        return
                else:
                    if op == "=":
                        condiciones.append(f"`{col}` == '{val}'")
                    elif op == "!=":
                        condiciones.append(f"`{col}` != '{val}'")
                    elif op == "comienza por":
                        condiciones.append(f"@self.df['{col}'].str.startswith('{val}')")
                    elif op == "termina por":
                        condiciones.append(f"@self.df['{col}'].str.endswith('{val}')")

            if not condiciones:
                messagebox.showwarning(title="Aviso", message="No se han definido filtros.")
                return

            query_str = " & ".join(condiciones)

            if any("startswith" in f or "endswith" in f for f in condiciones):
                df_filtrado = self.df[eval(query_str)]
            else:
                df_filtrado = self.df.query(query_str)

            # Aquí puedes usar el DataFrame filtrado, por ejemplo:
            print(df_filtrado)

        except Exception as e:
            messagebox.showerror(title="Error al filtrar", message=str(e))


    def top_level_params_ANO(self,metodo):
        
        if metodo == "-- Ninguna":
            self.cbo_ANO.set("A. No Superivosado")
            return
        top = ctk.CTkToplevel(self)
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
        lbl_cols = ctk.CTkLabel(top, text="Selecciona columnas:")
        lbl_cols.pack(pady=5)

        columnas = list(self.df.head(10).select_dtypes(include="number").columns)
        selected_cols = []

        for col in columnas:
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(top, text=col, variable=var)
            chk.pack(anchor="w", padx=10,pady=10)
            selected_cols.append((col, var))

        n_clusters_entry = None
        n_components_entry = None
        # Hiperparámetros
        print(metodo)
        if metodo == "KMeans":
            ctk.CTkLabel(top, text="Número de clusters:").pack(pady=5)
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
                df_filtrado = self.df[columnas_seleccionadas]
                modelo_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                self.df['cluster'] = modelo_kmeans.fit_predict(df_filtrado)
                print("Clustering completado. Nuevas etiquetas guardadas en 'cluster'.")
                

            elif metodo == "PCA":
                n_components = int(n_components_entry.get())
                print(f"PCA con columnas {columnas_seleccionadas} y {n_components} componentes")
                # Llama aquí a tu función de PCA con esos parámetros
                df_filtrado = self.df[columnas_seleccionadas]
                pca = PCA(n_components=n_components)
                componentes = pca.fit_transform(df_filtrado)

                # Guardar cada componente como nueva columna
                for i in range(n_components):
                    self.df[f'COMP_{i+1}'] = componentes[:, i]

                print(f"PCA completado. Se añadieron {n_components} componentes como columnas.")
            self.show_tree_viewport()
            self.cbo_ANO.set("A. No Superivosado")
            top.destroy()

        ctk.CTkButton(top, text="Aplicar", command=aplicar).pack(pady=10)

    def __convert_data_type(self):
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
        self.pop_conversion = ctk.CTkToplevel(self)
        self.pop_conversion.title("Conversion")
        self.pop_conversion.resizable(False, False)
        self.pop_conversion.transient(self)
        self.pop_conversion.lift()
        self.pop_conversion.focus_force()
        self.pop_conversion.grab_set()

        #centrar ventana
        self.pop_conversion.update()
        center_window(self.pop_conversion)

        # Crear un marco desplazable
        self.scroll_frame = ctk.CTkScrollableFrame(self.pop_conversion, width=500, height=300)
        self.scroll_frame.grid(row=0, column=0, padx=10, pady=10)

        # Guardar una lista para agregar nuevas filas dinámicamente
        self.conversion_row = 1

        # Fila inicial
        cbo_statistics = ctk.CTkComboBox(self.scroll_frame, values=values)
        cbo_statistics.grid(row=0, column=0, padx=(20, 20), pady=(20, 20))

        variable_conversion = ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns))
        variable_conversion.grid(row=0, column=1, padx=(0, 20), pady=(20, 20))

        self.chk_column = ctk.CTkCheckBox(self.scroll_frame, text="Misma columna")
        self.chk_column.grid(row=0, column=2, padx=(0, 20), pady=(20, 20))
        
        self.btn_add_variables = ctk.CTkButton(self.pop_conversion,
                                          text="+",
                                          width=50,
                                          command=lambda:self.add_variable_conversion(values)
                                          )
        self.btn_add_variables.grid(row=1,column=0,padx=20,pady=(0,20))

        self.btn_conversion = ctk.CTkButton(self.pop_conversion,
                                  text="Convertir Tipo",
                                  command=self.__conversion
                                  )
        self.btn_conversion.grid(row=2,column=0,padx=(0,20),pady=(0,20))

    def add_variable_conversion(self,values):
        fila = self.conversion_row

        ctk.CTkComboBox(self.scroll_frame, values=values).grid(row=fila, column=0, padx=(20, 20), pady=(0, 20))
        ctk.CTkComboBox(self.scroll_frame, values=list(self.df.columns)).grid(row=fila, column=1, padx=(0, 20), pady=(0, 20))
        ctk.CTkCheckBox(self.scroll_frame, text="Misma columna").grid(row=fila, column=2, padx=(0, 20), pady=(0, 20))

        self.conversion_row += 1
    def __conversion(self):
        pass


    def __calculate_statistics(self):
        values=[
                "media",
                "mediana",
                "desviacion_estandar",
                "varianza",
                "minimo",
                "maximo"
                ]
        self.popup_statistics = ctk.CTkToplevel(self)
        self.popup_statistics.title("Estadísticas")
        self.popup_statistics.resizable(False,False)

        # centrar ventana
        self.popup_statistics.update()
        center_window(self.popup_statistics)

        self.popup_statistics.transient(self)
        self.popup_statistics.lift()
        self.popup_statistics.focus_force()
        self.popup_statistics.grab_set()

        
        self.statistics_combos = []  # ← Aquí guardaremos los ComboBox

        # Añadir el primer par de ComboBox con referencias
        cbo_stat = ctk.CTkComboBox(self.popup_statistics, values=values)
        cbo_stat.grid(row=1, column=0, padx=(20, 20), pady=(20, 20))

        cbo_var = ctk.CTkComboBox(self.popup_statistics, values=list(self.df.columns))
        cbo_var.grid(row=1, column=1, padx=(0, 20), pady=(20, 20))

        self.statistics_combos.append((cbo_stat, cbo_var))
        
        self.btn_add_variables = ctk.CTkButton(self.popup_statistics,
                                          text="+",
                                          width=50,
                                          command=lambda:self.add_variable_statistics(values))
        self.btn_add_variables.grid(row=2,column=0,padx=20)

        self.btn_statistics = ctk.CTkButton(self.popup_statistics,
                                  text="Calcular",
                                  command=self.__statistics)
        self.btn_statistics.grid(row=3,column=1,padx=(0,20),pady=(0,20))

    def add_variable_statistics(self, values):
        fila = self.btn_add_variables.grid_info()["row"]
        
        cbo_stat = ctk.CTkComboBox(self.popup_statistics, values=values)
        cbo_stat.grid(row=fila, column=0, padx=(20, 20), pady=(0, 20))

        cbo_var = ctk.CTkComboBox(self.popup_statistics, values=list(self.df.columns))
        cbo_var.grid(row=fila, column=1, padx=(0, 20), pady=(0, 20))

        self.statistics_combos.append((cbo_stat, cbo_var))  # ← Guardamos los nuevos ComboBox

        self.btn_add_variables.grid_configure(row=fila + 1)
        self.btn_statistics.grid_configure(row=fila + 2)

        geo = self.popup_statistics.geometry()
        ancho_alto, x_y = geo.split('+', 1)
        ancho, alto = map(int, ancho_alto.split('x'))
        x, y = map(int, x_y.split('+'))
        nuevo_alto = alto + 50
        self.popup_statistics.geometry(f"{ancho}x{nuevo_alto}+{x}+{y}")

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
        popup_resultados = ctk.CTkToplevel(self)
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

        popup = ctk.CTkToplevel(self)
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
        
        self.popup_generate_graph = ctk.CTkToplevel(self)
        self.popup_generate_graph.geometry("620x100")
        self.popup_generate_graph.resizable(False,False)

        #centar ventana
        self.popup_generate_graph.update()
        center_window(self.popup_generate_graph)

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
        # ctk.CTkLabel(self.popup_generate_graph,
        #              text="Graficar Variables",
        #              width=700).grid(row=0,column=0,columnspan=5)
        ctk.CTkComboBox(self.popup_generate_graph,
                                            values=values,
                                            command=lambda valor, fila=1: self._type_graph(valor,1)
        ).grid(row=1,column=0,padx=(20,20),pady=(10,20))
        
        # cbo_variables = ctk.CTkComboBox(self.popup_generate_graph,
        #                                 values=list(self.df.columns))
        # cbo_variables.grid(row=1,column=1,pady=(20,20),padx=(0,20))

        self.btn_add_variables = ctk.CTkButton(self.popup_generate_graph,
                                          text="+",
                                          width=50,
                                          command=lambda:self.add_variable(values))
        self.btn_add_variables.grid(row=2,column=0,padx=20,pady=(0,20))

        # self.btn_graph = ctk.CTkButton(self.popup_generate_graph,
        #                           text="Graficar",
        #                           command=self._graph)
        # self.btn_graph.grid(row=3,column=1,padx=(20,20),pady=(0,20))

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
            cbo_variable = ctk.CTkComboBox(self.popup_generate_graph,
                                        values=list(self.df.select_dtypes(include="object").columns))
            cbo_variable.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            btn = ctk.CTkButton(self.popup_generate_graph,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor, categoria=cbo_variable.get()))
            btn.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            widgets.extend([cbo_variable, btn])

        elif valor in ["Linea", "Dispersión"]:
            cbo_x = ctk.CTkComboBox(self.popup_generate_graph,
                                    values=list(self.df.select_dtypes(include="number").columns))
            cbo_y = ctk.CTkComboBox(self.popup_generate_graph,
                                    values=list(self.df.select_dtypes(include="number").columns))
            cbo_x.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            cbo_y.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            btn = ctk.CTkButton(self.popup_generate_graph,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor, x=cbo_x.get(), y=cbo_y.get()))
            btn.grid(row=fila, column=3, pady=(10, 20), padx=(0, 20))
            widgets.extend([cbo_x, cbo_y, btn])

        elif valor == "Bigote":
            cbo_var = ctk.CTkComboBox(self.popup_generate_graph,
                                    values=list(self.df.select_dtypes(include="number").columns))
            cbo_var.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            btn = ctk.CTkButton(self.popup_generate_graph,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor, va=cbo_var.get()))
            btn.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            widgets.extend([cbo_var, btn])

        elif valor == "Bigote por categoría":
            cbo_num = ctk.CTkComboBox(self.popup_generate_graph,
                                    values=list(self.df.select_dtypes(include="number").columns))
            cbo_cat = ctk.CTkComboBox(self.popup_generate_graph,
                                    values=list(self.df.select_dtypes(include="object").columns))
            cbo_num.grid(row=fila, column=1, pady=(10, 20), padx=(0, 20))
            cbo_cat.grid(row=fila, column=2, pady=(10, 20), padx=(0, 20),sticky="w")
            btn = ctk.CTkButton(self.popup_generate_graph,
                                text="G",
                                width=50,
                                command=lambda: self._add_graph(valor,
                                                                va=cbo_num.get(),
                                                                categoria=cbo_cat.get()))
            btn.grid(row=fila, column=3, pady=(10, 20), padx=(0, 20))
            widgets.extend([cbo_num, cbo_cat, btn])

        self.graph_widgets[fila] = widgets
        self.popup_generate_graph.update()
        

    def add_variable(self, values):
        fila = self.btn_add_variables.grid_info()["row"]
        
        # Combo de tipo de gráfico
        cbo_tipo = ctk.CTkComboBox(self.popup_generate_graph,
                                values=values,
                                command=lambda valor, fila=fila: self._type_graph(valor, fila))
        cbo_tipo.grid(row=fila, column=0, padx=(20, 20), pady=(10, 20))
        
        self.graph_widgets[fila] = [cbo_tipo]

        # Actualiza ubicación de los botones
        self.btn_add_variables.grid_configure(row=fila + 1)
        #self.btn_graph.grid_configure(row=fila + 2)

        # Ajuste ventana
        geo = self.popup_generate_graph.geometry()
        ancho_alto, x_y = geo.split('+', 1)
        ancho, alto = map(int, ancho_alto.split('x'))
        x, y = map(int, x_y.split('+'))
        nuevo_alto = alto + 70
        self.popup_generate_graph.geometry(f"{ancho}x{nuevo_alto}+{x}+{y}")
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
        popup_choose_columns = ctk.CTkToplevel(self)
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
        btn_choose_columns.pack(anchor="w",pady=5,padx=20)

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

            popup_choose_columns = ctk.CTkToplevel(self)
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


    def __solicitud_post_csv(self,encoding,sep):
        
        if self.url_csv is None or encoding == "" or sep == "":
            messagebox.showerror("Campos Invalidos para la Transformación", "Por favor, completa todos los campos obligatorios.")
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
                    files=files,
                    
                )
                if response.ok :
                    print("✅",response.json())
                   
                    print("--- mostrando tabla csv")
                    self.df = pd.read_csv(self.url_csv,sep=sep,encoding=encoding)
                    self.show_tree_viewport()
                    self.form.destroy()
                    

                else:
                    print("❌ Error",response.text)
            except Exception as ex:
                print("❌ Excepción",ex)


        

    def __solicitud_post_excel(self,txt_sheet_name):
        sheet_name = txt_sheet_name.get()
        if self.url_excel is None or sheet_name=="" :
            messagebox.showwarning("Campos requeridos", "Por favor, Seleciona el archivo Excel con los datos y establece la Hoja.")
            return
        
        print("--- solicitar post excel")
        print("--datos: ",self.url_excel)
        print("Nombre hoja:",sheet_name)

        with open(self.url_excel,"rb") as f:
            files = {'file': f}
            data = {
                "fuente": "excel",
                "sheet_name":sheet_name,
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
                    print("--- mostrando datos en tabla")
                    self.df = pd.read_excel(self.url_excel,sheet_name=sheet_name)
                    self.show_tree_viewport()
                    

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
                self.form.destroy()
                self.df = pd.DataFrame(response.json()) 
                print("✅")
                
                self.show_tree_viewport()    
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

            lbl_sheet_name = ctk.CTkLabel(self.form,text="Hoja")
            lbl_sheet_name.grid(row=1,column=0,padx=(50,20),pady=(10,20))

            txt_sheet_name = ctk.CTkEntry(self.form)
            txt_sheet_name.grid(row=1,column=1,padx=(0,10),pady=(10,20))

            btn_enviar = ctk.CTkButton(self.form,
                                       text="Enviar",
                                       command=lambda:self.__solicitud_post_excel(txt_sheet_name))
            btn_enviar.grid(row=2,column=0,columnspan=2,pady=(10,20))
        
        elif tipo_bbdd.strip() == "Archivo CSV":
            
            self.form.geometry("370x200")

            lbl_file = ctk.CTkLabel(self.form,text="CSV")
            lbl_file.grid(row=0,column=0,padx=(50,20),pady=(20,10),sticky="e")
            txt_file = ctk.CTkEntry(self.form)
            txt_file.configure(state="disabled")

            txt_file.grid(row=0,column=1,padx=(0,50),pady=(20,10))
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
            
            btn_enviar.grid(row=3,column=1,pady=(10,10),padx=(0,50))

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

        self.btn_elegir_columnas = ctk.CTkButton(header_hijo,
                                                 text="Elegir Columnas",
                                                 command=self.__select_columns
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
                                           command= self.__transform_variables)
        cbo_transform_variables.grid(row=0,column=2,padx=(5,5),sticky="nsew",pady=(0,10))
        cbo_transform_variables.set("Transformar Variables")

        btn_generate_graph = ctk.CTkButton(header_hijo,
                                           text="Generar Gráfico",
                                           command=self._generate_graph)
        btn_generate_graph.grid(row=0,column=3,padx=(5,5),sticky="nsew",pady=(0,10))
        

        self.cbo_variable_dependiente = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "Columna1",
                                          "Columna2",
                                          "Columna3",
                                          "-- Ninguna"
                                           ])
        self.cbo_variable_dependiente.grid(row=0,column=4,padx=(5,10),sticky="nsew",pady=(0,10))
        self.cbo_variable_dependiente.set("Variable Dependiente")

        for col in range(5):  # Tienes 5 elementos
            header_hijo.grid_columnconfigure(col, weight=1)
        header_hijo.grid_rowconfigure(1, weight=1)

        # FILA 2: FILTRO , CONVERTIR TIPO, A.N.S., CALCULAR ESTÁDISTICAS,  APLICAR (CAMBIOS)

        btn_filtro = ctk.CTkButton(header_hijo,
                                   text="Filtrar",
                                   command=self.__filtrar)
        btn_filtro.grid(row=1,column=0,padx=(10,5),sticky="nsew")


        btn_convert_data_type = ctk.CTkButton(header_hijo,
                                              text="Convertir Tipo de Datos",
                                              command=self.__convert_data_type)
        btn_convert_data_type.grid(row=1,column=1,padx=(5,5),sticky="nsew")
        
        self.cbo_ANO = ctk.CTkComboBox(header_hijo,
                                      values=[
                                          "PCA",
                                          "KMeans",
                                          "-- Ninguna"
                                           ],
                                           command=self.top_level_params_ANO)
        self.cbo_ANO.grid(row=1,column=2,padx=(5,5),sticky="nsew")
        self.cbo_ANO.set("A. No Superivosado")
        
        
        btn_calculate_statistics = ctk.CTkButton(header_hijo,
                                                 text="Estadísticas",
                                                 command= self.__calculate_statistics
                                        )
        btn_calculate_statistics.grid(row=1,column=3,padx=(5,5),sticky="nsew")
        

        btn_aplicar = ctk.CTkButton(header_hijo,command=self.aplicar_cambios,text="Aplicar")
        btn_aplicar.grid(row=1,column=4,padx=(5,10),sticky="nsew")

        frame_tabla = ctk.CTkFrame(self.tab1,height=400,fg_color="#96fba4")
        frame_tabla.pack(fill="x",side="top",pady=(10,20),padx=20)
        
        scroll_x = ttk.Scrollbar(frame_tabla,orient="horizontal")
        scroll_x.pack(side="bottom",fill="x")     


        
        """ ------------obteniendo los datos---------------"""
        

        self.tree = ttk.Treeview(frame_tabla,
                            xscrollcommand=scroll_x.set ,
                           
                            show="headings")
        
        scroll_x.config(command=self.tree.xview)
        self.tree.pack(padx=20, pady=20, fill="both", expand=True)
    
    def show_tree_viewport(self):
        print("--- Renderizando tabla df")
        self.df.info()
        # tree 
        self.tree["columns"] = list(self.df.columns)
        self.cbo_variable_dependiente.configure(values=list(self.df.columns))

        # encambezado (cols)
        for col in self.df.columns:
            self.tree.heading(col,text=col.capitalize())
            self.tree.column(col, anchor="center")
        
        #limpiar filas
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar datos (50 primeras filas)
        for vector in self.df.values[:50]:
            self.tree.insert("","end",values=tuple(vector))


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

        frame_result = ctk.CTkFrame(self.tab2,height=400,fg_color="#ad96fb")
        frame_result.pack(fill="x",side="top",pady=(10,20),padx=20)
        btn_historial = ctk.CTkButton(frame_result,
                                      text="Mostrar Estidisticos",
                                      command=self.mostrar_historial_estadisticas)
        btn_historial.pack()

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


