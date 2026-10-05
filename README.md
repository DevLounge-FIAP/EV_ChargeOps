# EV ChargeOps | GoodWe + FIAP
## Plataforma de Gestão, Rateio Individual e IA Conversacional para Recarga de Veículos Elétricos

> **Enterprise Challenge 2026** — FIAP & GoodWe (Energy Innovation Lab - Estacionamento L1)  
> **Equipe:** `{Dev}Lounge`

### Integrantes da Equipe
- **Aelton Soares de Menezes** (RM: 573694) — *Backend REST API, IA EVA & Frontend Web*
- **Victor Mantovani** (RM: 570608) — *Machine Learning & Analytics*
- **Michelly Lima** (RM: 573625) — *Sistema de Tarifação & Simulação de Pagamentos*
- **Bruno Silva** (RM: 572073) — *Dashboard Administrativo, Gestão & Documentação*

---

## 1. Visão Geral da Solução

O **EV ChargeOps** é uma plataforma de software desenvolvida para solucionar os principais desafios da recarga compartilhada de veículos elétricos em condomínios residenciais e frotas corporativas.

Integrada aos dados do carregador **GoodWe HCA G2** instalado no **Energy Innovation Lab da FIAP**, a solução transforma telemetria bruta em:
1. **Faturamento Justo e Individualizado:** Rateio baseado estritamente na energia consumida em quilowatt-hora ($\text{Fatura} = \text{kWh} \times \text{Tarifa}$), eliminando divisões genéricas na taxa de condomínio;
2. **Inteligência Artificial Conversacional (IA EVA):** Assistente virtual com injeção dinâmica de contexto para tirar dúvidas de autonomia, custos e status da bateria;
3. **Simulador Paramétrico de Recarga:** Ferramenta interativa que correlaciona tempo de conexão, energia necessária e valor financeiro;
4. **Arquitetura Modular em FastAPI:** API REST escalável com documentação OpenAPI (`/docs`), servindo nativamente a interface web.

---

## 2. Decisões Técnicas e Desvios de Escopo (Sprint 01 → Sprint 02)

Para garantir um protótipo com código 100% autoral, robusto e compatível com as rubricas da FIAP, foram adotadas as seguintes decisões (registradas no documento `docs/Decisões Sprint 2.md`):

| Decisão / Desvio | Motivação & Limitação Técnica | Solução Implementada |
| :--- | :--- | :--- |
| **Backend em Python/FastAPI (Substituição do n8n)** | Plataformas low-code ocultam regras de negócio, geram dependência externa e enfraquecem a comprovação de autoria exigida na FIAP. | API autoral em **FastAPI**, com rotas documentadas (`/docs`), validação via Pydantic e execução assíncrona de alta performance. |
| **Ingestão via CSV Tratado da GoodWe** | O acesso à API oficial do SEMS+ não foi disponibilizado em tempo hábil para o ciclo de desenvolvimento. | Exportações periódicas de dados da estação GoodWe consolidadas no pipeline em `backend/data/tratados/estacao_diario.csv`. |
| **IA EVA com RAG em Memória / Context Injection** | Garantir respostas precisas sobre faturas e baterias sem risco de alucinação e com alta velocidade de resposta. | Injeção dinâmica do perfil do morador, veículo cadastrado, tarifa e histórico real do GoodWe diretamente no prompt da IA. |
| **Simulação Lógica de Sessão e Checkout** | Restrições logísticas de rede local e hardware RFID dedicado no estacionamento L1 da FIAP. | Autorização de recarga e checkout simulados via interface web integrada à API. |

---

## 3. Módulo 1: Backend REST API & IA EVA (Aelton Soares)

### 3.1. Arquitetura da API REST (`/backend/app`)
Construída com **Python 3**, **FastAPI** e **Uvicorn**, a API centraliza as regras de negócio e expõe documentação interativa Swagger UI em `/docs`:

- **Modularidade de Rotas:**
  - `/api/chat`: Processamento de linguagem natural com a IA EVA e sugestão de perguntas frequentes;
  - `/api/sessions`: Listagem sanitizada do histórico de recargas e agregações de telemetria (`/metrics`);
  - `/api/billing`: Cálculo oficial de rateio por kWh, decomposição de custos e simulador paramétrico;
  - `/api/analytics`: Ponto de integração para modelos de Machine Learning (Victor);
  - `/api/admin`: Ponto de integração para métricas executivas e gestão de condomínio (Bruno);
  - `/health` e `/api/status`: Verificação de integridade e metadados operacionais.
