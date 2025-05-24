import pandas as pd
class ColorDataFrame():
    def __init__(self):
        colores = {
            "DARK":{
                "COLOR_FONDO_APP":"#264653",
                "COLOR_FONDO_FRAME": "#2A9D8F",
                "COLOR_RELLENO_WIDGET":"#156082",
                "COLOR_BORDE_WIDGET":"#FFFFFF",
                "COLOR_LETRA_NORMAL" : "#272932",
                "COLOR_LETRA_NEGRITA": "#000000",
            },

            "LIGHT":{
                "COLOR_FONDO_APP":"#FFFFFF",
                "COLOR_FONDO_FRAME": "#DCEAF7",
                "COLOR_RELLENO_WIDGET":"#156082",
                "COLOR_BORDE_WIDGET":"#0070C0",
                "COLOR_LETRA_NORMAL" : "#272932",
                "COLOR_LETRA_NEGRITA": "#000000",
            },
            "DRACULA":{
                "COLOR_FONDO_APP":"#2D3047",
                "COLOR_FONDO_FRAME": "#1B998B",
                "COLOR_RELLENO_WIDGET":"#ED217C",
                "COLOR_BORDE_WIDGET":"#FFFD82",
                "COLOR_LETRA_NORMAL" : "#272932",
                "COLOR_LETRA_NEGRITA": "#000000",
            }
        }

        self.df_color = pd.DataFrame(colores)

        # print(self.df_color)
        # print(self.df_color.DARK.COLOR_FONDO_APP)
    def get_colores(self,tipo):
        tipo = tipo.upper()
        if tipo == "DARK":
            return self.df_color.DARK
        elif tipo == "LIGHT":
            return self.df_color.LIGHT
        elif tipo == "DRACULA":
            return self.df_color.DRACULA
        else:
            raise ValueError(f"La opcion elegido para el color no es valido. color= {tipo}")