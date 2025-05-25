import pandas as pd
class ColorDataFrame():
    def __init__(self):
        colores = {
            "DARK":{
                "COLOR_FONDO_APP":"#264653",
                "COLOR_FONDO_FRAME": "#2A9D8F",
                "COLOR_RELLENO_WIDGET":"#156082", #BOTON, CBO ITEMS, NOMBRES COLUMNAS (TABLA)
                "COLOR_BORDE_WIDGET":"#FFFFFF",
                "COLOR_LETRA_NORMAL" : "#272932",
                "COLOR_LETRA_NEGRITA": "#000000",
                'COLOR_LETRA_CBO':  '#156082',      # SOLO ENCABEZADO
                'COLOR_LETRA_BOTON':  '#FFFFFF', # BOTON, CBO ITEMS, NOMBRES COLUMNAS (TABLA)
                'COLOR_LETRA_FILAS':  '#FFFFFF',
                'COLOR_RELLENO_FILA_SELECCION':  '#264653',
                'COLOR_RELLENO_FILA_HOVER':  '#41798F',
                'COLOR_RELLENO_COLUMNA_HOVER':  '#264653',
            },

            "LIGHT":{
                "COLOR_FONDO_APP":"#FFFFFF",
                "COLOR_FONDO_FRAME": "#DCEAF7",
                "COLOR_RELLENO_WIDGET":"#156082",
                "COLOR_BORDE_WIDGET":"#0070C0",
                "COLOR_LETRA_NORMAL" : "#272932",
                "COLOR_LETRA_NEGRITA": "#000000",
                'COLOR_LETRA_CBO':  '#156082',
                'COLOR_LETRA_BOTON':  '#FFFFFF',
                'COLOR_LETRA_FILAS':  '#156082',
                'COLOR_RELLENO_FILA_SELECCION':  '#FFFFFF',
                'COLOR_RELLENO_FILA_HOVER':  '#F2F7FC',
                'COLOR_RELLENO_COLUMNA_HOVER':  '#0E425A',
            },
            "DRACULA":{
                "COLOR_FONDO_APP":"#2D3047",
                "COLOR_FONDO_FRAME": "#1B998B",
                "COLOR_RELLENO_WIDGET":"#ED217C",
                "COLOR_BORDE_WIDGET":"#FFFD82",
                "COLOR_LETRA_NORMAL" : "#272932",
                "COLOR_LETRA_NEGRITA": "#000000",
                'COLOR_LETRA_CBO':  '"#ED217C"',
                'COLOR_LETRA_BOTON':  '#FFFFFF',
                'COLOR_LETRA_FILAS':  '#2D3047',
                'COLOR_RELLENO_FILA_SELECCION':  '#FFFD82',
                'COLOR_RELLENO_FILA_HOVER':  '#FFFECD',
                'COLOR_RELLENO_COLUMNA_HOVER':  '#AA0E55',
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
        
