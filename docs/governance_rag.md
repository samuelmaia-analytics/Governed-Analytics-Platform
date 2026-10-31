# Assistente de Governanca (RAG)

## Implementado

Pagina independente `governance-assistant` na navegacao Streamlit. Ingestao
somente leitura, divisao por linhas com sobreposicao, metadados, embeddings
esparsos TF-IDF normalizados, recuperacao por similaridade cosseno e resposta
extrativa com citacoes. Nao e busca semantica neural. Nenhuma nova dependencia.
A extracao estruturada de produtos e a pagina GenAI permanecem separadas.

Fluxo: manifesto aprovado -> verificacao de caminho/hash/conteudo -> trechos
de ate 1400 caracteres com duas linhas de sobreposicao -> TF-IDF -> top-5 ->
evidencias citadas -> conferencia humana. A interface mostra fontes, linhas,
hash SHA-256, mtime UTC, dataset e owner quando presentes na fonte, e score.
Mtime nao e data de vigencia nem prova de freshness da execucao de governanca.

## Fontes e Aprovacao

As seis fontes abaixo foram autorizadas pelo usuario para uso local em
2026-10-31 e registradas em `config/governance_rag_sources.yml` com hashes:

- Contrato de privacidade de clientes.
- Contrato `gold_fact_orders`.
- Regras de qualidade.
- Politica DATA_GOVERNANCE.
- Relatorios de qualidade e monitoramento published em `docs/reports/`.

Novas fontes ficam fora da base ate aprovacao humana explicita. Revisar cada arquivo quanto a
autorizacao, sensibilidade, conteudo e vigencia. Registrar o hash SHA-256 dos
bytes revisados, normalizando apenas CRLF para LF, e somente entao definir
`approved: true`. Espacos e qualquer outra mudanca de conteudo alteram o hash.
O manifesto e uma
allowlist operacional, nao substitui o processo de aprovacao da organizacao.
Nao atribui owner, SLA, classificacao ou autoridade a fontes que nao os tenham.

Para calcular um hash, sem enviar conteudo para fora:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from src.governance_rag import document_digest; print(document_digest(Path('contracts/gold_fact_orders_contract.yml').read_bytes()))"
```

Registrar o valor retornado em `sha256` da entrada revisada. Novas fontes
exigem entrada explicita e aprovacao. Caminhos aceitos: arquivos MD/YAML em
`contracts/`, `policies/`, `docs/governance/` e `docs/reports/`. Nao ha glob nem
descoberta recursiva. Fontes alteradas desde a aprovacao sao excluidas.

Excluidos: `.env`, arquivos ocultos, segredos, credenciais, dados brutos,
bronze, amostras, external, logs, CSV/Parquet, artefatos de dados pessoais,
diretorios fora da allowlist, path traversal e links simbolicos. Uma verificacao
heuristica adicional exclui arquivos com padroes de chaves, CPF, email ou segredo.
Essa verificacao NAO substitui revisao humana e pode ter falsos positivos/negativos.
O tamanho por documento e limitado a 200 KB; UTF-8 e YAML seguro sao exigidos.

## Execucao e Atualizacao

Use o ambiente do projeto (Python 3.11 a 3.13), com as dependencias existentes:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/main.py
.\.venv\Scripts\python.exe -m src.governance_rag
.\.venv\Scripts\python.exe -m src.governance_rag --question "Quais regras de qualidade se aplicam a gold_fact_orders?"
```

Nao ha banco vetorial nem indice persistido. Cada consulta reconstrui o indice
em memoria a partir das fontes aprovadas. Ao atualizar documentos/relatorios,
revise novamente, registre o novo hash e mantenha ou revogue a aprovacao. Nao
execute o pipeline de dados para atualizar o RAG. Hash divergente impede uso
automatico de conteudo novo. Perguntas e respostas nao sao gravadas pelo RAG.
Ao atualizar o codigo enquanto o Streamlit esta aberto, reiniciar o servidor
local se houver divergencia entre modulos em memoria e arquivos atuais.

## Deploy Existente

O entrypoint do app analitico, conforme README.pt-BR.md, e `app/main.py`.
`app.py` e uma interface menor separada; nao foi substituida. Dependencias em
`requirements.txt` e runtime Python 3.11 em `runtime.txt` continuam inalterados.

O workflow `.github/workflows/deploy-streamlit.yml` promove `main` para
`streamlit-prod` apos CI verde. Promocoes manuais tambem exigem branch fonte
compativel: `develop` -> `streamlit-dev`, `release` -> `streamlit-stage`,
`main` -> `streamlit-prod`. Uma branch de funcionalidade nao pode ser promovida
diretamente pelos guardrails atuais. Enviar o commit nao significa publicar.
O passo seguinte e revisao/merge autorizado em `main`, CI e promocao existente,
seguido da conferencia da rota `governance-assistant` no app publicado.

Nenhum secret do Streamlit Cloud e alterado pelo RAG. O modo local dispensa
credenciais e provedor. A branch realmente selecionada no painel do Cloud
precisa ser confirmada pelo operador; o workflow declara a branch de destino,
mas nao configura o painel do Streamlit.

