README TESTS

# 🧪 Tests - Proyecto Smart Grid

Esta carpeta contiene pruebas automatizadas para asegurar que los módulos de limpieza y procesamiento de datos funcionen correctamente.

---

## ✅ ¿Cómo ejecutar los tests?

### Opción 1: Desde terminal con `pytest`

1. Abrí la terminal integrada de VS Code (o desde consola)
2. Desde la raíz del proyecto, ejecutá:

```bash
pytest tests/ -v
```

Esto mostrará el resultado detallado de cada test:

```
tests/test_data_cleaning.py::test_preprocess_removes_nulls PASSED
tests/test_data_cleaning.py::test_preprocess_removes_all_nulls PASSED
```

> Asegurate de tener `pytest` instalado:
> 
> ```bash
> pip install pytest
> ```

---

### Opción 2: Ejecutar desde VS Code con el botón

1. Abrí el archivo `test_data_cleaning.py`
2. Al lado de cada función, deberías ver:

```
▶ Run Test | Debug Test
```

3. También podés abrir la pestaña **"Testing"** en el panel izquierdo y ejecutar todos los tests desde ahí.

---

## 🛠 Configuración recomendada (si no ves los tests en VS Code)

1. `Ctrl + Shift + P` → "Python: Configure Tests"
2. Seleccioná:
   - Framework: `pytest`
   - Carpeta de tests: `tests/`
3. Guardá y reiniciá VS Code si es necesario

---

## 📦 Archivos actuales

- `test_data_cleaning.py`: pruebas para la función `preprocess_data()`

---

## 🧠 ¿Por qué usar tests?

- Detectan errores automáticamente al modificar el código
- Aseguran que la limpieza de datos funcione como se espera
- Son una buena práctica profesional y facilitan el mantenimiento del proyecto
