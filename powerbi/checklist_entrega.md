# Checklist Final de Entrega | Power BI


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

## Estrutura e consistência visual

- [ ] títulos dos visuais estão claros e executivos
- [ ] os 5 KPIs principais aparecem na primeira dobra da página
- [ ] há consistência visual entre cards, gráficos e filtros
- [ ] a página principal está limpa e defensável
- [ ] a hierarquia visual está favorecendo leitura executiva

## Filtros e navegação

- [ ] slicer de ano funcionando
- [ ] slicer de categoria funcionando
- [ ] slicer de pagamento funcionando
- [ ] slicer de status funcionando
- [ ] slicer de estado funcionando
- [ ] os visuais respondem corretamente aos filtros

## KPIs e métricas

- [ ] Receita Total está coerente
- [ ] Total de Pedidos está usando contagem distinta
- [ ] Ticket Médio está consistente com receita e pedidos
- [ ] Review Médio está com formatação adequada
- [ ] % Pedidos em Atraso está em percentual

## Modelo e consistência técnica

- [ ] relacionamentos do modelo estrela estão corretos
- [ ] não existem tabelas com `Column1`, `Column2` ou cabeçalhos genéricos
- [ ] `dim_date` está pronta para análise temporal
- [ ] não há relacionamento ambíguo ou duplicado
- [ ] o dashboard está compatível com os CSVs atuais de `data/processed/bi_exports`

## SQL e documentação

- [x] `sql/query_principal.sql` revisada
- [x] `powerbi/evidencia_query.md` preenchida
- [x] `powerbi/README_powerbi.md` revisado
- [x] `docs/bi_bonus.md` consistente com a entrega final
- [x] os nomes executivos do dashboard batem com a documentação

## Prints e arquivos finais

- [x] print geral do dashboard salvo
- [x] print com filtro ou drilldown salvo
- [x] arquivo `.pbix` salvo corretamente
- [x] nomes dos arquivos finais estão consistentes
- [x] caminhos referenciados no repositório existem de fato

## Validação final antes do envio

- [ ] abrir o dashboard do zero e validar carregamento
- [ ] revisar os números dos cards principais
- [ ] revisar um cenário de filtro extremo
- [ ] revisar ortografia dos títulos e rótulos
- [x] remover placeholders não preenchidos
- [x] garantir que a apresentação está defensável em entrevista técnica

## Leitura honesta do status atual

- Os itens marcados como concluídos nesta checklist possuem evidência no repositório por meio de arquivos, prints ou documentação.
- Os itens ainda em aberto dependem de validação manual no Power BI Desktop e não foram marcados sem prova objetiva.
