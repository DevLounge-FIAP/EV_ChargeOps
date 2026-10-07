#!/usr/bin/env bash
# Inicia o EV ChargeOps (API + site) com um comando só.
# Uso: bash iniciar.sh   (Git Bash, Linux ou Mac)

cd "$(dirname "$0")/backend" || exit 1

if command -v python >/dev/null 2>&1; then PY=python; else PY=python3; fi

if [ ! -d .venv ]; then
    echo "Criando o ambiente virtual (só na primeira vez)..."
    $PY -m venv .venv || { echo "Não foi possível criar o ambiente virtual. Confira se o Python 3.10 ou superior está instalado."; exit 1; }
fi

if [ -f .venv/Scripts/activate ]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo "Instalando as dependências (demora só na primeira vez)..."
pip install -q -r requirements.txt || { echo "Erro ao instalar as dependências."; exit 1; }

echo "Site e API em: http://localhost:8000  (para parar, use Ctrl + C)"
python run.py
