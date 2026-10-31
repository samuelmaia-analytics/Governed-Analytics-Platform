# Estudo de Caso: Governed Analytics Platform

## 1) Resumo executivo

Este projeto é uma **plataforma de analytics governado para portfólio, inspirada em cenários de produção**, desenvolvida para demonstrar práticas de Analytics Engineering e Governança de Dados desde a ingestão até o consumo executivo.

A solução combina:

- processamento modular de dados em Python;
- controles orientados à privacidade, inspirados na LGPD;
- validação de qualidade e contratos de dados;
- tomada de decisão explicável para publicação;
- entrega de analytics executivo por meio de Streamlit;
- quality gates de engenharia apoiados por CI.

O objetivo é demonstrar maturidade técnica sem apresentar o projeto como um sistema corporativo real em produção.

## 2) Problema de negócio

Equipes de analytics frequentemente publicam dashboards com rapidez, mas sem limites explícitos de governança.
Como consequência, organizações podem enfrentar:

- falta de clareza sobre propriedade e confiabilidade dos dados;
- definições inconsistentes de KPIs;
- controles de publicação frágeis;
- exposição desnecessária de informações sensíveis em produtos executivos.

A principal necessidade de negócio é entregar analytics executivo com evidências claras de governança, e não apenas visualizações.

## 3) Desafio de dados e governança

O desafio consiste em transformar conjuntos de dados relacionais, com características de e-commerce, em um produto analítico pronto para consumo executivo, equilibrando:

- utilidade analítica;
- minimização da exposição de dados sob a ótica de privacidade;
- confiabilidade da qualidade dos dados;
- reprodutibilidade e auditabilidade.

Sob a perspectiva de governança, a plataforma precisa tornar o status de publicação explícito e explicável.

## 4) Solução proposta

A solução proposta é um pipeline governado em camadas que:

1. ingere e prepara os dados de origem;
2. realiza profiling da estrutura e da qualidade dos dados;
3. classifica colunas utilizando lógica de sensibilidade inspirada na LGPD;
4. calcula risco de privacidade de forma explicável;
5. valida expectativas de schema e governança por meio de contratos de dados;
6. publica uma camada analítica controlada e minimizada;
7. disponibiliza scorecards e histórico de governança;
8. expõe os resultados por meio de uma aplicação executiva e artefatos de documentação.

## 5) Visão geral da arquitetura

A arquitetura separa o processamento interno da exposição executiva:

- cálculos analíticos e de governança realizados internamente em camadas curadas;
- outputs controlados disponibilizados em camadas publicadas;
- a aplicação executiva consome somente os outputs publicados.

Principais componentes arquiteturais:

- ingestão e carregamento;
- profiling e verificações de qualidade;
- classificação de privacidade;
- risk scoring;
- validação de contratos;
- controles de publicação;
- artefatos de monitoramento de governança;
- interface executiva em Streamlit;
- workflows de CI/CD.

## 6) Estratégia de qualidade de dados

A qualidade dos dados é tratada como uma entrada para o publication gate, e não como um relatório produzido apenas após a publicação.

A estratégia inclui:

- verificações declarativas e baseadas em código;
- validações de campos críticos para segurança da publicação;
- resumos de qualidade voltados à interpretação executiva;
- resultados rastreáveis dos checks para diagnóstico de engenharia.

Isso garante que o status de publicação considere simultaneamente sinais de privacidade e confiabilidade.

## 7) Estratégia de classificação de privacidade inspirada na LGPD

A plataforma classifica colunas utilizando uma abordagem em camadas:

- sinais heurísticos baseados no nome das colunas;
- sinais baseados em padrões regex;
- overrides definidos em contratos YAML para casos determinísticos de governança.

Os resultados da classificação alimentam:

- o risk scoring;
- recomendações de ação (`keep`, `review`, `mask`, `anonymize`, `remove`);
- a documentação da justificativa de publicação.

Trata-se explicitamente de uma modelagem técnica inspirada na LGPD para fins de demonstração em portfólio.

## 8) Estratégia de risk scoring

O risco de privacidade é calculado por componentes explicáveis e convertido em níveis de risco, como `low`, `medium` e `high`.

