
# [EV ChargeOps]
**Equipe:** {Dev}Lounge

**Integrantes:**
- Aelton Soares de Menezes (RM:573694)
- Maria (RM: 572267)
- Michelly (RM: 573625)
- Victor (RM: 570608)
- Bruno (RM: 572073)

**Objetivo:** Plataforma de software agnóstica para gestão e rateio de recargas de veículos elétricos em infraestruturas compartilhadas, integrada ao carregador GoodWe HCA G2. A solução aplica um modelo de faturamento baseado no consumo efetivo em kWh e utiliza Inteligência Artificial tanto para garantir a integridade dos dados que alimentam o rateio quanto para oferecer suporte conversacional automatizado ao usuário final.

---

## 1. Contexto e Definição do Problema

### Infraestruturas de recarga compartilhada

Infraestrutura de recarga compartilhada é o conjunto de pontos de carregamento instalados em garagens de condomínios residenciais, estacionamentos corporativos e campus universitários,espaços acessíveis por múltiplos usuários. Ao contrário da recarga doméstica individual, esse ambiente exige gestão ativa: controle de acesso, medição de consumo por usuário e critérios definidos para a divisão justa dos custos entre quem utiliza o equipamento.

O crescimento acelerado da frota elétrica torna esse problema urgente no Brasil. O país superou a marca de 250 mil veículos elétricos em 2024; no primeiro semestre desse mesmo ano, as vendas cresceram 146% em relação ao período anterior, totalizando 79,3 mil emplacamentos. Esse volume pressiona condomínios e gestores de espaços compartilhados que, em sua maioria, não dispõem de infraestrutura nem de ferramentas digitais preparadas para essa demanda.

Os principais gargalos operacionais identificados são:

- **Aprovação e burocracia interna:** a decisão de instalar carregadores em condomínio está sujeita à aprovação em assembleia, processo que pode ser longo e conflituoso, especialmente quando nem todos os moradores possuem veículo elétrico.
- **Capacidade elétrica insuficiente:** muitos prédios mais antigos não foram projetados para suportar o aumento na demanda que múltiplos carregadores simultâneos impõem à rede interna.
- **Ausência de rateio individualizado:** sem plataformas que monitorem o consumo de cada unidade, o custo da energia consumida no carregador é diluído na conta coletiva, gerando injustiça entre quem usa e quem não usa o equipamento.
- **Evolução regulatória constante:** a Lei 18.403/26, em vigor no Estado de São Paulo desde fevereiro de 2026, disciplina o direito de condôminos instalarem infraestrutura de recarga em vagas de uso privativo. O avanço é relevante, mas introduz novos desafios jurídicos, técnicos e operacionais para síndicos e gestores.
- **Responsabilidade técnica:** a recarga veicular envolve gestão de carga, conformidade técnica e responsabilidade ao longo de todo o ciclo,da instalação à operação,e não pode ser tratada de forma improvisada.

### Funcionamento técnico de uma sessão de recarga

Uma sessão começa no momento em que o cabo é conectado ao veículo. O carregador identifica o veículo via sinal de piloto (Control Pilot, conforme a norma IEC 61851), negocia a corrente máxima disponível e inicia o fluxo de energia. Durante toda a sessão, o equipamento registra continuamente: potência ativa (kW), energia acumulada entregue (kWh), tensão, corrente, horário de início e fim, e eventos como interrupções ou erros de comunicação.

Em carregadores conectados à rede, como o GoodWe HCA G2 instalado no campus da FIAP, esses dados são transmitidos em tempo real para a nuvem via Wi-Fi ou LAN, ficando disponíveis por APIs. A sessão é encerrada quando o usuário desconecta o cabo ou quando o limite configurado, por tempo, por kWh ou por nível de bateria, é atingido. O conjunto de dados de cada sessão é o insumo bruto que a plataforma EV ChargeOps transforma em fatura individual e inteligência operacional.

### Modelos de negócio para recarga compartilhada

Há cinco modelos em uso no Brasil e no mundo:

