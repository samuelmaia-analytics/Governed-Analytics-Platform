# Sync de Catalogo via API da Dadosfera

Este fluxo resolve a sincronizacao programatica de publicacao/catalogacao do projeto usando a API oficial do Maestro.

## O que foi implementado

- manifesto versionado em `contracts/catalog/dadosfera_catalog_assets.json`
- cliente de API em `src/dadosfera_catalog_sync.py`
- workflow GitHub Actions para sincronizacao em `.github/workflows/sync-dadosfera-catalog.yml`

## Credenciais esperadas

Defina no ambiente local ou nos secrets do GitHub:

- `DADOSFERA_MAESTRO_BASE_URL`
- `DADOSFERA_ACCESS_TOKEN` ou `DADOSFERA_API_TOKEN` para automacao nao interativa
- `DADOSFERA_USERNAME`
- `DADOSFERA_PASSWORD`
- `DADOSFERA_TOTP` apenas para execucao manual e interativa

## Restricao operacional importante

O workflow do GitHub Actions foi endurecido para nao tentar autenticacao interativa com MFA.

- se `DADOSFERA_ACCESS_TOKEN` ou `DADOSFERA_API_TOKEN` estiver definido, o workflow usa o token e ignora MFA
- se a automacao cair no modo usuario/senha e `DADOSFERA_TOTP` estiver definido nos secrets, o job encerra com aviso e sem erro
- para automacao nao interativa, o caminho recomendado e token tecnico ou conta tecnica sem MFA
- para uso manual local, `DADOSFERA_TOTP` continua suportado pelo script

## Como rodar localmente

```bash
python src/dadosfera_catalog_sync.py --dry-run
python src/dadosfera_catalog_sync.py
```

## Como funciona

1. autentica em `/auth/sign-in`
2. lista ativos existentes em `/catalog`
3. faz match por `external_url` e, como fallback, por `display_name`
4. cria ativos inexistentes em `/catalog`
5. atualiza descricao, tags e visibilidade em `/catalog/data-asset/{id}`

## Ativos sincronizados pelo manifesto

- app Streamlit publicado
- video de apresentacao
- repositorio GitHub
- documentacao do bonus GenAI

## Observacao operacional

O workflow de sincronizacao pode ser disparado manualmente ou automaticamente quando o manifesto de ativos mudar, desde que a credencial usada seja compativel com automacao nao interativa.
