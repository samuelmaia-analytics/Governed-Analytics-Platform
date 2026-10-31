# Evidências diagnósticas de publicação

O runner pode persistir evidências da execução atual para a página Publication
Governance. Os três registros são independentes e exigem ativação explícita:

```powershell
python src/run_platform_pipeline.py --steps contracts quality publish monitor --record-shadow-telemetry --record-dual-privacy-telemetry --record-content-provenance
```

Execute somente em um ambiente autorizado, com os dados internos e contratos
disponíveis. Esse comando executa as etapas indicadas, incluindo a publicação;
não é um comando de consulta. A geração dos arquivos não exige serviços externos.

Os resultados ficam em `data/published/monitoring/`:

| Flag | Arquivo | Conteúdo |
| --- | --- | --- |
| `--record-shadow-telemetry` | `publication_shadow_comparisons.jsonl` | Comparação da decisão histórica com a política canônica e validação da proveniência |
| `--record-dual-privacy-telemetry` | `dual_privacy_shadow_comparisons.jsonl` | Comparação dos riscos inherent e residual |
| `--record-content-provenance` | `dataset_content_provenance.jsonl` | Contagens e fingerprints dos dados internos e do candidato publicado |

A captura usa os objetos produzidos durante a execução, com o mesmo `run_id`.
Não carrega evidências históricas como se fossem resultados atuais. Quando as
entradas necessárias não existem, os diagnósticos registram indisponibilidade,
sem inventar uma aprovação. Falhas na escrita diagnóstica geram avisos e não
substituem a decisão histórica nem a autoridade do gate de publicação.

Sem as flags, os três arquivos não são gravados. As flags não alteram políticas,
limiares, classificação, cálculo de risco ou a decisão histórica de publicação.
Não versione os arquivos operacionais para preencher a demonstração pública.
