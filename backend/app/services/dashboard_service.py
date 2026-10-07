# Serviço do Dashboard Administrativo (Bruno Santos)
#
# Junta as sessões de recarga, a série diária da estação solar e o cadastro
# de usuários, e devolve os números que a aba "Dashboard Administrativo" mostra.

import pandas as pd

from ..config import settings
from .data_service import data_service

# Capacidade dos painéis solares da estação (relatório do SEMS+)
CAPACIDADE_PV_KWP = 6.0

COLUNAS_SESSAO = [
    "session_id", "user_id", "user_name", "unit", "vehicle_model", "battery_capacity_kwh",
    "start_time", "end_time", "duration_minutes", "energy_delivered_kwh", "power_peak_kw",
    "voltage_v", "current_a", "cost_rate_per_kwh", "total_cost_brl", "status",
    "inicio", "fim", "mes", "bateria_pct",
]


def arredonda(valor, casas=2):
    # NaN e None viram None, para o JSON sair válido
    if valor is None or pd.isna(valor):
        return None
    return round(float(valor), casas)


def porcentagem(parte, total):
    if total > 0:
        return arredonda(parte / total * 100)
    return None


def formata_duracao(minutos):
    if minutos is None:
        return None
    total = int(round(minutos))
    horas = total // 60
    resto = total % 60
    if horas > 0:
        return f"{horas}h {resto:02d}min"
    return f"{resto}min"


