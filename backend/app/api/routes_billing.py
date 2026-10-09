from fastapi import APIRouter, Query
from ..schemas.models import (
    RateioCalculateRequest,
    RateioCalculateResponse,
    SimulationRequest,
    SimulationResponse
)
from ..services.billing_service import billing_service
from ..services.data_service import data_service
from typing import Optional

router = APIRouter(prefix="/api/billing", tags=["Tarifação & Pagamentos (Michelly)"])

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

@router.post("/checkout", summary="Simulação de checkout e autorização de recarga")
def simulate_checkout(
    energy_kwh: float = Query(..., gt=0, description="Energia da recarga em kWh (maior que zero)"),
    unit: str = "Apto 42B",
    payment_method: str = "PIX",
    start_hour: Optional[int] = Query(None, ge=0, le=23, description="Hora de início da sessão (0 a 23). Vazio usa a hora atual"),
):
    """
    Simula autorização digital de pagamento e emissão de comprovante individualizado.
    """
    return billing_service.process_checkout_simulation(energy_kwh=energy_kwh, unit=unit, payment_method=payment_method, start_hour=start_hour)

@router.get("/config", summary="Retorna parâmetros tarifários do condomínio")
def get_billing_config():
    """Retorna dados de taxa e tarifação configurados."""
    metadata = data_service.get_condo_metadata()
    return metadata.get("condominium", {})

