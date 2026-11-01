# RAG de governança: demonstração segura

## Escopo e fontes

A rota governance-assistant em app/main.py oferece recuperação local TF-IDF e
respostas extrativas com citações. Não executa SQL, tools ou decisões de
publicação. Os contratos descrevem condições; não comprovam o resultado de uma
execução. Não é certificação LGPD nem assistente corporativo.

O manifesto config/governance_rag_sources.yml da demonstração contém somente
estas fontes técnicas do projeto, já aprovadas, versionadas e sem registros
reais de clientes:

| Fonte | Conteúdo |
| --- | --- |
| contracts/customer_privacy_contract.yml | Identificadores, pseudonimização e condições de publicação |
| contracts/gold_fact_orders_contract.yml | Schema e regras técnicas do contrato gold_fact_orders |
| contracts/data_quality_rules.yml | Catálogo de checks de qualidade |

Não foram criadas novas fontes ou regras de negócio. Os três hashes aprovados
foram preservados. A avaliação usa o manifesto real, sem recalcular/aprovar hashes
durante o teste. Também verifica que os três documentos são rastreados pelo Git.

Problemas encontrados no manifesto anterior:
- policies/DATA_GOVERNANCE.md: arquivo local não versionado, ausente no checkout limpo.
- docs/reports/data_quality_report.md: relatório gerado com hash diferente do aprovado.
- docs/reports/published_layer_monitoring.md: relatório gerado com hash diferente do aprovado.

Esses itens foram removidos do corpus da demonstração por serem instruções
locais/relatórios gerados, não reintroduzidos com novos hashes. A ingestão aceita
somente o diretório contracts/; políticas, documentos pessoais/corporativos,
relatórios, dados brutos e uploads estão fora do escopo. Não há ingestão automática
de diretórios nem busca externa.

## Aprovação e validação de hash

Uma fonte exige approved: true, caminho autorizado, SHA-256 válido, UTF-8,
tamanho até 200.000 bytes e ausência dos indicadores sensíveis reconhecidos.
Caminhos absolutos, traversal, arquivos ocultos e symlinks são rejeitados.
A heurística de conteúdo sensível não substitui revisão humana de privacidade.

O digest é SHA-256 dos bytes após trocar somente CRLF por LF. Assim, checkout
Windows/Linux não invalida uma aprovação; espaços, texto, BOM ou qualquer outra
mudança continuam alterando o digest. O hash valida integridade da revisão,
não autoria, vigência, veracidade ou ausência de dados pessoais.

Fonte ausente, ilegível, alterada ou potencialmente sensível não entra no índice.
A interface mostra o problema; as demais fontes válidas podem continuar locais.
Nunca copiar outra versão ou atualizar o hash automaticamente para ocultar o aviso.
Se uma das três fontes da demo falhar, interromper a demonstração e revisar a causa.
Mudanças futuras de conteúdo/aprovação exigem revisão separada.

~~~powershell
uv run python -m src.governance_rag --evaluate
uv run python -m src.governance_rag --question "Quais regras de qualidade se aplicam a gold_fact_orders?"
~~~

A CLI é exclusivamente local. Não há banco vetorial nem índice persistido.
Cada consulta relê e valida os documentos; não há histórico de perguntas/respostas.
Não execute o pipeline de dados para preparar a base RAG.

## Demonstração local sem chave

Use Python suportado pelo pyproject.toml e o ambiente do projeto. Na raiz do
worktree da demonstração:

~~~powershell
$env:OPENAI_ENABLED = "false"
$env:RAG_EXTERNAL_ENABLED = "false"
$env:PYTHON_DOTENV_DISABLED = "1"
uv run streamlit run app/main.py --server.address=127.0.0.1
~~~

O modo Local (TF-IDF) é o padrão e funciona sem OPENAI_API_KEY, secrets ou rede.
Não há fallback que chame o provedor. A pergunta e os excertos são exibidos como
texto; metadados recuperados não são renderizados como HTML/Markdown ativo.

Roteiro: consultar as regras de qualidade e privacidade dos contratos, abrir
as citações e conferir linhas/hash; perguntar sobre uma execução inexistente e
conferir a abstenção. Não usar perguntas com pessoas, clientes ou segredos.

## OpenAI opcional: configuração e consentimento

A chamada só ocorre se houver evidência recuperada e todas as condições:
1. Seleção explícita de OpenAI na consulta.
2. Consentimento booleano daquela consulta.
3. OPENAI_ENABLED=true e credencial configurada no servidor.
4. RAG_EXTERNAL_ENABLED=true e RAG_OPENAI_MODEL explícito.

Não há modelo padrão ou campo de chave na interface. O callback de envio consome
a autorização e desmarca o checkbox no servidor. O formulário também limpa os
campos ao enviar; uma próxima consulta exige autorização nova. O consentimento
não autoriza dados fora do escopo do manifesto.

Use secrets do Streamlit. Localmente, prefira o arquivo global fora do repositório,
por exemplo %USERPROFILE%/.streamlit/secrets.toml no Windows. Na Cloud, use o painel
privado de Secrets do app. Nunca coloque uma chave em código, commit, pergunta,
manifesto, log, screenshot, compartilhamento de tela ou documentação.