class DashboardService:

    def carregar_sessoes(self):
        sessoes = [s.model_dump() for s in data_service.get_all_sessions()]
        if len(sessoes) == 0:
            return pd.DataFrame(columns=COLUNAS_SESSAO)

        df = pd.DataFrame(sessoes)
        df["inicio"] = pd.to_datetime(df["start_time"], errors="coerce")
        df["fim"] = pd.to_datetime(df["end_time"], errors="coerce")
        # se faltar o horário de fim, calcula pelo início + duração
        df["fim"] = df["fim"].fillna(df["inicio"] + pd.to_timedelta(df["duration_minutes"], unit="m"))
        df["mes"] = df["inicio"].dt.strftime("%Y-%m")

        # O carregador não mede o nível da bateria do carro, então o percentual
        # é uma estimativa: energia entregue dividida pela capacidade da bateria.
        capacidade = df["battery_capacity_kwh"].where(df["battery_capacity_kwh"] > 0)
        df["bateria_pct"] = df["energy_delivered_kwh"] / capacidade * 100
        return df.sort_values("inicio").reset_index(drop=True)

    def carregar_estacao(self):
        caminho = settings.STATION_CSV_PATH
        if not caminho.exists():
            return pd.DataFrame()
        df = pd.read_csv(caminho, parse_dates=["data"])
        df["mes"] = df["data"].dt.strftime("%Y-%m")
        return df

    def filtrar_periodo(self, df, coluna, inicio, fim):
        if df.empty:
            return df
        if inicio:
            df = df[df[coluna] >= pd.Timestamp(inicio)]
        if fim:
            # soma 1 dia para incluir o dia final inteiro
            df = df[df[coluna] < pd.Timestamp(fim) + pd.Timedelta(days=1)]
        return df

    def sessoes_filtradas(self, user_id, inicio, fim, status=None):
        s = self.filtrar_periodo(self.carregar_sessoes(), "inicio", inicio, fim)
        if user_id and not s.empty:
            s = s[s["user_id"].str.lower() == user_id.strip().lower()]
        if status and not s.empty:
            s = s[s["status"].str.lower() == status.strip().lower()]
        return s

    # ---------------------------------------------------------------- dashboard

    def dashboard(self, user_id=None, inicio=None, fim=None):
        todas = self.carregar_sessoes()
        s = self.sessoes_filtradas(user_id, inicio, fim)
        e = self.filtrar_periodo(self.carregar_estacao(), "data", inicio, fim)
        condo = data_service.get_condo_metadata()

        periodo = {"inicio": None, "fim": None}
        if not todas.empty:
            periodo["inicio"] = todas["inicio"].min().strftime("%Y-%m-%d")
            periodo["fim"] = todas["inicio"].max().strftime("%Y-%m-%d")

        return {
            "filtros": {
                "user_id": user_id,
                "inicio": inicio.isoformat() if inicio else None,
                "fim": fim.isoformat() if fim else None,
                "periodo_disponivel": periodo,
            },
            "kpis": self.calcular_kpis(s, e, condo),
            "series_mensais": self.serie_mensal_sessoes(s),
            "estacao_mensal": self.serie_mensal_estacao(e),
            "por_usuario": self.resumo_por_usuario(s, condo, user_id),
            "por_veiculo": self.resumo_por_veiculo(s),
            "avisos": self.montar_avisos(s),
        }

    def calcular_kpis(self, s, e, condo):
        total_sessoes = len(s)

        # métricas das sessões de recarga
        energia = 0.0
        faturamento = 0.0
        tempo_medio = None
        tempo_mediana = None
        tempo_maior = None
        bateria_media = None
        bateria_maxima = None
        capacidade_media = None
        pendentes = s
        if total_sessoes > 0:
            energia = float(s["energy_delivered_kwh"].sum())
            faturamento = float(s["total_cost_brl"].sum())
            tempo_medio = arredonda(s["duration_minutes"].mean(), 1)
            tempo_mediana = arredonda(s["duration_minutes"].median(), 1)
            tempo_maior = int(s["duration_minutes"].max())
            bateria_media = arredonda(s["bateria_pct"].mean(), 1)
            bateria_maxima = arredonda(s["bateria_pct"].max(), 1)
            capacidade_media = arredonda(s["battery_capacity_kwh"].mean(), 1)
            pendentes = s[~s["status"].str.lower().isin(["completed", "paid"])]

        # métricas da estação solar
        geracao = 0.0
        consumo_estacao = 0.0
        autoconsumo = 0.0
        exportacao = 0.0
        if not e.empty:
            geracao = float(e["geracao_kwh"].sum())
            consumo_estacao = float(e["consumo_kwh"].sum())
            autoconsumo = float(e["autoconsumo_kwh"].sum())
            exportacao = float(e["exportacao_rede_kwh"].sum())

        energia_media = None
        ticket_medio = None
        pendente_brl = 0.0
        if total_sessoes > 0:
            energia_media = arredonda(energia / total_sessoes)
            ticket_medio = arredonda(faturamento / total_sessoes)
            pendente_brl = arredonda(float(pendentes["total_cost_brl"].sum()))

        status_carregador = condo.get("condominium", {}).get("charger", {}).get("status", "desconhecido")

        return {
            "consumo": {
                "energia_total_kwh": arredonda(energia),
                "energia_media_sessao_kwh": energia_media,
                "sessoes": total_sessoes,
                "consumo_estacao_kwh": arredonda(consumo_estacao),
            },
            "bateria": {
                "pct_medio_por_sessao": bateria_media,
                "pct_maximo_sessao": bateria_maxima,
                "capacidade_media_kwh": capacidade_media,
                "status_carregador": status_carregador,
                "estimado": True,
            },
            "tempo_carga": {
                "media_min": tempo_medio,
                "media_formatada": formata_duracao(tempo_medio),
                "mediana_min": tempo_mediana,
                "maior_min": tempo_maior,
            },
            "faturamento": {
                "total_brl": arredonda(faturamento),
                "ticket_medio_brl": ticket_medio,
                "tarifa_brl_kwh": settings.DEFAULT_RATE_PER_KWH,
                "pendente_brl": pendente_brl,
                "sessoes_pendentes": len(pendentes),
                # Os dados só têm sessões "completed", então não existe
                # informação real de inadimplência.
                "inadimplencia_medida": total_sessoes > 0 and len(pendentes) > 0,
            },
            "eficiencia": {
                # mesmas fórmulas do relatório da estação, recalculadas sobre a soma do período
                "autoconsumo_pct": porcentagem(autoconsumo, autoconsumo + exportacao),
                "contribuicao_pct": porcentagem(autoconsumo, consumo_estacao),
                "geracao_kwh": arredonda(geracao),
                "produtividade_kwh_kwp": arredonda(geracao / CAPACIDADE_PV_KWP, 1),
                "capacidade_pv_kwp": CAPACIDADE_PV_KWP,
            },
        }

    # ------------------------------------------------------------ séries mensais

    def serie_mensal_sessoes(self, s):
        lista = []
        if s.empty:
            return lista
        for mes, grupo in s.groupby("mes"):
            lista.append({
                "mes": mes,
                "sessoes": len(grupo),
                "energia_kwh": arredonda(grupo["energy_delivered_kwh"].sum()),
                "faturamento_brl": arredonda(grupo["total_cost_brl"].sum()),
                "duracao_media_min": arredonda(grupo["duration_minutes"].mean(), 1),
            })
        return lista

    def serie_mensal_estacao(self, e):
        lista = []
        if e.empty:
            return lista
        for mes, grupo in e.groupby("mes"):
            geracao = grupo["geracao_kwh"].sum()
            consumo = grupo["consumo_kwh"].sum()
            autoconsumo = grupo["autoconsumo_kwh"].sum()
            exportacao = grupo["exportacao_rede_kwh"].sum()
            importacao = grupo["importacao_rede_kwh"].sum()
            lista.append({
                "mes": mes,
                "geracao_kwh": arredonda(geracao),
                "consumo_kwh": arredonda(consumo),
                "autoconsumo_kwh": arredonda(autoconsumo),
                "exportacao_kwh": arredonda(exportacao),
                "importacao_kwh": arredonda(importacao),
                "autoconsumo_pct": porcentagem(autoconsumo, autoconsumo + exportacao),
                "contribuicao_pct": porcentagem(autoconsumo, consumo),
            })
        return lista

    # ------------------------------------------------------ gestão (painel admin)

    def resumo_por_usuario(self, s, condo, user_id):
        # começa pelo cadastro, para listar também quem não teve sessão no período
        cadastro = {}
        for u in condo.get("users", []):
            if u.get("user_id"):
                cadastro[u["user_id"]] = u

        # sessões de usuários que não estão no cadastro
        for _, linha in s.drop_duplicates("user_id").iterrows():
            if linha["user_id"] not in cadastro:
                cadastro[linha["user_id"]] = {
                    "user_id": linha["user_id"],
                    "name": linha["user_name"],
                    "unit": linha["unit"],
                    "vehicle": {
                        "model": linha["vehicle_model"],
                        "battery_capacity_kwh": linha["battery_capacity_kwh"],
                    },
                }

        resumo = []
        for uid, u in cadastro.items():
            if user_id and uid.lower() != user_id.strip().lower():
                continue
            sessoes = s[s["user_id"] == uid] if not s.empty else s
            veiculo = u.get("vehicle", {})
            tem_sessao = len(sessoes) > 0
            resumo.append({
                "user_id": uid,
                "nome": u.get("name"),
                "unidade": u.get("unit"),
                "veiculo": veiculo.get("model"),
                "bateria_kwh": veiculo.get("battery_capacity_kwh"),
                "autonomia_km": veiculo.get("estimated_range_km"),
                "sessoes": len(sessoes),
                "energia_kwh": arredonda(sessoes["energy_delivered_kwh"].sum()) if tem_sessao else 0.0,
                "faturamento_brl": arredonda(sessoes["total_cost_brl"].sum()) if tem_sessao else 0.0,
                "duracao_media_min": arredonda(sessoes["duration_minutes"].mean(), 1) if tem_sessao else None,
                "pct_bateria_medio": arredonda(sessoes["bateria_pct"].mean(), 1) if tem_sessao else None,
                "ultima_sessao": sessoes["inicio"].max().strftime("%Y-%m-%d %H:%M") if tem_sessao else None,
            })

        # quem mais consumiu aparece primeiro
        resumo.sort(key=lambda x: x["energia_kwh"] or 0, reverse=True)
        return resumo

    def resumo_por_veiculo(self, s):
        lista = []
        if s.empty:
            return lista
        for modelo, grupo in s.groupby("vehicle_model"):
            lista.append({
                "modelo": modelo,
                "sessoes": len(grupo),
                "energia_kwh": arredonda(grupo["energy_delivered_kwh"].sum()),
                "pct_bateria_medio": arredonda(grupo["bateria_pct"].mean(), 1),
                "capacidade_kwh": arredonda(grupo["battery_capacity_kwh"].iloc[0], 1),
            })
        lista.sort(key=lambda x: x["energia_kwh"], reverse=True)
        return lista

    def pagamentos(self, user_id=None, status=None, inicio=None, fim=None, limit=20, offset=0):
        s = self.sessoes_filtradas(user_id, inicio, fim, status)
        s = s.sort_values("inicio", ascending=False)
        pagina = s.iloc[offset: offset + limit]

        itens = []
        for _, linha in pagina.iterrows():
            itens.append({
                "session_id": linha["session_id"],
                "user_id": linha["user_id"],
                "usuario": linha["user_name"],
                "unidade": linha["unit"],
                "veiculo": linha["vehicle_model"],
                "data": linha["start_time"],
                "energia_kwh": arredonda(linha["energy_delivered_kwh"]),
                "tarifa_brl_kwh": arredonda(linha["cost_rate_per_kwh"]),
                "valor_brl": arredonda(linha["total_cost_brl"]),
                "status": linha["status"],
            })

        return {
            "total_registros": len(s),
            "total_brl": arredonda(s["total_cost_brl"].sum()) if len(s) > 0 else 0.0,
            "limit": limit,
            "offset": offset,
            "itens": itens,
        }

    def carregadores(self):
        condo = data_service.get_condo_metadata().get("condominium", {})
        carregador = condo.get("charger", {})
        s = self.carregar_sessoes()
        tem_sessao = len(s) > 0

        item = {
            "modelo": carregador.get("model", "GoodWe HCA G2"),
            "potencia_nominal_kw": carregador.get("power_rating_kw"),
            "conector": carregador.get("connector_type"),
            "protocolo": carregador.get("protocol"),
            "status": carregador.get("status", "desconhecido"),
            "local": condo.get("partner_lab"),
            "sessoes": len(s),
            "energia_kwh": arredonda(s["energy_delivered_kwh"].sum()) if tem_sessao else 0.0,
            "horas_em_uso": arredonda(s["duration_minutes"].sum() / 60, 1) if tem_sessao else 0.0,
            "pico_potencia_kw": arredonda(s["power_peak_kw"].max(), 1) if tem_sessao else None,
            "taxa_ocupacao_pct": None,
            "ultima_sessao": s["inicio"].max().strftime("%Y-%m-%d %H:%M") if tem_sessao else None,
        }

        if tem_sessao:
            # ocupação = minutos carregando / minutos entre a primeira e a última sessão
            janela_min = (s["fim"].max() - s["inicio"].min()).total_seconds() / 60
            minutos_em_uso = float(s["duration_minutes"].sum())
            item["taxa_ocupacao_pct"] = min(porcentagem(minutos_em_uso, janela_min) or 0.0, 100.0)

        return {"total": 1, "carregadores": [item]}

    def montar_avisos(self, s):
        tarifa = f"{settings.DEFAULT_RATE_PER_KWH:.2f}".replace(".", ",")
        avisos = [
            "O carregador não mede o nível de carga (SoC) do veículo: o percentual de bateria exibido é "
            "uma estimativa (energia entregue ÷ capacidade nominal da bateria).",
            "Usuários e veículos são simulados; horários, energia (kWh) e durações vêm do registro real do SEMS+.",
            f"A tarifa de R$ {tarifa}/kWh é provisória, ainda a confirmar com o grupo.",
        ]
        if not s.empty and set(s["status"].str.lower()) <= {"completed", "paid"}:
            avisos.insert(1, "Inadimplência não disponível: a fonte só registra sessões concluídas e não "
                             "traz informação de pagamento.")
        return avisos


dashboard_service = DashboardService()
