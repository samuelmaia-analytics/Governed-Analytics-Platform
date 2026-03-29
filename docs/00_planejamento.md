# 00 Planejamento do Projeto

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

Este documento registra o plano do case já reconciliado com o estado atual do repositório, distinguindo entregas concluídas, itens parcialmente preparados e pontos que ainda dependem de evidência final na plataforma.

## Objetivo do Planejamento

Garantir uma entrega organizada que cobrisse:

- base de dados
- integração
- catalogação
- qualidade
- SQL
- dashboard
- pipeline
- publicação
- documentação
- apresentação final

## Visão Geral das Etapas

```text
1. Definir base e objetivo do case
2. Ingerir os dados e organizar em camadas
3. Padronizar e modelar os dados
4. Validar qualidade e contratos
5. Catalogar ativos e publicar a camada segura
6. Gerar consultas SQL e análises
7. Publicar dashboard e consumo executivo
8. Empacotar operação recorrente
9. Registrar evidências visuais e links reais
10. Consolidar GitHub e apresentação final
```

## Plano em Formato de Checklist

### Fase 1 - Concepção

- [x] definir o domínio do case
- [x] selecionar uma base com mais de 100 mil registros
- [x] definir narrativa de e-commerce e plataforma de dados
- [x] estruturar o repositório base

### Fase 2 - Ingestão e Organização

- [x] carregar os arquivos raw
- [x] validar a integridade mínima dos arquivos
- [x] organizar os dados em camadas
- [x] publicar a base na Dadosfera

### Fase 3 - Exploração e Modelagem

- [x] gerar profiling exploratório
- [x] construir a tabela analítica principal
- [x] documentar granularidade e regras
- [x] expandir a modelagem para logística, seller e cohort
- [ ] materializar a exploração diretamente na plataforma Dadosfera

### Fase 4 - Qualidade e Governança

- [x] executar checks de qualidade locais
- [x] validar contratos de schema
- [x] documentar privacidade e governança
- [x] adicionar monitoramento recorrente da camada publicada
- [ ] evidenciar quality framework aderente ao enunciado com `great-expectations` ou `soda-core`

### Fase 5 - Catalogação

- [x] gerar manifesto local da coleção
- [x] gerar inventário de ativos
- [x] documentar classificação de dados
- [x] catalogar os ativos de verdade na Dadosfera
- [x] implementar sincronização complementar por API do catálogo

### Fase 6 - Análise

- [x] escrever queries SQL principais
- [x] exportar resultados
- [x] gerar screenshots tabulares
- [x] salvar queries e visualizações diretamente na Dadosfera

### Fase 7 - Aplicação e Visualização

- [x] publicar camada minimizada para dashboard
- [x] construir app em Streamlit
- [x] gerar prints finais do dashboard
- [x] conectar a narrativa do dashboard com ativos reais publicados na Dadosfera
- [x] automatizar a promoção do branch de deploy do Streamlit

### Fase 8 - Pipelines e IA

- [x] criar pipeline local em Python
- [x] empacotar operação agendada da camada publicada
- [x] implementar item de GenAI com dados desestruturados e features geradas por IA
- [ ] criar pipeline real dentro da Dadosfera
- [ ] catalogar esse pipeline na plataforma

### Fase 9 - Encerramento

- [x] organizar o README e a estrutura do case
- [x] preparar deck e talk track
- [x] gravar vídeo final
- [x] inserir links reais dos ativos na Dadosfera
- [x] validar itens centrais do edital com evidência já disponível

## Dependências Entre Etapas

| Etapa | Depende de | Saída principal |
| --- | --- | --- |
| Ingestão | base escolhida | dados em `raw` |
| Padronização | ingestão | dados em `standardized` |
| Modelagem | padronização | `fact_orders_enriched` |
| Qualidade | modelagem | relatório de qualidade |
| Publicação segura | modelagem | `fact_orders_dashboard` |
| Semântica publicada | publicação segura | marts de logística, seller e cohort |
| Monitoramento | publicação segura | checks de freshness e qualidade |
| SQL | modelagem | resultados analíticos |
| Dashboard | publicação segura | app e prints |
| Catalogação | modelagem e docs | manifesto, inventário e sync |
| Dadosfera | ativos prontos | links e prints reais |
| Apresentação | todos os anteriores | deck e vídeo |

## Pontos Críticos do Projeto

Os pontos mais sensíveis do case são:

1. publicar de fato os ativos na Dadosfera
2. gerar evidências reais da plataforma
3. manter honestidade sobre o que é local, o que é API e o que é nativo na plataforma
4. sustentar a camada publicada com operação recorrente e observabilidade

## Riscos do Projeto

| Risco | Impacto | Probabilidade | Mitigação |
| --- | --- | --- | --- |
| não publicar os dados na Dadosfera | alto | alta | priorizar a subida da camada `published/dashboard` |
| faltar print da plataforma | alto | alta | seguir o runbook `docs/dadosfera_capture_runbook.md` |
| vender integração não executada como pipeline nativo | alto | média | manter documentação honesta sobre status real |
| falha no app ou em ativos gerados | médio | baixa | reexecutar `src/run_case_pipeline.py` e monitoramento antes da entrega |
| falta de vídeo final | médio | baixa | manter vídeo e links já publicados como evidência consolidada |

## Estimativa Simplificada de Esforço

| Frente | Estado atual |
| --- | --- |
| engenharia local e modelagem | concluído |
| documentação técnica | concluído e elevado |
| Streamlit | concluído |
| Dadosfera real | concluído em publicação, catálogo e sync por API |
| operação recorrente da camada publicada | concluído |
| pipeline nativo na plataforma | pendente de evidência final |
| apresentação e vídeo | concluído |

## Ordem Final Recomendada

1. manter ativo publicado e links válidos na Dadosfera
2. manter docs alinhadas ao estado real do repositório
3. acompanhar os workflows de CI, lint e operação publicada
4. só promover pipeline nativo como “feito” quando houver evidência final de execução
