# Governed Data Lake Layers

Este projeto usa uma estrutura local de Data Lake governado para simular uma
arquitetura mais próxima de um ambiente real de dados em produção, mantendo o
escopo transparente como projeto técnico de portfólio.

## Bronze

A camada Bronze representa os dados brutos preservados, recebidos de fontes
externas ou landing zones. Ela deve manter os arquivos o mais próximos possível
do formato original, sem limpeza manual e sem enriquecimento de dados sensíveis.

Uso esperado no projeto:

- preservar entradas originais;
- apoiar rastreabilidade entre origem e processamento;
- evitar sobrescrita de dados recebidos.

## Silver

A camada Silver representa dados limpos, padronizados e preparados para
validação. Nesta etapa, os datasets podem passar por normalização de tipos,
padronização de nomes, profiling, checks iniciais de schema e classificação
LGPD.

Uso esperado no projeto:

- receber dados vindos da Bronze após ingestão;
- aplicar padronização técnica;
- gerar evidências iniciais de qualidade e conformidade.

## Gold

A camada Gold representa dados governados e prontos para consumo analítico. Ela
concentra datasets curados, marts, camadas semânticas e artefatos publicados
somente após controles de qualidade, LGPD, contratos e publication gate.

Uso esperado no projeto:

- servir dashboards e análises executivas;
- materializar métricas e visões confiáveis;
- separar consumo de negócio dos dados internos brutos.

## Quarantine

A camada Quarantine representa dados bloqueados, rejeitados ou reprovados por
critérios de qualidade, LGPD, contrato ou publication gate. Ela existe para
evitar que dados inseguros avancem para consumo analítico sem investigação.

Uso esperado no projeto:

- isolar registros ou arquivos com falhas críticas;
- registrar motivos de bloqueio e necessidade de remediação;
- impedir consumo direto pelo Streamlit ou por camadas publicadas.

## Por Que Isso Aproxima O Projeto De Produção

Separar dados em Bronze, Silver, Gold e Quarantine torna o fluxo mais auditável,
reduz o risco de exposição indevida e deixa claro onde cada controle de
governança atua. Essa organização facilita observabilidade, rastreabilidade,
controle de qualidade, aplicação de LGPD e decisões de publicação com evidência.

No contexto deste repositório, a estrutura é local e simulada, mas reproduz um
padrão usado em plataformas reais de dados governados.
