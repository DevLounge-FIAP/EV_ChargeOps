# Enterprise Challenge 2026 - GoodWe + FIAP
## Guia da Sprint 02 - Desenvolvimento e Prototipação

---

## 1. Divisão do Projeto

O **Enterprise Challenge 2026** será desenvolvido em duas sprints:

- **Sprint 01 - Pesquisa e documentação:** A equipe investiga o problema, mapeia o contexto técnico e regulatório, define a arquitetura da solução e documenta as decisões que guiarão o desenvolvimento.  
  *Concluída em:* `21/06/2026`.
- **Sprint 02 - Desenvolvimento e prototipação:** A equipe implementa a solução com base no que foi definido na Sprint 01.  
  *Prazo:* No encerramento da Fase 6.

> [!IMPORTANT]
> **Validação Presencial e Vídeo Pitch:**  
> No 2º semestre de 2026, durante a prova presencial obrigatória que você agendará, cada aluno deverá gravar um **vídeo pitch de 3 minutos** do seu projeto. Esse será o momento de validar o desenvolvimento técnico do desafio e habilitar o lançamento das notas. As notas das sprints só aparecerão no boletim após a validação técnica do vídeo pitch.

---

## 2. Contexto do Desafio

A **GoodWe** é uma das maiores fabricantes globais de inversores e sistemas de armazenamento de energia, com presença em mais de 100 países e capacidade instalada acumulada superior a 100 GW. No Brasil, a empresa mantém parceria com a FIAP por meio do **Energy Innovation Lab** (Unidade 2, Aclimação), onde opera um carregador de veículos elétricos (**GoodWe HCA G2**) instalado no estacionamento L1.

O crescimento acelerado de veículos elétricos impõe um problema operacional concreto: infraestruturas de recarga compartilhadas - em condomínios residenciais, edifícios corporativos e campus universitários - não dispõem de mecanismos integrados para:

- Estruturar sessões por usuário;
- Calcular consumo individual;
- Aplicar regras de rateio justas;
- Oferecer uma experiência digital clara para moradores e gestores.

Cada sessão de recarga produz dados úteis: duração, volume de energia entregue (kWh), horário de uso, frequência, picos e intervalos de ociosidade. Quando organizados, esses dados deixam de ser simples registros e passam a funcionar como base de inteligência operacional. O **EV ChargeOps** propõe exatamente essa transformação, com inteligência artificial como motor lógico da solução.

> ### Pergunta Norteadora
> *Como transformar sessões de recarga de veículos elétricos em uma infraestrutura compartilhada em dados estruturados, rateio justo e inteligência acionável?*

---

## 3. O Que a Equipe Deve Fazer?

Sua missão nessa sprint é **implementar a solução que o grupo desenvolveu na Sprint 01**. A arquitetura, o modelo de rateio, o papel da IA e as tecnologias escolhidas pela equipe na etapa anterior são o ponto de partida dessa implementação. Não há prescrição sobre quais tecnologias usar ou como organizar o código; essas decisões foram tomadas pela equipe na Sprint 01 e devem ser seguidas aqui.

> **Prioridade da Sprint 02:** Desenvolvimento e prototipação.  
> O entregável central é um **protótipo funcional** da solução proposta. Por isso, a equipe deve implementar o que foi planejado, justificar eventuais desvios e registrar as decisões técnicas tomadas ao longo do desenvolvimento.

---

## 4. O Que Entregar?

A equipe deve entregar um **protótipo funcional** da solução EV ChargeOps, implementando ao menos os seguintes aspectos que o grupo desenvolveu na Sprint 01:

1. **A lógica central da solução:** Mecanismo que registra sessões de recarga, calcula o consumo individual e aplica o modelo de rateio definido pela equipe;
2. **O módulo de inteligência artificial:** Implementado conforme o papel definido na Sprint 01, com função estrutural na solução - não como componente decorativo ou desconectado do fluxo principal;
3. **Evidências de funcionamento:** Demonstração de que a solução funciona na prática (capturas de tela, vídeo, notebook executado, dashboard ou qualquer outro formato que o grupo considere adequado).

> [!NOTE]
> A tecnologia utilizada em cada parte é livre, desde que esteja alinhada com o que o grupo definiu anteriormente. Portanto, desvios em relação ao que foi planejado na Sprint 01 devem ser justificados no `README.md`.

---

## 5. Sobre o Uso de Inteligência Artificial

O uso de ferramentas de IA para apoiar o desenvolvimento, depurar código, sugerir estruturas e revisar implementações é permitido e incentivado. Ferramentas como ChatGPT, Claude, Gemini e similares podem ser aliadas na resolução de problemas técnicos e na aceleração do desenvolvimento.

No entanto, o código entregue deve ser **compreendido e autoral**. Isso significa que:

- **Domínio técnico:** A equipe deve ser capaz de explicar qualquer trecho de código entregue, incluindo os gerados com auxílio de IA;
- **Senso crítico e decisão:** Decisões de arquitetura, escolha de tecnologias e lógica de negócio devem refletir o raciocínio da equipe, não sugestões copiadas sem análise crítica;
- **Integridade acadêmica:** Código gerado por IA e incluído sem adaptação ou entendimento será identificado na avaliação.

> *Um código que usa IA com inteligência é diferente de um código que foi copiado sem leitura crítica; a avaliação reconhece essa diferença.*

---

## 6. Entregável

O entregável dessa sprint deve ser um arquivo `.TXT` contendo o link do repositório do grupo. O repositório deve conter o código do protótipo funcional e um `README.md` atualizado.

### Conteúdo obrigatório do repositório:
- **Código-fonte:** Implementação do protótipo, organizado de forma clara e estruturada;
- **`README.md` atualizado:** Descrição da solução implementada, instruções detalhadas de execução/instalação, decisões técnicas tomadas e justificativa de eventuais desvios em relação ao planejado na Sprint 01;
- **Evidências de funcionamento:** Capturas de tela, vídeo de demonstração ou notebook com saídas executadas, conforme o tipo de entrega.

### Orientações para o repositório:
- O `README.md` deve ser escrito em português claro e direto, sem abuso de emojis;
- **Commits frequentes e descritivos:** Mensagens claras demonstram o processo contínuo de desenvolvimento da equipe e fazem parte da avaliação.

---

## 7. Rubrica de Avaliação

| Critério | Descrição | Pontuação |
| :--- | :--- | :---: |
| **Lógica Central** | A lógica central da solução está implementada e funciona conforme a proposta que o grupo entregou na Sprint 01. | 0 – 3,0 |
| **Módulo de IA** | O módulo de IA cumpre papel estrutural e está integrado à solução. | 0 – 3,0 |
| **Evidências de Funcionamento** | Há evidência de que a solução funciona, no formato que o grupo escolheu (prints, vídeo, notebook, dashboard). | 0 – 2,0 |
| **Autoria e Domínio Técnico** | O código reflete autoria e compreensão da equipe. | 0 – 1,0 |
| **Documentação e Organização** | O `README.md` está atualizado e o repositório está bem organizado. | 0 – 1,0 |
| **Total** | **Pontuação máxima da Sprint 02** | **0 – 10,0** |
