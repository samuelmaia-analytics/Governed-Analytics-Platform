from __future__ import annotations

import streamlit as st

from streamlit_shared import (
    DOCS_DIR,
    PIPELINE_LOG_PATH,
    PUBLICATION_DECISION_PATH,
    WORKFLOWS_DIR,
    file_status,
    read_json_safe,
    relative_path,
    render_artifact_diagnostics,
    render_file_warning,
)

_MAIN_WORKFLOW_STEPS = (
    ("Schedule Trigger", "Disparo agendado"),
    ("Set Execution Metadata", "Preparar metadados da execução"),
    ("Check Input Dataset", "Verificar dataset de entrada"),
    ("Input Dataset Exists?", "Dataset disponível?"),
    ("Run Data Quality Checks", "Executar verificações de qualidade"),
    ("Run LGPD Classification", "Executar classificação LGPD"),
    ("Run Privacy Risk Scoring", "Calcular risco de privacidade"),
    ("Generate Governance Docs", "Gerar documentos de governança"),
    ("Register Execution Log", "Registrar log da execução"),
    ("Send Success Alert", "Enviar alerta de sucesso"),
)
_ERROR_HANDLER_STEPS = (
    ("Error Trigger", "Disparo de erro"),
    ("Extract Error Metadata", "Extrair metadados do erro"),
    ("Register Error Log", "Registrar log de erro"),
    ("Send Error Alert", "Enviar alerta de erro"),
)
_NODE_LABELS_PT_BR = dict((*_MAIN_WORKFLOW_STEPS, *_ERROR_HANDLER_STEPS))
_WORKFLOW_STATUS_LABELS_PT_BR = {
    "importable JSON": "JSON disponível para inspeção",
    "read error": "Erro de leitura",
}
_ARTIFACT_STATUS_LABELS_PT_BR = {
    "available": "Disponível",
    "artifact not found": "Não encontrado",
}
_ARTIFACT_LABELS_PT_BR = {
    "n8n workflows directory": "Templates n8n",
    "Pipeline execution logs": "Logs de execução do pipeline",
    "Publication decision": "Decisão de publicação persistida",
    "n8n automation documentation": "Documentação da automação",
}


def _presentation_label(value: object, labels: dict[str, str]) -> str:
    technical_value = str(value)
    return labels.get(technical_value, technical_value)


def _workflow_rows(workflow_files):
    rows = []
    for path in workflow_files:
        payload = read_json_safe(path)
        nodes = payload.get("nodes", []) if isinstance(payload, dict) else []
        rows.append(
            {
                "workflow_file": relative_path(path),
                "workflow_name": payload.get("name", path.stem)
                if isinstance(payload, dict)
                else path.stem,
                "status": "importable JSON" if payload else "read error",
                "node_count": len(nodes),
            }
        )
    return rows


