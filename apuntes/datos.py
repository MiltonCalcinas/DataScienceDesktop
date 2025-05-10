import pandas as pd
import numpy as np

# Definir el número de filas y columnas
num_rows = 1000
num_columns = 15

# Crear un DataFrame con valores aleatorios
data = {
    f'Columna_{i+1}': [
        np.random.choice([np.nan, np.nan, np.random.randint(1, 100), np.random.choice(["A", "B", "C", "D"]), np.random.choice([True, False]), None]) 
        for _ in range(num_rows)
    ] 
    for i in range(num_columns)
}

# Crear el DataFrame
df = pd.DataFrame(data)
df["Enteros"] = np.random.randint(1,100000,size=df.shape[0])

matriz30 = np.random.randint(100,10_000,size=(1000,30))

columns_30=  [f"COLUMNA {i}"  for i in range(17,17+30)]
df[columns_30] = matriz30


df.to_csv("datos.csv")


# Mostrar las primeras filas del DataFrame
print(df.head())