- **Recarga gratuita:** o custo da energia é absorvido pelo operador como benefício ou atração. Insustentável à medida que a frota cresce, pois o custo escala sem controle e sem retorno direto.
- **Cobrança por kWh:** o usuário paga exatamente pelo que consumiu. É o modelo mais transparente e justo, mas exige medição individual confiável por sessão.
- **Cobrança por tempo:** o usuário paga pelo tempo de conexão, independentemente da energia consumida. Simples de implementar, mas estruturalmente injusto.
- **Assinatura mensal:** o usuário paga um valor fixo para acesso ao carregador. Previsível, mas gera subsídio cruzado entre quem usa muito e quem usa pouco.
- **Rateio condominial:** o custo total de energia do período é dividido entre os usuários proporcionalmente ao consumo medido de cada um. É o modelo mais adequado para condomínios, pois combina medição individual com a lógica de cobrança mensal já familiar ao condômino. É o modelo adotado pelo EV ChargeOps.

### Análise de mercado e posicionamento

Foram mapeadas quatro soluções que atuam em segmentos próximos ao do EV ChargeOps.

**Zaptec Pro** é voltada para gestão de carregamento compartilhado em edifícios com múltiplos pontos em um mesmo circuito, com balanceamento dinâmico de carga como diferencial técnico. O modelo de negócio é venda de hardware (cerca de US$ 1.950 por unidade), com portal incluso. O problema central para o nosso contexto: a solução só funciona com hardware próprio, tornando-a incompatível com qualquer instalação onde o carregador já esteja definido, como é o caso do GoodWe HCA G2 da FIAP.

**Wallbox Pulsar Plus** utiliza conectividade dupla (Wi-Fi e Bluetooth) para contornar o problema de sinal fraco em subsolos, permitindo que dados de sessão saiam do carregador via Bluetooth pelo celular do usuário. A plataforma foi desenvolvida para um único operador gerenciando um único espaço, sem suporte a múltiplos operadores ou integração com sistemas condominiais. Assim como a Zaptec, exige hardware próprio.

**ChargePoint** opera em escala global, mais de 352 mil pontos sob gestão, com foco em empresas, frotas e estacionamentos. O modelo CPaaS (ChargePoint as a Service) evita o investimento inicial em hardware por meio de contratos de 3 a 5 anos. Para o nosso cenário, a solução é superdimensionada e cara, sem presença relevante no Brasil e sem adaptação ao contexto regulatório da ANEEL.

**Copel Telecom EV** é a referência nacional de operação de eletropostos por uma distribuidora de energia, com foco exclusivo em eletropostos públicos em rodovias e espaços corporativos. A cobrança por minuto é estruturalmente inadequada para uso residencial, e a solução não está disponível como plataforma para terceiros.

O padrão das quatro soluções é claro: as plataformas internacionais resolvem bem o problema físico de conectividade e balanceamento, mas estão presas ao próprio hardware e não se adaptam à realidade condominial brasileira. A Copel tem o mérito de operar em escala nacional, mas com escopo exclusivamente público. Nenhuma das quatro explora os dados de sessão além do básico.

O EV ChargeOps entra nessa lacuna como uma camada de software agnóstica ao hardware, opera sobre o GoodWe HCA G2 já instalado, sem exigir troca de equipamento. O modelo de rateio condominial é adaptado à lógica de cobrança mensal que os moradores já conhecem. E o uso de IA não é cosmético: a proposta é usar os dados das sessões para otimizar a operação e gerar previsões, não apenas exibir números no aplicativo.

---

## 2. Base Regulatória e Técnica

### Regulação, RN ANEEL nº 1.000/2021

A Resolução Normativa ANEEL nº 1.000, de 7 de dezembro de 2021, consolida as Regras de Prestação do Serviço Público de Distribuição de Energia Elétrica. Ela rege a relação entre distribuidoras de energia elétrica e consumidores, incluindo condomínios e prestadores de serviço de recarga, e foi a primeira resolução a tratar a recarga de veículos elétricos dentro das regras gerais de distribuição.

**Comunicação à distribuidora (Art. 550):** toda instalação de estação de recarga deve ser comunicada previamente à distribuidora sempre que gerar necessidade de conexão nova, aumento ou redução de carga, ou alteração do nível de tensão. Ou seja: se o condomínio instalar ou expandir uma estação e isso impactar a carga contratada, existe obrigação formal de avisar a distribuidora.

