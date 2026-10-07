@echo off
rem Inicia o EV ChargeOps (API + site) com um comando so.
rem Uso: dois cliques neste arquivo, ou digite iniciar.bat no terminal.

cd /d "%~dp0backend"

if not exist .venv (
    echo Criando o ambiente virtual ^(so na primeira vez^)...
    python -m venv .venv
    if errorlevel 1 (
        echo Nao foi possivel criar o ambiente virtual. Confira se o Python 3.10 ou superior esta instalado.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

echo Instalando as dependencias ^(demora so na primeira vez^)...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Erro ao instalar as dependencias.
    pause
    exit /b 1
)

rem abre o navegador depois de 5 segundos, quando o servidor ja subiu
start "" cmd /c "timeout /t 5 >nul & start http://localhost:8000"

echo Site e API em: http://localhost:8000  ^(para parar, use Ctrl + C^)
python run.py
pause
