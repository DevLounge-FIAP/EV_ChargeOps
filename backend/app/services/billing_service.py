from ..config import settings
from ..schemas.models import (
    RateioCalculateRequest,
    RateioCalculateResponse,
    SimulationRequest,
    SimulationResponse
)
from .data_service import data_service

class BillingService:
    def calculate_rateio(self, req: RateioCalculateRequest) -> RateioCalculateResponse:
        """
        Aplica a fórmula oficial do rateio EV ChargeOps:
        Valor da Fatura = Energia Consumida (kWh) × Valor Cobrado por kWh
        """
        rate = req.rate_per_kwh if req.rate_per_kwh is not None else settings.DEFAULT_RATE_PER_KWH
        total_amount = round(req.energy_kwh * rate, 2)

        # Decomposição conceitual (energia base + cota de manutenção compartilhada)
        metadata = data_service.get_condo_metadata()
        tariff_info = metadata.get("condominium", {}).get("tariff", {})
        base_rate = tariff_info.get("base_energy_cost_brl", 0.82)
        maint_rate = tariff_info.get("maintenance_share_brl", 0.13)

        return RateioCalculateResponse(
            energy_kwh=round(req.energy_kwh, 2),
            rate_per_kwh=rate,
            formula_applied="Valor = Energia (kWh) × R$ Rateio/kWh",
            total_amount_brl=total_amount,
            breakdown={
                "base_energy_cost": round(req.energy_kwh * base_rate, 2),
                "charger_maintenance_share": round(req.energy_kwh * maint_rate, 2)
            }
        )

    def simulate_charge(self, sim: SimulationRequest) -> SimulationResponse:
        """
        Simula o carregamento relacionando:
        Tempo (horas) <-> Energia Entregue (kWh) <-> Custo Final (R$)
        """
        battery = sim.vehicle_battery_kwh or 44.9
        cur_soc = max(0.0, min(sim.current_soc_percent or 20.0, 100.0))
        target_soc = max(cur_soc, min(sim.target_soc_percent or 80.0, 100.0))
        power = sim.charger_power_kw or 7.4
        rate = sim.rate_per_kwh or settings.DEFAULT_RATE_PER_KWH

        # Volume necessário em kWh
        delta_percent = (target_soc - cur_soc) / 100.0
        energy_needed = round(battery * delta_percent, 2)

        # Tempo em horas considerando eficiência de 92% do carregador GoodWe
        effective_power = power * 0.92
        time_hours = round(energy_needed / effective_power, 2) if effective_power > 0 else 0.0

        # Formatação horas e minutos
        total_mins = int(time_hours * 60)
        hours = total_mins // 60
        mins = total_mins % 60
        formatted_time = f"{hours}h {mins:02d}min"

        # Custo financeiro
        total_cost = round(energy_needed * rate, 2)

        # Autonomia estimada adicionada (média de 6.8 km por kWh)
        added_range_km = round(energy_needed * 6.8, 1)

        return SimulationResponse(
            energy_needed_kwh=energy_needed,
            estimated_time_hours=time_hours,
            estimated_time_formatted=formatted_time,
            total_cost_brl=total_cost,
            estimated_added_range_km=added_range_km
        )

billing_service = BillingService()