**Rateio condominial como contrato privado:** a RN ANEEL não regula a relação interna entre condomínio e morador no que diz respeito ao uso do carregador compartilhado. O custo da energia consumida é tratado como contrato privado, regido por convenção de condomínio, regulamento interno ou contrato de prestação de serviço. A única obrigação que decorre da norma é que o consumo e os valores sejam transmitidos de forma clara e auditável.

**Geração distribuída e impacto no custo do kWh:** com a Lei nº 14.300/2022 (novo marco legal da geração distribuída) e a REN ANEEL nº 1.059/2023, surgiu o conceito de energia compensada, créditos de energia gerada (ex.: painéis solares) que podem ser abatidos do consumo da rede. No contexto do EV ChargeOps, isso significa que o custo real do kWh entregue ao veículo pode variar dependendo da origem da energia utilizada na sessão, o que o motor de rateio precisa considerar.

**Conformidade da solução:** o EV ChargeOps opera na camada de software, sobre um carregador já instalado e comunicado à distribuidora. O modelo de rateio é contratual e privado, compatível com a RN 1.000/2021. A plataforma garante rastreabilidade e auditabilidade completas dos dados de consumo, atendendo à exigência de transparência imposta pela norma.

### Hardware, GoodWe HCA G2

O HCA G2 é um carregador residencial CA projetado para veículos elétricos. Ele se comunica com inversores para aproveitar energia fotovoltaica no carregamento e pode se conectar a um medidor MID para geração de faturas reembolsáveis. Está disponível em três versões de potência: 7 kW, 11 kW e 22 kW.

**Interfaces e conectividade:**
- **RS-485:** comunicação com inversores fotovoltaicos ou medidores MID.
- **LAN:** comunicação com roteador local.
- **Wi-Fi e Bluetooth:** conectividade sem fio para integração com aplicativos e nuvem.
- **RFID:** autenticação do usuário por cartão; cada carregador suporta até 10 cartões vinculados.

**Protocolo de comunicação:** Modbus TCP, com integração ao SEMS Portal e às APIs disponibilizadas pela GoodWe.

**Modos de início de sessão:** via cartão RFID, pelo aplicativo ou em modo de início automático ao conectar o plugue.

**Modos de carregamento:** Rápido (Fast), com qualquer tipo de eletricidade; Prioridade Solar (PV Priority), usando apenas excedente fotovoltaico; e Solar + Bateria (PV+BAT), combinando geração própria e armazenamento.

**Funcionalidades relevantes para o projeto:** controle dinâmico de carga (ajusta a potência com base nos dados do medidor para evitar o disparo do fusível principal), registro contínuo de energia entregue por sessão, e status operacional acessível via SEMS Portal.

### APIs, GoodWe e Complementares

**APIs oficiais GoodWe:** a empresa disponibiliza três APIs distintas para acesso a dados e controle remoto.

- **Open API:** disponível para usuários com conta corporativa no portal SEMS. Permite acesso a dados e controle remoto de inversores. Usa protocolo HTTPS ponto a ponto (31 interfaces documentadas).
- **Real-Time Data API:** aberta a fornecedores terceiros, permite leitura de dados em tempo real do inversor e equipamentos conectados, sem suporte a controle remoto (7 interfaces).
- **Batch Remote Control API:** permite controle remoto em lote dos inversores, via plataforma Kafka, para fornecedores autorizados (6 interfaces).

**API SEMS Portal (não oficial):** além das APIs corporativas, existe a API que o próprio SEMS Portal utiliza internamente, mapeada por engenharia reversa pela comunidade de desenvolvedores (ex.: projeto open-source pygoodwe e integrações com Home Assistant). A autenticação é feita via endpoint CrossLogin (e-mail + senha), retornando um token e um uid. Com esses dados e o Station ID da instalação, é possível consultar endpoints como GetMonitorDetailByPowerstationId, que retornam dados de geração, consumo e energia entregue ao veículo por sessão. A limitação é relevante: por não ser oficial, não há SLA, suporte da GoodWe ou garantia de estabilidade, qualquer atualização no app ou portal pode quebrar a integração sem aviso. Essa é a via disponível para obter dados reais do carregador HCA G2 do Lab caso a equipe não obtenha aprovação para a Open API oficial dentro do prazo da Sprint 2.

