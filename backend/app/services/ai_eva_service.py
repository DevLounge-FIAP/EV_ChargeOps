import re
from typing import List, Dict, Any, Optional
from ..config import settings
from ..schemas.models import ChatMessage, ChatResponse
from .data_service import data_service
from .billing_service import billing_service

class AiEvaService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() != "":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception:
                self.client = None

    def _build_system_prompt(self, user_id: str) -> str:
        """Constrói o prompt de sistema com injeção dinâmica dos dados reais de recarga."""
        user_profile = data_service.get_user_profile(user_id)
        sessions = data_service.get_sessions_by_user(user_id) if user_id else []
        metrics = data_service.get_metrics()
        condo = data_service.get_condo_metadata()

        user_name = user_profile.get("name", "Condômino") if user_profile else "Condômino"
        unit = user_profile.get("unit", "Geral") if user_profile else "Geral"
        vehicle = user_profile.get("vehicle", {}) if user_profile else {}
        vehicle_model = vehicle.get("model", "Veículo Elétrico")
        battery_kwh = vehicle.get("battery_capacity_kwh", 40.0)
        est_range = vehicle.get("estimated_range_km", 280)

        # Histórico resumido
        recent_kwh = sum(s.energy_delivered_kwh for s in sessions)
        recent_cost = sum(s.total_cost_brl for s in sessions)

        prompt = f"""Você é a EVA (Energy Virtual Assistant), assistente de inteligência artificial oficial da plataforma EV ChargeOps, desenvolvida em parceria entre GoodWe e FIAP (Energy Innovation Lab).

Sua missão é dar suporte aos condôminos, sanar dúvidas sobre faturas, rateio de energia e status de carregamento, com base estrita nos dados do sistema.

DADOS CONTEXTUAIS DO USUÁRIO ATUAL:
- Nome: {user_name} ({unit})
- Veículo Cadastrado: {vehicle_model}
- Capacidade da Bateria: {battery_kwh} kWh (Autonomia estimada: {est_range} km)
- Consumo Registrado no Mês: {recent_kwh:.2f} kWh (Total Faturado: R$ {recent_cost:.2f})

PARÂMETROS DA INFRAESTRUTURA:
- Carregador: GoodWe HCA G2 (Potência de 7.4 kW / Monofásico 220V 32A, Conector Tipo 2)
- Local: Estacionamento do condomínio (Parceria Energy Innovation Lab - FIAP)
- Tarifa de Rateio Vigente: R$ {metrics.current_rate_per_kwh:.2f} por kWh
- Fórmula Oficial de Rateio: Fatura = Energia Consumida (kWh) × R$ {metrics.current_rate_per_kwh:.2f}

DIRETRIZES DE RESPOSTA:
1. Seja cordial, técnica, objetiva e transparente.
2. Utilize dados técnicos precisos para estimar autonomias e tempos.
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
        rate = settings.DEFAULT_RATE_PER_KWH

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
        reply = self._expert_rule_engine(message, user_profile, battery_kwh, vehicle_model, rate)
        return ChatResponse(
            reply=reply,
            source="eva_expert_engine",
            user_context_applied=bool(user_profile),
            suggested_actions=[
                "Quantos kWh faltam para completar a carga?",
                "Qual será o custo estimado da recarga?",
                "Como funciona o modelo de rateio?"
            ]
        )

    def _expert_rule_engine(self, msg: str, user: Optional[Dict[str, Any]], battery_kwh: float, model: str, rate: float) -> str:
        """Processamento de linguagem natural baseado em regras especialistas e dados reais."""
        m = msg.lower()
        user_name = user.get("name", "Condômino") if user else "Condômino"

        # Intenção 1: Rateio / Como funciona a cobrança
        if any(w in m for w in ["rateio", "regra", "divisão", "como funciona", "fórmula", "fatura"]):
            return (
                f"O rateio do **EV ChargeOps** adota o modelo de **Cobrança individual por kWh consumido**:\n\n"
                f"$$\\text{{Valor da Fatura}} = \\text{{Energia Consumida (kWh)}} \\times \\text{{Valor por kWh (R\\$ {rate:.2f})}}$$\n\n"
                f"**Pilares do modelo:**\n"
                f"1. Faturamento estritamente proporcional à energia consumida (kWh).\n"
                f"2. Ausência de taxas fixas para quem não utiliza o equipamento.\n"
                f"3. Dados extraídos das sessões registradas pelo carregador GoodWe HCA G2."
            )

        # Intenção 2: Sobre o carregador GoodWe HCA G2
        if any(w in m for w in ["goodwe", "carregador", "hca", "potencia", "conector"]):
            return (
                f"O carregador instalado é o **GoodWe HCA G2 Series**:\n\n"
                f"- **Potência nominal:** 7.4 kW (Monofásico 220V / 32A).\n"
                f"- **Conector:** Padrão Tipo 2 (IEC 62196-2).\n"
                f"- **Segurança:** Comunicação via sinal Control Pilot (IEC 61851), com proteção contra sobretensão e fuga de corrente.\n"
                f"- **Operação:** Monitorado em parceria com o **Energy Innovation Lab da FIAP**."
            )

        # Intenção 3: Quantas horas aguenta / autonomia
        if any(w in m for w in ["horas", "aguenta", "autonomia", "bateria atual", "duração"]):
            avg_range = user.get("vehicle", {}).get("estimated_range_km", 280) if user else 280
            return (
                f"Com base na bateria de **{battery_kwh} kWh** ({model}):\n\n"
                f"- **Autonomia total estimada:** cerca de **{avg_range} km** em ciclo misto.\n"
                f"- Se a bateria estiver com **50% de carga**, você dispõe de aproximadamente **{avg_range * 0.5:.0f} km** de alcance.\n"
                f"- Em condições urbanas de tráfego moderado, isso representa cerca de **4 a 6 horas contínuas de uso** antes de necessitar de recarga no GoodWe HCA G2."
            )

        # Intenção 4: Qual custo estimado da recarga
        if any(w in m for w in ["custo", "preço", "valor", "estimado", "quanto vai custar"]):
            full_charge_kwh = battery_kwh * 0.8
            cost = full_charge_kwh * rate
            return (
                f"O custo estimado para recarregar 80% ({full_charge_kwh:.2f} kWh) no {model} é de:\n\n"
                f"$$\\text{{Valor}} = {full_charge_kwh:.2f}\\text{{ kWh}} \\times \\text{{R\\$ }}{rate:.2f} = \\textbf{{R\\$ {cost:.2f}}}$$\n\n"
                f"- **Tarifa de rateio:** R$ {rate:.2f}/kWh (inclui energia efetiva + quota proporcional de manutenção do carregador).\n"
                f"- Cobrança individualizada estritamente pelo volume em kWh consumido."
            )

        # Intenção 5: Quantos kWh faltam para completar a carga
        if any(w in m for w in ["completar", "faltam", "terminar", "quanto falta"]):
            needed = battery_kwh * 0.8
            time_hours = needed / (7.4 * 0.92)
            total_mins = int(time_hours * 60)
            h = total_mins // 60
            mins = total_mins % 60
            return (
                f"Para uma recarga de 20% até 100% em uma bateria de **{battery_kwh} kWh** ({model}):\n\n"
                f"- **Energia necessária:** **{needed:.2f} kWh** (80% da capacidade).\n"
                f"- **Tempo estimado no GoodWe HCA G2 (7.4 kW):** aproximadamente **{h}h {mins:02d}min**.\n"
                f"- Ao atingir 100%, o carregador encerra o fluxo automaticamente via protocolo IEC 61851."
            )

        # Resposta padrão acolhedora sem emojis
        return (
            f"Olá, {user_name}! Sou a **EVA**, assistente virtual do **EV ChargeOps**.\n\n"
            f"Estou conectada ao sistema de recarga e ao carregador **GoodWe HCA G2**. Você pode me perguntar:\n"
            f"- *“Quantas horas o carro aguenta com a bateria atual?”*\n"
            f"- *“Quantos kWh faltam para completar a recarga?”*\n"
            f"- *“Qual será o custo estimado da minha próxima recarga?”*\n"
            f"- *“Como funciona o modelo de rateio por kWh?”*"
        )

ai_eva_service = AiEvaService()
