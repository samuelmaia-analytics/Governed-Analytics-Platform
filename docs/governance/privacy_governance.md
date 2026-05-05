# Privacidade, LGPD e Governança

Este documento descreve controles técnicos de privacidade aplicados no projeto.
Os controles são **LGPD-inspired** e não constituem parecer jurídico.

## Escopo e posicionamento

- foco em engenharia de dados e publicação analítica;
- objetivo de reduzir exposição desnecessária;
- validações técnicas para prontidão de publicação.

## Aviso importante

Este projeto não declara conformidade jurídica plena.
Ele demonstra controles técnicos orientados a privacidade por design.

## Data classification

A classificação é executada em `src/lgpd_classifier.py`.
Categorias usadas:

- `non_personal`
- `personal_data`
- `sensitive_personal_data`
- `indirect_identifier`

Essa classificação suporta decisões de exposição na camada publicada.

## Privacy risk scoring

O score é calculado em `src/risk_scoring.py`.
A saída inclui:

- score numérico;
- nível de risco (`low`, `medium`, `high`);
- recomendações de ação.

Esse mecanismo fornece explicabilidade para decisão de publicação.

## Publication controls

Antes da publicação, o fluxo valida:

- colunas obrigatórias esperadas;
- ausência de colunas proibidas;
- pseudonimização de chaves sensíveis;
- preenchimento de campos críticos.

Falhas nesses critérios podem bloquear publicação.

## Data minimization

A camada publicada mantém apenas atributos necessários para leitura executiva.
Identificadores não essenciais são removidos ou pseudonimizados.

Princípios aplicados:

- necessidade;
- adequação ao uso analítico;
- prevenção de exposição excessiva.

## Masking/anonymization preview

O projeto inclui preview técnico de transformações em `src/privacy_transformations.py`.
No app, esse preview ajuda a entender trade-offs entre utilidade e proteção.

## Camadas e exposição

- `data/raw/landing/`: ingestão bruta
- `data/standardized/`: padronização técnica
- `data/curated/analytics/`: camada interna de engenharia
- `data/published/dashboard/`: camada publicada para consumo

Regra de consumo:

o dashboard executivo deve consumir somente a camada publicada.

## Evidências operacionais

Evidências de governança e qualidade são materializadas em artefatos versionáveis:

- relatórios em `docs/`
- resultados de checks em `data/curated/quality/`
- status de governança em `data/published/monitoring/`

## Limitações

- dataset de demonstração público/sintético;
- sem implementação completa de IAM corporativo;
- sem trilha de auditoria centralizada em plataforma externa.

## Production considerations

Para evolução em cenário real:

- adotar matriz formal de acesso por perfil e ambiente;
- implementar retenção e descarte aprovados por jurídico/compliance;
- centralizar logs de acesso e publicação;
- revisar periodicamente pesos e regras de risco;
- validar controles com segurança e jurídico antes de dados pessoais reais.

## Conclusão

Este projeto entrega uma base **privacy-aware** e **production-oriented** para portfólio.
A proposta é demonstrar maturidade técnica de governança, sem extrapolar promessas jurídicas.
