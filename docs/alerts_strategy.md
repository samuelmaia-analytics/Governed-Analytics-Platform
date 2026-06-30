# Alerts Strategy

Este documento descreve como o Governed Analytics Platform poderia tratar
alertas operacionais em um ambiente real. Os arquivos em `alerts/` sao exemplos
controlados de portfolio, sem credenciais, webhooks ou dados sensiveis reais.

## Canais Possiveis

Em uma implantacao real, os alertas poderiam ser enviados por:

- **Amazon SNS**: topicos separados para sucesso, warning e falha critica.
- **E-mail**: notificacoes para data owners, analytics engineers e governanca.
- **Slack**: mensagens em canais como `#data-platform-alerts`.
- **Discord**: alternativa simples para comunidades ou projetos de portfolio.
- **Telegram**: notificacoes rapidas para operacao leve.
- **n8n**: roteamento visual com webhooks, e-mail, Slack, Telegram ou HTTP Request.

Neste repositorio, os workflows n8n usam placeholders e nao carregam credenciais.
Qualquer canal real deve ser configurado fora do Git.

## Tipos De Alerta

| Tipo | Quando usar | Acao esperada |
| --- | --- | --- |
| `SUCCESS` | Pipeline concluiu, scores dentro dos limites e Publication Gate aprovado. | Registrar sucesso e manter monitoramento. |
| `WARNING` | Pipeline concluiu, mas ha score em faixa de revisao, regra com ressalva ou risco moderado. | Revisao manual antes de promover ou comunicar consumo. |
| `FAILED` | Pipeline falhou, Publication Gate bloqueou ou existe issue critica. | Investigar causa raiz, bloquear publicacao e reprocessar apos correcao. |

## Como Isso Ajuda A Sustentacao

Alertas reduzem o tempo entre falha e investigacao. Eles tambem ajudam a:

- separar incidentes criticos de avisos monitoraveis;
- registrar contexto minimo para troubleshooting;
- direcionar a acao para o responsavel correto;
- evitar publicacao silenciosa de dados ruins ou de alto risco LGPD;
- demonstrar maturidade operacional em entrevistas tecnicas.

## Exemplos Versionados

- `alerts/success_alert_example.md`
- `alerts/warning_alert_example.md`
- `alerts/failure_alert_example.md`

Esses exemplos podem ser usados como base para mensagens de SNS, e-mail, Slack,
Discord, Telegram ou n8n, adaptando apenas o formato do canal.
