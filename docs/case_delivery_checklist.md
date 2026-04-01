# Checklist de Entrega do Case

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`
- Vídeo de apresentação: `https://youtu.be/SqJ0UF1Em9k`

## Estrutura do Repositório

- [x] `README.md`
- [x] `docs/`
- [x] `sql/`
- [x] `images/`
- [x] `presentation/`
- [x] `streamlit_app/`
- [x] `powerbi/`

## Pronto no Projeto

- [x] artefato de planejamento
- [x] base raw com volume suficiente
- [x] camada analítica final com mais de 100k registros
- [x] análise descritiva inicial
- [x] dicionário de dados
- [x] arquitetura em camadas
- [x] catálogo local e inventário de ativos
- [x] queries SQL salvas
- [x] prints dos resultados SQL
- [x] dashboard Streamlit implementado
- [x] export para Power BI
- [x] testes automatizados mínimos
- [x] camada publicada para consumo seguro do dashboard
- [x] camada semântica publicada para logística, seller e cohort
- [x] monitoramento recorrente da camada publicada
- [x] job operacional com artefatos e observabilidade

## GitHub

- [x] repositório git inicializado
- [x] remoto GitHub configurado
- [x] commitar a versão final da entrega
- [x] fazer push da versão final
- [x] validar `README` e docs no GitHub web
- [x] registrar o link final do GitHub

Link final do repositório:

- `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`

## Dadosfera

- [x] publicar dataset real na plataforma
- [x] validar preview/esquema do ativo publicado
- [x] catalogar ou registrar o ativo na plataforma
- [x] gerar evidências reais da plataforma
- [x] salvar capturas em `images/dadosfera/`
- [x] implementar sync complementar por API
- [x] preparar operação por token não interativo
- [x] validar `POST /auth/sign-in` com MFA real no tenant
- [ ] obter do suporte o artefato de sessão ou token reutilizável para `catalog` e `pipelines`
- [ ] evidenciar pipeline nativo real na plataforma
- [ ] evidenciar catalogação do pipeline nativo na plataforma

## GenAI e LLM

- [x] escolher dataset desestruturado para o item
- [x] gerar features com IA
- [x] documentar prompts utilizados
- [x] materializar tabela final de features

## Evidências Visuais Finais

- [x] prints da Dadosfera
- [x] prints do dashboard final em execução
- [x] print do item GenAI salvo em `images/genai/`
- [x] organizar imagens finais em `images/`

## Apresentação Final

- [x] estrutura da pasta `presentation/`
- [x] deck base em markdown
- [x] roteiro de fala inicial
- [x] deck final preenchido com imagens
- [x] links finais da Dadosfera inseridos na apresentação
- [x] link do vídeo inserido
- [x] vídeo de apresentação publicado no YouTube

## Leitura Correta do Status

- o projeto local está pronto para demonstração técnica
- o GitHub já está consolidado com as evidências principais
- a parte da Dadosfera já está comprovada para o ativo principal
- a operação recorrente da camada publicada já está implementada
- a API do Maestro foi validada até o limite exposto pelo tenant: `sign-in` com MFA funciona, mas `catalog` e `pipelines` seguem dependentes do fluxo oficial do suporte
- pipeline nativo na plataforma segue sem evidência final de execução
- item de GenAI com LLM externa já foi validado localmente
