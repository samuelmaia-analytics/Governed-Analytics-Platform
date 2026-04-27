from __future__ import annotations

from streamlit_app.formatting import get_format_locale

TRANSLATIONS: dict[str, dict[str, str]] = {
    "nav_header": {"pt-BR": "Navegação", "en-US": "Navigation"},
    "nav_help": {
        "pt-BR": "Use a barra abaixo para navegar entre os blocos principais da leitura executiva.",
        "en-US": "Use the bar below to navigate the key blocks of the executive readout.",
    },
    "presentation_mode_title": {"pt-BR": "Modo apresentação", "en-US": "Presentation mode"},
    "presentation_mode_copy": {
        "pt-BR": "A navegação foi reduzida ao fluxo principal: indicadores, tendência, categorias, performance regional e síntese final.",
        "en-US": "Navigation has been reduced to the core flow: KPIs, trend, categories, regional performance and final synthesis.",
    },
    "guided_read_title": {"pt-BR": "Leitura guiada", "en-US": "Guided read"},
    "guided_read_copy": {
        "pt-BR": "Esta visão concentra os blocos principais para leitura executiva. Operação detalhada, saúde da base, recortes semânticos e tabelas de apoio continuam disponíveis pela navegação acima.",
        "en-US": "This view centralizes the key blocks for executive reading. Detailed operations, data health, semantic slices and support tables remain available in the navigation above.",
    },
    "filtered_rows_caption": {"pt-BR": "Registros filtrados", "en-US": "Filtered rows"},
}

NAVIGATION_OPTIONS = [
    {"id": "Visão completa", "pt-BR": "Visão", "en-US": "Full View"},
    {"id": "Contexto", "pt-BR": "Contexto", "en-US": "Context"},
    {"id": "KPIs", "pt-BR": "KPIs", "en-US": "KPIs"},
    {"id": "Tempo", "pt-BR": "Tempo", "en-US": "Time"},
    {"id": "Categorias", "pt-BR": "Categorias", "en-US": "Categories"},
    {"id": "Regional", "pt-BR": "Regional", "en-US": "Regional"},
    {"id": "Operação", "pt-BR": "Operação", "en-US": "Operations"},
    {"id": "Saúde", "pt-BR": "Saúde", "en-US": "Health"},
    {"id": "Semântica", "pt-BR": "Semântica", "en-US": "Semantic"},
    {"id": "Insights", "pt-BR": "Insights", "en-US": "Insights"},
]


def tr(key: str) -> str:
    locale = get_format_locale()
    if key in TRANSLATIONS and locale in TRANSLATIONS[key]:
        return TRANSLATIONS[key][locale]
    return key
