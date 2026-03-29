# 00 Planejamento do Projeto


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

Este documento organiza as etapas do case do início ao fim, no formato de plano de execução com dependências, riscos e pontos críticos.

## Objetivo do Planejamento

Garantir que a entrega do case seja executada de forma organizada, cobrindo:

- base de dados
- integração
- catalogação
- qualidade
- SQL
- dashboard
- pipeline
- Data App
- apresentação final

## Visão Geral das Etapas

```text
1. Definir base e objetivo do case
2. Ingerir os dados e organizar em camadas
3. Padronizar e modelar os dados
4. Validar qualidade
5. Catalogar ativos
6. Gerar consultas SQL e análises
7. Publicar dashboard e Data App
8. Materializar ativos na Dadosfera
9. Registrar evidências visuais
10. Consolidar GitHub e apresentação final
```

## Plano em Formato de Checklist

### Fase 1 - Concepção

- [x] definir o dominio do case
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
- [ ] materializar a exploracao diretamente na plataforma Dadosfera

### Fase 4 - Qualidade e Governança

- [x] executar checks de qualidade locais
- [x] validar contratos de schema
- [x] documentar privacidade e governança
- [ ] evidenciar quality framework aderente ao enunciado com `great-expectations` ou `soda-core`

### Fase 5 - Catalogação

- [x] gerar manifesto local da coleção
- [x] gerar inventário de ativos
- [x] documentar classificação de dados
- [x] catalogar os ativos de verdade na Dadosfera
- [x] implementar sincronização complementar por API do catálogo

### Fase 6 - Analise

- [x] escrever queries SQL principais
- [x] exportar resultados
- [x] gerar screenshots tabulares
- [x] salvar queries e visualizacoes diretamente na Dadosfera

### Fase 7 - Aplicação e Visualização

- [x] publicar camada minimizada para dashboard
- [x] construir app em Streamlit
- [x] gerar prints finais do dashboard
- [x] conectar a narrativa do dashboard com ativos reais publicados na Dadosfera
- [x] automatizar a promoção do branch de deploy do Streamlit

### Fase 8 - Pipelines e IA

- [x] criar pipeline local em Python
- [ ] criar pipeline real dentro da Dadosfera
- [ ] catalogar esse pipeline na plataforma
- [x] implementar item de GenAI com dados desestruturados e features geradas por IA

### Fase 9 - Encerramento

- [x] organizar o README e a estrutura do case
- [x] preparar deck e talk track
- [x] gravar vídeo final
- [x] inserir links reais dos ativos na Dadosfera
- [ ] validar todos os itens do edital antes da submissão

## Dependências Entre Etapas

| Etapa | Depende de | Saida principal |
| --- | --- | --- |
| Ingestão | base escolhida | dados em `raw` |
| Padronização | ingestão | dados em `standardized` |
| Modelagem | padronizacao | `fact_orders_enriched` |
| Qualidade | modelagem | relatório de qualidade |
| Publicação segura | modelagem | `fact_orders_dashboard` |
| SQL | modelagem | resultados analíticos |
| Dashboard | publicação segura | app e prints |
| Catalogação | modelagem e docs | manifesto e inventário |
| Dadosfera | ativos prontos | links e prints reais |
| Apresentação | todos os anteriores | deck e vídeo |

## Pontos Críticos do Projeto

Os pontos mais sensíveis do case são:

1. publicar de fato os ativos na Dadosfera
2. gerar evidências reais da plataforma
3. fechar pipeline e visualização na plataforma
4. demonstrar honestamente o que é local e o que é plataforma

## Riscos do Projeto

| Risco | Impacto | Probabilidade | Mitigacao |
| --- | --- | --- | --- |
| não publicar os dados na Dadosfera | alto | alta | priorizar a subida da camada `published/dashboard` |
| faltar print da plataforma | alto | alta | seguir o runbook `docs/dadosfera_capture_runbook.md` |
| vender integração não executada | alto | média | manter documentação honesta sobre status real |
| falha no app ou em ativos gerados | médio | baixa | reexecutar `src/run_case_pipeline.py` antes da entrega |
| falta de vídeo final | médio | média | gravar após concluir capturas e links |

## Estimativa Simplificada de Esforço

| Frente | Esforco estimado |
| --- | --- |
| engenharia local e modelagem | concluído |
| documentação técnica | concluído em grande parte |
| Streamlit | concluído |
| Dadosfera real | concluído em publicação, catálogo e sync por API |
| Power BI bônus | fora do escopo core, com material complementar já disponível |
| apresentação e vídeo | concluído |

## Alocação de Recursos

Como este case foi executado individualmente, a alocacao de recursos pode ser vista assim:

- papel de engenharia de dados: ingestão, modelagem, pipeline e qualidade
- papel de analytics engineering: tabela final, SQL e camada publicada
- papel de data product: dashboard, narrativa e evidências
- papel de arquitetura: desenho de camadas, catalogação e proposta com Dadosfera

## Ordem Final Recomendada

1. subir ativo real na Dadosfera
2. catalogar o ativo e tirar prints
3. criar query, visualização e pipeline na plataforma
4. atualizar docs com links reais
5. gravar o vídeo
6. revisar checklist final e submeter