Os tres contratos aprovados estao versionados sem mudancas de conteudo. A
politica local nao versionada e as versoes locais modificadas dos relatorios
nao entram no commit do RAG. Em checkout limpo, essas fontes sao excluidas se
ausentes ou com hash divergente; os contratos continuam disponiveis. Nao
aprovar automaticamente a versao diferente de um relatorio para eliminar
avisos. A inclusao dessas versoes exige uma contribuicao separada revisada.
Nao ha benchmark de relevancia de relatorios ausentes no checkout publicado.

## Provedor Opcional

O modo local e padrao e nunca acessa o provedor. O modo OpenAI exige TODOS:
`OPENAI_ENABLED=true`, `OPENAI_API_KEY` pelo mecanismo seguro existente de
`src/settings.py`, `RAG_EXTERNAL_ENABLED=true`, `RAG_OPENAI_MODEL` explicito,
e consentimento na interface para enviar a pergunta e os trechos aprovados.
Nao colocar chaves no manifesto, em perguntas, no Git ou na documentacao.

A recuperacao e os embeddings continuam locais. OpenAI seleciona apenas
citacoes e excertos verbatim em JSON; ids inexistentes ou texto inventado sao
rejeitados. Erros de rede/API/formato sao apresentados sem corpo de resposta,
credenciais ou detalhes internos. Sem fallback silencioso para outro provedor.
Timeout: 20 segundos; uma chamada sem retries; saida ate 1200 tokens. Somente
pergunta e ate cinco trechos sao enviados; o restante da base nao e enviado.
O envio exige tambem aprovacao organizacional para transferencia ao provedor.
Nao houve chamada real, paga, medicao de tokens ou validacao de custo nesta
implementacao. A CLI oferece apenas modo local.

## Evidencia e Seguranca

Trechos sao dados nao confiaveis, jamais instrucoes. O prompt do provedor
proibe alteracao de regras, exfiltracao e acoes. As saidas sao validadas contra
citacoes e texto exato das fontes e exibidas como texto, sem HTML executavel.
Titulo, dataset e owner recuperados tambem sao texto simples, nao Markdown.
Os trechos permitem quebra de linha para leitura em celular.
Nao ha tools do modelo, SQL gerado, execucao, gravacao de dados ou decisao
automatica de publicacao. Um trecho malicioso pode aparecer como evidencia:
nao e executado, mas ainda exige revisao humana da fonte e da resposta.

Falta de dois termos relevantes, cobertura lexical menor que 40%, similaridade
menor que 0.08 ou ausencia de trechos produz falta de evidencia. Essas heuristicas
nao provam que uma resposta seja correta. Politicas descrevem condicoes, nao
comprovam por que uma execucao especifica foi bloqueada. Para investigar uma
decisao concreta, aprove um relatorio que identifique a execucao, tabela,
resultado e evidencias. Fontes conflitantes/desatualizadas precisam ser
conciliadas por uma pessoa; o RAG nao decide autoridade nem vigencia.

## Avaliacao

O manifesto inclui perguntas e fontes esperadas, incluindo negativos para
execucao inexistente e pergunta fora do dominio. Executar sobre a base aprovada:

```powershell
.\.venv\Scripts\python.exe -m src.governance_rag --evaluate
.\.venv\Scripts\python.exe -m pytest tests/test_governance_rag.py tests/test_governance_assistant_page.py tests/test_app_main.py tests/test_genai_feature_extraction_module.py -q -p no:cacheprovider
```

`recall_at_k` e a fracao das fontes esperadas recuperadas no top-k (por caminho,
sem duplicar trechos). `hit_at_k` informa se alguma fonte esperada apareceu.
Nos casos negativos, sucesso significa nao recuperar nada (`negative_accuracy`).
A media de recall inclui somente casos positivos; conferir os resultados
individuais. Base vazia tem status `empty_corpus` e nao constitui validacao de
relevancia. Testes usam conteudo controlado e um manifesto temporario para
avaliar os candidatos reais, sem aprovar o manifesto operacional. Integracoes
sao simuladas: nenhum segredo real ou chamada paga.

## Limitacoes e Propostas

Implementado: RAG extrativo local e selecao opcional de evidencia via OpenAI.
Nao implementado: embeddings semanticos neurais, banco vetorial, reranker,
respostas abstrativas livres, historico, aprovacao corporativa automatizada,
RBAC documental ou avaliacao ampla de qualidade de respostas. Nao sao
necessarios para executar o fluxo local e nao devem ser apresentados como prontos.

TF-IDF depende de vocabulario (com pequeno glossario PT/EN), pode perder
parafrases e recuperar trechos pouco relevantes. Trechos podem dividir tabelas
ou YAML; consulte a fonte inteira. Latencia cresce com o tamanho da base pois
o indice e reconstruido. API acrescenta latencia, custo e transferencia externa.
Nao ha medicao real dessas grandezas, certificacao LGPD ou garantia de ausencia
de PII. Em ambiente multiusuario, a base aprovada e compartilhada; nao incluir
documentos sujeitos a permissoes individuais sem implementar controle de acesso.