import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Función para crear el gráfico
def crear_grafico():
    # Crear un gráfico simple con Matplotlib
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
    ax.set_title('Gráfico de línea')
    
    # Convertir la figura de Matplotlib en un canvas de Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# Crear la ventana principal de CustomTkinter
root = ctk.CTk()

# Crear un frame para mostrar el gráfico
frame_grafico = ctk.CTkFrame(root)
frame_grafico.pack(fill="both", expand=True)

# Botón para crear el gráfico
btn_grafico = ctk.CTkButton(root, text="Crear gráfico", command=crear_grafico)
btn_grafico.pack(padx=20, pady=20)

# Ejecutar la ventana
root.mainloop()

