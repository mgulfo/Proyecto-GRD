# config.py

"""
Archivo de configuración.
Contiene parámetros de conexión a InfluxDB y otras configuraciones globales.
"""
'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuraciones generales del proyecto
EXECUTE_VISUALIZATION = False
SHOW_GRAPHS = False
SAVE_OUTPUTS = False
EJECUTAR_CAMMESA = False
# Directorios de salida
OUTPUT_DIR = os.path.join("data", "raw")
IMAGES_DIR = os.path.join("data", "images")

# Definición de Rango para generate_ts_anomalies()
RANGE = 180

# Definición de Rango de entradas de datos para empezar a calcular el MAE
MAX_ST = 180

# Ejecución análisis de anomaliás (False: X)
EJECUTAR_ANALISIS_ANOMALIAS = False

 # Poner en False si no querés ver el gráfico
VISUALIZAR_MAE = False  

# Configuración para InfluxDB 1.8
INFLUXDB1_CONFIG = {
    'host': 'smartsetdb.brazilsouth.cloudapp.azure.com',
    'port': 7195,
    'username': 'mpoliti',
    'password': 'GenInti23',
    'database': 'ss_genrod',
    'ssl': True,
    'timeout': 300,
    'verify_ssl': False
}

# Configuración para InfluxDB 2.7
INFLUXDB2_CONFIG = {
    'url': "http://149.78.55.22:10010",
    'token': "z66S7YKFLYmofPczzaKMCSbWNlowKGytBYBdmnPwxGyU5ueOZK288-Q_1GLjXjNlSBn8uc4bG6Dq-jmxUVOTQQ==",
    'org': "97d58b9470b74eb5",
    'timeout': 90000,
    'ssl': True,
    'verify_ssl': False,
    'bucket': "ss_genrod"
}
# Configuración para InfluxDB 2.7 INTI
INFLUXDB2_CONFIG_INTI = {
    'url': "http://149.78.55.22:10010",
    'token': "Lpk2-Fsiv0wKs2xaCUAGYhIEiN5JXwEvLcTWBrSb8GcMHB2hE4fW83c-QgjpHRwVH_ccl9dMQbT8wSuC0Q4xWw==",
    'org': "97d58b9470b74eb5",
    'timeout': 90000,
    'ssl': True,
    'verify_ssl': False,
    'bucket': "ss_inti"
}
# Otros parámetros globales
LOCAL_TIMEZONE = 'America/Argentina/Buenos_Aires'

# Activar uso de InfluxDB 2 como base primaria
USE_INFLUXDB_2 = True

 #Localizaciones en planta
MEDIA = "MEDIA"
SET1 = "SET01"
SET2 = "SET02"
SET3 = "SET03"
SET4 = "SET04"
'''

