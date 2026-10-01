"""
Rotas de Machine Learning & Analytics — EV ChargeOps
Responsável: Victor Mantovani
"""

from fastapi import APIRouter, Query
from ..services.ml_service import ml_service

router = APIRouter(prefix="/api/analytics", tags=["Machine Learning & Analytics (Victor Mantovani)"])

@router.get("/summary", summary="Retorna sumário estatístico da estação para ML")
def get_ml_summary():
    """
    Retorna métricas consolidadas de geração, recarga e importação da estação GoodWe
    para fundamentar análises estatísticas e modelos preditivos.
    """
    return ml_service.get_station_summary()

@router.get("/demand-prediction", summary="Previsão de demanda energética de recarga")
def get_demand_prediction(days: int = Query(7, ge=1, le=30, description="Dias à frente para projeção de demanda")):
    """
    Retorna a curva de projeção de consumo em kWh para os próximos dias,
    permitindo mitigar picos no condomínio e balancear a infraestrutura elétrica.
    """
    return ml_service.predict_demand(days_ahead=days)
