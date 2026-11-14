# Capturas reais do Streamlit

O processo oficial reutiliza `scripts/capture_streamlit_screenshots.py` e inicia `app/main.py` localmente, com o mesmo Python usado para executar o script. Uma porta livre de loopback evita capturar outra instância aberta.

## Preparação e execução

Na raiz do GAP, com Python 3.11–3.13:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts/capture_streamlit_screenshots.py
```

Playwright está declarado no extra `dev` do `pyproject.toml`. O Chromium precisa ser instalado separadamente. O processo encerra somente a instância Streamlit que iniciou.

## Dimensões e carregamento

- Viewport desktop: **1440 × 900**, escala de pixels **1** e zoom padrão.
- Captura nativa do viewport, sem página inteira, recorte posterior, montagem ou redimensionamento.
- Aguarda o título da página, o término da execução do Streamlit e as fontes antes de salvar.
- Aborta diante de página não encontrada, exceção do aplicativo ou dimensões diferentes de 1440 × 900.
- A prévia exige selecionar a aba real “Prévia de transformações”.

## Arquivos atualizados

| Arquivo em `assets/screenshots/` | Conteúdo |
|---|---|
| `executive_overview.png` | Cabeçalho, navegação, acesso rápido e início dos cards executivos |
| `lgpd_privacy_risk.png` | Diagnóstico demonstrativo de privacidade |
| `data_quality.png` | Validações e indicadores de qualidade |
| `governance_control_center.png` | Laboratório de governança e contexto |
| `privacy_transformation_preview.png` | Aba de transformações e resumo de ações |

As capturas mostram o app local e o dataset selecionado por padrão; não comprovam deploy no Community Cloud. Os valores e a freshness podem variar. Conteúdo abaixo do limite de 900 pixels continua acessível por rolagem no aplicativo.

## Revisão antes da publicação

Abra cada PNG no tamanho original e confirme legibilidade, proporção, página correta, ausência de carregamento pendente e de exceções. Verifique a navegação lateral e os indicadores. Não altere o estado demonstrativo para produzir resultados mais favoráveis.

Os READMEs usam os nomes canônicos acima. `executive_overview_v2.png` e `executive_overview_v3.png` são capturas históricas. Atualize as referências somente depois da revisão visual. Nenhum commit, push ou publicação é realizado pelo script.
