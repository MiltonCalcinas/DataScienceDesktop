import tkinter as tk
import customtkinter as ctk


class MovableResizableFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        # Hacer el frame movible
        self._drag_data = {"x": 0, "y": 0}
        self.bind("<Button-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)

        # Inicializar el tamaño del frame
        self._resize_data = {"width": 300, "height": 250}
        self.configure(width=self._resize_data["width"], height=self._resize_data["height"])

    def _on_drag_start(self, event):
        """ Captura la posición inicial para mover el frame. """
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        """ Mueve el frame mientras el usuario arrastra el mouse. """
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        
        # Mover el frame
        new_x = self.winfo_x() + delta_x
        new_y = self.winfo_y() + delta_y
        self.place(x=new_x, y=new_y)

    def adjust_width(self, width_percentage):
        """ Ajusta el ancho del frame según el porcentaje de la barra de progreso. """
        new_width = int(width_percentage * 500)  # Ajusta el valor máximo según lo desees
        self.configure(width=new_width)
        self._resize_data["width"] = new_width



# Crear la ventana principal
# root = ctk.CTk()

# # Crear el frame movible y redimensionableef crear_frame_movil():
# frame = MovableResizableFrame(root, bg_color="lightgray")
# frame.place(x=100, y=100)
    

# # Función para ajustar el valor de la barra de progreso y el tamaño del frame
# def adjust_slider(value):
#     # Ajustar el ancho del frame basado en el valor del slider
#     frame.adjust_width(float(value))

# # Crear el control deslizante (slider)
# slider = ctk.CTkSlider(root, from_=0, to=1, number_of_steps=100, command=adjust_slider)
# slider.set(0.4)  # Valor inicial de la barra
# slider.pack(pady=20)

# # Iniciar el loop de la interfaz
# root.mainloop()