- **Servidor Web Integrado:** A API monta e serve automaticamente os arquivos estáticos da interface web na raiz (`/`).

### 3.2. Pipeline de Ingestão de Dados (`estacao_diario.csv`)
A fonte oficial de dados da aplicação é o arquivo `backend/data/tratados/estacao_diario.csv`, contendo **395 dias de dados históricos** do carregador GoodWe HCA G2:
- O `DataService` filtra e sanitiza os **285 registros de recarga efetiva** (> 0 kWh);
- Converte os dados diários em sessões individuais de recarga completas com identificador único, data/hora, condômino, veículo elétrico, duração estimada no carregador de 7.4 kW e valor do rateio;
- Alimenta os KPIs em tempo real:
  - **Energia Total Registrada:** `387.20 kWh`
  - **Faturamento Total:** `R$ 367.54`
  - **Total de Sessões:** `285 recargas concluídas`

### 3.3. IA EVA — Assistente Virtual Inteligente
A **EVA** (*Energy Virtual Assistant*) foi desenvolvida com arquitetura de alta resiliência (*Dual Engine*):

1. **Modo Conectado (OpenAI GPT-4o-mini):** Quando uma chave `OPENAI_API_KEY` válida é configurada no arquivo `.env`, as respostas são formuladas dinamicamente via LLM com injeção de contexto em tempo real;
2. **Modo Especialista Autônomo (Offline Engine):** Caso a API externa esteja indisponível ou sem chave configurada, um motor especialista baseado em regras técnicas entra em ação imediatamente, garantindo que o protótipo nunca falhe na avaliação.

**Consultas Obrigatórias Suportadas em Linguagem Natural:**
- *“Quantas horas o carro aguenta com a bateria atual?”* → Calcula a autonomia urbana e mista com base na capacidade da bateria cadastrada (ex: 44.9 kWh do BYD Dolphin);
- *“Quantos kWh faltam para completar a carga?”* → Calcula o volume em kWh até 100% e o tempo estimado de conexão no GoodWe HCA G2 (7.4 kW / eficiência de 92%);
- *“Qual será o custo estimado da recarga?”* → Aplica a fórmula oficial de rateio e decompõe energia efetiva e quota de manutenção;
- *“Como funciona o modelo de rateio por kWh?”* → Explica os pilares da cobrança individualizada.

### 3.4. Frontend Web Centralizador (`/frontend`)
Aplicação Web responsiva desenvolvida em **HTML5**, **CSS3 (Vanilla)** e **JavaScript modular**, sem frameworks externos pesados:
- **Tema Escuro (Dark Mode):** Visual premium com glassmorphism, paleta curada e tipografia moderna (*Outfit* e *Inter*);
- **Header Informativo:** Seletor de unidade/apartamento (ex: `Apto 42B`) e indicador de status de conexão com a API em tempo real;
- **Painel de KPIs:** Exibição dinâmica da energia entregue, faturamento acumulado, especificações do carregador GoodWe e tarifa ativa;
- **Aba IA EVA:** Chat interativo com histórico, botões de perguntas rápidas e indicador de digitação;
- **Aba Simulador de Recarga:** Sliders interativos de SoC inicial e final (%), cálculo instantâneo de kWh necessários, tempo estimado de carga e botão de simulação de autorização/pagamento;
- **Aba Telemetria GoodWe:** Tabela completa com paginação e histórico das 285 sessões sanitizadas.

---

## 4. Instruções de Instalação e Execução

### Pré-requisitos
- **Python 3.10 ou superior** instalado;
- Gerenciador de pacotes **pip** ou **uv**.

