# ⚡ Proyecto: Detección de Perturbaciones y Predicción de Consumo en Redes Eléctricas Industriales

Este proyecto analiza series temporales provenientes de medidores industriales, con el objetivo de detectar perturbaciones eléctricas y predecir el consumo energético en redes Smart Grid.

---

## 📁 Estructura del Proyecto

```
Proyecto-GRD/
├── data/
│   ├── raw/             # Datos crudos y limpios
│   └── images/          # Visualizaciones guardadas
├── logs/                # Logs del sistema
├── notebooks/           # Notebooks exploratorios
├── src/                 # Código fuente modular
│   ├── data_processing/             
│       ├── data_cleaning.py            
│   ├── models/         
│       └── anomaly_detection.py          
│   ├── utils/             
│       ├── logger.py         
│       ├── utils.py             
│   ├── analysis.py          
│   ├── config.py         
│   ├── db_connector.py         
│   ├── query_engine.py          
│   ├── visualization.py          
├── tests/               # Pruebas automáticas
├── resources/           # Recursos, bibliografía, otros
├── main_logger.py       # Pipeline principal con logging
├── main_sin_logger.py       # Pipeline principal sin logging
├── requirements.txt     # Dependencias
└── README.md
```

## 📋 Diccionario de Variables

| Variable         | Significado                               |
|------------------|-------------------------------------------|
| `time`           | Timestamp de la medición                  |
| `Vrms_L1_Ins`    | Tensión RMS Instantánea Fase 1            |
| `Vrms_L2_Ins`    | Tensión RMS Instantánea Fase 2            |
| `Vrms_L3_Ins`    | Tensión RMS Instantánea Fase 3            |
| `THDV_L1_Ins`    | THD de Tensión en Fase 1                  |
| `THDV_L2_Ins`    | THD de Tensión en Fase 2                  |
| `THDV_L3_Ins`    | THD de Tensión en Fase 3                  |
| `PowA_L1_Ins`    | Potencia Activa Instantánea Fase 1        |
| `PowA_L2_Ins`    | Potencia Activa Instantánea Fase 2        |
| `PowA_L3_Ins`    | Potencia Activa Instantánea Fase 3        |
| `PowS_L1_Ins`    | Potencia Aparente Instantánea Fase 1      |
| `PowS_L2_Ins`    | Potencia Aparente Instantánea Fase 2      |
| `PowS_L3_Ins`    | Potencia Aparente Instantánea Fase 3      |
| `PowF_T_Ins`     | Factor de Potencia Total Instantáneo      |
| `EA_I_IV_T`      | Energía Activa Importada Total            |
| `Fre_Ins`        | Frecuencia Instantánea                    |
| `Irms_L1_Ins`    | Corriente RMS Instantánea Fase 1          |
| `Irms_L2_Ins`    | Corriente RMS Instantánea Fase 2          |
| `Irms_L3_Ins`    | Corriente RMS Instantánea Fase 3          |
| `THDI_L1_Ins`    | THD de Corriente en Fase 1                |
| `THDI_L2_Ins`    | THD de Corriente en Fase 2                |
| `THDI_L3_Ins`    | THD de Corriente en Fase 3                |

---

## 🚀 Ejecución Rápida

```bash
python main_logger.py
```

Esto ejecuta todo el flujo: consulta → limpieza → visualización. Los resultados se guardan automáticamente.

---

## ⚙️ Configuración

Editar el archivo `src/config.py` para ajustar:
- Fechas de consulta
- Ubicación (`location`)
- Flags: `SHOW_GRAPHS`, `SAVE_OUTPUTS`, `EXECUTE_VISUALIZATION`

---

## 🧪 Pruebas

Este proyecto usa `pytest`. Ejecutá las pruebas con:

```bash
pytest tests/
```

---

## 🛠️ Requisitos

- Python 3.8+
- InfluxDB 1.8 y/o 2.x (conexión ya configurada)
- Librerías: pandas, numpy, matplotlib, seaborn, influxdb-client, pytest
- Grafana
- Bertual
- Machine Learning (RNN)
- Pandas, NumPy, Matplotlib

Instalación rápida:

```bash
pip install -r requirements.txt
```

---

## 📚 Recursos y Bibliografía
Los manuales y papers relevantes están en la carpeta resources/.

---

## 📌 Pendientes

- [ ] Detección de eventos
- [ ] Modelos de predicción
- [ ] Validación avanzada de parámetros
- [ ] Documentación extendida

📌 Autor: [INTI-IoE]
📅 Última actualización: [31/03/2025]
