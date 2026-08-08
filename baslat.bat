@echo off
title Sertifika Olusturucu
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   Sertifika Olusturucu baslatiliyor...
echo   Tarayici adres: http://127.0.0.1:5000
echo   Durdurmak icin: Ctrl+C
echo ==========================================
echo.

start "" http://127.0.0.1:5000
python app.py

pause