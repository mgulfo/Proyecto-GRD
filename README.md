# ⚡ Proyecto GRD

Este proyecto tiene como objetivo desarrollar un sistema integral para la detección de perturbaciones eléctricas y la predicción de consumo en entornos industriales, utilizando datos reales de medidores con frecuencia de muestreo de 10 segundos. Se trabaja con variables como tensión, corriente, potencia activa, distorsión armónica (THD), frecuencia y factor de potencia (FP), en configuraciones trifásicas.

El sistema implementado abarca todo el pipeline de análisis, desde la consulta a la base de datos hasta la visualización y predicción de eventos, utilizando herramientas modernas de ciencia de datos, aprendizaje automático y visualización.

---

## 🎯 Objetivos del Proyecto

- Consolidar una base de datos unificada en InfluxDB 1.8 / 2.7.
- Detectar perturbaciones mediante métodos estadísticos y de series temporales.
- Analizar la sensibilidad de distintas variables eléctricas ante eventos anómalos.
- Entrenar modelos de predicción (LSTM) para detección anticipada basada en errores.
- Evaluar y justificar la efectividad de los enfoques mediante métricas, gráficos y documentación técnica.

---

## 📄 Documentación Técnica del Proyecto

🔗 **[Ver Bitácora Técnica](https://drive.google.com/drive/folders/1tCQ2pb9OmT4hnKJpD__YTpGoqdQZVu-g?usp=drive_link)**  
Documento Técnica donde se detallan cada una de las fases del proyecto, incluyendo:

- Justificación técnica de cada decisión
- Análisis estadístico de variables
- Evaluación de modelos
- Gráficos y resultados
- Vinculación con bibliografía relevante y código fuente

🔗 **[Ver Github del Proyecto](hhttps://github.com/mgulfo/Proyecto-GRD)**  

---

## 📁 Estructura del Proyecto

```
Proyecto-GRD/
├── data/
├── logs/                # Logs del sistema
├── notebooks/           # Notebooks exploratorios
├── src/                 # Código fuente modular
│   ├── data_processing/ 
│   ├── ejecucion_continua/ 
│   ├── graphs/                     
│   ├── models/                
│   ├── utils/                         
│   ├── analysis.py          
│   ├── config.py         
│   ├── db_connector.py         
│   ├── query_engine.py          
│   ├── visualization.py          
├── tests/               # Pruebas automáticas
├── resources/           # Recursos, bibliografía, otros
├── main.py       # Pipeline principal
├── requirements.txt     # Dependencias
└── README.md
```

---

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
python main.py
```

Esto ejecuta todo el flujo

---

## ⚙️ Configuración

Editar el archivo `src/config.py` para ajustar:
- Fechas de consulta
- Ubicación
- Flags

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

---

## 📚 Recursos y Bibliografía

Los manuales y papers relevantes están en [la carpeta Bibliografía del drive](https://drive.google.com/drive/folders/1tv9Mvj972xAfFvOs7zQrCA4IotLX5HLP)

---

## 📌 Pendientes

- [ ] Detección de eventos
- [ ] Modelos de predicción
- [ ] Validación avanzada de parámetros
- [ ] Documentación extendida

📌 Autor: [INTI-IoE]
📅 Última actualización: [28/06/2025]
