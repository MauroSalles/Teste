@echo off
REM ============================================================
REM setup.bat — Configuração automática do ambiente de desenvolvimento
REM Sistema de Gelateria — Windows
REM ============================================================
REM Uso: Clique duas vezes ou execute no CMD dentro da pasta do projeto

setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo    🍦  Setup — Sistema de Gelateria
echo ============================================
echo.

REM ── 1. Verificar Git ─────────────────────────────────────────
echo [INFO] Verificando Git...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Git nao encontrado.
    echo        Instale em: https://git-scm.com/downloads
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('git --version') do echo [OK] %%i

REM ── 2. Verificar Python 3.9+ ────────────────────────────────
echo.
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Python nao encontrado pelo comando 'python'.
    echo         Tentando 'py'...
    py --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Python nao encontrado.
        echo        Instale em: https://www.python.org/downloads/
        echo        Marque a opcao "Add Python to PATH" durante a instalacao!
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)
for /f "tokens=*" %%i in ('!PYTHON_CMD! --version') do echo [OK] %%i

REM ── 3. Verificar Node.js ─────────────────────────────────────
echo.
echo [INFO] Verificando Node.js...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Node.js nao encontrado. Instale em: https://nodejs.org
    echo         Necessario apenas para o frontend.
) else (
    for /f "tokens=*" %%i in ('node --version') do echo [OK] Node.js %%i
)

REM ── 4. Criar ambiente virtual Python ─────────────────────────
echo.
echo [INFO] Criando ambiente virtual Python (venv)...
if exist "venv\" (
    echo [AVISO] Pasta 'venv' ja existe — pulando criacao.
) else (
    !PYTHON_CMD! -m venv venv
    echo [OK] Ambiente virtual criado em .\venv
)

REM Ativar venv
call venv\Scripts\activate.bat
echo [OK] Ambiente virtual ativado.

REM ── 5. Instalar dependências Python ──────────────────────────
echo.
if exist "requirements.txt" (
    echo [INFO] Instalando dependencias Python ^(requirements.txt^)...
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo [OK] Dependencias Python instaladas.
) else (
    echo [AVISO] requirements.txt nao encontrado.
)

REM ── 6. Instalar dependências Node.js ─────────────────────────
echo.
if exist "package.json" (
    echo [INFO] Instalando dependencias Node.js na raiz...
    npm install
    echo [OK] Dependencias Node.js instaladas.
)

if exist "frontend\package.json" (
    echo [INFO] Instalando dependencias Node.js em .\frontend ...
    cd frontend
    npm install
    cd ..
    echo [OK] Dependencias Node.js instaladas em .\frontend
)

REM ── 7. Criar arquivo .env ─────────────────────────────────────
echo.
if exist ".env.example" (
    if exist ".env" (
        echo [AVISO] Arquivo .env ja existe — nao sera sobrescrito.
    ) else (
        copy .env.example .env >nul
        echo [OK] Arquivo .env criado a partir do .env.example
        echo [AVISO] Edite o .env com suas credenciais reais antes de rodar o projeto!
    )
) else (
    echo [AVISO] .env.example nao encontrado — crie o .env manualmente.
)

REM ── 8. Resumo final ──────────────────────────────────────────
echo.
echo ============================================
echo    Setup concluido!
echo ============================================
echo.
echo Proximos passos:
echo.
echo   1. Edite o arquivo .env com suas credenciais:
echo      Abra .env no Bloco de Notas ou VS Code
echo.
echo   2. Inicie o PostgreSQL:
echo      Abra o pgAdmin ou inicie o servico 'postgresql-x64-xx'
echo      em Gerenciamento de Computador ^> Servicos
echo.
echo   3. Inicie o backend:
echo      venv\Scripts\activate
echo      python backend\app.py
echo      Acesse: http://localhost:5000
echo.
echo   4. Inicie o frontend ^(outro CMD^):
echo      cd frontend ^&^& npm start
echo      Acesse: http://localhost:3000
echo.
echo Documentacao:
echo   SETUP_LOCAL.md             - Guia completo
echo   REQUISITOS.md              - O que precisa instalar
echo   TROUBLESHOOTING_VERCEL.md  - Problemas com Vercel
echo.
pause
