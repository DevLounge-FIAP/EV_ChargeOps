# Decisões Técnicas e Arquitetura - Sprint 02
## Projeto EV ChargeOps | GoodWe + FIAP

---

## 1. Justificativa de Desvios e Adaptações de Escopo (Sprint 01 → Sprint 02)

Para viabilizar a entrega de um protótipo funcional no prazo da Sprint 02, foram necessárias adaptações técnicas e operacionais em relação ao planejamento inicial da Sprint 01:

| Decisão / Desvio | Motivação & Limitação Técnica | Solução Adotada no Protótipo |
| :--- | :--- | :--- |
| **Ingestão via CSV em vez da API SEMS+** | A liberação e o acesso direto à API oficial do SEMS+ (GoodWe) não foram disponibilizados em tempo hábil para o ciclo de desenvolvimento. | Exportação periódica de dados reais do carregador GoodWe em formato **CSV**, submetidos a um pipeline de limpeza e validação de dados. |
| **Persistência desacoplada em JSON** | Simplificar a camada de infraestrutura de banco de dados na prototipação rápida, garantindo portabilidade entre os módulos. | Armazenamento de sessões de consumo, tempos de carga, usuários e veículos em estruturas estruturadas de arquivos **JSON**. |
| **Descontinuação da conexão direta aos carregadores** | Restrições logísticas de rede local e segurança no Energy Innovation Lab da FIAP (Estacionamento L1). | O controle e a simulação das sessões de recarga operam sobre o fluxo de dados coletados, desacoplados do acionamento físico imediato. |
| **Substituição de RFID / Bluetooth** | Limitações de disponibilidade de hardware dedicado (leitores e tags) e complexidade de integração embarcada na fase atual. | A identificação do usuário e a autorização de recarga são realizadas diretamente via interface da aplicação e simulação lógica. |

---

## 2. Especificação dos Módulos da Solução

### 2.1. Inteligência Artificial Conversacional - Chatbot
* **Responsável:** Aelton  
* **Tecnologias:** N8N (orquestração de fluxos), OpenAI API (modelos GPT).  
* **Fontes de Dados:** Arquivo CSV tratado da GoodWe e dados das sessões em JSON.  
* **Responsabilidades:**
  - Validação, limpeza e formatação dos dados provenientes da GoodWe.
  - Implementação de agente conversacional inteligente conectado à base da plataforma.
  - Suporte a consultas em linguagem natural pelos usuários/condôminos:
    1. *“Quantas horas o carro aguenta com a bateria atual?”*
    2. *“Quantos kWh faltam para completar a carga?”*
    3. *“Qual será o custo estimado da recarga?”*

---

### 2.2. Machine Learning & Analytics - Predição e Consumo
* **Responsável:** Victor Mantovani  
* **Entregáveis:** Modelos preditivos e rotinas analíticas integradas aos dados JSON.  
* **Responsabilidades:**
  - Análise histórica e temporal do consumo energético.
  - Modelo de predição de uso e demanda para mitigar picos no condomínio.
  - Lógica para precificação dinâmica e inteligente.
  - Conversão automatizada e paramétrica: **Tempo $\leftrightarrow$ kWh $\leftrightarrow$ Custo**.
  - Exportação e integração das saídas preditivas (ML) para consumo do Chatbot e Dashboard.

---

### 2.3. Sistema de Tarifação e Simulação de Pagamentos
* **Responsável:** Michelly  
* **Responsabilidades:**
  - Interface e regras de negócio para parametrização da recarga pelo condômino:
    1. Escolha por tempo de carregamento;
    2. Escolha por volume de energia desejado (kWh);
    3. Exibição automática e transparente do cálculo de custo de rateio;
    4. Simulação de checkout e confirmação de pagamento digital no aplicativo.
  - Formulação de metodologias de custo (energia efetiva vs. durabilidade e proteção da bateria).
  - Integração dos valores simulados com as respostas do Chatbot.

---

### 2.4. Interface do Usuário (Frontend Web)
* **Responsável:** Aelton  
* **Responsabilidades:**
  - Desenvolvimento da aplicação web centralizadora do sistema.
  - Integração dos componentes visuais: chat com IA, simulador de recarga/pagamento e dados do usuário em um painel único e responsivo.

---

### 2.5. Dashboard Administrativo, Gestão e Documentação
* **Responsável:** Bruno  
* **Responsabilidades:**
  - Desenvolvimento de dashboard gerencial alimentado pela base de dados tratada da GoodWe.
  - Painel com métricas operacionais essenciais:
    1. Consumo energético total e por sessão;
    2. Nível e status da bateria;
    3. Tempo médio de permanência e carga;
    4. Faturamento total e taxa de inadimplência/rateio;
    5. Indicadores de eficiência energética do ponto de recarga.
  - Painel administrativo para gestão de usuários, credenciais, veículos e histórico de pagamentos.
  - Consolidação e manutenção do `README.md` e artefatos de entrega da sprint.

---

## 3. Fluxo de Dados e Integração dos Módulos

```mermaid
flowchart TD
    GW[Carregador GoodWe / SEMS+] -->|Exportação Amostral| CSV[Arquivo CSV Histórico]
    CSV --> CLEAN[Pipeline de Limpeza e Validação]
    CLEAN --> JSON[(Base de Dados JSON:\nSessões, Usuários e Veículos)]

    JSON --> ML[Módulo ML & Analytics - Victor\nPredição, Demanda e Métricas]
    JSON --> PAY[Sistema de Tarifação - Michelly\nTempo, kWh e Rateio]

    ML --> N8N[Orquestrador N8N + OpenAI - Aelton\nChatbot com Dados em Tempo Real]
    PAY --> N8N

    JSON --> DASH[Dashboard Gerencial - Bruno\nMétricas, Faturamento e Gestão]
    ML --> DASH

    N8N --> FRONT[Frontend Integrador - Aelton\nInterface Web do Usuário]
    PAY --> FRONT
    DASH --> FRONT
```

---

## 4. Matriz de Responsabilidades e Janelas de Execução

| Módulo / Frente | Responsável | Escopo Principal | Janela Prevista |
| :--- | :--- | :--- | :---: |
| **Chatbot Inteligente** | Aelton | Automação no N8N, integração com API OpenAI e sanitização de dados | 28 – 01 |
| **IA & Analytics** | Victor Mantovani | Modelos de consumo, predição de demanda e conversão energética | 28 – 01 |
| **Sistema de Pagamento** | Michelly | Regras de rateio, simulação de checkout e métodos de cálculo | 28 – 05 |
| **Dashboard e Gestão** | Bruno | Painel de controle em CSV/JSON, gestão operacional e documentação | 05 – 10 |
| **Frontend Web** | Aelton | Interface do usuário integrando chat, simulação e visualização | 28 – 08 |

---

## 5. Diferenciais Competitivos da Solução

- **IA Conversacional Contextualizada:** Assistente virtual diretamente alimentado pelos dados de recarga e veículo, respondendo dúvidas práticas em linguagem natural.
- **Predição Preditiva de Demanda:** Algoritmos para balanceamento e prevenção de sobrecarga na rede elétrica interna do condomínio.
- **Rateio Justo e Transparente:** Faturamento baseado no consumo real medido (kWh), superando a divisão genérica na taxa condominial.
- **Painel Administrativo Unificado:** Visão ponta a ponta para síndicos e administradoras acompanharem métricas energéticas e faturamento.
- **Experiência Digital Fluida:** Jornada do morador comparável aos principais aplicativos modernos de mobilidade e conveniência urbana.
