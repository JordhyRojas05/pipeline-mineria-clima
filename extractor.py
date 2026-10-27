
import requests
import json
import os

API_URL = "https://api.open-meteo.com/v1/forecast"

# Primero se prueba localmente.
# Despues se reemplaza con la URL real de Render.
SERVICIO_URL = os.getenv(
    "SERVICIO_URL",
    "http://127.0.0.1:5000/procesar"
)

parametros = {
    "latitude": 32.5149,
    "longitude": -117.0382,
    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "wind_speed_10m"
    ),
    "timezone": "America/Tijuana"
}

try:
    print("1. Consultando Open-Meteo...")

    respuesta = requests.get(
        API_URL,
        params=parametros,
        timeout=30
    )
    respuesta.raise_for_status()

    datos = respuesta.json()
    datos["ciudad"] = "Tijuana, Baja California"

    print("2. Datos recibidos:")
    print(json.dumps(datos, indent=4, ensure_ascii=False))

    print("3. Enviando al microservicio...")

    respuesta_analisis = requests.post(
        SERVICIO_URL,
        json=datos,
        timeout=120
    )
    respuesta_analisis.raise_for_status()

    resultado = respuesta_analisis.json()

    print("4. Resultado analitico:")
    print(json.dumps(
        resultado,
        indent=4,
        ensure_ascii=False
    ))

    with open(
        "resultado.json",
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            resultado,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    print("Resultado guardado en resultado.json")

except requests.exceptions.RequestException as error:
    print("Error de conexion o servicio:", error)

except ValueError as error:
    print("Error al interpretar JSON:", error)
