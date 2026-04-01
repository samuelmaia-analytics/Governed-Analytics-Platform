# Operação de Pipeline Nativo na Dadosfera

Este runbook reduz o gap entre publicação/catálogo e tentativa real de operação nativa de pipeline na plataforma.

## O que este repositório passa a suportar

- autenticação na Dadosfera via API do Maestro
- suporte a credencial não interativa por `DADOSFERA_ACCESS_TOKEN` ou `DADOSFERA_API_TOKEN`
- listagem de pipelines por endpoint configurável
- criação de pipeline a partir de payload JSON versionado
- deploy idempotente reaproveitando pipeline existente pelo nome
- execução de pipeline já existente via API

O ponto de entrada operacional é `src/dadosfera_pipeline_ops.py`.

## O que isso ainda nao resolve sozinho

- não cria automaticamente uma conexão de origem acessível pela plataforma
- não gera payload válido sem definição real do pipeline da Dadosfera
- não substitui evidências visuais de execução e catalogação na plataforma

Em outras palavras: o repositório agora consegue operar a API de pipelines, mas a absorção nativa total ainda depende de modelar e executar um pipeline real no ambiente da Dadosfera.

## Pre-requisitos reais para dizer que a transformacao foi absorvida pela plataforma

- fonte de dados acessível pela Dadosfera
- definição real do pipeline em JSON ou export equivalente da plataforma
- execução bem-sucedida na interface ou na API
- evidências visuais de run, output e catalogação
- consumidor final lendo o output da plataforma, e não apenas o artefato gerado localmente

## Uso do operador de pipelines

### Credenciais recomendadas

Para automação não interativa, prefira:

- `DADOSFERA_ACCESS_TOKEN`
- `DADOSFERA_API_TOKEN`

O fallback por `DADOSFERA_USERNAME` + `DADOSFERA_PASSWORD` continua suportado, mas MFA/TOTP não é apropriado para job recorrente.

### 1. Listar pipelines

```bash
python src/dadosfera_pipeline_ops.py list
```

### 2. Consultar um pipeline

```bash
python src/dadosfera_pipeline_ops.py get --pipeline-id <PIPELINE_ID>
```

### 3. Criar um pipeline a partir de JSON

```bash
python src/dadosfera_pipeline_ops.py create --definition path/to/pipeline.json
```

### 4. Criar e executar em seguida

```bash
python src/dadosfera_pipeline_ops.py create --definition path/to/pipeline.json --execute
```

### 5. Garantir pipeline e executar em seguida

```bash
python src/dadosfera_pipeline_ops.py deploy --definition path/to/pipeline.json --execute
```

### 6. Executar pipeline existente

```bash
python src/dadosfera_pipeline_ops.py run --pipeline-id <PIPELINE_ID>
```

### 7. Listar execuções da pipeline

```bash
python src/dadosfera_pipeline_ops.py runs --pipeline-id <PIPELINE_ID>
```

## Template versionado para primeira tentativa real

O repositório agora inclui um template inicial em:

- `contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json`

Uso recomendado:

1. criar ou identificar uma conexão na Dadosfera e obter o `config_id`
2. subir `data/published/dashboard/fact_orders_dashboard.parquet` para um bucket S3 acessível pela conexão
3. substituir `SUBSTITUIR_BUCKET_S3`, `SUBSTITUIR_PREFIX` e `SUBSTITUIR_CONFIG_ID_S3`
4. criar a pipeline:

```bash
python src/dadosfera_pipeline_ops.py create --definition contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json
```

Para operação recorrente, prefira o comando idempotente:

```bash
python src/dadosfera_pipeline_ops.py deploy --definition contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json --execute
```

## Escolha de conexão recomendada

Para este case, a conexão mais defensável é:

- `AWS S3` como origem
- `Parquet` como formato do ativo publicado

Motivos:

- a camada publicada já existe como artefato físico controlado
- `Parquet` preserva schema melhor do que `CSV`
- o desenho fica mais próximo de operação recorrente e menos dependente de upload manual
- evita vender a plataforma como transformadora principal antes de validar a ingestão nativa do ativo publicado

## Campos que você precisa preencher com valores reais

- `source_bucket`: nome do bucket S3
- `source_prefix`: caminho do arquivo ou prefixo dentro do bucket
- `config_id`: identificador da conexão S3 cadastrada na Dadosfera

## Sequência mínima para dizer que a plataforma passou a executar pipeline nativo

1. criar a conexão S3 na Dadosfera
2. subir o Parquet publicado para o bucket
3. criar a pipeline com o JSON versionado
4. executar a pipeline
5. capturar evidências de:
   - pipeline criada
   - pipeline executada
   - output gerado
   - ativo catalogado ou utilizável na plataforma

## Endpoints configuráveis

Como a estrutura da API pode variar por módulo, tenant ou versão, o operador aceita override por argumentos ou variáveis de ambiente:

- `DADOSFERA_PIPELINE_LIST_ENDPOINT`
- `DADOSFERA_PIPELINE_CREATE_ENDPOINT`
- `DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE`
- `DADOSFERA_PIPELINE_RUN_ENDPOINT`
- `DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE`

Defaults atuais:

- list: `/platform/pipelines`
- create: `/platform/pipeline`
- get: `/platform/pipeline/{pipeline_id}`
- run: `/platform/pipeline/execute`
- runs: `/platform/pipeline/{pipeline_id}/pipeline_run`

Esses defaults refletem o tenant validado em 31/03/2026: a listagem respondeu no caminho plural e os demais fluxos continuaram no namespace singular. Se a plataforma responder `404` ou `405`, ajuste o endpoint para o caminho real do seu tenant ou módulo.

## Leitura rigorosa de status

Depois desta adição, a afirmação correta passa a ser:

- o repositório agora está preparado para tentar criar e executar pipelines nativos via API
- a absorção nativa total ainda depende de pipeline real, fonte real e evidências de run bem-sucedido
