# 10 Apresentação Final

## Objetivo

Consolidar a defesa do projeto em uma narrativa curta, executiva e tecnicamente rigorosa. A apresentação deve demonstrar valor de produto analítico, robustez de engenharia, publicação comprovada e clareza sobre o que ainda não foi evidenciado na plataforma.

## Tese de Apresentação

A formulação mais forte para a banca é:

“Este projeto mostra a construção de um produto analítico operacionalizado, não apenas de um dashboard. O ativo foi modelado, governado, publicado, monitorado e consumido com evidência real, mantendo honestidade sobre o que ainda não roda nativamente na plataforma.”

## Estrutura Narrativa Recomendada

Use a sequência abaixo:

1. o problema não era visualização, era transformar dado bruto em ativo utilizável
2. a solução foi organizar o projeto em camadas e preservar granularidade defensável
3. o ativo central é `fact_orders_enriched`
4. o consumo executivo acontece sobre `fact_orders_dashboard`
5. a camada publicada já conta com monitoramento recorrente e recortes semânticos
6. a publicação está comprovada na Dadosfera/Metabase
7. o que permanece fora do escopo comprovado é a execução nativa do pipeline dentro da plataforma

## O Que Precisa Aparecer

- arquitetura em camadas
- racional da modelagem
- separação entre camada interna e camada publicada
- recortes semânticos de logística, seller e cohort
- monitoramento recorrente e jobs operacionais
- robustez técnica com testes, cobertura e gates
- SQL e insights de negócio
- dashboard em operação
- publicação e catálogo na Dadosfera
- extensões em Power BI e GenAI

## O Que Já Está Comprovado

- `fact_orders_enriched` com `112.650` registros
- `fact_orders_dashboard` com `34` colunas publicadas
- `124/124` testes passando
- cobertura total acima de `83%`
- publicação do ativo principal na plataforma
- catálogo e coleção navegáveis na Dadosfera/Metabase
- operação recorrente da camada publicada com artefatos operacionais

## O Que Continua Fora do Escopo Comprovado

- pipeline nativo executando dentro da plataforma com evidência final de run
- output gerado por pipeline nativo real no tenant
- catálogo do pipeline nativo na interface da plataforma

Essa distinção precisa ser dita explicitamente. Ela fortalece a credibilidade da apresentação.

## Tradeoffs e Riscos Que Valem Dizer em Voz Alta

- a transformação principal foi endurecida fora da plataforma para garantir reprodutibilidade e controle técnico
- a Dadosfera já comprova publicação, catálogo e consumo, mas não deve ser vendida como motor nativo já validado de ponta a ponta
- a evolução natural é reduzir esse gap operacional com execução nativa evidenciada e alertas externos, não reabrir a discussão de modelagem

## Pergunta Difícil Esperada

Se perguntarem por que a transformação ainda roda majoritariamente fora da plataforma, a resposta mais forte é:

“Porque o objetivo do projeto foi provar valor analítico com governança e consumo reais sem alegar automação nativa não evidenciada. A plataforma já está integrada ao fluxo publicado, e o próximo ganho natural é operacionalizar a execução nativa com a mesma disciplina de evidência.”

## Artefatos Já Prontos

- resumo executivo: `docs/executive_summary.md`
- deck: `presentation/project_deck.md`
- roteiro: `presentation/talk_track.md`
- vídeo: `https://youtu.be/SqJ0UF1Em9k`
- app: `https://governed-analytics-platform.streamlit.app/`
- coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

## Imagens Prioritárias

- `images/dashboard/01_overview.png`
- `images/dashboard/03_temporal.png`
- `images/dadosfera/01_importacao_dataset.png`
- `images/dadosfera/02_catalogo_metadados.png`
- `images/dadosfera/04_volume_100k.png`
- `images/genai/01_product_text_features_openai.png`

## Frase de Fechamento

“Em termos práticos, o projeto prova capacidade de modelar um ativo analítico confiável, controlar sua exposição, endurecer sua operação e operacionalizar o consumo com evidência suficiente para revisão técnica.”
