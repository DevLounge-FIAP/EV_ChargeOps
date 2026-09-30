import csv
import json
from typing import List, Dict, Any, Optional
from ..config import settings
from ..schemas.models import SessionItem, MetricsResponse

class DataService:
    def __init__(self):
        self.csv_path = settings.CSV_FILE_PATH
        self.json_path = settings.JSON_FILE_PATH

    def get_all_sessions(self) -> List[SessionItem]:
        """Lê e sanitiza as sessões do arquivo CSV do GoodWe HCA G2."""
        sessions = []
        if not self.csv_path.exists():
            return sessions

        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    item = SessionItem(
                        session_id=row["session_id"].strip(),
                        user_id=row["user_id"].strip(),
                        user_name=row["user_name"].strip(),
                        unit=row["unit"].strip(),
                        vehicle_model=row["vehicle_model"].strip(),
                        battery_capacity_kwh=float(row.get("battery_capacity_kwh") or 0.0),
                        start_time=row["start_time"].strip(),
                        end_time=row["end_time"].strip() if row.get("end_time") else None,
                        duration_minutes=int(row.get("duration_minutes") or 0),
                        energy_delivered_kwh=round(float(row.get("energy_delivered_kwh") or 0.0), 2),
                        power_peak_kw=float(row.get("power_peak_kw") or 0.0),
                        voltage_v=float(row.get("voltage_v") or 0.0),
                        current_a=float(row.get("current_a") or 0.0),
                        cost_rate_per_kwh=float(row.get("cost_rate_per_kwh") or settings.DEFAULT_RATE_PER_KWH),
                        total_cost_brl=round(float(row.get("total_cost_brl") or 0.0), 2),
                        status=row["status"].strip()
                    )
                    sessions.append(item)
                except Exception as e:
                    # Registra e ignora linha com formato inválido para resiliência
                    continue
        return sessions

    def get_sessions_by_user(self, user_id: str) -> List[SessionItem]:
        """Filtra histórico de sessões por ID de usuário."""
        all_sessions = self.get_all_sessions()
        return [s for s in all_sessions if s.user_id == user_id]

    def get_metrics(self) -> MetricsResponse:
        """Calcula métricas analíticas operacionais a partir das sessões."""
        sessions = self.get_all_sessions()
        if not sessions:
            return MetricsResponse(
                total_energy_kwh=0.0,
                total_revenue_brl=0.0,
                total_sessions_count=0,
                average_session_duration_minutes=0.0,
                average_energy_per_session_kwh=0.0,
                active_chargers_count=1,
                current_rate_per_kwh=settings.DEFAULT_RATE_PER_KWH
            )

        total_kwh = sum(s.energy_delivered_kwh for s in sessions)
        total_rev = sum(s.total_cost_brl for s in sessions)
        total_duration = sum(s.duration_minutes for s in sessions)
        count = len(sessions)

        return MetricsResponse(
            total_energy_kwh=round(total_kwh, 2),
            total_revenue_brl=round(total_rev, 2),
            total_sessions_count=count,
            average_session_duration_minutes=round(total_duration / count, 1) if count > 0 else 0.0,
            average_energy_per_session_kwh=round(total_kwh / count, 2) if count > 0 else 0.0,
            active_chargers_count=1,
            current_rate_per_kwh=settings.DEFAULT_RATE_PER_KWH
        )

    def get_condo_metadata(self) -> Dict[str, Any]:
        """Retorna configurações mestres do condomínio e tarifas."""
        if not self.json_path.exists():
            return {
                "condominium": {"name": "Residencial EcoPark Aclimação"},
                "tariff": {"rate_per_kwh_brl": settings.DEFAULT_RATE_PER_KWH}
            }
        with open(self.json_path, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca perfil de usuário e veículo no JSON."""
        data = self.get_condo_metadata()
        users = data.get("users", [])
        for u in users:
            if u.get("user_id") == user_id:
                return u
        return None

data_service = DataService()
