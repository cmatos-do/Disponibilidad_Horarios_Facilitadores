@echo off
title Servidor de Disponibilidad y Horarios - INFOTEP
echo =====================================================================
echo    INICIANDO EL VISUALIZADOR DE DISPONIBILIDAD Y HORARIOS (INFOTEP)
echo =====================================================================
echo.
echo [1/3] Detectando archivos de Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    echo Por favor, instala Python 3 para poder procesar los horarios.
    pause
    exit /b
)

echo [2/3] Instalando dependencias de lectura de PDF (pypdf)...
python -m pip install pypdf --quiet

echo [3/3] Iniciando el servidor de actualizacion en tiempo real...
echo.
echo =====================================================================
echo  ¡TODO LISTO!
echo  El visualizador se abrira automaticamente en tu navegador.
echo  Deja esta ventana abierta para que los horarios se actualicen solos.
echo =====================================================================
echo.

start "" "http://localhost:8000"
python server.py
pause