"""
Rotas do Dashboard Administrativo & Gestão — EV ChargeOps
Responsável: Bruno Santos
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query
import pandas as pd
from ..config import settings
from ..services.data_service import data_service
from ..services.dashboard_service import dashboard_service

router = APIRouter(prefix="/api/admin", tags=["Dashboard & Gestão Administrativa (Bruno Santos)"])

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


# Rotas usadas pela aba "Dashboard Administrativo"

@router.get("/dashboard", summary="Métricas gerais do dashboard (consumo, bateria, tempo, faturamento, eficiência)")
def get_dashboard(
    user_id: Optional[str] = Query(None, description="Filtra por usuário, ex: USR-001"),
    inicio: Optional[date] = Query(None, description="Data inicial (AAAA-MM-DD)"),
    fim: Optional[date] = Query(None, description="Data final (AAAA-MM-DD), inclusive"),
):
    """KPIs, séries mensais, resumo por usuário e veículo e avisos sobre os dados."""
    return dashboard_service.dashboard(user_id, inicio, fim)

@router.get("/payments", summary="Histórico de pagamentos (rateio por sessão)")
def get_payments(
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="Ex: completed"),
    inicio: Optional[date] = Query(None),
    fim: Optional[date] = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Pagamentos por sessão (kWh x tarifa), do mais recente para o mais antigo, com paginação."""
    return dashboard_service.pagamentos(user_id, status, inicio, fim, limit, offset)

@router.get("/chargers", summary="Gestão de carregadores: especificações e uso")
def get_chargers():
    """Dados do carregador GoodWe e indicadores de uso (sessões, horas e ocupação)."""
    return dashboard_service.carregadores()
