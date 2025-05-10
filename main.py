from App import App
from login import Login
import customtkinter as ctk


if __name__ == "__main__":
    ctk.set_appearance_mode("light")

    # login = Login()
    # login.mainloop()
    app = App()
    app.mainloop()