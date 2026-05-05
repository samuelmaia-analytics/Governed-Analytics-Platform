# 09 GenAI e LLMs - Processar


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/Governed-Analytics-Platform`
- Dashboard Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento organiza o item de GenAI do projeto, separando o que já existe no repositório do que ainda precisa ser implementado para aderir totalmente ao escopo.

## Objetivo do Item

Demonstrar a capacidade de:

- trabalhar com dado desestruturado
- usar IA para gerar features
- transformar texto bruto em estrutura útil para análise

## O que já existe no projeto

Hoje o projeto já possui:

- camada analítica estruturada do Olist
- dashboard com insights executivos
- documentação da extensão de GenAI em:
  - `docs/genai_bonus.md`
- script de extração de features:
  - `src/genai_feature_extraction.py`
- dataset desestruturado de exemplo:
  - `data/external/genai/product_text_samples.csv`
- tabela final de features:
  - `data/curated/genai/product_text_features.csv`

## Status atual

- insights heurísticos no dashboard: feitos
- uso de LLM externa para extração de features: executado e validado localmente via API
- dataset desestruturado dedicado para este item: materializado em amostra versionada
- tabela final de features: materializada com saída real da API

## O que o edital pede

Para fechar este item, ainda falta:

- não encontrei evidência suficiente de print da execução para documentação visual

## Estrutura sugerida para execução

### Entrada recomendada

Uma tabela ou arquivo com colunas como:

- `title`
- `description`

### Processo esperado

1. selecionar amostra ou dataset desestruturado
2. definir schema de saída das features
3. enviar texto ao modelo
4. receber a resposta estruturada
5. consolidar as features em tabela final

### Exemplo de features possíveis

- categoria inferida
- material
- atributos de uso
- compatibilidade
- sinais de qualidade
- palavras-chave
- embeddings ou grupos semanticos

## Sugestão de entregáveis

- notebook ou script de geração
- tabela com features extraídas
- markdown com prompts usados
- exemplos de entrada e saída

## Campos preenchidos para a versão atual

### Dataset desestruturado escolhido

- `data/external/genai/product_text_samples.csv`

### Colunas de entrada

- `source_id`
- `title`
- `product_description`

### Modelo utilizado

- `gpt-4.1-mini` no modo API
- `reference_output` no modo reprodutível versionado

### Prompt principal

- prompt de extração para JSON estrito com schema fixo de features de produto
- implementado em `src/genai_feature_extraction.py`

### Estrutura de saída

- `category`
- `material`
- `compatibility`
- `quality_signals`
- `functional_features`
- `security_features`
- `aesthetic_signals`
- `target_use_cases`
- `summary`

### Arquivo final das features

- `data/curated/genai/product_text_features.csv`
- `data/curated/genai/product_text_features.jsonl`

### Link do notebook ou script

- `src/genai_feature_extraction.py`

## Evidências recomendadas

Salvar em `docs/` ou `images/presentation/`:

- exemplo de entrada textual: `data/external/genai/product_text_samples.csv`
- exemplo de JSON de saída: `data/curated/genai/product_text_features.jsonl`
- tabela final: `data/curated/genai/product_text_features.csv`

## Risco principal deste item

O maior risco é vender heurística como se fosse LLM real. A documentação final deve deixar isso explícito:

- se foi heurístico, dizer heurístico
- se foi LLM, dizer qual modelo foi usado

## Status atual

- base documental do item: pronta
- implementação mínima do item: pronta
- chamada real à LLM: validada localmente com `gpt-4.1-mini`
- saída final atual: `data/curated/genai/product_text_features.csv` com `extraction_mode=openai_api`