**API complementar, ANEEL Open Data:** portal de dados abertos da ANEEL, construído sobre CKAN. Consultas via endpoint `datastore_search` com retorno em JSON. O dataset mais relevante para o projeto é a Relação de Empreendimentos de Mini e Micro Geração Distribuída (MMGD), que traz, por unidade consumidora com geração própria: distribuidora, tipo e fonte de geração, potência instalada, município/UF e data de conexão. No EV ChargeOps, essa API funciona como camada de contexto regulatório e cadastral, permite cruzar o município da instalação com dados de geração distribuída registrada, agregando uma camada de conformidade à solução. Acesso público, sem custo e sem autorização prévia para uso básico.

**API complementar, Google Places API:** parte da Places API (New) da Google, retorna dados sobre estações de recarga de VE por meio do campo `evChargeOptions`. Para cada agrupamento de conectores, a API informa quantidade total, disponíveis e fora de serviço, além do tipo de conector (J1772, Tesla, GB/T, entre outros) e horário da última atualização. Suporta busca por taxa mínima de carregamento e tipo de conector. No EV ChargeOps, essa API serve como camada de contexto geográfico externo: dentro da interface do usuário, é possível exibir pontos de recarga alternativos nas proximidades quando o carregador principal estiver ocupado ou em manutenção. A cobrança é baseada nos campos solicitados (field masking), o que permite controlar o custo de uso.

---

## 3. Arquitetura da Solução e Fluxo de Dados

### Camadas da plataforma

A arquitetura do EV ChargeOps é organizada em quatro camadas:

- **Camada física:** carregador GoodWe HCA G2, responsável pela entrega de energia ao veículo e pelo registro dos dados de sessão.
- **Camada de conectividade:** comunicação via Wi-Fi ou LAN com o SEMS Portal; exportação de dados via CSV/Excel (Sprint 1) ou integração via API SEMS (Sprint 2, sujeita à aprovação de acesso).
- **Camada de aplicação:** banco de dados relacional, IA Energética (previsão de consumo e detecção de anomalias) e Motor de Rateio (cálculo das faturas individuais).
- **Camada de apresentação:** interface móvel para o morador e dashboard web para o gestor do condomínio.

### Fluxo operacional, da sessão à fatura

O processo se inicia quando o usuário conecta seu veículo ao carregador GoodWe HCA G2. A partir desse momento, o carregador registra automaticamente os dados da sessão: energia entregue em kWh, duração, horário de início e término, e identificação do usuário via RFID ou autenticação no aplicativo.

O administrador acessa o SEMS Portal e exporta os dados das sessões realizadas. Na Sprint 1, essa exportação ocorre manualmente, via arquivo CSV ou Excel importado diretamente na plataforma. A integração via API do SEMS, prevista como evolução para a Sprint 2, automatizaria esse processo; como o acesso à API não está garantido, o projeto é planejado com a importação manual como operação padrão.

Com os dados armazenados, a IA Energética da plataforma entra em ação com duas funções principais: previsão de consumo, analisando o histórico de sessões para estimar o uso futuro de cada usuário; e detecção de anomalias, identificando sessões fora do padrão, como consumo excessivo ou registros inconsistentes. Os resultados dessa análise alimentam diretamente o Motor de Rateio.

Com base nos dados processados pela IA, o Motor de Rateio calcula a fatura individual de cada usuário utilizando a fórmula de rateio definida (detalhada na seção 4). O morador acessa a plataforma para visualizar o valor a pagar e seu histórico de carregamentos. O gestor do condomínio tem acesso a um dashboard com visão consolidada de todas as sessões, consumo total do período e faturas geradas por unidade.

### Diagrama de arquitetura

