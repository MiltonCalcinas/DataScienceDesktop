from login import Login
from App import App
import json


def leer_session():
    try:
        with open("session.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    


if __name__ == "__main__":
    token = leer_session()

    if token:
        print("Token encontrado. Accediendo directamente...")
        app = App()
        app.mainloop()
    else:
        login = Login()
        login.mainloop()

        if login.authenticated:
            app = App()
            app.mainloop()


