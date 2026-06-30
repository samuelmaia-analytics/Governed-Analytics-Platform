# Operational Logs

Este projeto inclui logs operacionais simulados e estruturados para demonstrar
observabilidade de pipeline, qualidade, LGPD, publication gate e erros. Os
arquivos versionados em `logs/` sao exemplos controlados, sem credenciais e sem
dados sensiveis reais.

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `logs/pipeline_execution_logs.csv` | Resume execucoes do pipeline, etapa, duracao, volume processado, rejeicoes, scores e status final. |
| `logs/data_quality_logs.csv` | Registra checks de qualidade, severidade, linhas afetadas e descricao da regra avaliada. |
| `logs/lgpd_classification_logs.csv` | Demonstra classificacao de colunas por categoria LGPD, sensibilidade, risco e recomendacao. |
| `logs/publication_gate_logs.csv` | Mostra a decisao de publicacao por dataset com score de qualidade, risco LGPD, issues criticas e motivo. |
| `logs/error_logs.csv` | Consolida erros e warnings operacionais com acao recomendada para troubleshooting. |

## Como Interpretar Status

- `SUCCESS`: a etapa concluiu dentro dos criterios esperados.
- `WARNING`: a etapa terminou, mas gerou achado que requer revisao.
- `FAILED`: a etapa falhou ou bloqueou a promocao/publicacao.
- `PASS`: regra ou controle passou.
- `WARN`: regra passou com ressalva ou indicou desvio monitoravel.
- `Approved`: dataset pode ser consumido pela camada publicada.
- `Needs Review`: requer revisao manual antes de promocao.
- `Blocked`: nao deve ser publicado ate remediacao.

## Uso Em Auditoria E Troubleshooting

Os logs ajudam a responder perguntas operacionais comuns:

- quando o pipeline rodou;
- qual etapa falhou ou gerou alerta;
- quantos registros foram processados ou rejeitados;
- quais regras de qualidade afetaram o publication gate;
- quais colunas exigem cuidado LGPD;
- qual acao recomendada deve ser tomada antes de rerun.

Em uma entrevista tecnica, esses arquivos demonstram como o projeto pensa em
observabilidade, auditoria, rastreabilidade e suporte operacional, mesmo sendo
uma simulacao local de portfolio.
