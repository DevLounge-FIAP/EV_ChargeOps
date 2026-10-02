"""
Rotas do Dashboard Administrativo & Gestão — EV ChargeOps
Responsável: Bruno Silva
"""

from fastapi import APIRouter
import pandas as pd
from ..config import settings
from ..services.data_service import data_service

router = APIRouter(prefix="/api/admin", tags=["Dashboard & Gestão Administrativa (Bruno Silva)"])

@router.get("/overview", summary="Visão consolidada para o síndico e administradora")
def get_admin_overview():
    """
    Retorna métricas executivas consolidadas: faturamento total, volume de energia entregue,
    tempo médio de recarga e status do carregador GoodWe HCA G2.
    """
    metrics = data_service.get_metrics()
    condo = data_service.get_condo_metadata()
    return {
        "condominio": condo.get("condominium", {}),
        "carregador": condo.get("condominium", {}).get("charger", {}),
        "metricas_operacionais": metrics,
        "faturamento_total_brl": metrics.total_revenue_brl,
        "total_sessoes_registradas": metrics.total_sessions_count,
        "tarifa_ativa": metrics.current_rate_per_kwh
    }

@router.get("/users", summary="Gestão e listagem de usuários e veículos cadastrados")
def list_registered_users():
    """
    Retorna lista dos condôminos autorizados, unidades e especificações dos veículos elétricos.
    """
    metadata = data_service.get_condo_metadata()
    return {
        "total_cadastrados": len(metadata.get("users", [])),
        "usuarios": metadata.get("users", [])
    }

@router.get("/efficiency-indicators", summary="Indicadores de eficiência energética do ponto de recarga")
def get_efficiency_indicators():
    """
    Consolida taxas de autoconsumo e contribuição da estação solar/rede GoodWe a partir de estacao_diario.csv.
    """
    csv_path = settings.CSV_FILE_PATH
    if not csv_path.exists():
        return {"error": "estacao_diario.csv não encontrado"}

    df = pd.read_csv(csv_path)
    return {
        "media_taxa_autoconsumo_pct": round(float(df["taxa_autoconsumo_pct"].mean()), 2),
        "media_taxa_contribuicao_pct": round(float(df["taxa_contribuicao_pct"].mean()), 2),
        "dias_com_geracao_solar": int((df["geracao_kwh"] > 0).sum()),
        "total_geracao_solar_kwh": round(float(df["geracao_kwh"].sum()), 2),
        "total_consumo_kwh": round(float(df["consumo_kwh"].sum()), 2)
    }
