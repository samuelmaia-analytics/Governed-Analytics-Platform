# Failure Alert Example

| Campo | Valor |
| --- | --- |
| Pipeline | `governed_analytics_pipeline` |
| Status | `FAILED` |
| Etapa com falha | `publication_gate` |
| Erro | Critical checks failed before publication |
| Severidade | `high` |
| Acao recomendada | Corrigir falhas criticas de qualidade e risco LGPD antes de nova tentativa |
| Retry recomendado ou nao | Nao recomendado antes da remediacao |
| Horario | `2026-06-30T16:40:30Z` |
| Link/local dos logs | `logs/error_logs.csv` |

Mensagem sugerida:

> Publicacao bloqueada. Nao promover o dataset ate que as issues criticas sejam
> corrigidas e o Publication Gate seja executado novamente.
