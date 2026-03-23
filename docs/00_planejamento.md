# 00 Planejamento do Projeto

Este documento organiza as etapas do case do inicio ao fim, no formato de plano de execucao com dependencias, riscos e pontos criticos.

## Objetivo do Planejamento

Garantir que a entrega do case seja executada de forma organizada, cobrindo:

- base de dados
- integracao
- catalogacao
- qualidade
- SQL
- dashboard
- pipeline
- Data App
- apresentacao final

## Visao Geral das Etapas

```text
1. Definir base e objetivo do case
2. Ingerir os dados e organizar em camadas
3. Padronizar e modelar os dados
4. Validar qualidade
5. Catalogar ativos
6. Gerar consultas SQL e analises
7. Publicar dashboard e Data App
8. Materializar ativos na Dadosfera
9. Registrar evidencias visuais
10. Consolidar GitHub e apresentacao final
```

## Plano em Formato de Checklist

### Fase 1 - Concepcao

- [x] definir o dominio do case
- [x] selecionar uma base com mais de 100 mil registros
- [x] definir narrativa de e-commerce e plataforma de dados
- [x] estruturar o repositorio base

### Fase 2 - Ingestao e Organizacao

- [x] carregar os arquivos raw
- [x] validar a integridade minima dos arquivos
- [x] organizar os dados em camadas
- [ ] publicar a base na Dadosfera

### Fase 3 - Exploracao e Modelagem

- [x] gerar profiling exploratorio
- [x] construir a tabela analitica principal
- [x] documentar granularidade e regras
- [ ] materializar a exploracao diretamente na plataforma Dadosfera

### Fase 4 - Qualidade e Governanca

- [x] executar checks de qualidade locais
- [x] validar contratos de schema
- [x] documentar privacidade e governanca
- [ ] evidenciar quality framework aderente ao enunciado com `great-expectations` ou `soda-core`

### Fase 5 - Catalogacao

- [x] gerar manifesto local da colecao
- [x] gerar inventario de ativos
- [x] documentar classificacao de dados
- [ ] catalogar os ativos de verdade na Dadosfera

### Fase 6 - Analise

- [x] escrever queries SQL principais
- [x] exportar resultados
- [x] gerar screenshots tabulares
- [ ] salvar queries e visualizacoes diretamente na Dadosfera

### Fase 7 - Aplicacao e Visualizacao

- [x] publicar camada minimizada para dashboard
- [x] construir app em Streamlit
- [x] gerar prints finais do dashboard
- [ ] conectar a narrativa do dashboard com ativos reais publicados na Dadosfera

### Fase 8 - Pipelines e IA

- [x] criar pipeline local em Python
- [ ] criar pipeline real dentro da Dadosfera
- [ ] catalogar esse pipeline na plataforma
- [ ] implementar item de GenAI com dados desestruturados e features geradas por IA

### Fase 9 - Encerramento

- [x] organizar o README e a estrutura do case
- [x] preparar deck e talk track
- [ ] gravar video final
- [ ] inserir links reais dos ativos na Dadosfera
- [ ] validar todos os itens do edital antes da submissao

## Dependencias Entre Etapas

| Etapa | Depende de | Saida principal |
| --- | --- | --- |
| Ingestao | base escolhida | dados em `raw` |
| Padronizacao | ingestao | dados em `standardized` |
| Modelagem | padronizacao | `fact_orders_enriched` |
| Qualidade | modelagem | relatorio de qualidade |
| Publicacao segura | modelagem | `fact_orders_dashboard` |
| SQL | modelagem | resultados analiticos |
| Dashboard | publicacao segura | app e prints |
| Catalogacao | modelagem e docs | manifesto e inventario |
| Dadosfera | ativos prontos | links e prints reais |
| Apresentacao | todos os anteriores | deck e video |

## Pontos Criticos do Projeto

Os pontos mais sensiveis do case sao:

1. publicar de fato os ativos na Dadosfera
2. gerar evidencias reais da plataforma
3. fechar pipeline e visualizacao na plataforma
4. demonstrar honestamente o que e local e o que e plataforma

## Riscos do Projeto

| Risco | Impacto | Probabilidade | Mitigacao |
| --- | --- | --- | --- |
| nao publicar os dados na Dadosfera | alto | alta | priorizar a subida da camada `published/dashboard` |
| faltar print da plataforma | alto | alta | seguir o runbook `docs/dadosfera_capture_runbook.md` |
| vender integracao nao executada | alto | media | manter documentacao honesta sobre status real |
| falha no app ou em ativos gerados | medio | baixa | reexecutar `src/run_case_pipeline.py` antes da entrega |
| falta de video final | medio | media | gravar apos concluir capturas e links |

## Estimativa Simplificada de Esforco

| Frente | Esforco estimado |
| --- | --- |
| engenharia local e modelagem | concluido |
| documentacao tecnica | concluido em grande parte |
| Streamlit | concluido |
| Dadosfera real | pendente |
| Power BI bonus | opcional e pendente |
| apresentacao e video | parcial |

## Alocacao de Recursos

Como este case foi executado individualmente, a alocacao de recursos pode ser vista assim:

- papel de engenharia de dados: ingestao, modelagem, pipeline e qualidade
- papel de analytics engineering: tabela final, SQL e camada publicada
- papel de data product: dashboard, narrativa e evidencias
- papel de arquitetura: desenho de camadas, catalogacao e proposta com Dadosfera

## Ordem Final Recomendada

1. subir ativo real na Dadosfera
2. catalogar o ativo e tirar prints
3. criar query, visualizacao e pipeline na plataforma
4. atualizar docs com links reais
5. gravar o video
6. revisar checklist final e submeter
