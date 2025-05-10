import customtkinter as ctk

def abrir_emergente():
    ventana = ctk.CTkToplevel(root)  # Toplevel depende de la raíz
    ventana.title("Soy una ventana emergente")
    ventana.geometry("300x200")

    label = ctk.CTkLabel(ventana, text="¡Hola, soy un pop-up!")
    label.pack(pady=20)

    boton_cerrar = ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy)
    boton_cerrar.pack(pady=10)

root = ctk.CTk()
root.geometry("500x400")

boton = ctk.CTkButton(root, text="Abrir ventana emergente", command=abrir_emergente)
boton.pack(pady=20)

root.mainloop()
