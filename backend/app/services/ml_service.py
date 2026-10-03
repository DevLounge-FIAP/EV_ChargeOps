"""
Módulo de Machine Learning & Analytics — EV ChargeOps
Responsável: Victor Mantovani

Modelo de demanda: mediana de kWh por dia da semana, aprendida com as sessões
de recarga (sessoes_condominio.csv, lidas pelo data_service).
A comparação com as outras variantes testadas está em
backend/notebooks/02_modelo_demanda.ipynb.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from ..config import settings
from .data_service import data_service

# Data que separa treino (antes) e teste (a partir dela) na validação por data.
DATA_CORTE_VALIDACAO = "2026-06-01"

# pandas: segunda = 0 ... domingo = 6
NOMES_DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


class MlService:
    def __init__(self):
        # Guarda o modelo depois de treinado, para não recalcular a cada chamada.
        self._modelo = None

    # ------------------------------------------------------------------
    # Dados
    # ------------------------------------------------------------------
    def _serie_diaria(self) -> pd.Series:
        """kWh de recarga de cada dia do calendário (0 nos dias sem recarga)."""
        sessoes = data_service.get_all_sessions()
        inicio = pd.to_datetime([s.start_time for s in sessoes])
        kwh = pd.Series([s.energy_delivered_kwh for s in sessoes], index=inicio)

        por_dia = kwh.groupby(kwh.index.normalize()).sum()
        calendario = pd.date_range(por_dia.index.min(), por_dia.index.max(), freq="D")
        return por_dia.reindex(calendario, fill_value=0.0)

    def _horario_pico(self) -> Tuple[int, float]:
        """Hora de início da janela de 2 horas com mais energia, e a % da energia nela."""
        sessoes = data_service.get_all_sessions()
        hora = pd.Series([pd.Timestamp(s.start_time).hour for s in sessoes])
        kwh = pd.Series([s.energy_delivered_kwh for s in sessoes])

        por_hora = kwh.groupby(hora).sum().reindex(range(24), fill_value=0.0)
        janela = por_hora + por_hora.shift(-1, fill_value=0.0)  # hora h + hora h+1
        hora_inicio = int(janela.idxmax())
        percentual = float(janela.max() / por_hora.sum() * 100)
        return hora_inicio, round(percentual, 1)

    # ------------------------------------------------------------------
    # Modelo
    # ------------------------------------------------------------------
    def _treinar(self) -> Dict[str, Any]:
        """Aprende as 7 medianas (modelo final) e mede o erro com validação por data."""
        diario = self._serie_diaria()

        # Modelo final: mediana de cada dia da semana com TODOS os dias.
        medianas = diario.groupby(diario.index.dayofweek).median()

        # Validação: aprende só com o treino e prevê o teste, que o modelo não viu.
        corte = pd.Timestamp(DATA_CORTE_VALIDACAO)
        treino = diario[diario.index < corte]
        teste = diario[diario.index >= corte]

        medianas_treino = treino.groupby(treino.index.dayofweek).median()
        previsao_teste = pd.Series(teste.index.dayofweek, index=teste.index).map(medianas_treino)
        erro = (teste - previsao_teste).abs()

        mae = float(erro.mean())
        erro_por_dia = erro.groupby(erro.index.dayofweek).mean()
        nivel_por_dia = teste.groupby(teste.index.dayofweek).mean()

        # confiança = 1 - erro médio / nível médio do dia (acurácia = 1 - WAPE)
        confianca_por_dia = (1 - erro_por_dia / nivel_por_dia).clip(lower=0, upper=1).fillna(0.0)

        hora_pico, percentual_pico = self._horario_pico()

        return {
            "medianas": {int(d): float(v) for d, v in medianas.items()},
            "erro_por_dia": {int(d): float(v) for d, v in erro_por_dia.items()},
            "confianca_por_dia": {int(d): float(v) for d, v in confianca_por_dia.items()},
            "mae": mae,
            "dias_treino": len(treino),
            "dias_teste": len(teste),
            "dias_total": len(diario),
            "hora_pico": hora_pico,
            "percentual_pico": percentual_pico,
        }

    def _obter_modelo(self) -> Dict[str, Any]:
        if self._modelo is None:
            self._modelo = self._treinar()
        return self._modelo

    # ------------------------------------------------------------------
    # Rotas
    # ------------------------------------------------------------------
    def get_station_summary(self) -> Dict[str, Any]:
        """
        Resumo das recargas (sessões) e do contexto da planta (estacao_diario.csv).
        A recarga vem das sessões. A coluna energia_carregada_kwh da planta NÃO é
        recarga de carro e não é usada.
        """
        try:
            diario = self._serie_diaria()
        except Exception as e:
            return {"error": f"Falha ao processar as sessões de recarga: {str(e)}"}

        resumo = {
            "periodo_dias_analisados": len(diario),
            "total_energia_carregada_kwh": round(float(diario.sum()), 2),
            "media_diaria_recarga_kwh": round(float(diario.mean()), 2),
        }

        csv_path = settings.STATION_CSV_PATH
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                resumo["dias_planta_analisados"] = len(df)
                resumo["total_energia_gerada_kwh"] = round(float(df["geracao_kwh"].sum()), 2)
                resumo["total_energia_importada_rede_kwh"] = round(float(df["importacao_rede_kwh"].sum()), 2)
                resumo["total_energia_exportada_rede_kwh"] = round(float(df["exportacao_rede_kwh"].sum()), 2)
            except Exception as e:
                resumo["aviso_planta"] = f"Falha ao ler os dados da planta: {str(e)}"
        else:
            resumo["aviso_planta"] = "Arquivo estacao_diario.csv não encontrado"

        resumo["status_modelo"] = "modelo_treinado_mediana_por_dia_da_semana"
        return resumo

    def predict_demand(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Previsão de demanda (kWh) para os próximos dias: a mediana histórica do
        dia da semana de cada data. Não depende do que aconteceu "ontem", então
        vale para qualquer horizonte (1 a 30 dias).
        """
        try:
            modelo = self._obter_modelo()
        except Exception as e:
            return {"error": f"Falha ao treinar o modelo de demanda: {str(e)}"}

        hoje = pd.Timestamp.today().normalize()
        previsoes = []
        for d in range(1, days_ahead + 1):
            data = hoje + pd.Timedelta(days=d)
            dia = data.dayofweek
            previsoes.append({
                "dia_relativo": f"+{d}d",
                "data": data.strftime("%Y-%m-%d"),
                "dia_semana": NOMES_DIAS[dia],
                "demanda_estimada_kwh": round(modelo["medianas"][dia], 2),
                "confianca": round(modelo["confianca_por_dia"][dia], 2),
                "erro_tipico_kwh": round(modelo["erro_por_dia"][dia], 2),
            })

        hora = modelo["hora_pico"]
        return {
            "dias_projetados": days_ahead,
            "metodologia": (
                "Mediana de kWh por dia da semana, aprendida com "
                f"{modelo['dias_total']} dias de sessões. Validação por data "
                f"(treino até {DATA_CORTE_VALIDACAO}, {modelo['dias_teste']} dias de teste): "
                f"erro médio de {modelo['mae']:.2f} kWh por dia. "
                "Confiança = 1 - erro médio / nível médio do dia no teste."
            ),
            "previsoes": previsoes,
            "recomendacao_operacional": (
                f"Cerca de {modelo['percentual_pico']}% da energia das recargas começa entre "
                f"{hora}h e {(hora + 1) % 24}h. Incentivar o uso fora dessa janela "
                "reduz o pico no condomínio."
            ),
            "observacoes": [
                "A previsão é o dia típico (mediana) e não prevê picos isolados.",
                "Os dados vêm de um único cartão RFID; usuários e veículos são simulados.",
            ],
        }


ml_service = MlService()