# Uso de Inteligência Artificial no Desenvolvimento
## Projeto EV ChargeOps | GoodWe + FIAP

> Equipe {Dev}Lounge. Última atualização: 09/10/2026.

O guia da Sprint 02 permite o uso de ferramentas de IA no desenvolvimento, desde que o código entregue seja compreendido e autoral. Este documento registra, de forma transparente, onde e como a equipe usou IA.

---

## 1. Ferramenta, período e escopo

| Item | Descrição |
| :--- | :--- |
| **Ferramenta** | Claude Code (assistente de programação da Anthropic), no VS Code |
| **Período** | Uma única sessão em 09/10/2026, na fase final da Sprint 02 |
| **Escopo** | Revisão do projeto contra a rubrica e o plano da Sprint 01, diagnóstico de defeitos, ajustes de integração entre os módulos, testes e atualização da documentação |
| **Outros usos** | A equipe declara que **não houve uso de ferramentas de IA além dessa sessão** |

**Desenvolvido pela equipe, sem IA:** arquitetura da solução, modelo de rateio, escolha das tecnologias, tratamento dos dados do SEMS+, análise temporal e modelo de demanda, precificação dinâmica, API em FastAPI, IA EVA (versão inicial), simulador, dashboard administrativo, frontend e testes do dashboard. Corresponde ao histórico de commits até `41e614b`.

**Commits da sessão com apoio de IA:** `4924c19` (correção aplicada pela equipe a partir do diagnóstico), `b1b91c9` e `8fa85f6`.

---

## 2. O que a IA fez

### 2.1. Revisão do projeto

A IA comparou o repositório com o guia da Sprint 02 (`exigencias_sprint2.md`), a definição do trabalho e as entregas da Sprint 01. Depois instalou o projeto em um ambiente limpo, rodou os testes, chamou todas as rotas da API e testou a EVA. O resultado foi um checklist dos itens exigidos, com os pontos a corrigir.

### 2.2. Diagnóstico de dois defeitos na tarifação

A IA apontou a causa de cada defeito. A correção foi aplicada pela equipe (commit `4924c19`).

| Defeito | Causa | Correção |
| :--- | :--- | :--- |
| A tarifa dinâmica nunca era aplicada (sempre R$ 0,95) | O `billing_service` lia uma chave com nome diferente da devolvida pelo `ml_service`, e o erro era capturado por um `except` genérico | Nome da chave unificado (`tabela_hora_inicio`) |
| `POST /api/billing/checkout` retornava erro 500 | O método `calculate_tarifa_atual` foi declarado sem o parâmetro `self` | `self` adicionado |

### 2.3. Ajustes de integração (commits `b1b91c9` e `8fa85f6`)

- **Frontend do simulador** (`frontend/js/app.js` e `frontend/index.html`):
  - deixou de enviar tarifa e potência fixas;
  - mostra a tarifa do horário e a decomposição proporcional;
  - o botão de autorização chama `/api/billing/checkout`;
  - o modo offline usa a mesma relação calibrada do backend.
- **IA EVA** (`backend/app/services/ai_eva_service.py`):
  - as estimativas de tempo e custo usam o simulador do `billing_service`;
  - a tarifa vem da precificação dinâmica do `ml_service`;
  - novas consultas: "Qual o melhor horário para carregar?" e "Por que minha fatura subiu?";
  - o prompt do Modo Conectado recebe o consumo mensal do morador e a previsão de demanda.
- **Validação**: o checkout rejeita energia menor ou igual a zero e hora fora de 0 a 23.
- **Testes**: novo arquivo `backend/tests/test_billing_eva.py`, que levou o total de 8 para 16 testes.
- **Documentação**:
  - atualização do `README.md` e do `docs/Decisões Sprint 2.md`, com status corrigidos, desvios do módulo de IA justificados e referências restauradas;
  - novas capturas de tela da EVA e do simulador.

---

## 3. Como a equipe usou as sugestões

- Toda alteração foi revisada pela equipe antes do commit.
- As decisões de arquitetura, rateio e modelos continuaram sendo da equipe. A IA apontou inconsistências entre o código, a documentação e o plano da Sprint 01, e propôs correções.
- As justificativas dos desvios se baseiam em fatos do próprio projeto:
  - os dados vêm de um único cartão RFID;
  - a exportação do SEMS+ não traz eventos de falha;
  - o condomínio é simulado.
- Cada integrante revisou os trechos que afetam o seu módulo e é capaz de explicá-los.
