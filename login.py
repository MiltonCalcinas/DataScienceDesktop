import customtkinter as ctk
import requests
import json
from tkinter import messagebox

class Login(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.interfaz_login()
        

        
    
    def __send_signin(self, txt_nombre, txt_password):
        nombre = txt_nombre.get()
        password = txt_password.get()

        data = {
            "username": nombre,
            "password": password
        }

        try:
            res = requests.post("http://127.0.0.1:8000/api/signin/", json=data)

            if res.status_code == 200:
                self.authenticated = True
                token = res.json().get("token")
                
                print("Login correcto. Token:", token)

                if self.recordarme_var.get():
                    # cambiar por bbdd
                    session_data = {
                        "token": token,
                        "username": nombre,
                    }
                    with open("session.json", "w") as f:
                        json.dump(session_data, f)

                self.authenticated = True
                self.after(100, self.destroy)

            else:
                self.authenticated = False
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        except Exception as e:
            messagebox.showerror("Error de red", str(e))


    def __send_signup(self,txt_nombre,txt_password,txt_password2):
        nombre = txt_nombre.get()
        password1 = txt_password.get()
        password2 = txt_password2.get()

        data = {
            "username": nombre,
            "password1": password1,
            "password2": password2
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            res = requests.post("http://127.0.0.1:8000/api/signup/", data=json.dumps(data), headers=headers)

            if res.status_code == 201:
                token = res.json()["token"]
                print("Registrado con éxito, token:", token)
                messagebox.showinfo("Éxito", "Usuario creado correctamente.")
                self.authenticated = True
                self.after(100, self.destroy)

            else:
                print("Error:", res.json())
                messagebox.showerror("Error", res.json().get("error", "Error desconocido."))
                self.authenticated = False
        except Exception as e:
            print("Error", e)
            messagebox.showerror("Error de red", str(e))


    def __frame_signup(self):
        for widget in self.frame_incio.winfo_children():
            widget.destroy()

        lbl_titulo = ctk.CTkLabel(self.frame_incio,text="Registrarse",font=("Arial",20,"bold"))
        lbl_titulo.grid(row=0,column=0,columnspan=3)

        lbl_nombre = ctk.CTkLabel(self.frame_incio,text="Nombre")
        lbl_nombre.grid(row=1,column=0,padx=(50,20),pady=(50,20))

        txt_nombre = ctk.CTkEntry(self.frame_incio,)
        txt_nombre.grid(row=1,column=1,padx=(0,10),pady=(50,20))

        lbl_password = ctk.CTkLabel(self.frame_incio,text="Password")
        lbl_password.grid(row=2,column=0,padx=(50,20),pady=(0,20))

        txt_password = ctk.CTkEntry(self.frame_incio,show="*")
        txt_password.grid(row=2,column=1,padx=(0,10),pady=(0,20))


        lbl_password2 = ctk.CTkLabel(self.frame_incio,text="Password")
        lbl_password2.grid(row=3,column=0,padx=(50,20),pady=(0,20))

        txt_password2 = ctk.CTkEntry(self.frame_incio,show="*")
        txt_password2.grid(row=3,column=1,padx=(0,10),pady=(0,20))


        self.visible = False
        btn_mostrar = ctk.CTkButton(self.frame_incio,
                                    text="👁",
                                    command=lambda: self.__toogle_password(txt_password,txt_password2),
                                    width=10)
        btn_mostrar.grid(row=2,column=2,padx=(0,50),pady=(0,20))

        btn_signup = ctk.CTkButton(self.frame_incio,
                                         text="SIGNUP",
                                         command=lambda:self.__send_signup(
                                             txt_nombre, 
                                             txt_password, 
                                             txt_password2
                                         ),
                                         font=("Arial",20,"bold"),
                                         )
        btn_signup.grid(row=4,column=0,columnspan=3,pady=(0,20))

        btn_singin = ctk.CTkButton(self.frame_incio,
                                        text="SIGNIN",
                                        command=self.__frame_singin
                                        )
        btn_singin.grid(row=5,column=0,columnspan=3)

    def __toogle_password(self,*args):
        if  not self.visible:
            for wid in args:
                wid.configure(show="")

            self.visible=True
        else:
            for wid in args:
                wid.configure(show="*")
            self.visible=False
    
    def __frame_singin(self):
        
        for widget in self.frame_incio.winfo_children():
            widget.destroy()

        lbl_titulo = ctk.CTkLabel(self.frame_incio,text="Inicia Sesión",font=("Arial",20,"bold"))
        lbl_titulo.grid(row=0,column=0,columnspan=3)

        lbl_nombre = ctk.CTkLabel(self.frame_incio,text="Nombre")
        lbl_nombre.grid(row=1,column=0,padx=(50,20),pady=(50,20))

        txt_nombre = ctk.CTkEntry(self.frame_incio,)
        txt_nombre.grid(row=1,column=1,padx=(0,10),pady=(50,20))

        lbl_password = ctk.CTkLabel(self.frame_incio,text="Password")
        lbl_password.grid(row=2,column=0,padx=(50,20),pady=(0,20))

        txt_password = ctk.CTkEntry(self.frame_incio,show="*")
        txt_password.grid(row=2,column=1,padx=(0,10),pady=(0,20))

        self.visible = False
        btn_mostrar = ctk.CTkButton(self.frame_incio,
                                    text="👁",
                                    command=lambda: self.__toogle_password(txt_password),
                                    width=10)
        btn_mostrar.grid(row=2,column=2,padx=(0,50),pady=(0,20))



        btn_signin = ctk.CTkButton(self.frame_incio,
                                         text="SIGNIN",
                                         command=lambda: self.__send_signin(
                                             txt_nombre,
                                             txt_password
                                         ),
                                         font=("Arial",20,"bold"),
                                         )
        btn_signin.grid(row=3,column=0,columnspan=3,pady=(0,20))

        btn_signup = ctk.CTkButton(self.frame_incio,
                                        text="SIGNUP",
                                        command=self.__frame_signup
                                        )
        btn_signup.grid(row=4,column=0,columnspan=3)


        self.recordarme_var = ctk.BooleanVar()

        check_recordarme = ctk.CTkCheckBox(
            self.frame_incio,
            text="Recordarme",
            variable=self.recordarme_var
        )
        check_recordarme.grid(row=5, column=1, sticky="w")
    

    def interfaz_login(self):
        self.geometry("400x500")
        self.title("Inicia Sesión")
        self.resizable(False,False)

        # Encambezado
        lbl_bienvenido = ctk.CTkLabel(self,
                                      text="Ciencia de Datos",
                                      font=("Arial",24,"bold"))
        lbl_bienvenido.pack(fill="x",pady=(20,20))

        self.frame_incio =ctk.CTkFrame(self,)
        self.frame_incio.pack()
        
        self.btn_signup = ctk.CTkButton(self.frame_incio,text="signup",command=self.__frame_signup)
        self.btn_signup.pack(pady=(0,20))
        self.btn_sigin = ctk.CTkButton(self.frame_incio,text="signin",command= self.__frame_singin)
        self.btn_sigin.pack()   



        

