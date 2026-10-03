from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ==========================================
# Schemas de IA e Chatbot (EVA)
# ==========================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Papel: 'user', 'assistant' ou 'system'")
    content: str = Field(..., description="Texto da mensagem")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pergunta ou solicitação do usuário")
    user_id: Optional[str] = Field("USR-001", description="ID do usuário para contexto personalizado")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Histórico prévio da conversa")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Resposta contextualizada gerada pela IA EVA")
    source: str = Field("openai_gpt" , description="Fonte da resposta ('openai_gpt' ou 'eva_expert_engine')")
    user_context_applied: bool = Field(True, description="Indica se os dados do veículo/consumo foram injetados no contexto")
    suggested_actions: Optional[List[str]] = Field(default_factory=list, description="Ações ou perguntas sugeridas")

# ==========================================
# Schemas de Sessões de Recarga (GoodWe HCA G2)
# ==========================================

class SessionItem(BaseModel):
    session_id: str
    user_id: str
    user_name: str
    unit: str
    vehicle_model: str
    battery_capacity_kwh: float
    start_time: str
    end_time: Optional[str] = None
    duration_minutes: int
    energy_delivered_kwh: float
    power_peak_kw: float
    voltage_v: float
    current_a: float
    cost_rate_per_kwh: float
    total_cost_brl: float
    status: str

class SessionsListResponse(BaseModel):
    total_sessions: int
    sessions: List[SessionItem]

class MetricsResponse(BaseModel):
    total_energy_kwh: float
    total_revenue_brl: float
    total_sessions_count: int
    average_session_duration_minutes: float
    average_energy_per_session_kwh: float
    active_chargers_count: int
    current_rate_per_kwh: float

# ==========================================
# Schemas de Tarifação e Rateio
# ==========================================

class RateioCalculateRequest(BaseModel):
    energy_kwh: float = Field(..., gt=0, description="Volume de energia consumida em kWh")
    rate_per_kwh: Optional[float] = Field(None, description="Taxa aplicada em R$/kWh (se omitido, usa a do condomínio)")

class RateioCalculateResponse(BaseModel):
    energy_kwh: float
    rate_per_kwh: float
    formula_applied: str
    total_amount_brl: float
    breakdown: Dict[str, float]

class SimulationRequest(BaseModel):
    vehicle_battery_kwh: Optional[float] = Field(69.0, description="Capacidade total da bateria em kWh (ex: 69.0 do Volvo EX30)")
    vehicle_range_km: Optional[float] = Field(None, description="Autonomia oficial do veículo no ciclo Inmetro, em km (ex: 338 para o Volvo EX30)")
    current_soc_percent: Optional[float] = Field(20.0, description="Nível atual de carga (%)")
    target_soc_percent: Optional[float] = Field(80.0, description="Nível desejado de carga (%)")
    charger_power_kw: Optional[float] = Field(7.0, description="Potência nominal do carregador GoodWe em kW (GW7K: 7.0)")
    rate_per_kwh: Optional[float] = Field(0.95, description="Valor cobrado por kWh")

class SimulationResponse(BaseModel):
    energy_needed_kwh: float
    estimated_time_hours: float
    estimated_time_formatted: str
    total_cost_brl: float
    estimated_added_range_km: float
