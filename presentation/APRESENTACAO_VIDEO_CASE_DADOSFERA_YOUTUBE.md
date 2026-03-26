# Apresentação do Video Case Dadosfera

---

## Slide 1 - Do dado bruto ao ativo analítico

**Título na tela:**
Do dado bruto ao ativo analítico

**Texto na tela:**

- case técnico construído sobre o dataset Olist
- foco em analytics engineering, governança e consumo
- entrega pensada como produto analítico

**Imagem:**

![Importação do dataset na Dadosfera](../images/dadosfera/01_importacao_dataset.png)

---

## Slide 2 - Arquitetura com separação clara de camadas

**Título na tela:**
Arquitetura com separação clara de camadas

**Texto na tela:**

- `fact_orders_enriched` como base analítica principal
- `112.650` registros com granularidade defensável
- camada publicada separada da camada interna

**Bloco visual na tela:**

```text
raw -> standardized -> staging -> curated -> published -> dashboard
```

---

## Slide 3 - Publicação organizada na Dadosfera

**Título na tela:**
Publicação organizada na Dadosfera

**Texto na tela:**

- coleção `Samuel Maia - 03_2026`
- ativos organizados para descoberta e leitura
- dashboard final e ativo principal publicados

**Imagem:**

![Coleção publicada com os ativos do case](../images/dadosfera/dadosfera_colecao_ativos_publicados.png)

---

## Slide 4 - Perguntas de negócio respondidas com SQL

**Título na tela:**
Perguntas de negócio respondidas com SQL

**Texto na tela:**

- receita e evolução ao longo do tempo
- status dos pedidos e eficiência operacional
- leitura geográfica e atraso logístico

**Imagem:**

![Visualização de pedidos atrasados no Metabase](../images/dadosfera/dadosfera_query_08_pedidos_atrasados.png)

---

## Slide 5 - Consumo executivo sem perder rigor técnico

**Título na tela:**
Consumo executivo sem perder rigor técnico

**Texto na tela:**

- dashboard Streamlit para leitura executiva
- KPIs, tempo, geografia e operação
- coerência entre dado, narrativa e visualização

**Imagem:**

![Visão geral do dashboard Streamlit](../images/dashboard/01_overview.png)

---

## Slide 6 - Entrega atual e próximos passos

**Título na tela:**
Entrega atual e próximos passos

**Texto na tela:**

- pipeline, publicação e documentação concluídos
- governança mínima aplicada ao ativo publicado
- evolução futura com Dadosfera nativa e GenAI

**Imagem:**

![Evidência do item de GenAI](../images/genai/01_product_text_features_openai.png)

---

## Links finais

- Repositório: `github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard: `samuelmaia-032026.streamlit.app`
- Coleção: `metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Vídeo publicado: `https://youtu.be/SqJ0UF1Em9k`