### Passo a Passo de Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/DevLounge-FIAP/EV_ChargeOps.git
   cd EV_ChargeOps
   ```

2. **Configure o arquivo de ambiente (Opcional para a IA OpenAI):**
   ```bash
   cp backend/.env.example backend/.env
   ```
   *(Caso deseje usar a OpenAI, insira sua `OPENAI_API_KEY` no arquivo `backend/.env`. Se não configurar, o sistema usará o motor especialista autônomo sem nenhum prejuízo às funcionalidades).*

3. **Instale as dependências:**
   ```bash
   pip install -r backend/requirements.txt
   ```
   *Ou utilizando o uv (rápido e automatizado):*
   ```bash
   uv run --directory backend --with-requirements requirements.txt python run.py
   ```

4. **Inicie o servidor Backend:**
   ```bash
   python backend/run.py
   ```

5. **Acesse a aplicação no navegador:**
   - **Interface Web:** [http://localhost:8000/](http://localhost:8000/)
   - **Documentação Swagger (OpenAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Documentação Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Estrutura de Integração para os Demais Integrantes

O backend foi preparado com pontos de conexão dedicados para que cada integrante conecte sua respectiva parte de forma simples e independente:

```
backend/
├── app/
│   ├── api/
│   │   ├── routes_chat.py       # [Aelton] Rotas da IA EVA
│   │   ├── routes_sessions.py   # [Aelton] Histórico de sessões e telemetria
│   │   ├── routes_billing.py    # [Michelly] Tarifação e simulação de checkout
│   │   ├── routes_analytics.py  # [Victor] Modelos e predições de Machine Learning
│   │   └── routes_admin.py      # [Bruno] Métricas administrativas e gestão
│   ├── services/
│   │   ├── ai_eva_service.py    # [Aelton] Lógica conversacional da EVA
│   │   ├── data_service.py      # [Aelton] Leitura e sanitização de estacao_diario.csv
│   │   ├── billing_service.py   # [Michelly] Motor de rateio e pagamentos
│   │   └── ml_service.py        # [Victor] Modelos preditivos de demanda e ML
│   ├── main.py                  # Ponto central da API e servidor do Frontend
│   └── config.py                # Configurações gerais da aplicação
└── data/
    └── tratados/
        └── estacao_diario.csv   # Fonte de verdade oficial da GoodWe
```

---

## 6. Módulo 2: Machine Learning & Analytics (Victor Mantovani)

> *Espaço reservado para documentação dos modelos preditivos e análises de Victor Mantovani.*

### Onde conectar seu código:
- **Lógica dos Modelos:** `backend/app/services/ml_service.py`
  - Métodos já preparados: `get_station_summary()` e `predict_demand()`.
- **Rotas da API:** `backend/app/api/routes_analytics.py`
  - Endpoints já disponíveis: `GET /api/analytics/summary` e `GET /api/analytics/demand-prediction`.
- **Base de Dados:** Os dados tratados para treinamento e análise temporal estão disponíveis em `backend/data/tratados/estacao_diario.csv`.

*(Victor: adicione aqui os detalhes dos modelos desenvolvidos, algoritmos utilizados, gráficos de previsão e insights de demanda).*

---

## 7. Módulo 3: Sistema de Tarifação e Simulação de Pagamentos (Michelly Lima)

> *Espaço reservado para documentação das regras de rateio e fluxo de pagamento de Michelly Lima.*

### Onde conectar seu código:
- **Regras de Negócio & Pagamentos:** `backend/app/services/billing_service.py`
  - Métodos já preparados: `calculate_rateio()`, `simulate_charge()` e `process_checkout_simulation()`.
- **Rotas da API:** `backend/app/api/routes_billing.py`
  - Endpoints já disponíveis: `POST /api/billing/calculate`, `POST /api/billing/simulate`, `POST /api/billing/checkout` e `GET /api/billing/config`.

*(Michelly: adicione aqui a formulação matemática de tarifação, divisão de custos fixos vs energia e a documentação da simulação do checkout digital).*

---

## 8. Módulo 4: Dashboard Administrativo & Gestão (Bruno Santos)

> *Espaço reservado para documentação do dashboard gerencial e painel de controle de Bruno Santos.*

### Onde conectar seu código:
- **Rotas de Gestão:** `backend/app/api/routes_admin.py`
  - Endpoints já disponíveis: `GET /api/admin/overview`, `GET /api/admin/users` e `GET /api/admin/efficiency-indicators`.
- **Consumo de Dados:** O painel administrativo pode consumir diretamente os endpoints REST acima ou ler o arquivo `backend/data/tratados/estacao_diario.csv`.

*(Bruno: adicione aqui a documentação do dashboard administrativo, métricas para o síndico, gestão de usuários e indicadores de eficiência energética).*

---

## 9. Evidências de Funcionamento (Sprint 02)

> *Seção reservada para a inclusão das capturas de tela e demonstração técnica da solução integrada antes da entrega final.*

- [ ] Captura de tela da documentação interativa Swagger (`/docs`);
- [ ] Captura de tela do chat interativo com a IA EVA respondendo em linguagem natural;
- [ ] Captura de tela da simulação paramétrica de recarga e cálculo de rateio;
- [ ] Captura de tela da tabela de histórico com as 285 sessões do GoodWe HCA G2;
- [ ] Link do vídeo pitch de 3 minutos para validação presencial da FIAP.