def render_n8n_automation() -> None:
    st.title("Automação e Orquestração")
    st.markdown(
        "Visão arquitetural dos templates n8n versionados para orquestração, "
        "tratamento de falhas e rastreabilidade do pipeline."
    )
    st.caption(
        "Esta página é somente demonstrativa e read-only. Nenhum workflow n8n, "
        "comando, webhook ou integração externa é executado pelo Streamlit."
    )

    st.markdown("### Como interpretar esta página")
    st.write(
        "Os workflows exibidos são templates versionados no repositório. A "
        "interface mostra sua estrutura e os artefatos relacionados, mas não "
        "confirma que estejam importados, ativos ou executando em uma instância n8n."
    )
    st.warning(
        "**Templates demonstrativos — nenhuma execução é iniciada aqui.**\n\n"
        "Nodes de comando e integração presentes nos JSONs representam configuração "
        "declarada. Eles somente se tornam operacionais se o template for importado, "
        "configurado e ativado externamente no n8n."
    )

    status_rows = [
        file_status("n8n workflows directory", WORKFLOWS_DIR),
        file_status("Pipeline execution logs", PIPELINE_LOG_PATH),
        file_status("Publication decision", PUBLICATION_DECISION_PATH),
        file_status("n8n automation documentation", DOCS_DIR / "n8n_automation.md"),
    ]
    workflow_files = (
        sorted(WORKFLOWS_DIR.glob("*.json")) if WORKFLOWS_DIR.exists() else []
    )
    workflow_rows = _workflow_rows(workflow_files)

    st.markdown("## Resumo")
    metric_columns = st.columns(3)
    metric_columns[0].metric("Templates encontrados", len(workflow_files))
    metric_columns[1].metric(
        "Nodes declarados",
        sum(int(row["node_count"]) for row in workflow_rows),
    )
    metric_columns[2].metric(
        "Artefatos disponíveis",
        sum(row.get("status") == "available" for row in status_rows),
    )

    st.markdown("## Arquitetura")
    st.markdown("### Fluxo principal")
    for index, (_technical_name, display_name) in enumerate(
        _MAIN_WORKFLOW_STEPS, start=1
    ):
        st.write(f"{index}. {display_name}")
    st.info(
        "**Trigger declarado: a cada 24 horas.** Este valor está definido no "
        "template JSON e não comprova que o workflow esteja ativo em uma instância n8n."
    )

    st.markdown("## Resiliência")
    st.markdown("### Tratamento de falhas")
    for index, (_technical_name, display_name) in enumerate(
        _ERROR_HANDLER_STEPS, start=1
    ):
        st.write(f"{index}. {display_name}")
    st.caption(
        "O workflow principal referencia o error handler em settings.errorWorkflow. "
        "Isso não comprova que o error handler esteja ativo."
    )
    st.markdown("### Resiliência declarada nos templates")
    for item in (
        "Workflow separado de tratamento de erro: configurado no JSON.",
        "Referência a errorWorkflow: configurada no workflow principal.",
        "Retry: não configurado neste template.",
        "Fila: não configurada neste template.",
        "Webhook: não configurado neste template.",
        "Endpoint HTTP: não configurado neste template.",
    ):
        st.write(f"- {item}")

    st.markdown("## Artefatos")
    st.caption(
        "Disponível indica apenas que o artefato existe no ambiente atual. Não "
        "representa sucesso, validade, aprovação, freshness ou execução."
    )
    artifact_presentation = [
        {
            "Artefato": _presentation_label(
                row["artifact"], _ARTIFACT_LABELS_PT_BR
            ),
            "Estado": _presentation_label(
                row["status"], _ARTIFACT_STATUS_LABELS_PT_BR
            ),
        }
        for row in status_rows
    ]
    st.dataframe(artifact_presentation, width="stretch", hide_index=True)

    if not WORKFLOWS_DIR.exists():
        st.warning("Os templates n8n não estão disponíveis neste ambiente.")
        render_file_warning(
            WORKFLOWS_DIR,
            "Crie ou importe templates em `workflows/n8n/`.",
        )
        render_artifact_diagnostics()
        return

    if not workflow_files:
        st.warning(
            "Nenhum arquivo JSON de workflow foi encontrado em `workflows/n8n/`."
        )
        render_artifact_diagnostics()
        return

    st.markdown("## Inspeção dos Workflows")
    st.caption(
        "JSON disponível para inspeção significa apenas que o arquivo foi lido "
        "como um payload JSON não vazio. Não representa validação de schema, "
        "importação ou ativação no n8n."
    )
    workflow_presentation = [
        {
            "Arquivo": row["workflow_file"],
            "Workflow": row["workflow_name"],
            "Estado do arquivo": _presentation_label(
                row["status"], _WORKFLOW_STATUS_LABELS_PT_BR
            ),
            "Nodes declarados": row["node_count"],
        }
        for row in workflow_rows
    ]
    st.dataframe(workflow_presentation, width="stretch", hide_index=True)

    selected = st.selectbox(
        "Inspecionar workflow", [relative_path(path) for path in workflow_files]
    )
    selected_path = next(
        path for path in workflow_files if relative_path(path) == selected
    )
    payload = read_json_safe(selected_path)
    node_rows = []

    if payload:
        st.markdown(f"### {payload.get('name', selected_path.stem)}")
        node_rows = [
            {
                "node": node.get("name", ""),
                "type": node.get("type", ""),
                "notes": node.get("notes", ""),
            }
            for node in payload.get("nodes", [])
        ]
        node_presentation = [
            {
                "Etapa": _presentation_label(row["node"], _NODE_LABELS_PT_BR),
                "Node": row["node"],
                "Tipo técnico": row["type"],
                "Configuração resumida": row["notes"],
            }
            for row in node_rows
        ]
        st.dataframe(node_presentation, width="stretch", hide_index=True)

        st.caption(
            "Os nodes são definições versionadas. Credenciais e ativação específica "
            "do ambiente devem ser configuradas externamente no n8n, nunca no Streamlit."
        )

        with st.expander("JSON técnico do workflow"):
            st.caption("Conteúdo original versionado no repositório.")
            st.json(payload)
    else:
        st.warning(
            f"O artefato `{relative_path(selected_path)}` não pôde ser lido como JSON."
        )

    st.markdown("## Detalhes técnicos")
    with st.expander("Detalhes técnicos da automação"):
        st.caption(
            "Valores originais, paths relativos e identificadores técnicos "
            "preservados sem transformação."
        )
        st.markdown("**Status técnico dos artefatos**")
        st.dataframe(status_rows, width="stretch", hide_index=True)
        st.markdown("**Workflows — valores técnicos**")
        st.dataframe(workflow_rows, width="stretch", hide_index=True)
        st.markdown("**Sequência técnica do workflow principal**")
        st.write(" → ".join(name for name, _label in _MAIN_WORKFLOW_STEPS))
        st.markdown("**Sequência técnica do error handler**")
        st.write(" → ".join(name for name, _label in _ERROR_HANDLER_STEPS))
        if node_rows:
            st.markdown("**Nodes — valores técnicos**")
            st.dataframe(node_rows, width="stretch", hide_index=True)

    render_artifact_diagnostics()
