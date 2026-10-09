import re
from collections import defaultdict
from typing import List, Dict, Any, Optional
from ..config import settings
from ..schemas.models import ChatMessage, ChatResponse, SimulationRequest
from .data_service import data_service
from .billing_service import billing_service
from .ml_service import ml_service

# Potência nominal do carregador de referência (GW7K-HCA-20), a mesma usada no simulador
POTENCIA_CARREGADOR_KW = 7.0

class AiEvaService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() != "":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception:
                self.client = None

    # ------------------------------------------------------------------
    # Dados vindos dos outros módulos (tarifação e ML)
    # ------------------------------------------------------------------
    def _precificacao(self) -> Optional[Dict[str, Any]]:
        """Tarifas de pico e fora do pico calculadas pelo ml_service (None se indisponível)."""
        p = ml_service.get_dynamic_pricing()
        return None if "error" in p else p

    def _consumo_mensal(self, sessions) -> Dict[str, Dict[str, float]]:
        """kWh, valor e número de sessões por mês (AAAA-MM), em ordem cronológica."""
        meses = defaultdict(lambda: {"kwh": 0.0, "brl": 0.0, "sessoes": 0})
        for s in sessions:
            m = meses[s.start_time[:7]]
            m["kwh"] += s.energy_delivered_kwh
            m["brl"] += s.total_cost_brl
            m["sessoes"] += 1
        return dict(sorted(meses.items()))

    def _simular(self, battery_kwh: float, range_km: float, soc_atual: float, soc_alvo: float):
        """Usa o simulador calibrado do billing_service (tempo real das sessões e tarifa do horário)."""
        return billing_service.simulate_charge(SimulationRequest(
            vehicle_battery_kwh=battery_kwh,
            vehicle_range_km=range_km,
            current_soc_percent=soc_atual,
            target_soc_percent=soc_alvo,
            charger_power_kw=POTENCIA_CARREGADOR_KW
        ))

    def _build_system_prompt(self, user_id: str) -> str:
        """Constrói o prompt de sistema com injeção dinâmica dos dados reais de recarga."""
        user_profile = data_service.get_user_profile(user_id)
        sessions = data_service.get_sessions_by_user(user_id) if user_id else []

        user_name = user_profile.get("name", "Condômino") if user_profile else "Condômino"
        unit = user_profile.get("unit", "Geral") if user_profile else "Geral"
        vehicle = user_profile.get("vehicle", {}) if user_profile else {}
        vehicle_model = vehicle.get("model", "Veículo Elétrico")
        battery_kwh = vehicle.get("battery_capacity_kwh", 40.0)
        est_range = vehicle.get("estimated_range_km", 280)

        # Histórico resumido
        total_kwh = sum(s.energy_delivered_kwh for s in sessions)
        total_cost = sum(s.total_cost_brl for s in sessions)
        meses = self._consumo_mensal(sessions)
        ultimos = list(meses.items())[-3:]
        linhas_meses = "\n".join(
            f"  - {mes}: {m['kwh']:.2f} kWh em {m['sessoes']} sessões (R$ {m['brl']:.2f})" for mes, m in ultimos
        ) or "  - Sem sessões registradas"

        tarifa_agora = billing_service.calculate_tarifa_atual()
        p = self._precificacao()
        if p:
            linha_tarifa = (
                f"- Tarifa dinâmica por horário de início: R$ {p['tarifa_pico_brl_kwh']:.2f}/kWh no pico "
                f"({p['janela_pico']['hora_inicio']}:00 às {p['janela_pico']['hora_fim']}:59) e "
                f"R$ {p['tarifa_fora_pico_brl_kwh']:.2f}/kWh fora dele (tarifa base R$ {p['tarifa_base_brl_kwh']:.2f})"
            )
        else:
            linha_tarifa = f"- Tarifa base: R$ {settings.DEFAULT_RATE_PER_KWH:.2f}/kWh"

        demanda = ml_service.predict_demand(7)
        linhas_demanda = "\n".join(
            f"  - {d['data']} ({d['dia_semana']}): {d['demanda_estimada_kwh']:.2f} kWh"
            for d in demanda.get("previsoes", [])
        ) or "  - Indisponível"

        prompt = f"""Você é a EVA (Energy Virtual Assistant), assistente de inteligência artificial oficial da plataforma EV ChargeOps, desenvolvida em parceria entre GoodWe e FIAP (Energy Innovation Lab).

Sua missão é dar suporte aos condôminos, sanar dúvidas sobre faturas, rateio de energia e status de carregamento, com base estrita nos dados do sistema.

DADOS CONTEXTUAIS DO USUÁRIO ATUAL:
- Nome: {user_name} ({unit})
- Veículo Cadastrado: {vehicle_model}
- Capacidade da Bateria: {battery_kwh} kWh (Autonomia Inmetro: {est_range} km)
- Consumo total registrado: {total_kwh:.2f} kWh em {len(sessions)} sessões (Total Faturado: R$ {total_cost:.2f})
- Últimos meses com sessões:
{linhas_meses}

PARÂMETROS DA INFRAESTRUTURA:
- Carregador: GoodWe HCA G2 (GW7K-HCA-20, potência nominal de 7 kW, Conector Tipo 2). Nas sessões reais a potência média foi de cerca de 2,1 kW, então o tempo de recarga segue a relação calibrada: tempo (h) = 0,94 + 0,366 x kWh
- Local: Estacionamento do condomínio (Parceria Energy Innovation Lab - FIAP)
{linha_tarifa}
- Tarifa vigente agora: R$ {tarifa_agora:.2f}/kWh
- Fórmula Oficial de Rateio: Fatura = Energia Consumida (kWh) × Tarifa do horário de início da sessão
- As sessões históricas foram faturadas com a tarifa base de R$ {settings.DEFAULT_RATE_PER_KWH:.2f}/kWh

PREVISÃO DE DEMANDA DA ESTAÇÃO (modelo de ML, próximos 7 dias):
{linhas_demanda}

DIRETRIZES DE RESPOSTA:
1. Seja cordial, técnica, objetiva e transparente.
2. Use apenas os dados acima. Se um dado não estiver disponível (por exemplo, o nível de carga atual do carro, que o carregador não informa), diga isso.
3. Explique cálculos de rateio de forma simples e mostre a fórmula.
4. Se o usuário perguntar algo fora do escopo de carregamento elétrico e condomínio, redirecione educadamente para o tema.
"""
        return prompt

    def generate_response(self, message: str, user_id: str = "", history: Optional[List[ChatMessage]] = None) -> ChatResponse:
        """Gera resposta via OpenAI API ou via motor especialista integrado."""
        user_profile = data_service.get_user_profile(user_id) if user_id else None
        vehicle = user_profile.get("vehicle", {}) if user_profile else {}
        battery_kwh = vehicle.get("battery_capacity_kwh", 40.0)
        vehicle_model = vehicle.get("model", "Veículo Elétrico")
        rate = billing_service.calculate_tarifa_atual()

        # Tentativa via OpenAI se a chave estiver configurada
        if self.client:
            try:
                system_prompt = self._build_system_prompt(user_id)
                messages = [{"role": "system", "content": system_prompt}]

                if history:
                    for h in history[-4:]:
                        messages.append({"role": h.role, "content": h.content})

                messages.append({"role": "user", "content": message})

                completion = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=0.4,
                    max_tokens=400
                )
                reply_text = completion.choices[0].message.content
                return ChatResponse(
                    reply=reply_text,
                    source="openai_gpt",
                    user_context_applied=bool(user_profile),
                    suggested_actions=[
                        "Simular recarga agora",
                        "Ver histórico de faturas",
                        "Como é calculada a tarifa?"
                    ]
                )
            except Exception:
                pass

        # Fallback especialista inteligente integrado
        reply = self._expert_rule_engine(message, user_profile, battery_kwh, vehicle_model, rate, user_id)
        return ChatResponse(
            reply=reply,
            source="eva_expert_engine",
            user_context_applied=bool(user_profile),
            suggested_actions=[
                "Quantos kWh faltam para completar a carga?",
                "Qual o melhor horário para carregar?",
                "Quanto gastei este mês?"
            ]
        )

    def _expert_rule_engine(self, msg: str, user: Optional[Dict[str, Any]], battery_kwh: float, model: str, rate: float, user_id: str = "") -> str:
        """Processamento de linguagem natural baseado em regras especialistas e dados reais."""
        m = msg.lower()
        user_name = user.get("name", "Condômino") if user else "Condômino"
        range_km = user.get("vehicle", {}).get("estimated_range_km", 280) if user else 280
        p = self._precificacao()

        # Intenção 1: Melhor horário / tarifa dinâmica (saída do modelo de ML)
        if any(w in m for w in ["horário", "horario", "pico", "mais barato", "tarifa dinâmica", "tarifa dinamica"]):
            if not p:
                return f"A tarifa dinâmica está indisponível no momento. Vale a tarifa base de R$ {settings.DEFAULT_RATE_PER_KWH:.2f}/kWh."
            h0, h1 = p["janela_pico"]["hora_inicio"], p["janela_pico"]["hora_fim"]
            economia = (1 - p["tarifa_fora_pico_brl_kwh"] / p["tarifa_pico_brl_kwh"]) * 100
            return (
                f"A tarifa depende da hora em que a recarga **começa**:\n\n"
                f"- **Pico ({h0}:00 às {h1}:59):** R$ {p['tarifa_pico_brl_kwh']:.2f}/kWh. É a janela que concentra "
                f"{p['parcela_energia_pico_pct']:.1f}% da energia das recargas do condomínio.\n"
                f"- **Fora do pico (demais horários):** R$ {p['tarifa_fora_pico_brl_kwh']:.2f}/kWh.\n\n"
                f"Iniciar a recarga fora do pico sai cerca de **{economia:.0f}% mais barato** por kWh "
                f"e ajuda a reduzir a carga na rede do condomínio. Tarifa vigente agora: **R$ {rate:.2f}/kWh**."
            )

        # Intenção 2: Gasto do mês / por que a fatura subiu (histórico do usuário)
        if any(w in m for w in ["gastei", "gasto", "subiu", "aumentou", "meu consumo", "este mês", "esse mês"]):
            meses = list(self._consumo_mensal(data_service.get_sessions_by_user(user_id) if user_id else []).items())
            if not meses:
                return f"{user_name}, não encontrei sessões de recarga registradas para a sua unidade."
            mes, atual = meses[-1]
            resposta = (
                f"No último mês com recargas registradas (**{mes}**), você teve **{atual['sessoes']} sessões**, "
                f"com **{atual['kwh']:.2f} kWh** e fatura de **R$ {atual['brl']:.2f}**."
            )
            if len(meses) > 1:
                mes_ant, ant = meses[-2]
                dif = atual["brl"] - ant["brl"]
                sentido = "subiu" if dif > 0 else "caiu" if dif < 0 else "ficou igual"
                resposta += (
                    f"\n\nEm relação a {mes_ant} ({ant['sessoes']} sessões, {ant['kwh']:.2f} kWh, R$ {ant['brl']:.2f}), "
                    f"a fatura **{sentido}** R$ {abs(dif):.2f}. Como a fatura é kWh × tarifa e o histórico usa a tarifa "
                    f"base de R$ {settings.DEFAULT_RATE_PER_KWH:.2f}/kWh, a diferença vem da energia consumida."
                )
            return resposta

        # Intenção 3: Rateio / Como funciona a cobrança
        if any(w in m for w in ["rateio", "regra", "divisão", "como funciona", "fórmula", "fatura", "tarifa", "calculad"]):
            linha_tarifa = (
                f"4. Tarifa por horário de início: R$ {p['tarifa_pico_brl_kwh']:.2f}/kWh no pico e "
                f"R$ {p['tarifa_fora_pico_brl_kwh']:.2f}/kWh fora dele (base de R$ {settings.DEFAULT_RATE_PER_KWH:.2f}/kWh)."
                if p else f"4. Tarifa base de R$ {settings.DEFAULT_RATE_PER_KWH:.2f}/kWh."
            )
            return (
                f"O rateio do **EV ChargeOps** adota o modelo de **Cobrança individual por kWh consumido**:\n\n"
                f"$$\\text{{Valor da Fatura}} = \\text{{Energia Consumida (kWh)}} \\times \\text{{Tarifa do horário (agora R\\$ {rate:.2f})}}$$\n\n"
                f"**Pilares do modelo:**\n"
                f"1. Faturamento estritamente proporcional à energia consumida (kWh).\n"
                f"2. Ausência de taxas fixas para quem não utiliza o equipamento.\n"
                f"3. Dados extraídos das sessões registradas pelo carregador GoodWe HCA G2.\n"
                f"{linha_tarifa}"
            )

        # Intenção 4: Sobre o carregador GoodWe HCA G2
        if any(w in m for w in ["goodwe", "carregador", "hca", "potencia", "potência", "conector"]):
            return (
                f"O carregador instalado é o **GoodWe HCA G2 Series**:\n\n"
                f"- **Modelo de referência:** GW7K-HCA-20, potência nominal de **7 kW**.\n"
                f"- **Potência observada:** nas sessões reais, média de cerca de 2,1 kW e máxima de 3,4 a 3,5 kW (16 A em 220 V).\n"
                f"- **Conector:** Padrão Tipo 2 (IEC 62196-2).\n"
                f"- **Segurança:** Comunicação via sinal Control Pilot (IEC 61851), com proteção contra sobretensão e fuga de corrente.\n"
                f"- **Operação:** Monitorado em parceria com o **Energy Innovation Lab da FIAP**."
            )

        # Intenção 5: Quantas horas aguenta / autonomia
        if any(w in m for w in ["horas", "aguenta", "autonomia", "bateria atual", "duração"]):
            km_por_kwh = range_km / battery_kwh if battery_kwh else 0
            return (
                f"Com base na bateria de **{battery_kwh} kWh** ({model}):\n\n"
                f"- **Autonomia total (Inmetro):** cerca de **{range_km} km**, ou {km_por_kwh:.1f} km por kWh.\n"
                f"- Com **50% de carga**, você dispõe de aproximadamente **{range_km * 0.5:.0f} km** de alcance.\n"
                f"- O carregador não informa o nível de carga atual do carro, por isso a estimativa usa 50% como exemplo. "
                f"O tempo de uso em horas depende da velocidade média e do trajeto."
            )

        # Intenção 6: Qual custo estimado da recarga
        if any(w in m for w in ["custo", "preço", "valor", "estimado", "quanto vai custar"]):
            sim = self._simular(battery_kwh, range_km, 20.0, 100.0)
            resposta = (
                f"O custo estimado para recarregar de 20% a 100% ({sim.energy_needed_kwh:.2f} kWh) no {model}, "
                f"iniciando agora, é de:\n\n"
                f"$$\\text{{Valor}} = {sim.energy_needed_kwh:.2f}\\text{{ kWh}} \\times \\text{{R\\$ }}{rate:.2f} = \\textbf{{R\\$ {sim.total_cost_brl:.2f}}}$$\n\n"
                f"- **Tarifa do horário atual:** R$ {rate:.2f}/kWh (energia efetiva + quota proporcional de manutenção do carregador)."
            )
            if p:
                pico = sim.energy_needed_kwh * p["tarifa_pico_brl_kwh"]
                fora = sim.energy_needed_kwh * p["tarifa_fora_pico_brl_kwh"]
                resposta += f"\n- **Comparação:** R$ {pico:.2f} se iniciar no pico e R$ {fora:.2f} fora dele."
            return resposta

        # Intenção 7: Quantos kWh faltam para completar a carga
        if any(w in m for w in ["completar", "faltam", "terminar", "quanto falta"]):
            sim = self._simular(battery_kwh, range_km, 20.0, 100.0)
            return (
                f"Para uma recarga de 20% até 100% em uma bateria de **{battery_kwh} kWh** ({model}):\n\n"
                f"- **Energia necessária:** **{sim.energy_needed_kwh:.2f} kWh** (80% da capacidade).\n"
                f"- **Tempo estimado no GoodWe HCA G2:** aproximadamente **{sim.estimated_time_formatted}**, "
                f"pela relação calibrada nas sessões reais (o carregador entregou em média cerca de 2,1 kW).\n"
                f"- **Custo estimado iniciando agora:** R$ {sim.total_cost_brl:.2f} (R$ {rate:.2f}/kWh).\n"
                f"- O carregador não informa o nível de carga atual do carro, por isso o cálculo parte de 20% como exemplo."
            )

        # Resposta padrão acolhedora sem emojis
        return (
            f"Olá, {user_name}! Sou a **EVA**, assistente virtual do **EV ChargeOps**.\n\n"
            f"Estou conectada ao sistema de recarga e ao carregador **GoodWe HCA G2**. Você pode me perguntar:\n"
            f"- *“Quantas horas o carro aguenta com a bateria atual?”*\n"
            f"- *“Quantos kWh faltam para completar a recarga?”*\n"
            f"- *“Qual será o custo estimado da minha próxima recarga?”*\n"
            f"- *“Qual o melhor horário para carregar?”*\n"
            f"- *“Quanto gastei este mês?”*\n"
            f"- *“Como funciona o modelo de rateio por kWh?”*"
        )

ai_eva_service = AiEvaService()
