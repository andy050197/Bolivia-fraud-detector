@echo off
echo Compilando Bolivia Fraud Detector...
pyinstaller --onefile --windowed --name BoliviaFraudDetector --add-data "data;data" --add-data "assets;assets" main.py
echo.
echo Listo! El archivo .exe se encuentra en la carpeta dist/
pause
