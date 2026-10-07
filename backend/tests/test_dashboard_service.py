# Testes do DashboardService (Bruno Santos).
# Para rodar, dentro da pasta backend: python -m pytest tests -v

import pytest

from app.services.dashboard_service import dashboard_service as svc


def test_totais_do_kpi_batem_com_series_e_usuarios():
    d = svc.dashboard()
    total = d["kpis"]["consumo"]["energia_total_kwh"]
    assert total > 0
    assert sum(r["energia_kwh"] for r in d["series_mensais"]) == pytest.approx(total, abs=0.1)
    assert sum(u["energia_kwh"] for u in d["por_usuario"]) == pytest.approx(total, abs=0.1)
    assert sum(v["energia_kwh"] for v in d["por_veiculo"]) == pytest.approx(total, abs=0.1)


def test_faturamento_e_igual_ao_total_de_pagamentos():
    d = svc.dashboard()
    p = svc.pagamentos(limit=1)
    assert d["kpis"]["faturamento"]["total_brl"] == pytest.approx(p["total_brl"], abs=0.01)
    assert d["kpis"]["consumo"]["sessoes"] == p["total_registros"]


def test_filtro_por_usuario_reduz_o_resultado():
    todos = svc.dashboard()["kpis"]["consumo"]["sessoes"]
    um = svc.dashboard(user_id="USR-001")
    assert 0 < um["kpis"]["consumo"]["sessoes"] < todos
    assert [u["user_id"] for u in um["por_usuario"]] == ["USR-001"]


def test_periodo_sem_dados_nao_quebra():
    from datetime import date
    d = svc.dashboard(inicio=date(2030, 1, 1))
    assert d["kpis"]["consumo"]["sessoes"] == 0
    assert d["kpis"]["tempo_carga"]["media_min"] is None
    assert d["series_mensais"] == [] and d["estacao_mensal"] == []


def test_paginacao_de_pagamentos_nao_repete_registros():
    a = svc.pagamentos(limit=10, offset=0)["itens"]
    b = svc.pagamentos(limit=10, offset=10)["itens"]
    assert len(a) == len(b) == 10
    assert not {i["session_id"] for i in a} & {i["session_id"] for i in b}
    assert a[0]["data"] >= a[-1]["data"]  # mais recente primeiro


def test_eficiencia_usa_as_formulas_do_relatorio_da_estacao():
    e = svc.dashboard()["kpis"]["eficiencia"]
    assert 0 <= e["autoconsumo_pct"] <= 100
    assert 0 <= e["contribuicao_pct"] <= 100
    assert e["produtividade_kwh_kwp"] == pytest.approx(e["geracao_kwh"] / e["capacidade_pv_kwp"], abs=0.1)


def test_inadimplencia_nao_e_inventada():
    d = svc.dashboard()
    if not d["kpis"]["faturamento"]["inadimplencia_medida"]:
        assert any("Inadimpl" in a for a in d["avisos"])


def test_carregador_informa_uso():
    c = svc.carregadores()["carregadores"][0]
    assert c["sessoes"] > 0 and 0 <= c["taxa_ocupacao_pct"] <= 100
