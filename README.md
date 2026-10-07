# EV ChargeOps | GoodWe + FIAP
## Plataforma de Gestão, Rateio Individual e IA Conversacional para Recarga de Veículos Elétricos

> **Enterprise Challenge 2026** — FIAP & GoodWe (Energy Innovation Lab - Estacionamento L1)  
> **Equipe:** `{Dev}Lounge`

### Integrantes da Equipe
- **Aelton Soares de Menezes** (RM: 573694) — *Backend REST API, IA EVA & Frontend Web*
- **Victor Mantovani** (RM: 570608) — *Machine Learning & Analytics*
- **Michelly Lima** (RM: 573625) — *Sistema de Tarifação & Simulação de Pagamentos*
- **Bruno Santos** (RM: 572073) — *Dashboard Administrativo, Gestão & Documentação*

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

Esta é a aba **Dashboard Administrativo** do site. Ela mostra as métricas gerais da recarga e da estação solar e tem um painel de consulta com usuários, carregadores e pagamentos. Os cálculos são feitos em Python (pandas), dentro da API. O navegador só desenha o resultado.

### 8.1 Como funciona

```
sessoes_condominio.csv --+
estacao_diario.csv ------+--> DataService e DashboardService (pandas) --> /api/admin --> aba do site
cadastro de usuarios ----+
```

| Arquivo | O que faz |
|---|---|
| `backend/app/services/dashboard_service.py` | Calcula as métricas, as séries mensais, o resumo por usuário e veículo, os pagamentos e os dados do carregador |
| `backend/app/api/routes_admin.py` | Rotas `/api/admin/*`. As três rotas que já existiam foram mantidas |
| `frontend/js/dashboard.js` e `frontend/css/dashboard.css` | Aba do dashboard: busca os dados na API e desenha cartões, gráficos e tabelas |
| `frontend/js/vendor/chart.umd.js` | Biblioteca Chart.js 4.4.1 (licença MIT), guardada no projeto para funcionar sem internet |
| `backend/tests/test_dashboard_service.py` | Testes automáticos do serviço |

### 8.2 Rotas

| Rota | O que devolve |
|---|---|
| `GET /api/admin/dashboard` | Métricas, séries mensais, resumo por usuário e veículo e avisos. Aceita os filtros `user_id`, `inicio` e `fim` (AAAA-MM-DD) |
| `GET /api/admin/payments` | Histórico de pagamentos por sessão, com paginação (`limit` e `offset`) |
| `GET /api/admin/chargers` | Dados do carregador e indicadores de uso |
| `GET /api/admin/overview`, `/users`, `/efficiency-indicators` | Rotas anteriores, mantidas |

### 8.3 Métricas e como são calculadas

| Métrica | Fonte | Cálculo |
|---|---|---|
| Consumo | `sessoes_condominio.csv` | Soma de `energy_delivered_kwh` (total, média por sessão, por mês e por usuário) |
| Bateria | `sessoes_condominio.csv` | Estimativa: energia entregue dividida pela capacidade da bateria do veículo, por sessão |
| Tempo médio de carga | `sessoes_condominio.csv` | Média de `duration_minutes` (também mediana e maior sessão) |
| Faturamento | `sessoes_condominio.csv` | Soma de `total_cost_brl` (kWh x tarifa), por mês e por usuário |
| Eficiência energética | `estacao_diario.csv` | Autoconsumo = autoconsumo / (autoconsumo + exportação). Contribuição = autoconsumo / consumo. Produtividade = geração / 6 kWp. Os percentuais são recalculados sobre a soma do período, e não pela média dos percentuais diários |

### 8.4 Painel administrativo

- **Usuários e veículos:** cadastro com unidade, veículo, sessões, energia, rateio, tempo médio e última sessão.
- **Carregadores:** modelo, potência, conector, status, sessões, energia, horas em uso e taxa de ocupação.
- **Pagamentos:** histórico por sessão (kWh x tarifa), com filtro por usuário e período e botão "Ver mais".

O painel é de consulta. O projeto não tem banco de dados, então não há cadastro, edição nem baixa de pagamentos.

### 8.5 Decisões técnicas e desvios em relação ao plano

- **Dashboard feito em código, e não em ferramenta de BI.** Foi usado FastAPI com Chart.js, pelo mesmo motivo da troca do n8n (seção 2): manter a regra de negócio no código do grupo e não depender de serviço externo na avaliação.
- **Nível da bateria estimado.** O carregador não informa o nível de carga (SoC) do veículo. O percentual mostrado é energia entregue dividida pela capacidade da bateria, e a tela avisa isso.
- **Inadimplência não calculada.** Os dados só têm sessões concluídas e nenhuma informação de pagamento. A tela mostra "sem dados" em vez de um valor inventado.
- **Gestão de credenciais não implementada.** O plano do módulo (`docs/Decisões Sprint 2.md`, seção 2.5) cita credenciais, mas o projeto não tem login nem banco de dados.
- **Painel somente de consulta**, pelo mesmo motivo (sem banco de dados).
- **`energia_carregada_kwh` da estação não é tratada como recarga de veículos** e não entra no consumo das sessões (ver `docs/Decisões Sprint 2.md`).
- **Usuários e veículos são simulados.** Horários, energia (kWh) e durações vêm do registro real do SEMS+.
- **Tarifa de R$ 0,95/kWh provisória**, ainda a confirmar com o grupo.

### 8.6 Como executar e testar

Com um comando só (cria o ambiente virtual, instala as dependências e sobe a API e o site):

- **Windows:** dar dois cliques em `iniciar.bat`, ou rodar `iniciar.bat` no terminal.
- **Git Bash, Linux ou Mac:** `bash iniciar.sh`

Depois, abrir `http://localhost:8000` e clicar na aba "Dashboard Administrativo". O backend FastAPI já entrega o frontend, então existe um único processo e não é preciso subir o site separado.

Execução manual (alternativa):

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash). No Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Testes automáticos (dentro da pasta `backend`, com o ambiente virtual ativo):

```bash
pip install pytest
python -m pytest tests -v
```

A documentação das rotas fica em `http://localhost:8000/docs`.

---

## 9. Evidências de Funcionamento (Sprint 02)

> *Seção reservada para a inclusão das capturas de tela e demonstração técnica da solução integrada antes da entrega final.*

- [ ] Captura de tela da documentação interativa Swagger (`/docs`);
- [ ] Captura de tela do chat interativo com a IA EVA respondendo em linguagem natural;
- [ ] Captura de tela da simulação paramétrica de recarga e cálculo de rateio;
- [ ] Captura de tela da tabela de histórico com as 285 sessões do GoodWe HCA G2;
- [ ] Link do vídeo pitch de 3 minutos para validação presencial da FIAP.

### Dashboard Administrativo (Bruno Santos)

Capturas de tela da aba, com a API rodando em `http://localhost:8000`:

![Cartões de métricas e gráficos](imagens/dashboard_cartoes_graficos.png)

![Limitações dos dados e tabela de usuários e veículos](imagens/dashboard_usuarios_limitacoes.png)

![Tabela de carregadores e histórico de pagamentos](imagens/dashboard_carregadores_pagamentos.png)
