# utils.py

"""
Módulo de utilidades generales.
Incluye funciones auxiliares que pueden ser reutilizadas en distintos módulos.
"""

from datetime import datetime
import pytz
from config import LOCAL_TIMEZONE

def convert_utc_to_local(utc_date_str, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """
    Convierte una fecha en formato UTC a la zona local definida en la configuración.

    Args:
        utc_date_str (str): Fecha en formato UTC.
        fmt (str): Formato de la fecha.

    Returns:
        datetime: Fecha convertida a la zona local.
    """
    utc_dt = datetime.strptime(utc_date_str, fmt)
    utc_dt = pytz.utc.localize(utc_dt)
    local_tz = pytz.timezone(LOCAL_TIMEZONE)
    return utc_dt.astimezone(local_tz)
