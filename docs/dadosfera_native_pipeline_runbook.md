# Operacao de Pipeline Nativo na Dadosfera

Este runbook fecha o gap entre publicacao/catalogacao e tentativa real de operacao nativa de pipeline na plataforma.

## O que este repositório passa a suportar

- autenticacao na Dadosfera via API do Maestro
- listagem de pipelines por endpoint configuravel
- criacao de pipeline a partir de payload JSON versionado
- execucao de pipeline ja existente via API

O ponto de entrada operacional e `src/dadosfera_pipeline_ops.py`.

## O que isso ainda nao resolve sozinho

- nao inventa automaticamente uma conexao de origem acessivel pela plataforma
- nao gera payload valido sem definicao real do pipeline da Dadosfera
- nao substitui evidencias visuais de execucao e catalogacao na plataforma

Em outras palavras: o repositório agora consegue operar a API de pipelines, mas a absorcao nativa total ainda depende de modelar e executar um pipeline real no ambiente da Dadosfera.

## Pre-requisitos reais para dizer que a transformacao foi absorvida pela plataforma

- fonte de dados acessivel pela Dadosfera
- definicao real do pipeline em JSON ou export equivalente da plataforma
- execucao bem-sucedida na interface ou na API
- evidencias visuais de run, output e catalogacao
- consumidor final lendo o output da plataforma, e nao apenas o artefato gerado localmente

## Uso do operador de pipelines

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

### 5. Executar pipeline existente

```bash
python src/dadosfera_pipeline_ops.py run --pipeline-id <PIPELINE_ID>
```

### 6. Listar execucoes da pipeline

```bash
python src/dadosfera_pipeline_ops.py runs --pipeline-id <PIPELINE_ID>
```

## Template versionado para primeira tentativa real

O repositório agora inclui um template inicial em:

- `contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json`

Uso recomendado:

1. criar ou identificar uma conexao na Dadosfera e obter o `config_id`
2. subir `data/published/dashboard/fact_orders_dashboard.parquet` para um bucket S3 acessivel pela conexao
3. substituir `SUBSTITUIR_BUCKET_S3`, `SUBSTITUIR_PREFIX` e `SUBSTITUIR_CONFIG_ID_S3`
3. criar a pipeline:

```bash
python src/dadosfera_pipeline_ops.py create --definition contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json
```

## Escolha de conexao recomendada

Para este case, a conexao mais defensavel e:

- `AWS S3` como origem
- `Parquet` como formato do ativo publicado

Motivos:

- a camada publicada ja existe como artefato fisico controlado
- `Parquet` preserva schema melhor do que `CSV`
- o desenho fica mais proximo de operacao recorrente e menos dependente de upload manual
- evita vender a plataforma como transformadora principal antes de validar a ingestao nativa do ativo publicado

## Campos que voce precisa preencher com valores reais

- `source_bucket`: nome do bucket S3
- `source_prefix`: caminho do arquivo ou prefixo dentro do bucket
- `config_id`: identificador da conexao S3 cadastrada na Dadosfera

## Sequencia minima para dizer que a plataforma passou a executar pipeline nativo

1. criar a conexao S3 na Dadosfera
2. subir o Parquet publicado para o bucket
3. criar a pipeline com o JSON versionado
4. executar a pipeline
5. capturar evidencias de:
   - pipeline criada
   - pipeline executada
   - output gerado
   - ativo catalogado ou utilizavel na plataforma

## Endpoints configuraveis

Como a estrutura da API pode variar por modulo, tenant ou versao, o operador aceita override por argumentos ou variaveis de ambiente:

- `DADOSFERA_PIPELINE_LIST_ENDPOINT`
- `DADOSFERA_PIPELINE_CREATE_ENDPOINT`
- `DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE`
- `DADOSFERA_PIPELINE_RUN_ENDPOINT`
- `DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE`

Defaults atuais:

- list: `/platform/pipeline`
- create: `/platform/pipeline`
- get: `/platform/pipeline/{pipeline_id}`
- run: `/platform/pipeline/execute`
- runs: `/platform/pipeline/{pipeline_id}/pipeline_run`

Esses defaults foram alinhados aos endpoints da documentação oficial da Dadosfera Maestro Platform API. Se a plataforma responder `404` ou `405`, ajuste o endpoint para o caminho real do seu tenant ou modulo.

## Leitura rigorosa de status

Depois desta adicao, a afirmacao correta passa a ser:

- o repositório agora esta preparado para tentar criar e executar pipelines nativos via API
- a absorcao nativa total ainda depende de pipeline real, fonte real e evidencias de run bem-sucedido
