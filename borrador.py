import requests

# URL de la API
url = "http://127.0.0.1:8000/obtener_graficos/"

# Token de autenticación (reemplaza con uno válido)
token = "d69eb568191c6d2e64c8ad3ebd5b49e9536782d1"

# Parámetros GET
params = {
    "table_name": "manuel_tab"
}

# Headers con el token de autenticación
headers = {
    "Authorization": f"Token {token}"
}

# Hacer la petición GET
response = requests.get(url, headers=headers, params=params)

# Mostrar resultados
print("Status code:", response.status_code)
print("Response JSON:", response.json())
