# Data Contracts

Este projeto inclui contratos YAML governados para demonstrar expectativas de
schema, qualidade, privacidade e publicacao por camada. Eles sao artefatos de
portfolio e complementam os contratos ja usados pelo pipeline.

## Contratos

| Contrato | Camada | Finalidade |
| --- | --- | --- |
| `contracts/raw_orders_contract.yml` | Bronze | Define expectativas minimas para pedidos brutos preservados. |
| `contracts/silver_orders_contract.yml` | Silver | Define padronizacao, tipos e regras de qualidade para pedidos limpos. |
| `contracts/gold_fact_orders_contract.yml` | Gold | Define a tabela fato governada para consumo analitico. |
| `contracts/customer_privacy_contract.yml` | Governance | Define controles LGPD para identificadores e atributos de clientes. |

## Campos Principais

Cada contrato inclui:

- `dataset`, `layer`, `owner` e `description`;
- `primary_key` e `refresh_frequency`;
- `columns` com tipo, nulabilidade e unicidade;
- secoes explicitas de `data_types`, `nullable` e `uniqueness`;
- `quality_rules` para validacao operacional;
- `privacy` e `lgpd_classification` para governanca LGPD;
- `publication_policy` e `publication` para limites de publicacao.

## Como Usar Em Revisao Tecnica

Esses contratos ajudam a explicar:

- quais campos sao obrigatorios;
- quais campos podem ser publicados;
- quais regras bloqueiam promocao;
- como qualidade e LGPD influenciam o Publication Gate;
- quem e responsavel por cada camada.

Antes de promover um dataset, os contratos devem ser comparados com os dados
gerados, os logs de qualidade e a decisao registrada pelo Publication Gate.
