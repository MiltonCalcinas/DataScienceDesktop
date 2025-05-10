import plotly.graph_objs as go
import plotly.offline as pyo

# Datos para el gráfico
x = [1, 2, 3, 4, 5]
y = [10, 11, 12, 13, 14]

# Crear el gráfico
trace = go.Scatter(
    x=x,
    y=y,
    mode='lines',  # El tipo de gráfico: 'lines', 'markers', 'lines+markers', etc.
    name='Línea de ejemplo'  # Nombre de la línea
)

# Agrupar los datos en una lista
data = [trace]

# Definir el layout del gráfico (opcional)
layout = go.Layout(
    title='Gráfico de Línea Simple',
    xaxis=dict(title='Eje X'),
    yaxis=dict(title='Eje Y')
)

# Crear el objeto de la figura con los datos y el layout
fig = go.Figure(data=data, layout=layout)

# Mostrar el gráfico en el navegador (sin necesidad de una interfaz gráfica como Tkinter)
pyo.plot(fig)
