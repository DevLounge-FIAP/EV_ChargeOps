from typing import Optional
from fastapi import APIRouter, Query
from ..schemas.models import SessionsListResponse, MetricsResponse
from ..services.data_service import data_service

router = APIRouter(prefix="/api/sessions", tags=["Sessões & Telemetria (GoodWe)"])

@router.get("", response_model=SessionsListResponse, summary="Lista histórico de sessões de recarga")
def list_sessions(user_id: Optional[str] = Query(None, description="Filtrar sessões por ID de usuário")):
    """
    Retorna o histórico de recargas sanitizado a partir dos dados do GoodWe HCA G2.
    Permite filtrar por condômino específico.
    """
    if user_id:
        sessions = data_service.get_sessions_by_user(user_id)
    else:
        sessions = data_service.get_all_sessions()
    
    return SessionsListResponse(
        total_sessions=len(sessions),
        sessions=sessions
    )

@router.get("/metrics", response_model=MetricsResponse, summary="Retorna métricas operacionais consolidadas")
def get_metrics():
    """
    Agregações de telemetria: consumo total em kWh, faturamento total,
    tempo médio por recarga e tarifa vigente.
    """
    return data_service.get_metrics()
