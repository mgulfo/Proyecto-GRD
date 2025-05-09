
# db_connector.py

"""
Módulo para gestionar la conexión a InfluxDB.
Se implementa una clase DBConnector que ofrece métodos para conectarse a InfluxDB 1.8 y 2.7, y realizar consultas.
"""

# src/db_connector.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytz
from datetime import datetime
from influxdb import InfluxDBClient
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from utils.utils import convert_df_utc_to_local
from config import INFLUXDB1_CONFIG, INFLUXDB2_CONFIG, LOCAL_TIMEZONE

class DBConnector:
    def __init__(self):
        self.client1 = None
        self.client2 = None

    def connect_influxdb1(self):

        """Conecta a InfluxDB 1.8 utilizando la configuración definida."""
        self.client1 = InfluxDBClient(
            host=INFLUXDB1_CONFIG['host'],
            port=INFLUXDB1_CONFIG['port'],
            username=INFLUXDB1_CONFIG['username'],
            password=INFLUXDB1_CONFIG['password'],
            database=INFLUXDB1_CONFIG['database'],
            ssl=INFLUXDB1_CONFIG['ssl'],
            timeout=INFLUXDB1_CONFIG['timeout'],
            verify_ssl=INFLUXDB1_CONFIG['verify_ssl']
        )
        return self.client1

    def connect_influxdb2(self):
        """Conecta a InfluxDB 2.7 utilizando la configuración definida."""
        self.client2 = influxdb_client.InfluxDBClient(
            url=INFLUXDB2_CONFIG['url'],
            token=INFLUXDB2_CONFIG['token'],
            org=INFLUXDB2_CONFIG['org'],
            timeout=INFLUXDB2_CONFIG['timeout'],
            ssl=INFLUXDB2_CONFIG['ssl'],
            verify_ssl=INFLUXDB2_CONFIG['verify_ssl']
        )
        return self.client2

    def query_influx1(self, query):
        """Realiza una consulta a InfluxDB 1.8.
        
        Args:
            query (str): Consulta en lenguaje InfluxQL.
        
        Returns:
            DataFrame o lista de puntos.
        """

        if self.client1 is None:
            self.client1 = InfluxDBClient(
                host=INFLUXDB1_CONFIG['host'],
                port=INFLUXDB1_CONFIG['port'],
                username=INFLUXDB1_CONFIG['username'],
                password=INFLUXDB1_CONFIG['password'],
                database=INFLUXDB1_CONFIG['database'],
                ssl=INFLUXDB1_CONFIG['ssl'],
                timeout=INFLUXDB1_CONFIG['timeout'],
                verify_ssl=INFLUXDB1_CONFIG['verify_ssl']
            )
        return self.client1

    def connect_influxdb2(self):
        if self.client2 is None:
            self.client2 = influxdb_client.InfluxDBClient(
                url=INFLUXDB2_CONFIG['url'],
                token=INFLUXDB2_CONFIG['token'],
                org=INFLUXDB2_CONFIG['org'],
                timeout=INFLUXDB2_CONFIG['timeout'],
                ssl=INFLUXDB2_CONFIG['ssl'],
                verify_ssl=INFLUXDB2_CONFIG['verify_ssl']
            )
        return self.client2

    def query_influx1(self, query):

        if not self.client1:
            self.connect_influxdb1()
        result = self.client1.query(query)
        return list(result.get_points())

    def query_influx2(self, query):

        """Realiza una consulta a InfluxDB 2.7 usando Flux.
        
        Args:
            query (str): Consulta en lenguaje Flux.
        
        Returns:
            DataFrame con los resultados.
        """

        if not self.client2:
            self.connect_influxdb2()
        query_api = self.client2.query_api()
        return query_api.query_data_frame(query=query)

    @staticmethod
    def convert_to_local(utc_date_str, fmt="%Y-%m-%dT%H:%M:%SZ"):

        """Convierte una fecha UTC a la zona local definida en la configuración.
        
        Args:
            utc_date_str (str): Fecha en formato UTC.
            fmt (str): Formato de la fecha.
        
        Returns:
            datetime: Fecha convertida a la zona local.
        """

        utc_time = datetime.strptime(utc_date_str, fmt)
        utc_time = pytz.utc.localize(utc_time)
        local_tz = pytz.timezone(LOCAL_TIMEZONE)
        return utc_time.astimezone(local_tz)
