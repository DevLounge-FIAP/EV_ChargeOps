# Testes da tarifação dinâmica, do checkout e da integração da EVA com a tarifação.
# Para rodar, dentro da pasta backend: python -m pytest tests -v

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.models import SimulationRequest
from app.services.billing_service import billing_service
from app.services.ml_service import ml_service
from app.services.ai_eva_service import ai_eva_service

client = TestClient(app)


@pytest.fixture
def eva_offline(monkeypatch):
    """Força o motor especialista, sem chamar a OpenAI mesmo que haja chave no .env."""
    monkeypatch.setattr(ai_eva_service, "client", None)


def test_tarifa_do_horario_vem_da_precificacao_dinamica():
    p = ml_service.get_dynamic_pricing()
    hora_pico = p["janela_pico"]["hora_inicio"]
    hora_fora = (p["janela_pico"]["hora_fim"] + 6) % 24
    assert billing_service.calculate_tarifa_atual(hora_pico) == p["tarifa_pico_brl_kwh"]
    assert billing_service.calculate_tarifa_atual(hora_fora) == p["tarifa_fora_pico_brl_kwh"]


def test_checkout_aplica_a_tarifa_da_hora_de_inicio():
    p = ml_service.get_dynamic_pricing()
    r = client.post("/api/billing/checkout", params={"energy_kwh": 10, "start_hour": p["janela_pico"]["hora_inicio"]})
    assert r.status_code == 200
    assert r.json()["total_amount_brl"] == pytest.approx(10 * p["tarifa_pico_brl_kwh"], abs=0.01)


@pytest.mark.parametrize("params", [
    {"energy_kwh": -5},
    {"energy_kwh": 0},
    {"energy_kwh": 10, "start_hour": 24},
    {"energy_kwh": 10, "start_hour": -1},
])
def test_checkout_rejeita_entradas_invalidas(params):
    assert client.post("/api/billing/checkout", params=params).status_code == 422


def test_eva_usa_o_simulador_calibrado(eva_offline):
    sim = billing_service.simulate_charge(SimulationRequest(
        vehicle_battery_kwh=82.5, vehicle_range_km=372,
        current_soc_percent=20, target_soc_percent=100, charger_power_kw=7.0
    ))
    r = ai_eva_service.generate_response("Quantos kWh faltam para completar a carga?", user_id="USR-001")
    assert sim.estimated_time_formatted in r.reply
    assert f"{sim.total_cost_brl:.2f}" in r.reply


def test_eva_responde_melhor_horario_com_tarifas_do_ml(eva_offline):
    p = ml_service.get_dynamic_pricing()
    r = ai_eva_service.generate_response("Qual o melhor horário para carregar?", user_id="USR-001")
    assert f"{p['tarifa_pico_brl_kwh']:.2f}" in r.reply
    assert f"{p['tarifa_fora_pico_brl_kwh']:.2f}" in r.reply