![Diagrama de Arquitetura da Solução](https://github.com/DevLounge-FIAP/EV_ChargeOps/blob/main/imagens/diagrama_arquitetura.png?raw=true)

*(O diagrama de arquitetura deve ser adicionado ao repositório com o nome `diagrama_arquitetura.png` e este link atualizado.)*

### Fluxo de UX, primeiro contato do usuário com a plataforma

Após a utilização do carregador e o armazenamento dos dados, o usuário acessa a plataforma EV ChargeOps pelo celular. No primeiro contato, o administrador realiza o cadastro e envia as credenciais de acesso por e-mail. No primeiro login, o usuário cria sua própria senha, mantendo o controle sobre quem utiliza o carregador condominial.

Dentro da plataforma, o usuário tem acesso a seis funcionalidades:

- **Chatbot para dúvidas (IA EVA):** assistente integrado alimentado com informações contextuais sobre o EV ChargeOps, incluindo regras de uso do carregador, funcionamento da plataforma e detalhes sobre a fatura, sem necessidade de contato direto com o administrador.
- **Perfil do veículo:** o usuário cadastra o modelo do veículo elétrico, e a plataforma exibe especificações técnicas, autonomia total e capacidade da bateria em kWh.
- **Pagamento da fatura:** acesso à fatura gerada pelo Motor de Rateio com pagamento via PIX ou boleto bancário, por integração a um gateway de pagamento a ser definido na Sprint 2.
- **Histórico de carregamentos:** registro completo de todas as sessões, com data, horário, duração, energia consumida em kWh e valor cobrado por recarga.
- **Acessibilidade:** filtro para daltonismo, ajuste de tamanho de fonte e transcrição de conteúdo para deficientes visuais.
- **Notificações e alertas:** avisos sobre conclusão de carregamento, geração de fatura mensal e anomalias detectadas pela IA. O administrador também recebe alertas sobre uso fora do padrão ou falha no equipamento.

---

## 4. Modelo de Rateio

### Princípio fundamental

O EV ChargeOps adota um princípio direto: cada usuário paga exatamente pela quantidade de energia que consumiu, medida em quilowatt-hora (kWh), e por nada além disso. O kWh é para energia elétrica o que o litro é para combustível, cobrar diretamente por ele garante que o valor da fatura represente com exatidão o que foi utilizado, sem taxas fixas, sem estimativas de tempo e sem negociações adicionais.

Esse modelo se diferencia das alternativas mais comuns por dois motivos. Cobranças por assinatura mensal distribuem custos de forma uniforme, independentemente do uso real, o que cria subsídio cruzado entre quem carrega frequentemente e quem quase não usa o equipamento. Cobranças por tempo de conexão penalizam usuários cujos veículos já terminaram de carregar mas permaneceram conectados, algo que ocorre com frequência em condomínios residenciais. O rateio por kWh elimina essas distorções.

### Fórmula de cálculo

O valor da fatura de cada usuário é calculado por uma única fórmula:

```
Valor da Fatura = Energia Consumida (kWh) × Valor Cobrado por kWh
```

A **energia consumida** é a quantidade de energia, em kWh, que o carregador efetivamente entregou ao veículo do usuário durante o período de faturamento. O **valor cobrado por kWh** é o preço por unidade de energia, definido para refletir o custo real da eletricidade utilizada, podendo incluir uma parcela proporcional destinada à manutenção do carregador, de modo que esse custo também seja distribuído conforme o uso, e não como uma cobrança fixa sobre todos os condôminos.

A fórmula é aplicável em qualquer ambiente onde o carregador compartilhado esteja instalado, condomínio residencial, empresa ou instituição de ensino. O que varia de um contexto para outro é apenas o valor cobrado por kWh, definido conforme o custo de energia e a política de manutenção local. A forma de calcular a fatura permanece sempre a mesma.

### Tratamento de exceções

Durante o uso do carregador, podem ocorrer situações que exigem regras claras de tratamento:

1. **Sessão interrompida antes do esperado:** o usuário paga apenas pela energia efetivamente entregue até o momento da interrupção. Nenhuma estimativa é feita sobre o que "deveria" ter sido consumido caso a sessão tivesse continuado, evitando contestações sobre o valor cobrado.

2. **Usuário que não utilizou o carregador no mês:** como o modelo não possui cobrança fixa, quem não consumiu energia no período simplesmente não recebe cobrança. O cálculo resulta automaticamente em zero, sem necessidade de regra especial.

3. **Mais de um veículo por unidade:** o sistema soma toda a energia consumida pelos veículos vinculados à mesma pessoa ou unidade e aplica a fórmula sobre o total. Não é necessário gerar faturas separadas por veículo, o que importa é o consumo total de quem está sendo cobrado.

### Benchmarking de modelos de rateio

A definição acima foi construída a partir da análise de duas abordagens distintas utilizadas em condomínios que já implantaram carregadores compartilhados.

O primeiro modelo, comum em instalações que não dispõem de medição individual por sessão, consiste em dividir o custo total de energia do mês igualmente entre todos os moradores que têm acesso ao carregador, independentemente do quanto cada um utilizou. A vantagem é a simplicidade operacional. A limitação é estrutural: moradores que não possuem veículo elétrico ou que carregaram pouco subsidiam os que carregaram muito, gerando percepção de injustiça e potencial conflito em assembleias.

O segundo modelo, adotado por plataformas que já dispõem de medição por sessão, é exatamente o rateio proporcional ao consumo medido em kWh. Cada usuário paga pelo que consumiu, com o valor por kWh fixado antecipadamente pelo administrador. Esse modelo é mais complexo operacionalmente, exige registro confiável de cada sessão e uma plataforma que processe e distribua as faturas —, mas é o único que garante justiça real entre os usuários.

O EV ChargeOps adota o segundo modelo porque ele é o único compatível com os dados que o GoodWe HCA G2 já produz por sessão e com a proposta de transparência e auditabilidade da plataforma. O primeiro modelo só faz sentido na ausência de medição individual, exatamente o problema que a plataforma resolve.

---

## 5. O Papel da IA no EV ChargeOps

A Inteligência Artificial no EV ChargeOps não é um elemento decorativo. Ela cumpre duas funções estruturais complementares: garantir a confiabilidade dos dados que alimentam o Motor de Rateio e oferecer suporte conversacional ao usuário final, reduzindo a carga operacional do administrador.

### IA de Controle Operacional

Essa camada funciona como um módulo de monitoramento e previsão, atuando sobre os dados armazenados de cada sessão de recarga. Cumpre três funções principais:

1. **Previsão de consumo mensal:** com base no histórico de uso de cada usuário, a IA estima, antes mesmo do fim do mês, qual será aproximadamente o valor da fatura. Isso permite que o usuário se planeje financeiramente. Tecnicamente, essa função é implementada por um modelo de regressão, técnica que aprende, a partir de dados históricos, a estimar valores futuros.

2. **Estimativa do tempo restante de carga:** durante uma sessão em andamento, a IA calcula quanto tempo falta até o veículo terminar de carregar, com base na taxa com que a energia está sendo entregue.

3. **Detecção de anomalias:** a IA observa o comportamento padrão de cada sessão e identifica desvios, uma sessão que não encerra corretamente, consumo muito acima ou abaixo do habitual, ou indícios de problema no equipamento. A identificação precoce permite que o problema seja corrigido antes que o usuário perceba e antes que os dados inconsistentes contaminem o cálculo da fatura.

Essa camada é o que garante que os dados usados na fórmula de rateio sejam confiáveis. Sem ela, um registro de sessão corrompido ou um consumo atípico não detectado poderia gerar uma fatura incorreta.

### IA EVA, Energy Virtual Assistant

A segunda abordagem é uma camada de suporte conversacional construída com arquitetura RAG (Retrieval-Augmented Generation). Um modelo de linguagem responde com base em uma base de conhecimento fechada e controlada, composta por três fontes: o manual técnico do carregador HCA G2, o regulamento interno de uso do carregador compartilhado e a documentação da fórmula de rateio.

O objetivo é reduzir o volume de dúvidas encaminhadas ao gestor ou síndico para perguntas que se repetem com frequência: "Como o valor da minha fatura foi calculado?", "Por que minha cobrança subiu este mês?" ou "Como conectar o veículo ao carregador?". Além disso, a EVA permite que o próprio usuário audite o rateio sem precisar consultar planilhas ou acionar suporte manual.

A escolha da arquitetura RAG, em vez de um modelo de linguagem genérico, é deliberada: ela restringe as respostas ao escopo da plataforma, evita alucinações sobre regras e valores e permite que a base de conhecimento seja atualizada quando o regulamento interno ou as condições de faturamento mudarem.

Como evolução futura, a integração da EVA com as saídas da IA de Controle Operacional permitiria respostas personalizadas com base nos dados reais de consumo de cada usuário, por exemplo, explicar por que a fatura de um mês específico ficou acima da média com base no histórico de sessões daquele usuário.

---

## 6. Plano de Ação, Sprint 02

### Stack tecnológica

- **Banco de dados:** PostgreSQL, escolhido pela integridade transacional necessária para registros financeiros de rateio e pelo suporte robusto a consultas relacionais entre sessões, usuários e faturas.
- **Back-end e IA:** Python com FastAPI para construção da API; Scikit-Learn para os modelos de regressão e detecção de anomalias; LangChain para a implementação da EVA com arquitetura RAG.
- **Front-end:** React para o dashboard do gestor (web) e React Native para o aplicativo do morador.
- **Integração de pagamentos:** API do Stripe ou simulação de fluxo PIX para liquidação das faturas mensais.
- **Integração de dados:** importação de arquivos CSV/Excel exportados do SEMS Portal como operação padrão; integração via API SEMS como evolução, sujeita à aprovação de acesso durante a sprint.

### Cronograma faseado

**Julho, Fundação (semanas 1 a 4)**

Configuração do ambiente de desenvolvimento, criação da estrutura do banco de dados (PostgreSQL) com as entidades Usuário, Unidade, Sessão e Fatura, desenvolvimento das rotas da API em Python (FastAPI) e implementação da rotina de importação de arquivos CSV originados do SEMS Portal.

**Agosto, Inteligência e Motor de Rateio (semanas 5 a 8)**

Treinamento e integração da IA de Controle Operacional (modelos de regressão e detecção de anomalias), implementação do Motor de Rateio com a fórmula definida e desenvolvimento do modelo base da IA EVA com arquitetura RAG. Início da construção da interface web do dashboard do gestor.

**Setembro, Interfaces e validação (semanas 9 a 12)**

Conclusão das interfaces web e mobile, testes de usabilidade, simulação de ciclo completo de rateio com dados reais ou simulados. Gravação do vídeo pitch de 3 minutos para validação técnica do projeto.

---

## 7. Referências Bibliográficas

ANEEL, Agência Nacional de Energia Elétrica. **Resolução Normativa nº 1.000, de 7 de dezembro de 2021.** Estabelece as Regras de Prestação do Serviço Público de Distribuição de Energia Elétrica. Disponível em: https://www.aneel.gov.br

BRASIL. **Lei nº 14.300, de 6 de janeiro de 2022.** Institui o marco legal da microgeração e minigeração distribuída, o Sistema de Compensação de Energia Elétrica (SCEE) e o Programa de Energia Renovável Social (PERS). Disponível em: https://www.planalto.gov.br

BRASIL. **Lei Estadual nº 18.403, de 2026 (São Paulo).** Disciplina o direito de condôminos à instalação de infraestrutura de recarga de veículos elétricos em vagas de uso privativo.

ABVE, Associação Brasileira do Veículo Elétrico. **Estatísticas de emplacamentos de veículos elétricos, 2024.** Disponível em: https://www.abve.org.br

ANEEL. **Portal de Dados Abertos, Relação de Empreendimentos de Mini e Micro Geração Distribuída (MMGD).** Disponível em: https://dadosabertos.aneel.gov.br

GOODWE. **Manual Técnico do Carregador Residencial CA, Série HCA G2.** Especificações técnicas, interfaces de hardware e parâmetros de operação.

GOODWE. **SEMS Portal, Documentação de APIs.** Disponível em: https://semsplus.goodwe.com/

GOOGLE. **Places API (New), Documentação do campo evChargeOptions.** Disponível em: https://developers.google.com/maps/documentation/places

OPEN CHARGE MAP. **API REST, Documentação de endpoints.** Disponível em: https://openchargemap.org/site/develop

FIAP; GOODWE. **Edital Enterprise Challenge 2026, GOODWE + FIAP.** Documento orientador, rubrica de avaliação e requisitos de entrega. São Paulo, 2026.

ZAPTEC. **Documentação técnica do Zaptec Pro.** Disponível em: https://www.zaptec.com

WALLBOX. **Documentação técnica do Pulsar Plus e Pulsar Pro.** Disponível em: https://wallbox.com

CHARGEPOINT. **Relatório financeiro e documentação do modelo CPaaS, 3º trimestre fiscal 2025.** Disponível em: https://www.chargepoint.com

COPEL TELECOM. **Rede de eletropostos, Documentação operacional e Lex Mobility.** Disponível em: https://www.copel.com
