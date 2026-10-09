from ..config import settings
from ..schemas.models import (
    RateioCalculateRequest,
    RateioCalculateResponse,
    SimulationRequest,
    SimulationResponse
)
from .data_service import data_service
from .ml_service import ml_service
from datetime import datetime

# Tempo de recarga calibrado com as 242 sessões reais do SEMS+ (R² 0,86, erro médio de 22 min):
# tempo (h) = TEMPO_FIXO_H + TEMPO_POR_KWH_H x energia (kWh)
TEMPO_FIXO_H = 0.94
TEMPO_POR_KWH_H = 0.366

# Média do consumo dos 3 modelos do catálogo (capacidade total ÷ autonomia Inmetro), em km por kWh.
# Usada quando a requisição não informa a autonomia do veículo.
KM_POR_KWH_PADRAO = 4.6

class BillingService:
    def calculate_tarifa_atual(self, hora=None):
            """
                Calcula a tarifa com base no horário atual
            """
            if hora is None: #se não receber um horário, utiliza o horário atual 
                hora = datetime.now().hour
            try:
                tabela = ml_service.get_dynamic_pricing()["tabela_hora_inicio"]
                return next(t["tarifa_brl_kwh"] for t in tabela if t["hora_inicio"] == hora)
            except Exception:
                return settings.DEFAULT_RATE_PER_KWH
    
    def calculate_rateio(self, req: RateioCalculateRequest) -> RateioCalculateResponse:
        """
        Aplica a fórmula oficial do rateio EV ChargeOps:
        Valor da Fatura = Energia Consumida (kWh) × Valor Cobrado por kWh
        """
        rate = req.rate_per_kwh if req.rate_per_kwh is not None else self.calculate_tarifa_atual()
        total_amount = round(req.energy_kwh * rate, 2)

        base = settings.DEFAULT_RATE_PER_KWH
        variacao_pct = round((rate - base) / base * 100, 2)

        if variacao_pct > 0:
            reason = f"Tarifa de horário de pico: + {variacao_pct}% sobre a tarifa base (R$ {base:.2f}/kWh)"
        elif variacao_pct < 0:
            reason = f"Tarifa de horário fora de pico: {variacao_pct}% sobre a tarifa base (R$ {base:.2f}/kWh)"
        else:
            reason = "Tarifa base aplicada"

        return RateioCalculateResponse(
            energy_kwh=round(req.energy_kwh, 2),
            rate_per_kwh=rate,
            formula_applied="Valor = Energia (kWh) × R$ Rateio/kWh",
            total_amount_brl=total_amount,
            breakdown={
                "tarifa_base_brl_kwh": base,
                "variacao_percentual": variacao_pct
            },
            rate_reason=reason
        )
    
    def simulate_charge(self, sim: SimulationRequest) -> SimulationResponse:
        """
        Simula o carregamento relacionando:
        Tempo (horas) <-> Energia Entregue (kWh) <-> Custo Final (R$)
        O tempo vem de uma relação calibrada com sessões reais, e a autonomia segue a
        convenção capacidade total ÷ autonomia Inmetro de cada veículo.
        """
        battery = sim.vehicle_battery_kwh or 69.0
        cur_soc = 20.0 if sim.current_soc_percent is None else max(0.0, min(sim.current_soc_percent, 100.0))
        target_soc = 80.0 if sim.target_soc_percent is None else max(cur_soc, min(sim.target_soc_percent, 100.0))
        power = sim.charger_power_kw or 7.0
        rate = sim.rate_per_kwh or self.calculate_tarifa_atual()

        # Volume necessário em kWh
        delta_percent = (target_soc - cur_soc) / 100.0
        energy_needed = round(battery * delta_percent, 2)

        # Tempo em horas: relação calibrada nas sessões reais, com o piso físico da potência nominal
        if energy_needed > 0:
            calibrated_hours = TEMPO_FIXO_H + TEMPO_POR_KWH_H * energy_needed
            minimum_hours = energy_needed / power
            time_hours = round(max(calibrated_hours, minimum_hours), 2)
        else:
            time_hours = 0.0

        # Formatação horas e minutos
        total_mins = int(round(time_hours * 60))
        hours = total_mins // 60
        mins = total_mins % 60
        formatted_time = f"{hours}h {mins:02d}min"

        # Custo financeiro
        total_cost = round(energy_needed * rate, 2)

        # Autonomia adicionada: consumo do veículo = capacidade total ÷ autonomia Inmetro (km por kWh)
        if sim.vehicle_range_km and battery > 0:
            km_per_kwh = sim.vehicle_range_km / battery
        else:
            km_per_kwh = KM_POR_KWH_PADRAO
        added_range_km = round(energy_needed * km_per_kwh, 1)

        return SimulationResponse(
            energy_needed_kwh=energy_needed,
            estimated_time_hours=time_hours,
            estimated_time_formatted=formatted_time,
            total_cost_brl=total_cost,
            estimated_added_range_km=added_range_km
        )

    def process_checkout_simulation(self, energy_kwh: float, unit: str = "Apto 42B", payment_method: str = "PIX", start_hour: int = None):
        """
        Gera recibo de rateio atrelado à unidade do condômino.
        """
        rate = self.calculate_tarifa_atual(start_hour)
        total = round(energy_kwh * rate, 2)
        import time
        return {
            "status": "approved",
            "transaction_id": f"PAY-{int(time.time())}",
            "unit": unit,
            "energy_kwh": round(energy_kwh, 2),
            "rate_per_kwh": rate,
            "total_amount_brl": total,
            "payment_method": payment_method,
            "receipt_message": f"Pagamento simulado com sucesso para {unit}. Volume de {energy_kwh:.2f} kWh autorizado no GoodWe HCA G2."
        }



billing_service = BillingService()

