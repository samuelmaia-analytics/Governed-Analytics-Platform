# Project Deck

## Estrutura Narrativa

A apresentação funciona melhor se seguir a lógica:

1. problema
2. decisão arquitetural
3. ativo central
4. governança da exposição
5. prova de consumo
6. prova de publicação
7. robustez operacional
8. limite real

## Slide 1 | Tese

**Mensagem**

Transformar um dataset relacional bruto em um ativo analítico governado, publicado e operacionalizado para consumo executivo.

**Fala**

“O objetivo deste projeto foi sair de dados transacionais fragmentados e chegar a um produto analítico utilizável. A solução foi desenhada para mostrar modelagem, governança, publicação, operação recorrente e consumo como partes da mesma arquitetura.”

## Slide 2 | Problema

**Mensagem**

Olist é rico em dado, mas pobre em legibilidade executiva na forma original.

**Pontos**

- múltiplas tabelas e dependência de joins
- dificuldade de responder perguntas de negócio diretamente na origem
- necessidade de separar engenharia, exposição e consumo

## Slide 3 | Arquitetura

**Mensagem**

A solução foi organizada em camadas para reduzir ambiguidade de uso e melhorar governança.

**Pontos**

- `raw -> standardized -> staging -> curated -> published`
- `curated` como camada interna de engenharia
- `published` como camada oficial de exposição
- `published/semantic` e `published/monitoring` fechando consumo e operação

## Slide 4 | Ativo Central

**Mensagem**

`fact_orders_enriched` é a espinha dorsal da solução.

**Pontos**

- granularidade: `1 linha por item de pedido`
- volume: `112.650` linhas
- uso: SQL, qualidade, documentação, BI e derivação da publicada

## Slide 5 | Governança da Exposição

**Mensagem**

O dashboard não consome a camada interna completa.

**Pontos**

- `fact_orders_dashboard` deriva da tabela principal
- pseudonimização de `order_id`, `customer_unique_id` e `seller_key`
- remoção de identificadores e quase-identificadores desnecessários
- separação clara entre engenharia e consumo

## Slide 6 | SQL e Evidência Analítica

**Mensagem**

A modelagem foi validada por perguntas reais de negócio.

**Pontos**

- top categorias por receita
- evolução temporal
- receita por estado
- atraso por categoria
- distribuição por meio de pagamento

## Slide 7 | Dashboard

**Mensagem**

O Streamlit é o produto executivo da solução.

**Pontos**

- KPIs, tendência, categorias, geografia e insights
- consumo exclusivo da camada publicada
- coerência entre base, narrativa e visual

## Slide 8 | Semântica Expandida

**Mensagem**

A camada publicada passou a suportar recortes adicionais sem expor a base inteira.

**Pontos**

- logística
- seller
- cohort

**Fala**

“Esse ponto mostra que a camada publicada não ficou estática. Ela evoluiu para suportar novas leituras de negócio sem reabrir a exposição da camada interna.”

## Slide 9 | Dadosfera e Catálogo

**Mensagem**

A entrega foi além do ambiente local.

**Pontos**

- ativo principal publicado na plataforma
- evidências de importação, catálogo, coleção e volume
- manifesto local e inventário versionado
- sync complementar de catálogo via API do Maestro

## Slide 10 | Robustez Operacional

**Mensagem**

O projeto já tem operação recorrente da camada publicada.

**Pontos**

- monitoramento de freshness e qualidade
- job agendado com artefatos operacionais
- autenticação não interativa por token para operação por API
- relatórios operacionais e observabilidade de falha

## Slide 11 | Robustez de Engenharia

**Mensagem**

A solução foi pensada para resistir à revisão técnica.

**Pontos**

- `124/124` testes passando
- cobertura total acima de `83%`
- gate mínimo de cobertura em `80%`
- contratos simples de schema
- checks de qualidade
- workflows de CI, lint e promoção do branch de deploy

## Slide 12 | Escopo Real

**Mensagem**

O projeto está pronto como produto analítico, mas não infla o que ainda não foi evidenciado.

**Pontos**

- feito: modelagem, governança, publicação, dashboard, catálogo, monitoramento, sync API, automação GitHub
- não feito: pipeline nativo comprovadamente executando dentro da Dadosfera

## Slide 13 | Fechamento

**Mensagem final**

“Se eu resumir a entrega em uma frase: este projeto demonstra a capacidade de transformar dado bruto em ativo analítico operacionalizado, com critério de modelagem, controle de exposição, robustez de engenharia e prova real de consumo.”
