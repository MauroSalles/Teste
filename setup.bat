@echo off
REM ============================================================
REM Gelateria Sistema — Setup Automático (Windows)
REM Uso: setup.bat
REM ============================================================
title Gelateria Setup

echo.
echo   ===================================
echo   Gelateria Sistema - Setup Local
echo   ===================================
echo.

REM 1. Python
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado. Instale em https://python.org
  pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Python %PY_VER% detectado

REM 2. Virtual env
if not exist ".venv" (
  python -m venv .venv
  echo [OK] Ambiente virtual criado
) else (
  echo [OK] Ambiente virtual ja existe
)
call .venv\Scripts\activate.bat
echo [OK] Ambiente virtual ativado

REM 3. Dependencias
echo [INFO] Instalando dependencias...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt pytest pytest-cov
echo [OK] Dependencias instaladas

REM 4. .env
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo [AVISO] .env criado - edite as credenciais do banco
) else (
  echo [OK] .env ja existe
)

echo.
echo   =====================
echo   Setup concluido!
echo   =====================
echo.
echo   Proximos passos:
echo     1. Edite .env com suas credenciais
echo     2. Inicie: python -m flask run
echo     3. Testes: pytest tests\ -v
echo.
pause