Configuração inicial segura no painel de Secrets, em chaves de nível raiz:

~~~toml
OPENAI_ENABLED = false
RAG_EXTERNAL_ENABLED = false
~~~

Para ligar a demo externa, configure no painel privado OPENAI_API_KEY com a chave
real, RAG_OPENAI_MODEL com um modelo autorizado compatível com Chat Completions,
temperature=0 e resposta JSON, e passe as duas flags para true. A página inicializa
os secrets de nível raiz como variáveis de ambiente somente na consulta externa
consentida; a chave não é lida para renderização nem exibida.

Não crie uma seção TOML [openai] para estas variáveis: secrets aninhados não são
exportados como variáveis de ambiente. A representação de OpenAISettings omite
a chave. Não imprimir o objeto de configuração ou o ambiente.

Para desligar: definir RAG_EXTERNAL_ENABLED=false e OPENAI_ENABLED=false no painel,
reiniciar o app para reaplicar configuração e confirmar o modo Local. Remover a
chave do painel se ela não for mais necessária; revogá-la no provedor se exposta.
Reiniciar após remoção de secrets evita valores antigos no ambiente do processo.

## Limites e privacidade

| Controle | Limite |
| --- | --- |
| Pergunta | 2.000 caracteres |
| Documento | 200.000 bytes |
| Trecho | 1.400 caracteres |
| Contexto enviado | Até 5 trechos, total até 7.000 caracteres |
| Saída solicitada | max_completion_tokens=1.200 |
| Corpo de resposta lido | 32.000 bytes; excesso rejeitado |
| Resposta exibida | Até 8.000 caracteres |
| Rede | Timeout de I/O de 20 segundos, uma chamada, sem retries |

O timeout de rede não é garantia de latência total exata (por exemplo, resolução
DNS e fases de rede variam). O teste simula timeout; nenhuma chamada paga é usada.
Apenas pergunta e trechos recuperados são enviados. O índice e os embeddings
continuam locais. store=false é explícito; isso não garante retenção zero pelo
provedor. Conferir a política de dados e as permissões da conta antes da demo.

A saída do provedor só pode selecionar IDs válidos e citações verbatim dos trechos.
JSON inválido, erros HTTP/rede, timeout, excesso ou citações inventadas falham com
mensagem genérica, sem corpo da resposta, credenciais ou cadeia interna de erro.
Não há retry nem fallback externo. Local continua disponível para nova consulta.

O RAG não grava perguntas, respostas ou chave em arquivos/logs/cache. Valores dos
widgets e resposta existem transitoriamente na sessão do Streamlit; não há histórico
da aplicação nem garantia de apagamento forense da memória. Configuração de logs,
acesso ao host e retenção do provedor devem ser conferidos pelo operador.

## Custos e demonstração privada no Streamlit Cloud

Local não tem custo de API. OpenAI cobra conforme modelo e tokens de entrada/saída,
incluindo o contexto e instruções. O teto de saída não fixa o custo da consulta nem
substitui orçamento da conta; caracteres não são tokens. Consultar preços oficiais,
usar projeto/chave dedicados e monitorar uso. Não há custo medido ou modelo validado
com chamada real neste trabalho.

Após revisão e publicação do código autorizadas separadamente:
1. Confirmar repositório, branch, Python e entrypoint app/main.py no app de demo.
2. Configurar acesso privado e convidados no painel; testar o bloqueio com uma
   sessão não autorizada antes de compartilhar o link. Não foi implementada nova
   autenticação/RBAC nesta mudança.
3. Começar com ambas as flags false e sem chave. Confirmar três fontes e nenhum
   aviso de hash; testar o modo Local e as citações.
4. Se houver necessidade e autorização para envio, configurar somente pelo painel
   de Secrets e ligar as flags. Não compartilhar a tela de Secrets.
5. Autorizar uma pergunta sintética na consulta e conferir a indicação de chamada
   externa. Submeter outra sem consentimento deve bloquear o envio.
6. Desligar as flags, reiniciar e retestar Local após a demonstração.

Não houve commit, push ou deploy nesta preparação. O fluxo existente de promoção
de branches não foi modificado; não promover uma feature contornando guardrails.
A configuração de privacidade e o funcionamento do provedor na Cloud ainda
dependem dessa verificação manual. Não anunciar o app como privado só pelo nome.

## Verificações e limitações

~~~powershell
uv run pytest tests/test_governance_rag.py tests/test_governance_assistant_page.py tests/test_settings.py -q
uv run ruff check src app tests
uv run python -m src.governance_rag --evaluate
git diff --check
~~~

Testes usam rede simulada. Cobrem configuração desligada, ausência de chave e de
consentimento, autorização consumida por consulta, limites, erro seguro, hashes,
CRLF/LF e manifesto real. TF-IDF é lexical e pode não entender paráfrases;
a avaliação pequena não prova correção geral. Conferir as fontes e sua vigência.
Perguntas sobre resultados de execuções não são suportadas por estes contratos.

Referências oficiais:
- Streamlit secrets: https://docs.streamlit.io/develop/concepts/connections/secrets-management
- Streamlit Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Formulário: https://docs.streamlit.io/develop/api-reference/execution-flow/st.form
- API e limites/store: https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
