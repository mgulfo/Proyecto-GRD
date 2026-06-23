import os
import sys
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / 'constantes.env'

# Carga el archivo indicando la ruta exacta y permitiendo sobrescribir
load_dotenv(dotenv_path=env_path, override=True)

print(f"Ruta buscada: {env_path}")
print(f"Variable cargada: {os.getenv('TU_VARIABLE')}")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def _env_bool(key: str, default: bool) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def _env_int(key: str, default: int) -> int:
    v = os.getenv(key)
    return int(v) if v is not None and v.strip() != "" else default

def _env_str(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    return v if v is not None and v != "" else default

def _env_float(key: str, default: float) -> float:
    v = os.getenv(key)
    return float(v) if v is not None and v.strip() != "" else default

EXECUTE_VISUALIZATION = _env_bool("GRD_EXECUTE_VISUALIZATION", True)
EJECUTAR_CAMMESA = _env_bool("GRD_EJECUTAR_CAMMESA", False)
SHOW_GRAPHS = _env_bool("GRD_SHOW_GRAPHS", True)
SAVE_OUTPUTS = _env_bool("GRD_SAVE_OUTPUTS", True)

OUTPUT_DIR = os.path.join("data", "raw")
IMAGES_DIR = os.path.join("data", "images")

RANGE = _env_int("GRD_RANGE", 300)
MAX_ST = _env_int("GRD_MAX_ST", 10)

EJECUTAR_ANALISIS_ANOMALIAS = _env_bool("GRD_EJECUTAR_ANALISIS_ANOMALIAS", False)
VISUALIZAR_MAE = _env_bool("GRD_VISUALIZAR_MAE", False)
PRED_DEFAULT = "'Irms_L1_Ins', 'Irms_L2_Ins','Irms_L3_Ins'"
LOCAL_TIMEZONE = _env_str("GRD_LOCAL_TIMEZONE", "America/Argentina/Buenos_Aires")
LISTA_DATOS_PREDICCION = _env_str('GRD_LISTA_PARAMETROS_PREDICCION',PRED_DEFAULT)
USAR_TRENDS = _env_int("GRD_USAR_TRENDS", 0)
freq = _env_int("GRD_FREQ", 8640)
UNITS = _env_int("GRD_UNITS", 32)
PASOS = _env_int("GRD_PASOS", 360)
ERROR_UMBRAL = _env_float("GRD_ERROR_UMBRAL",0.10)
TAM_VENTANA = _env_int("GRD_TAM_VENTANA", 60)
FRACCION_ENTRENAMIENTO = _env_float("GRD_FRACCION_ENTRENAMIENTO", 0.8)
SET_1 = _env_str("GRD_SET_1", "SET01")
SET_2 = _env_str("GRD_SET_2", "SET02")
SET_3 = _env_str("GRD_SET_3", "SET03")
SET_4 = _env_str("GRD_SET_4", "SET04")
MEDIA = _env_str("GRD_MEDIA1", "MEDIA")
FECHA_INI_TEST_EVENTOS = _env_str("GRD_FECHA_INI_TEST_EVENTOS", "2023-02-28T21:00:00")
FECHA_FIN_TEST_EVENTOS = _env_str("GRD_FECHA_FIN_TEST_EVENTOS", "2023-03-30T00:00:30")

# Influx 1.8
INFLUXDB1_CONFIG = {
    "host": _env_str("GRD_INFLUX1_HOST"),
    "port": _env_int("GRD_INFLUX1_PORT", 7195),
    "username": _env_str("GRD_INFLUX1_USERNAME"),
    "password": _env_str("GRD_INFLUX1_PASSWORD"),
    "database": _env_str("GRD_INFLUX1_DATABASE"),
    "ssl": _env_bool("GRD_INFLUX1_SSL", True),
    "timeout": _env_int("GRD_INFLUX1_TIMEOUT", 300),
    "verify_ssl": _env_bool("GRD_INFLUX1_VERIFY_SSL", True),
}

# Influx 2.7
INFLUXDB2_CONFIG = {
    "url": _env_str("GRD_INFLUX2_URL"),
    "token": _env_str("GRD_INFLUX2_TOKEN"),
    "org": _env_str("GRD_INFLUX2_ORG"),
    "bucket": _env_str("GRD_INFLUX2_BUCKET"),
    "timeout": _env_int("GRD_INFLUX2_TIMEOUT", 90000),
    "ssl":_env_bool("GRD_INFLUX2_SSL", True),
    "verify_ssl": _env_bool("GRD_INFLUX2_VERIFY_SSL", False),
}
INFLUXDB2_CONFIG_INTI = {
    "url": _env_str("GRD_INFLUX2_INTI_URL"),
    "token": _env_str("GRD_INFLUX2_INTI_TOKEN"),
    "org": _env_str("GRD_INFLUX2_INTI_ORG"),
    "bucket": _env_str("GRD_INFLUX2_INTI_BUCKET"),
    "timeout": _env_int("GRD_INFLUX2_INTI_TIMEOUT", 90000),
    "verify_ssl": _env_bool("GRD_INFLUX2_INTI_VERIFY_SSL", False),
    "ssl":_env_bool("GRD_INFLUX2_INTI_SSL", True),
}
DB_CHIRPSTACK_CONF = {
    "host": _env_str("GRD_CHIRPSTACK_HOST","192.168.1.50"),
    "database": _env_str("GRD_CHIRPSTACK_DB","chirpstack_as"),
    "user": _env_str("GRD_CHIRPSTACK_USER","usuario"),
    "password": _env_str("GRD_CHIRPSTACK_PASS","mi_password"),
    "port": _env_int("GRD_CHIRPSTACK_PORT", 5432),
}
MQTT_CONF = {
    "host": _env_str("GRD_CHIRPSTACK_HOST_MQTT","192.168.1.50"),
    "port":  _env_int("GRD_CHIRPSTACK_PORT_MQTT", 5432),
    "topic": _env_str("GRD_CHIRPSTACK_TOPIC","application/+/device/+/event/up"),
}
USE_INFLUXDB_2 = _env_bool("GRD_USE_INFLUXDB_2", True)

if MAX_ST < 2:
    raise ValueError("MAX_ST debe ser >= 2")

