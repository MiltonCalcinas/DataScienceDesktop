import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
#import seaborn as sns

# Reproducibilidad
np.random.seed(123)

# Número de observaciones
n = 200

# Variables correlacionadas
X1 = np.random.normal(50, 10, n)
X2 = 0.8 * X1 + np.random.normal(0, 5, n)
X3 = -0.5 * X1 + 0.3 * X2 + np.random.normal(0, 3, n)
X4 = np.random.normal(100, 20, n)




# DataFrame
df = pd.DataFrame({
    'X1': X1,
    'X2': X2,
    'X3': X3,
    'X4': X4,

})

features = ['X1', 'X2', 'X3', 'X4']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# PCA
pca = PCA(n_components=1)
X_pca = pca.fit_transform(X_scaled)

# Generación de Y basada en PCA + ruido controlado
noise = np.random.normal(loc=0, scale=1, size=n)
Y = X_pca.flatten()* 3  + noise
df['Y'] = Y

# Regresión lineal con componentes principales
model = LinearRegression()
model.fit(X_pca, df['Y'])
y_pred = model.predict(X_pca)
r2 = r2_score(df['Y'], y_pred)
print(r2)
from sklearn.metrics import mean_squared_error

# Cálculo de RMSE
rmse = np.sqrt(mean_squared_error(df['Y'], y_pred))
print(f"RMSE: {rmse:.4f}")


df = pd.DataFrame({
    'Y':Y,
    'X1': X1,
    'X2': X2,
    'X3': X3,
    'X4': X4,
})


df.round(4).to_csv('datos_regresion.csv',encoding='utf-8',sep=';')