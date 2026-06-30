# Warning Alert Example

| Campo | Valor |
| --- | --- |
| Pipeline | `governed_analytics_pipeline` |
| Status | `WARNING` |
| Motivo | Score de qualidade em faixa de revisao |
| Etapa | `data_quality` |
| Registros afetados | `12` |
| Acao recomendada | Revisar regra `review_score_range` e confirmar origem do desvio |
| Severidade | `medium` |
| Proximo passo | Abrir `logs/data_quality_logs.csv`, investigar registros afetados e reexecutar quality gate |

Mensagem sugerida:

> Pipeline finalizado com alerta. A publicacao deve passar por revisao manual
> antes de promocao para consumo executivo.
