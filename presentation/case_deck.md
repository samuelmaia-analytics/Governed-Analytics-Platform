# Case Deck

## Estrutura narrativa

A apresentação funciona melhor se seguir a lógica:

1. problema
2. decisão arquitetural
3. ativo central
4. prova de consumo
5. prova de publicação
6. limite real

## Slide 1 | Tese

**Mensagem**

Transformar um dataset relacional bruto em um ativo analítico governado, testado e pronto para consumo executivo.

**Fala**

“O objetivo deste case foi sair de dados transacionais fragmentados e chegar a um produto analítico utilizável. A entrega foi desenhada para mostrar modelagem, governança, publicação e consumo como partes da mesma solução.”

## Slide 2 | Problema

**Mensagem**

Olist é rico em dado, mas pobre em legibilidade executiva na forma original.

**Pontos**

- múltiplas tabelas e dependência de joins
- dificuldade de responder perguntas de negócio diretamente na origem
- necessidade de separar engenharia, exposição e consumo

## Slide 3 | Arquitetura

**Mensagem**

A solução foi organizada em camadas para reduzir ambiguidade de uso e melhorar governança.

**Pontos**

- `raw -> standardized -> staging -> curated -> published`
- `curated` como camada interna de engenharia
- `published` como camada oficial de exposição

**Apoio**

- referenciar `docs/architecture.md`

## Slide 4 | Ativo Central

**Mensagem**

`fact_orders_enriched` é a espinha dorsal da solução.

**Pontos**

- granularidade: `1 linha por item de pedido`
- volume: `112.650` linhas
- uso: SQL, qualidade, documentação, BI e derivação da publicada

**Fala**

“Essa decisão de granularidade foi a mais importante do projeto, porque ela sustenta consumo analítico sem sacrificar rastreabilidade.”

## Slide 5 | Governança

**Mensagem**

O dashboard não consome a camada interna completa.

**Pontos**

- `fact_orders_dashboard` deriva da fato principal
- pseudonimização de `order_id` e `customer_unique_id`
- remoção de identificadores e quase-identificadores desnecessários

**Fala**

“Essa separação mostra maturidade de produto: a base de engenharia continua rica, mas a camada executiva expõe apenas o necessário.”

## Slide 6 | SQL e Evidência Analítica

**Mensagem**

A modelagem foi validada por perguntas reais de negócio.

**Pontos**

- top categorias por receita
- evolução temporal
- receita por estado
- atraso por categoria
- distribuição por meio de pagamento

**Apoio**

- `powerbi/query_principal_resultado.png`
- mosaico com screenshots de `data/screenshots/query_results/`

## Slide 7 | Dashboard

**Mensagem**

O Streamlit é o produto executivo da solução.

**Pontos**

- KPIs, tendência, categorias, geografia e insights
- consumo exclusivo da camada publicada
- coerência entre base, narrativa e visual

**Apoio**

- `images/dashboard/01_overview.png`
- `images/dashboard/03_temporal.png`
- `images/dashboard/04_categories.png`

## Slide 8 | Dadosfera e Catálogo

**Mensagem**

A entrega foi além do ambiente local.

**Pontos**

- ativo principal publicado na plataforma
- evidências de importação, catálogo, coleção e volume
- manifesto local e inventário versionado
- sync complementar de catálogo via API do Maestro

**Fala**

“Eu deixaria explícito que a publicação e a catalogação estão comprovadas. O que não está sendo vendido como concluído é pipeline nativo rodando dentro da plataforma.”

## Slide 9 | Robustez

**Mensagem**

A solução foi pensada para resistir à revisão técnica.

**Pontos**

- testes automatizados
- `114/114` testes passando
- cobertura total acima de `86%`
- gate mínimo de cobertura em `80%`
- contratos simples de schema
- checks de qualidade
- workflows de CI, lint e promoção do branch de deploy

## Slide 10 | Operação e Governança

**Mensagem**

O case não termina no código; ele inclui operação mínima e governança explícita.

**Pontos**

- `CODEOWNERS`, `CONTRIBUTING.md` e `SECURITY.md`
- runbooks de release, rollback e operating model
- recomendação formal de branch protection e environment control
- separação clara entre escopo core e extensões

## Slide 11 | Extensões

**Mensagem**

A solução já se abre para múltiplos canais de consumo.

**Pontos**

- Power BI com modelo auxiliar
- GenAI com extração estruturada de features textuais

## Slide 12 | Escopo Real

**Mensagem**

O case está pronto como produto analítico, mas não infla o que ainda não foi evidenciado.

**Pontos**

- feito: modelagem, governança, publicação, dashboard, catálogo, sync API, automação GitHub
- não feito: pipeline nativo dentro da Dadosfera

## Slide 13 | Fechamento

**Mensagem final**

“Se eu resumir a entrega em uma frase: este projeto demonstra a capacidade de transformar dado bruto em ativo analítico operacionalizado, com critério de modelagem, controle de exposição, robustez de engenharia e prova real de consumo.”

## Materiais de apoio

- repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- app: `https://samuelmaia-032026.streamlit.app/`
- vídeo: `https://youtu.be/SqJ0UF1Em9k`
- coleção publicada: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- dashboard publicado: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- modelo principal: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- tabela pública: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`
