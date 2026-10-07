import csv
import json
from typing import List, Dict, Any, Optional
from ..config import settings
from ..schemas.models import SessionItem, MetricsResponse

class DataService:
        # Perfis simulados do condomínio: usuários e distribuição de veículos criados pelo grupo.
    # Os veículos vêm do catálogo data/referencia/veiculos.csv (bateria total e autonomia Inmetro).
    DEFAULT_USERS = [
        {
            "user_id": "USR-001",
            "name": "Aelton Menezes",
            "unit": "Apto 42B",
            "vehicle": {
                "model": "BYD Seal",
                "battery_capacity_kwh": 82.5,
                "estimated_range_km": 372
            }
        },
        {
            "user_id": "USR-002",
            "name": "Michelly Lima",
            "unit": "Apto 15A",
            "vehicle": {
                "model": "Volvo EX30",
                "battery_capacity_kwh": 69.0,
                "estimated_range_km": 338
            }
        },
        {
            "user_id": "USR-003",
            "name": "Victor Mantovani",
            "unit": "Apto 83C",
            "vehicle": {
                "model": "Volvo EX30",
                "battery_capacity_kwh": 69.0,
                "estimated_range_km": 338
            }
        },
        {
            "user_id": "USR-004",
            "name": "Bruno Santos",
            "unit": "Apto 102",
            "vehicle": {
                "model": "BYD Seal",
                "battery_capacity_kwh": 82.5,
                "estimated_range_km": 372
            }
        },
        {
            "user_id": "USR-005",
            "name": "Lab FIAP",
            "unit": "Estacionamento L1",
            "vehicle": {
                "model": "Mercedes-Benz EQE 350+",
                "battery_capacity_kwh": 96.0,
                "estimated_range_km": 421
            }
        }
    ]

    def __init__(self):
        self.csv_path = settings.SESSIONS_CSV_PATH
        self.json_path = settings.JSON_FILE_PATH
        self._cached_sessions: Optional[List[SessionItem]] = None

    def get_all_sessions(self) -> List[SessionItem]:
        """
        Lê as sessões de recarga do arquivo sessoes_condominio.csv (SESSIONS_CSV_PATH).
        Horários, kWh e durações vêm do registro real do SEMS+. Usuário e veículo são simulados.
        """
        if self._cached_sessions is not None:
            return self._cached_sessions

        sessions = []
        if not self.csv_path.exists():
            return sessions

        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            if "session_id" not in fieldnames:
                raise ValueError(
                    f"{self.csv_path} não está no formato de sessões (coluna 'session_id' ausente)."
                )

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
                        power_peak_kw=float(row.get("power_peak_kw") or 7.4),
                        voltage_v=float(row.get("voltage_v") or 220.0),
                        current_a=float(row.get("current_a") or 32.0),
                        cost_rate_per_kwh=float(row.get("cost_rate_per_kwh") or settings.DEFAULT_RATE_PER_KWH),
                        total_cost_brl=round(float(row.get("total_cost_brl") or 0.0), 2),
                        status=row.get("status", "completed").strip()
                    )
                    sessions.append(item)
                except Exception:
                    continue

        # Ordena do mais recente para o mais antigo
        sessions.reverse()
        self._cached_sessions = sessions
        return sessions

    def get_sessions_by_user(self, user_identifier: str) -> List[SessionItem]:
        """Filtra histórico de sessões por ID de usuário ou Unidade/Apto."""
        all_sessions = self.get_all_sessions()
        ident = user_identifier.strip().lower()
        return [
            s for s in all_sessions 
            if s.user_id.lower() == ident or s.unit.lower() == ident or s.user_name.lower() == ident
        ]

    def get_metrics(self) -> MetricsResponse:
        """Calcula métricas analíticas operacionais a partir das sessões reais."""
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
        """Retorna configurações mestres do condomínio, carregador GoodWe e tarifas."""
        if self.json_path.exists():
            try:
                with open(self.json_path, mode="r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "condominium": {
                "name": "Residencial EcoPark Aclimação",
                "partner_lab": "FIAP Energy Innovation Lab - Estacionamento L1",
                "charger": {
                    "model": "GoodWe HCA G2",
                    "power_rating_kw": 7.4,
                    "connector_type": "Tipo 2 (IEC 62196-2)",
                    "protocol": "IEC 61851 / Control Pilot",
                    "status": "operational"
                },
                "tariff": {
                    "rate_per_kwh_brl": settings.DEFAULT_RATE_PER_KWH,
                    "base_energy_cost_brl": 0.82,
                    "maintenance_share_brl": 0.13,
                    "currency": "BRL",
                    "billing_cycle": "monthly"
                }
            },
            "users": self.DEFAULT_USERS
        }

    def get_user_profile(self, user_identifier: str) -> Optional[Dict[str, Any]]:
        """Busca perfil de usuário por ID, Unidade ou Nome."""
        if not user_identifier:
            return None
        ident = user_identifier.strip().lower()
        data = self.get_condo_metadata()
        users = data.get("users", self.DEFAULT_USERS)
        for u in users:
            if (
                u.get("user_id", "").lower() == ident 
                or u.get("unit", "").lower() == ident 
                or u.get("name", "").lower() == ident
            ):
                return u
        return None

data_service = DataService()
