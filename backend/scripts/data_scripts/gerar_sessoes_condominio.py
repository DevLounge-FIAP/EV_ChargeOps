import random
import sys
from pathlib import Path

import pandas as pd

PASTA_BACKEND = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PASTA_BACKEND))

from app.config import settings
from app.services.data_service import DataService

SEMENTE = 42
INCLUIR_SEM_CARTAO = False
POTENCIA_PICO_KW = 3.5
TENSAO_V = 220.0
CORRENTE_A = 16.0

COLUNAS = [
    "session_id", "user_id", "user_name", "unit", "vehicle_model",\
    "battery_capacity_kwh", "start_time", "end_time", "duration_minutes",
    "energy_delivered_kwh", "power_peak_kw", "voltage_v", "current_a",
    "cost_rate_per_kwh", "total_cost_brl", "status",
]


def gerar_sessoes():
    reais = pd.read_csv(
        PASTA_BACKEND / "data" / "tratados" / "sessoes_reais.csv",
        parse_dates=["inicio", "fim"],
    )
    reais["cartao_id"] = reais["cartao_id"].fillna("")

    filtro = reais["valida"]
    if not INCLUIR_SEM_CARTAO:
        filtro = filtro & (reais["cartao_id"] != "")
    reais = reais[filtro].sort_values("inicio").reset_index(drop=True)

    usuarios = DataService.DEFAULT_USERS
    sorteio = random.Random(SEMENTE)
    tarifa = settings.DEFAULT_RATE_PER_KWH

    linhas = []
    for sessao in reais.itertuples():
        usuario = usuarios[int(sorteio.random() * len(usuarios))]
        energia = round(float(sessao.energia_kwh), 2)
        linhas.append({
            "session_id": f"GW-{sessao.inicio:%Y%m%d%H%M}",
            "user_id": usuario["user_id"],
            "user_name": usuario["name"],
            "unit": usuario["unit"],
            "vehicle_model": usuario["vehicle"]["model"],
            "battery_capacity_kwh": usuario["vehicle"]["battery_capacity_kwh"],
            "start_time": f"{sessao.inicio:%Y-%m-%d %H:%M}",
            "end_time": f"{sessao.fim:%Y-%m-%d %H:%M}",
            "duration_minutes": int(round(sessao.duracao_h * 60)),
            "energy_delivered_kwh": energia,
            "power_peak_kw": POTENCIA_PICO_KW,
            "voltage_v": TENSAO_V,
            "current_a": CORRENTE_A,
            "cost_rate_per_kwh": tarifa,
            "total_cost_brl": round(energia * tarifa, 2),
            "status": "completed",
        })
    return pd.DataFrame(linhas, columns=COLUNAS)


if __name__ == "__main__":
    sessoes = gerar_sessoes()
    destino = settings.SESSIONS_CSV_PATH
    sessoes.to_csv(destino, index=False)

    print("Sessões geradas:", len(sessoes))
    print("IDs únicos:", sessoes["session_id"].is_unique)
    print("Energia total (kWh):", round(sessoes["energy_delivered_kwh"].sum(), 2))
    resumo = sessoes.groupby(["user_id", "vehicle_model"]).agg(
        sessoes=("session_id", "size"),
        kwh=("energy_delivered_kwh", "sum"),
    ).round(1)
    print(resumo)
    print("Salvo em:", destino)