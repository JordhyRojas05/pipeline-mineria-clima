
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import re
import unicodedata

app = Flask(__name__)

def normalizar_texto(texto):
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto if not unicodedata.combining(c)
    )
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def numero(valor):
    try:
        if valor is None or isinstance(valor, bool):
            return None
        return float(valor)
    except (ValueError, TypeError):
        return None


def clasificar_clima(temperatura):
    if temperatura < 15:
        return "frio"
    elif temperatura < 25:
        return "templado"
    elif temperatura < 35:
        return "calido"
    return "calor_extremo"


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "servicio": "Pipeline de mineria meteorologica",
        "estado": "activo",
        "endpoint": "/procesar"
    })


@app.route("/procesar", methods=["POST"])
def procesar():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Se requiere un objeto JSON"
        }), 400

    actual = datos.get("current")

    if not isinstance(actual, dict):
        return jsonify({
            "error": "Falta el objeto current"
        }), 400

    temperatura = numero(actual.get("temperature_2m"))
    humedad = numero(actual.get("relative_humidity_2m"))
    viento = numero(actual.get("wind_speed_10m"))

    if temperatura is None:
        return jsonify({
            "error": "Temperatura faltante o invalida"
        }), 422

    if not -100 <= temperatura <= 65:
        return jsonify({
            "error": "Temperatura fuera de rango"
        }), 422

    imputaciones = []

    if humedad is None:
        humedad = 50.0
        imputaciones.append("humedad: valor de referencia 50")

    if viento is None:
        viento = 0.0
        imputaciones.append("viento: valor de referencia 0")

    if not 0 <= humedad <= 100 or viento < 0:
        return jsonify({
            "error": "Humedad o viento fuera de rango"
        }), 422

    ciudad = normalizar_texto(
        datos.get("ciudad", "desconocida")
    )

    categoria = clasificar_clima(temperatura)

    puntuacion = round(
        min(100, max(0, (temperatura + 10) * 2)),
        2
    )

    resultado = {
        "estado": "procesado",
        "fecha_procesamiento": datetime.now(
            timezone.utc
        ).isoformat(),
        "datos_limpios": {
            "ciudad": ciudad,
            "temperatura_c": temperatura,
            "humedad_porcentaje": humedad,
            "viento_kmh": viento,
            "fecha_medicion": actual.get("time")
        },
        "preprocesamiento": {
            "normalizacion": True,
            "imputaciones": imputaciones
        },
        "analisis": {
            "algoritmo": "clasificacion_por_reglas",
            "categoria": categoria,
            "puntuacion_termica": puntuacion
        }
    }

    return jsonify(resultado), 200


if __name__ == "__main__":
    app.run(debug=True)
