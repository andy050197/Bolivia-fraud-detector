@echo off
echo ============================================
echo   Bolivia Fraud Detector - Instalador
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python no encontrado.
    echo Descarga Python 3.11 desde: https://python.org/downloads
    echo Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

echo [OK] Python encontrado.
echo.
echo Instalando dependencias...
pip install -r requirements.txt

IF ERRORLEVEL 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo [OK] Instalacion completada!
echo.
echo Para ejecutar el programa: python main.py
echo Para compilar el .exe:     pyinstaller --onefile --windowed --name BoliviaFraudDetector main.py
echo.
pause
