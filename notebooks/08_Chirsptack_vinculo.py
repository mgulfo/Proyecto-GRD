import os
import sys

import json
import sqlite3 # Por si usas la integración SQLite de ChirpStack
import pandas as pd
import paho.mqtt.client as mqtt
import psycopg2

class ChirpStackReader:
    """Clase para conectar con ChirpStack y extraer datos directamente en Pandas DataFrames."""

    def __init__(self, db_config=None, mqtt_config=None):
        """
        Inicializa las configuraciones de bases de datos y MQTT.
        
        db_config: dict con llaves (host, database, user, password, port)
        mqtt_config: dict con llaves (host, port, topic)
        """
        self.db_config = db_config
        self.mqtt_config = mqtt_config
        self._mqtt_data = [] # Almacenamiento temporal para Live Streaming

    def fetch_historical_uplinks(self, limit=1000, flatten_json=True):
        """
        Se conecta a la base de datos PostgreSQL de ChirpStack y devuelve
        un DataFrame con los últimos uplinks históricos.
        """
        if not self.db_config:
            raise ValueError("No se ha proporcionado la configuración de la Base de Datos (db_config).")

        query = f"""
        SELECT 
            created_at AS timestamp, 
            dev_eui, 
            f_port, 
            f_cnt, 
            rssi, 
            snr, 
            object_json AS payload
        FROM device_up
        ORDER BY created_at DESC
        LIMIT {limit};
        """
        
        try:
            conn = psycopg2.connect(**self.db_config)
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Desenredar el JSON interno si el usuario lo solicita
            if flatten_json and not df.empty and 'payload' in df.columns:
                df = self._flatten_payload_column(df, 'payload')
                
            return df
        except Exception as e:
            print(f"Error al leer la base de datos: {e}")
            return pd.DataFrame()

    def stream_live_uplinks(self, max_records=10, timeout=60, flatten_json=True):
        """
        Se conecta al broker MQTT de ChirpStack, captura un número 'max_records'
        de mensajes en vivo y los devuelve como un DataFrame.
        """
        if not self.mqtt_config:
            raise ValueError("No se ha proporcionado la configuración de MQTT (mqtt_config).")

        self._mqtt_data = [] # Reiniciar contenedor
        host = self.mqtt_config.get("host", "localhost")
        port = self.mqtt_config.get("port", 1883)
        topic = self.mqtt_config.get("topic", "application/+/device/+/event/up")

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                # Estructura compatible con ChirpStack v4
                record = {
                    "timestamp": payload.get("publishedAt"),
                    "device_name": payload.get("deviceInfo", {}).get("deviceName"),
                    "dev_eui": payload.get("deviceInfo", {}).get("devEui"),
                    "f_cnt": payload.get("fCnt"),
                    "payload": payload.get("object") # Datos decodificados del sensor
                }
                self._mqtt_data.append(record)
                
                # Detener al alcanzar el límite deseado
                if len(self._mqtt_data) >= max_records:
                    client.disconnect()
            except Exception as e:
                print(f"Error parseando mensaje MQTT: {e}")

        # Configurar cliente MQTT
        client = mqtt.Client()
        client.on_message = on_message
        
        try:
            client.connect(host, port, timeout)
            client.subscribe(topic)
            print(f"Escuchando MQTT en {host}:{port}... Esperando {max_records} mensajes.")
            client.loop_forever() # Bloquea hasta que se desconecta en on_message
        except Exception as e:
            print(f"Error en la conexión MQTT: {e}")
        
        # Crear DataFrame
        df = pd.DataFrame(self._mqtt_data)
        
        if flatten_json and not df.empty and 'payload' in df.columns:
            df = self._flatten_payload_column(df, 'payload')
            
        return df

    def _flatten_payload_column(self, df, column_name):
        """Método privado para convertir columnas JSON/Dict en columnas individuales de Pandas."""
        # Asegurar que los strings de la BD se conviertan a diccionarios si es necesario
        if isinstance(df[column_name].iloc[0], str):
            df[column_name] = df[column_name].apply(lambda x: json.loads(x) if x else {})
            
        df_expanded = pd.json_normalize(df[column_name].tolist())
        df = pd.concat([df.drop(columns=[column_name]), df_expanded], axis=1)
        return df
'''
#################################################################################
#Lectura de datos en programa principal
#################################################################################
from chirpstack_reader import ChirpStackReader

# 1. Configurar credenciales
DB_CONF = {
    "host": "192.168.1.50",
    "database": "chirpstack_as",
    "user": "postgres",
    "password": "mi_password",
    "port": "5432"
}

MQTT_CONF = {
    "host": "192.168.1.50",
    "port": 1883,
    "topic": "application/+/device/+/event/up"
}

# 2. Inicializar la biblioteca
cs = ChirpStackReader(db_config=DB_CONF, mqtt_config=MQTT_CONF)

# ---- EJEMPLO 1: Obtener Datos Históricos ----
print("--- Cargando datos históricos ---")
df_historico = cs.fetch_historical_uplinks(limit=50)
print(df_historico.head())

# ---- EJEMPLO 2: Obtener Datos en Vivo ----
print("\n--- Capturando 5 datos en tiempo real ---")
df_en_vivo = cs.stream_live_uplinks(max_records=5)
print(df_en_vivo)

'''