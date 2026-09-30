import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se existir
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "EV ChargeOps API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "API REST do ecossistema EV ChargeOps (GoodWe + FIAP). "
        "Centraliza a lógica de rateio por kWh, ingestão de dados e IA EVA."
    )
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DEFAULT_RATE_PER_KWH: float = float(os.getenv("DEFAULT_RATE_PER_KWH", "0.95"))
    
    # Caminhos para arquivos de dados
    DATA_DIR: Path = BASE_DIR / "data"
    CSV_FILE_PATH: Path = DATA_DIR / "goodwe_sessions_sample.csv"
    JSON_FILE_PATH: Path = DATA_DIR / "ev_chargeops_data.json"

settings = Settings()
