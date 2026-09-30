from fastapi import APIRouter
from ..schemas.models import (
    RateioCalculateRequest,
    RateioCalculateResponse,
    SimulationRequest,
    SimulationResponse
)
from ..services.billing_service import billing_service
from ..services.data_service import data_service

router = APIRouter(prefix="/api/billing", tags=["Tarifação & Motor de Rateio"])

@router.post("/calculate", response_model=RateioCalculateResponse, summary="Calcula a fatura pelo modelo de rateio")
def calculate_bill(request: RateioCalculateRequest):
    """
    Aplica a fórmula oficial do rateio:
    `Valor da Fatura = Energia Consumida (kWh) × Valor Cobrado por kWh`
    """
    return billing_service.calculate_rateio(request)

@router.post("/simulate", response_model=SimulationResponse, summary="Simulador paramétrico de recarga")
def simulate_charge(request: SimulationRequest):
    """
    Converte parâmetros de recarga:
    `Tempo de Conexão ↔ kWh Necessários ↔ Custo Estimado da Recarga`
    """
    return billing_service.simulate_charge(request)

@router.get("/config", summary="Retorna parâmetros tarifários do condomínio")
def get_billing_config():
    """Retorna dados de taxa e tarifação configurados."""
    metadata = data_service.get_condo_metadata()
    return metadata.get("condominium", {})
