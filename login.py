import customtkinter as ctk
import requests
import json
from tkinter import messagebox
import config
import colores

class Login(ctk.CTkToplevel):

    def __init__(self,parent,mode):
        super().__init__(parent)
        self.parent = parent
        self.authenticated = False
        self.with_df = False
        self.is_new_user = False
        self.mode=mode
        self.colores = colores.ColorDataFrame().get_colores(self.mode)

        #self.transient(self)
        self.lift()
        self.focus_force()
        self.grab_set()
    
        self.interfaz_login()

        
    
    def __send_signin(self, txt_nombre, txt_password):
        nombre = txt_nombre.get()
        password = txt_password.get()

        data = {
            "username": nombre,
            "password": password
        }
        import config
        try:
            res = requests.post(config.VIEW_SIGIN, json=data)

            if res.status_code == 200:
                self.authenticated = True
                 
                auth_token= res.json()["token"]
                self.parent.auth_token = auth_token
                self.is_new_user=False
                print("-- Servidor : Logeado con éxito, token:", auth_token)
                

                if self.recordarme_var.get():
                    session_data = {
                        "auth_token": auth_token,
                        "username": nombre,
                    }
                    with open("session.json", "w") as f:
                        json.dump(session_data, f)

                    self.after(100, self.destroy)
                
                self.destroy()
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
            res = requests.post(config.VIEW_SIGUP, data=json.dumps(data), headers=headers)

            if res.status_code == 201:
                self.authenticated = True

                auth_token= res.json()["token"]
                self.parent.auth_token = auth_token
                self.is_new_user = True
                print("Registrado con éxito, token:", auth_token)

                if self.recordarme_var.get():
                    session_data = {
                        "auth_token": auth_token,
                        "username": nombre,
                    }
                    with open("session.json", "w") as f:
                        json.dump(session_data, f)


                messagebox.showinfo("Éxito", "Usuario creado correctamente.")
                self.after(100, self.destroy)
                self.destroy()
            else:
                print("Error:", res.json())
                messagebox.showerror("Error", res.json().get("error", "Error desconocido."))
                self.authenticated = False
            

        except Exception as e:
            print("Error", e)
            messagebox.showerror("Error de red", str(e))


    def __frame_signup(self):
        self.title("Registrarse")
        for widget in self.frame_incio.winfo_children():
            widget.destroy()        

        lbl_titulo = ctk.CTkLabel(self.frame_incio,text="Registrarse", font=("Arial", 16, "bold"))
        lbl_titulo.grid(row=0,column=0,columnspan=3)
        lbl_titulo.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)

        label_width = 100

        lbl_nombre = ctk.CTkLabel(self.frame_incio,text="Nombre", width=label_width, anchor="w")
        lbl_nombre.grid(row=1,column=0,padx=(70,0),pady=(30,20))
        lbl_nombre.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)

        txt_nombre = ctk.CTkEntry(self.frame_incio,)
        txt_nombre.grid(row=1,column=1,padx=(0,10),pady=(30,20))
        txt_nombre.configure(text_color=self.colores.COLOR_LETRA_NORMAL)

        lbl_password = ctk.CTkLabel(self.frame_incio,text="Password", width=label_width, anchor="w")
        lbl_password.grid(row=2,column=0,padx=(70,0),pady=(0,20))
        lbl_password.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)

        txt_password = ctk.CTkEntry(self.frame_incio,show="*")
        txt_password.grid(row=2,column=1,padx=(0,10),pady=(0,20))
        txt_password.configure(text_color=self.colores.COLOR_LETRA_NORMAL)


        lbl_password2 = ctk.CTkLabel(self.frame_incio,text="Password", width=label_width, anchor="w")
        lbl_password2.grid(row=3,column=0,padx=(70,0),pady=(0,20))
        lbl_password2.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)

        txt_password2 = ctk.CTkEntry(self.frame_incio,show="*")
        txt_password2.grid(row=3,column=1,padx=(0,10),pady=(0,20))
        txt_password2.configure(text_color=self.colores.COLOR_LETRA_NORMAL)


        self.visible = False
        btn_mostrar = ctk.CTkButton(self.frame_incio,
                                    text="👁",
                                    command=lambda: self.__toogle_password(txt_password,txt_password2),
                                    width=10)
        btn_mostrar.grid(row=2,column=2,padx=(0,50),pady=(0,20))
        btn_mostrar.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)

        btn_signup = ctk.CTkButton(self.frame_incio,
                                         text="SignUp",
                                         command=lambda:self.__send_signup(
                                             txt_nombre, 
                                             txt_password, 
                                             txt_password2
                                         ),
                                         )
        btn_signup.grid(row=4,column=1,padx=(0,10),pady=(0,20))
        btn_signup.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)

        btn_singin = ctk.CTkButton(self.frame_incio,
                                        text="SignIn",
                                        command=self.__frame_singin
                                        )
        btn_singin.grid(row=5,column=1,padx=(0,10),pady=(0,20))
        btn_singin.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)


        self.recordarme_var = ctk.BooleanVar()

        check_recordarme = ctk.CTkCheckBox(
            self.frame_incio,
            text="Recordarme",
            variable=self.recordarme_var,
            border_color=self.colores.COLOR_BORDE_WIDGET, 
            text_color=self.colores.COLOR_LETRA_SOBRE_FONDO
        )
        check_recordarme.grid(row=6, column=1, sticky="w")

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
        self.title("Inicia Sesión")
        for widget in self.frame_incio.winfo_children():
            widget.destroy()

        lbl_titulo = ctk.CTkLabel(self.frame_incio,text="Inicia Sesión", font=("Arial", 16, "bold"))
        lbl_titulo.grid(row=0,column=0,columnspan=3)
        lbl_titulo.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)
        
        label_width = 100

        lbl_nombre = ctk.CTkLabel(self.frame_incio,text="Nombre", width=label_width, anchor="w")
        lbl_nombre.grid(row=1,column=0,padx=(70,0),pady=(30,20))
        lbl_nombre.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)

        txt_nombre = ctk.CTkEntry(self.frame_incio,)
        txt_nombre.grid(row=1,column=1,padx=(0,10),pady=(30,20))
        txt_nombre.configure(text_color=self.colores.COLOR_LETRA_NORMAL)

        lbl_password = ctk.CTkLabel(self.frame_incio,text="Password", width=label_width, anchor="w")
        lbl_password.grid(row=2,column=0,padx=(70,0),pady=(0,20))
        lbl_password.configure(text_color=self.colores.COLOR_LETRA_SOBRE_FONDO)

        txt_password = ctk.CTkEntry(self.frame_incio,show="*")
        txt_password.grid(row=2,column=1,padx=(0,10),pady=(0,20))
        txt_password.configure(text_color=self.colores.COLOR_LETRA_NORMAL)

        self.visible = False
        btn_mostrar = ctk.CTkButton(self.frame_incio,
                                    text="👁",
                                    command=lambda: self.__toogle_password(txt_password),
                                    width=10)
        btn_mostrar.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)
        btn_mostrar.grid(row=2,column=2,padx=(0,50),pady=(0,20))



        btn_signin = ctk.CTkButton(self.frame_incio,
                                         text="SignIn",
                                         command=lambda: self.__send_signin(
                                             txt_nombre,
                                             txt_password
                                         ),
                                         
                                         )
        btn_signin.grid(row=3,column=1,padx=(0,10),pady=(0,20))
        btn_signin.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)

        btn_signup = ctk.CTkButton(self.frame_incio,
                                        text="SignUp",
                                        command=self.__frame_signup
                                        )
        btn_signup.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)
        btn_signup.grid(row=4,column=1,padx=(0,10),pady=(0,20))


        self.recordarme_var = ctk.BooleanVar()

        check_recordarme = ctk.CTkCheckBox(
            self.frame_incio,
            text="Recordarme",
            variable=self.recordarme_var,
            border_color=self.colores.COLOR_BORDE_WIDGET,
            text_color=self.colores.COLOR_LETRA_SOBRE_FONDO
        )
        check_recordarme.grid(row=5, column=1, sticky="w")
    

    def interfaz_login(self):
        self.geometry("400x500")
        self.title("Inicia Sesión")
        self.resizable(False,False)
        self.configure(fg_color=self.colores.COLOR_FONDO_APP)
                # Encambezado
        lbl_bienvenido = ctk.CTkLabel(self,
                                      text="Ciencia de Datos",
                                      fg_color=self.colores.COLOR_RELLENO_WIDGET,
                                      font=("Arial", 20, "bold")
                                      )
        lbl_bienvenido.configure(text_color=self.colores.COLOR_LETRA_BOTON)
        lbl_bienvenido.pack(fill="x",pady=(20,50))

        self.frame_incio =ctk.CTkFrame(self,)
        self.frame_incio.configure(fg_color=self.colores.COLOR_FONDO_APP)

        self.frame_incio.pack()
        
        self.btn_signup = ctk.CTkButton(self.frame_incio,text="SignUp",command=self.__frame_signup)
        self.btn_signup.pack(pady=(0,20))
        self.btn_signup.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)
        
        self.btn_sigin = ctk.CTkButton(self.frame_incio,text="SignIn",command= self.__frame_singin)
        self.btn_sigin.pack()
        self.btn_sigin.configure(fg_color=self.colores.COLOR_RELLENO_WIDGET)   



        

