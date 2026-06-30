# Publication Gate

O Publication Gate e um controle operacional simples para decidir se um dataset
pode avancar para consumo na camada Gold/publicada. Ele usa scores de qualidade,
risco LGPD e quantidade de issues criticas para registrar uma decisao auditavel.

## Regras De Decisao

| Condicao | Decisao |
| --- | --- |
| `quality_score >= 90`, `lgpd_risk_score <= 60` e `critical_issues = 0` | `Approved` |
| `quality_score` entre 70 e 89 ou `lgpd_risk_score` entre 61 e 80 | `Needs Review` |
| `quality_score < 70`, `lgpd_risk_score > 80` ou `critical_issues > 0` | `Blocked` |

## Saida

As decisoes sao registradas em:

```text
data/gold/publication_decisions.csv
```

Campos registrados:

- `execution_id`
- `dataset_name`
- `quality_score`
- `lgpd_risk_score`
- `critical_issues`
- `decision`
- `reason`
- `approved_by`
- `approved_at`

## Uso

```bash
python scripts/run_publication_gate.py --dataset-name olist_orders --quality-score 92 --lgpd-risk-score 45 --critical-issues 0
```

O script tambem aceita `--input-file` apontando para CSV ou JSON com os campos de
entrada. Quando o arquivo de decisoes ainda nao existe, ele cria o cabecalho
automaticamente.

## Valor De Governanca

Esse mecanismo demonstra uma etapa essencial de plataformas de dados governadas:
o dashboard nao deve consumir datasets apenas porque eles foram gerados. Antes
da publicacao, o dataset precisa passar por controles minimos de qualidade,
privacidade e severidade operacional.
