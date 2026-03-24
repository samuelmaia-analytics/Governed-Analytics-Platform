# Checklist Final de Entrega | Power BI

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

- [ ] `sql/query_principal.sql` revisada
- [ ] `powerbi/evidencia_query.md` preenchida
- [ ] `powerbi/README_powerbi.md` revisado
- [ ] `docs/bi_bonus.md` consistente com a entrega final
- [ ] os nomes executivos do dashboard batem com a documentação

## Prints e arquivos finais

- [x] print geral do dashboard salvo
- [ ] print com filtro ou drilldown salvo
- [x] arquivo `.pbix` salvo corretamente
- [ ] nomes dos arquivos finais estão consistentes
- [ ] caminhos referenciados no repositório existem de fato

## Validação final antes do envio

- [ ] abrir o dashboard do zero e validar carregamento
- [ ] revisar os números dos cards principais
- [ ] revisar um cenário de filtro extremo
- [ ] revisar ortografia dos títulos e rótulos
- [ ] remover placeholders não preenchidos
- [ ] garantir que a apresentação está defensável em entrevista técnica
