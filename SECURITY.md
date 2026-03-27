# Security Policy

## Escopo

Este projeto usa dados públicos do case Olist e publica apenas a camada minimizada `published/dashboard`. Mesmo assim, incidentes de segurança ou exposição indevida de dados devem ser tratados formalmente.

## Como reportar

- Não abra issue pública para relatar vazamento de segredo, credencial ou exposição indevida de dados.
- Envie o relato ao mantenedor do repositório com contexto, impacto e evidência mínima para reprodução.
- Inclua quais arquivos, variáveis de ambiente ou workflows podem estar afetados.

## O que é considerado incidente aqui

- Exposição de credenciais em código, workflow, logs ou documentação.
- Publicação acidental de camadas internas em vez da camada `published/dashboard`.
- Quebra de pseudonimização ou reintrodução de identificadores removidos.
- Falhas de automação que alterem ativos publicados sem validação mínima.

## Resposta esperada

- Confirmar recebimento.
- Classificar severidade.
- Corrigir o artefato ou workflow impactado.
- Registrar a decisão corretiva em commit e documentação quando aplicável.
