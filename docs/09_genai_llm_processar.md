# 09 GenAI e LLMs - Processar

Este documento organiza o item de GenAI do case, separando o que ja existe no projeto do que ainda precisa ser implementado para aderir totalmente ao edital.

## Objetivo do Item

Demonstrar a capacidade de:

- trabalhar com dado desestruturado
- usar IA para gerar features
- transformar texto bruto em estrutura util para analise

## O que ja existe no projeto

Hoje o projeto ja possui:

- camada analitica estruturada do Olist
- dashboard com insights executivos
- documentacao do bonus de GenAI em:
  - [docs/genai_bonus.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\genai_bonus.md)

## Status honesto atual

- insights heurísticos no dashboard: feitos
- uso de LLM externa para extracao de features: nao implementado neste repositorio
- dataset desestruturado dedicado para este item: nao materializado neste repositorio

## O que o edital pede

Para fechar este item, ainda falta:

- escolher ou criar um dataset desestruturado
- executar extracao de features com IA
- documentar prompts e saidas
- mostrar a estrutura final gerada

## Estrutura sugerida para execucao

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

## Campos para preencher apos a implementacao

### Dataset desestruturado escolhido

- `PREENCHER`

### Colunas de entrada

- `PREENCHER`

### Modelo utilizado

- `PREENCHER`

### Prompt principal

- `PREENCHER`

### Estrutura de saida

- `PREENCHER`

### Arquivo final das features

- `PREENCHER`

### Link do notebook ou script

- `PREENCHER`

## Evidencias recomendadas

Salvar em `docs/` ou `images/presentation/`:

- exemplo de entrada textual
- exemplo de JSON de saida
- print do notebook ou da execucao

## Risco principal deste item

O maior risco e vender heuristica como se fosse LLM real. A documentacao final deve deixar isso explicito:

- se foi heuristico, dizer heuristico
- se foi LLM, dizer qual modelo foi usado

## Status atual

- base documental do item: pronta
- implementacao real do item: pendente
