from fastapi import APIRouter, HTTPException
from ..schemas.models import ChatRequest, ChatResponse
from ..services.ai_eva_service import ai_eva_service

router = APIRouter(prefix="/api/chat", tags=["Inteligência Artificial (EVA)"])

@router.post("", response_model=ChatResponse, summary="Envia mensagem para a assistente IA EVA")
def send_chat_message(request: ChatRequest):
    """
    Recebe pergunta em linguagem natural de um condômino e processa via
    **IA EVA** com dados contextuais injetados (veículo, histórico e rateio GoodWe).
    """
    try:
        response = ai_eva_service.generate_response(
            message=request.message,
            user_id=request.user_id or "USR-001",
            history=request.history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem na IA EVA: {str(e)}")

@router.get("/suggested-questions", summary="Retorna lista de perguntas frequentes para a EVA")
def get_suggested_questions():
    """Sugestões rápidas de interação para o condômino."""
    return [
        {"id": "q1", "text": "Quantas horas o carro aguenta com a bateria atual?"},
        {"id": "q2", "text": "Quantos kWh faltam para completar a carga?"},
        {"id": "q3", "text": "Qual será o custo estimado da recarga?"},
        {"id": "q4", "text": "Como funciona o modelo de rateio por kWh?"},
        {"id": "q5", "text": "Quais são as especificações do carregador GoodWe HCA G2?"},
        {"id": "q6", "text": "Qual o melhor horário para carregar?"},
        {"id": "q7", "text": "Por que minha fatura subiu este mês?"}
    ]
