# 09 GenAI e LLMs - Processar

Este documento organiza o item de GenAI do case, separando o que já existe no projeto do que ainda precisa ser implementado para aderir totalmente ao edital.

## Objetivo do Item

Demonstrar a capacidade de:

- trabalhar com dado desestruturado
- usar IA para gerar features
- transformar texto bruto em estrutura util para analise

## O que já existe no projeto

Hoje o projeto já possui:

- camada analítica estruturada do Olist
- dashboard com insights executivos
- documentacao do bonus de GenAI em:
  - `docs/genai_bonus.md`
- script de extração de features:
  - `src/genai_feature_extraction.py`
- dataset desestruturado de exemplo:
  - `data/external/genai/product_text_samples.csv`
- tabela final de features:
  - `data/curated/genai/product_text_features.csv`

## Status honesto atual

- insights heurísticos no dashboard: feitos
- uso de LLM externa para extração de features: preparado via script, depende de chave/API
- dataset desestruturado dedicado para este item: materializado em amostra versionada
- tabela final de features: materializada em modo de referência

## O que o edital pede

Para fechar este item, ainda falta:

- escolher ou criar um dataset desestruturado
- executar extracao de features com IA
- documentar prompts e saidas
- mostrar a estrutura final gerada

## Estrutura sugerida para execução

### Entrada recomendada

Uma tabela ou arquivo com colunas como:

- `title`
- `description`

### Processo esperado

1. selecionar amostra ou dataset desestruturado
2. definir schema de saida das features
3. enviar texto ao modelo
4. receber a resposta estruturada
5. consolidar as features em tabela final

### Exemplo de features possiveis

- categoria inferida
- material
- atributos de uso
- compatibilidade
- sinais de qualidade
- palavras-chave
- embeddings ou grupos semanticos

## Sugestao de entregaveis

- notebook ou script de geracao
- tabela com features extraidas
- markdown com prompts usados
- exemplos de entrada e saida

## Campos preenchidos para a entrega atual

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

### Estrutura de saida

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

## Evidencias recomendadas

Salvar em `docs/` ou `images/presentation/`:

- exemplo de entrada textual: `data/external/genai/product_text_samples.csv`
- exemplo de JSON de saída: `data/curated/genai/product_text_features.jsonl`
- tabela final: `data/curated/genai/product_text_features.csv`

## Risco principal deste item

O maior risco e vender heuristica como se fosse LLM real. A documentacao final deve deixar isso explicito:

- se foi heuristico, dizer heuristico
- se foi LLM, dizer qual modelo foi usado

## Status atual

- base documental do item: pronta
- implementacao minima do item: pronta
- chamada real à LLM: depende de credencial/API externa