A estratégia combina:

- sinais de exposição de dados sensíveis;
- contexto de reidentificação indireta;
- penalidades relacionadas à qualidade, quando aplicáveis;
- recomendações de ação para governança.

O resultado do risco não representa um parecer jurídico; trata-se de um mecanismo de apoio à decisão de engenharia.

## 9) Estratégia de contratos de dados

Os contratos são utilizados para formalizar expectativas de governança, incluindo:

- colunas obrigatórias;
- colunas proibidas;
- expectativas de pseudonimização;
- regras de preenchimento padrão e consistência;
- restrições de schema e qualidade.

As verificações de contrato ajudam a evitar alterações silenciosas na estrutura dos dados e tornam os controles de publicação auditáveis.

## 10) Fluxo de decisão de publicação

A plataforma modela a publicação por meio de estados explícitos:

- **Candidate**: dataset preparado e aguardando avaliação de governança;
- **Validated**: rotinas de validação executadas com geração de evidências;
- **Needs Review**: achados de risco médio e/ou qualidade exigem revisão ou remediação;
- **Approved**: os controles indicam condição aceitável para publicação;
- **Blocked**: falhas críticas de governança, qualidade ou privacidade impedem a publicação.

Esse fluxo torna as decisões de go/no-go visíveis e explicáveis para revisores técnicos e de negócio.

## 11) Estratégia de observabilidade e monitoramento

A observabilidade de governança é tratada por meio de:

- scorecards dos resultados dos controles;
- artefatos de monitoramento em caminhos publicados;
- snapshots históricos append-only de governança;
- artefatos técnicos de lineage para rastreabilidade das transformações.

O objetivo é documentar não apenas os outputs de dados, mas também a confiabilidade das operações de governança ao longo do tempo.

## 12) Uso do dashboard executivo

A aplicação executiva em Streamlit oferece suporte a:

- interpretação de KPIs e status de governança;
- visibilidade sobre qualidade e risco de privacidade;
- justificativa da decisão de publicação;
- discussões de revisão sustentadas por evidências.

A solução foi projetada para fluxos executivos e de revisão, e não apenas para exploração analítica.

## 13) Práticas de engenharia

### Python modular

As responsabilidades do pipeline são distribuídas entre módulos dedicados para manter limites claros e facilitar manutenção e evolução.

### Testes

Testes automatizados cobrem comportamentos centrais relacionados a governança, qualidade, publicação e aplicação.

### CI/CD

Workflows no GitHub aplicam linting, testes automatizados e limites mínimos de cobertura.

### Verificação de tipos quando aplicável

Type checking é aplicado a módulos selecionados para aumentar a confiabilidade e facilitar revisões de código.

### Documentação

A documentação faz parte da entrega do projeto e inclui arquitetura, controles de governança, narrativa do estudo de caso e resumos direcionados a recrutadores.

## 14) Limitações

- Este projeto **não é** um sistema corporativo real de cliente em produção.
- Utiliza apenas contexto de dados de exemplo, sintéticos ou públicos.
- Não declara possuir certificação jurídica de conformidade com a LGPD.
- IAM corporativo e operações centralizadas de segurança estão fora do escopo atual.

Esses limites são intencionais e apresentados de forma transparente.

## 15) Melhorias futuras

- Adicionar uma camada de modelagem em dbt com governança semântica mais robusta.
- Expandir a profundidade do catálogo de metadados e as informações de ownership.
- Melhorar a observabilidade histórica de longo prazo e a análise de tendências.
- Tornar o publication gate automatizado mais rigoroso por meio de thresholds de política mais restritivos.
- Adicionar verificações de segurança mais robustas e validações de policy-as-code.

## 16) Competências demonstradas

Este case demonstra competências relevantes para posições como Analytics Engineer, Data Engineer e funções com foco em Governança de Dados:

- desenho de arquitetura de analytics governado;
- padrões de publicação de dados orientados à privacidade;
- confiabilidade baseada em qualidade e contratos de dados;
- apoio à decisão baseado em risco;
- workflows de engenharia reprodutíveis com gates de CI;
- comunicação técnica voltada a públicos executivos e processos seletivos.
