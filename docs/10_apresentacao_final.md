# 10 Apresentação Final

## Objetivo

Consolidar a defesa do case em uma narrativa curta, executiva e tecnicamente rigorosa. A apresentação deve mostrar problema, decisão arquitetural, ativo central, prova de consumo e limite real de escopo.

## Linha narrativa recomendada

Use a sequência abaixo:

1. o problema não era visualização, era transformar dado bruto em ativo utilizável
2. a solução foi organizar o projeto em camadas e preservar granularidade defensável
3. o ativo central é `fact_orders_enriched`
4. o consumo executivo acontece sobre `fact_orders_dashboard`
5. a publicação está comprovada na Dadosfera/Metabase
6. o que permanece fora do escopo é pipeline nativo dentro da plataforma

## Mensagem central

Se a apresentação precisar ser resumida em poucos segundos, a formulação mais forte é:

“Esta entrega mostra a construção de um produto analítico, não apenas de um dashboard. O ativo foi modelado, governado, publicado e consumido com evidência real, mantendo honestidade sobre o que ainda não roda nativamente na plataforma.”

## O que precisa aparecer

- arquitetura em camadas
- racional da modelagem
- governança da camada publicada
- robustez técnica com testes, cobertura e gates
- SQL e insights de negócio
- dashboard em operação
- publicação e catálogo na Dadosfera
- extensões em Power BI e GenAI

## Artefatos já prontos

- deck: `presentation/case_deck.md`
- roteiro: `presentation/talk_track.md`
- vídeo: `https://youtu.be/SqJ0UF1Em9k`
- app: `https://samuelmaia-032026.streamlit.app/`
- ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

## Imagens prioritárias

- `images/dashboard/01_overview.png`
- `images/dashboard/03_temporal.png`
- `images/dadosfera/01_importacao_dataset.png`
- `images/dadosfera/02_catalogo_metadados.png`
- `images/dadosfera/04_volume_100k.png`
- `images/genai/01_product_text_features_openai.png`

## Postura recomendada

Adote uma defesa objetiva. O que fortalece a apresentação não é prometer maturidade total de plataforma, mas mostrar clareza sobre:

- o que foi implementado
- o que foi publicado
- o que foi automatizado
- o que foi testado e endurecido em engenharia
- o que ainda seria uma evolução natural

## Números que valem mencionar

- `fact_orders_enriched` com `112.650` registros
- `fact_orders_dashboard` com `22` colunas publicadas
- `114/114` testes passando
- cobertura total acima de `86%`
- gate mínimo de cobertura em `80%`

## Frase de fechamento

“Em termos práticos, a entrega prova capacidade de modelar um ativo analítico confiável, controlar sua exposição, endurecer sua operação e operacionalizar o consumo com evidência suficiente para revisão técnica.”
