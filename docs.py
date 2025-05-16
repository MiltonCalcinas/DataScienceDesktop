import customtkinter as ctk

# Función que lanza una ventana emergente
def lanzar_popup(app):
    
    popup = ctk.CTkToplevel(app)
    popup.title("Ventana Emergente")
    popup.geometry("250x150")
    
    label = ctk.CTkLabel(popup, text="¡Esto es una ventana emergente!")
    label.pack(pady=20)






app = ctk.CTk()
app.geometry("400x300")

# lanzar_popup(app)

app.mainloop()
