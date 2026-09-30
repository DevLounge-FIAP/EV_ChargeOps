#!/usr/bin/env python3
"""
Script de inicializacao da API EV ChargeOps (GoodWe + FIAP)
Execucao: python run.py
"""
import sys
import uvicorn
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("EV ChargeOps - Backend & IA EVA (GoodWe + FIAP)")
    print(f"Iniciando servidor em: http://{settings.HOST}:{settings.PORT}")
    print(f"Documentacao Swagger: http://localhost:{settings.PORT}/docs")
    print("Carregador integrado: GoodWe HCA G2")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
