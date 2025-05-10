import tkinter as tk
import customtkinter as ctk

class DynamicCTkTabview(ctk.CTkTabview):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        # Contador para las pestañas
        self.tab_counter = 1

    def add_dynamic_tab(self, tab_name=None):
        """
        Añade una nueva pestaña de manera dinámica.
        Si no se proporciona un nombre, usa el contador para generar un nombre.
        """
        if tab_name is None:
            tab_name = f"Hoja {self.tab_counter}"

        # Crear una nueva pestaña
        new_tab = self.add(tab_name)

        # Crear un frame dentro de la nueva pestaña
        frame = ctk.CTkFrame(new_tab, fg_color="#ffffff")
        frame.grid(row=0, column=0, sticky="nsew")

        # Configurar las filas y columnas para que se expandan en la nueva pestaña
        new_tab.grid_rowconfigure(0, weight=1)
        new_tab.grid_columnconfigure(0, weight=1)

        # Incrementar el contador para la siguiente pestaña
        self.tab_counter += 1

        return new_tab


# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         self.title("Dynamic Tabview Example")
#         self.geometry("600x400")

#         # Crear un Tabview dinámico
#         self.dashboard = DynamicCTkTabview(self)
#         self.dashboard.pack(fill="both", expand=True, padx=10, pady=10)

#         # Crear un botón para agregar nuevas pestañas
#         self.add_button = ctk.CTkButton(self, text="Añadir pestaña", command=self.add_tab)
#         self.add_button.pack(pady=10)

#     def add_tab(self):
#         # Llamar al método de la clase para agregar una nueva pestaña dinámica
#         self.dashboard.add_dynamic_tab()


# # Crear y ejecutar la aplicación
# app = App()
# app.mainloop()
