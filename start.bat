@echo off
title Stonelytics Studio - SRIE Engine
cd /d "%~dp0"

:: ============================================
::  STONELYTICS STUDIO - SRIE ENGINE
::  OpenAI API Key configurada
:: ============================================

:MENU
cls
echo.
echo  ============================================
echo    STONELYTICS STUDIO - SRIE ENGINE
echo    Ingenieria Empresarial Asistida por IA
echo  ============================================
echo.
echo  1. Iniciar servidor (SQLite - desarrollo local)
echo  2. Iniciar servidor (PostgreSQL - produccion)
echo  3. Salir
echo.
set /p opcion="Selecciona una opcion (1-3): "

if "%opcion%"=="1" set DATABASE_URL=sqlite:///studio.db & goto START
if "%opcion%"=="2" set DATABASE_URL=postgresql://stonelytics:stonelytics@localhost:5432/stonelytics & goto START
if "%opcion%"=="3" exit /b
goto MENU

:START

:: OpenAI - API Key (desde .env o variable de entorno)
if exist .env (
    for /f "tokens=*" %%a in (.env) do set %%a
)
if "%OPENAI_API_KEY%"=="" (
    echo [WARN] OPENAI_API_KEY no configurada. Crea un archivo .env con: OPENAI_API_KEY=tu-key
)

:: Crear entorno virtual si no existe
if not exist venv\Scripts\python.exe (
    echo.
    echo [1/3] Creando entorno virtual...
    py -m venv venv
)

:: Activar venv
call venv\Scripts\activate.bat

:: Instalar dependencias
python -m pip install --upgrade pip -q >nul 2>&1

echo [2/3] Instalando dependencias...
python -m pip install Flask==3.1.1 Flask-Mail==0.9.1 Flask-SQLAlchemy==3.1.1 Flask-WTF==1.2.2 flask-limiter==3.8.0 python-dotenv==1.1.0 requests==2.32.3 email-validator==2.2.0 flask-login==0.6.3 -q
echo [OK] Dependencias instaladas

echo [3/3] Iniciando servidor...
echo.
echo  ========================================
echo   Stonelytics Studio - SRIE Engine
echo  ========================================
echo.
echo   Admin:    http://localhost:10000/admin/login
echo   Studio:   http://localhost:10000/studio/
echo.
echo   Email:    daviddb@stonelytics.tech
echo   Password: StonelyticsAdmin2026!
echo.
echo   DATABASE: %DATABASE_URL%
echo  ========================================
echo.

python app.py

pause
