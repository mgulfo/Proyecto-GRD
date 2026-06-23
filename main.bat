@echo off
SET PYTHON_CMD=python main.py

echo Iniciando el script supervisor en Windows...

:start_loop
echo --------------------------------------------------
echo Iniciando programa Python...
%PYTHON_CMD%

echo El programa Python ha terminado. Reiniciando en 10 segundos...
timeout /t 10 /nobreak
goto start_loop
