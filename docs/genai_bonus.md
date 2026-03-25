# Bônus de GenAI

## Objetivo do bônus

Este bônus agora possui duas frentes complementares no repositório:

- um copiloto analítico heurístico no dashboard, chamado `Insights Inteligentes`
- uma prova de conceito de extração de features em texto desestruturado usando prompt estruturado para LLM

Com isso, o projeto cobre tanto a ideia de Data App orientado à decisão quanto o item específico do edital sobre transformar texto bruto em atributos estruturados.

## Caso de uso implementado

Foi adicionada uma amostra desestruturada de produto com:

- `title`
- `product_description`

Arquivos:

- entrada: `data/external/genai/product_text_samples.csv`
- saída tabular: `data/curated/genai/product_text_features.csv`
- saída completa: `data/curated/genai/product_text_features.jsonl`
- script: `src/genai_feature_extraction.py`

## Features geradas

O processo foi desenhado para extrair:

- categoria inferida
- material
- compatibilidade
- sinais de qualidade
- funcionalidades
- sinais de segurança
- sinais estéticos
- casos de uso
- resumo executivo do item

## Como rodar

Modo reprodutível versionado no repositório:

```bash
python src/genai_feature_extraction.py --mode reference
```

Modo com LLM real via OpenAI API:

```bash
set OPENAI_API_KEY=sua_chave
python src/genai_feature_extraction.py --mode openai --model gpt-4.1-mini
```

## Leitura honesta do status

O que está implementado e comprovado:

- dataset desestruturado de exemplo
- schema de saída das features
- prompt estruturado para extração
- script executável para materializar as features
- tabela final já salva em `data/curated/genai/`

O que depende de credencial externa:

- chamada real a uma LLM via API

No ambiente atual do repositório, a saída versionada foi materializada no modo `reference`, para manter reprodutibilidade e não simular uma chamada externa que não foi executada aqui.

## Prompt principal

O script usa um prompt com instrução de JSON estrito e schema fixo para reduzir ambiguidade e facilitar auditoria da resposta.

Campos esperados:

- `category`
- `material`
- `compatibility`
- `quality_signals`
- `functional_features`
- `security_features`
- `aesthetic_signals`
- `target_use_cases`
- `summary`

## Como defender na apresentação

Fala simples e honesta:

- o item de GenAI foi tratado como extração estruturada de features a partir de texto desestruturado de produto
- o repositório já entrega entrada, prompt, schema e tabela final materializada
- a execução totalmente online depende apenas de chave de API, mas a lógica e a estrutura do caso já estão demonstradas

## Valor adicional para o case

Este bônus mostra que a solução não se limita a tabelas prontas. Ela também consegue transformar texto bruto em atributos analíticos utilizáveis, o que aproxima o projeto de cenários reais de enrichment de catálogo, product intelligence e preparação de dados para busca semântica ou recomendação.
