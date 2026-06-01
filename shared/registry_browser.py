"""
Shared Registry Browser Widget.

Any app can call render_registry_browser() in a Streamlit page to show
the artifact history for the current workspace.
"""
import os
import pandas as pd


def render_registry_browser(workspace_path: str = None, app_id: str = None):
    """
    Render a registry browser panel in a Streamlit app.

    workspace_path: if provided, reads the per-workspace registry CSV.
    app_id: if provided, filters to only this app's artifacts.
    Falls back to the global registry.csv if no workspace given.
    """
    import streamlit as st
    from pathlib import Path

    st.markdown("### 📋 Output History")

    # Locate registry
    registry_path = None
    if workspace_path:
        ws_reg = Path(workspace_path) / "registry" / "registry.csv"
        if ws_reg.exists():
            registry_path = ws_reg

    if registry_path is None:
        # Fall back to global registry
        global_reg = Path(__file__).parent.parent / "registry.csv"
        if global_reg.exists():
            registry_path = global_reg

    if registry_path is None:
        st.info("No output history yet. Generate outputs to populate the registry.")
        return

    try:
        df = pd.read_csv(registry_path, encoding="utf-8")
    except Exception as e:
        st.warning(f"Could not read registry: {e}")
        return

    if df.empty:
        st.info("No outputs registered yet.")
        return

    # Filter by app_id if provided
    if app_id and "app_id" in df.columns:
        df = df[df["app_id"].str.upper() == app_id.upper()]

    # Sort newest first
    if "date_generated" in df.columns:
        df = df.sort_values("date_generated", ascending=False)

    total = len(df)
    st.caption(f"**{total} artifact(s)** registered")

    # Summary metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Outputs", total)
    if "app_id" in df.columns:
        m2.metric("Apps Used", df["app_id"].nunique())
    if "project" in df.columns:
        m3.metric("Projects", df["project"].nunique())

    # Filter controls
    fc1, fc2 = st.columns(2)
    app_filter = fc1.multiselect(
        "Filter by App",
        options=sorted(df["app_id"].dropna().unique().tolist()) if "app_id" in df.columns else [],
        key="reg_app_filter",
    )
    proj_filter = fc2.multiselect(
        "Filter by Project",
        options=sorted(df["project"].dropna().unique().tolist()) if "project" in df.columns else [],
        key="reg_proj_filter",
    )

    filtered = df.copy()
    if app_filter:
        filtered = filtered[filtered["app_id"].isin(app_filter)]
    if proj_filter:
        filtered = filtered[filtered["project"].isin(proj_filter)]

    # Display columns
    display_cols = [c for c in [
        "date_generated", "app_id", "artifact_id", "project",
        "report_type", "status", "source_file", "config_name",
    ] if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    # Lineage drill-down
    if not filtered.empty:
        with st.expander("🔍 Lineage — trace a specific output"):
            artifact_options = filtered["artifact_id"].dropna().tolist() if "artifact_id" in filtered.columns else []
            if artifact_options:
                sel_artifact = st.selectbox("Select artifact", artifact_options, key="reg_lineage_sel")
                row = filtered[filtered["artifact_id"] == sel_artifact].iloc[0] if not filtered.empty else None
                if row is not None:
                    st.markdown(f"**Artifact ID:** `{row.get('artifact_id', '—')}`")
                    st.markdown(f"**Generated:** {row.get('date_generated', '—')}")
                    st.markdown(f"**App:** {row.get('app_id', '—')}")
                    st.markdown(f"**Project:** {row.get('project', '—')}")
                    if row.get("source_file"):
                        st.markdown(f"**Source file:** `{row.get('source_file')}`")
                    if row.get("config_name"):
                        st.markdown(f"**Config used:** {row.get('config_name')} (v{row.get('config_version', '?')})")
                    if row.get("output_file"):
                        st.markdown(f"**Output file:** `{row.get('output_file')}`")
                        output_path = row.get("output_file", "")
                        if output_path and os.path.exists(output_path):
                            try:
                                with open(output_path, "rb") as f:
                                    st.download_button(
                                        "⬇ Re-download this output",
                                        f.read(),
                                        file_name=os.path.basename(output_path),
                                        use_container_width=True,
                                    )
                            except Exception:
                                st.caption("Output file no longer available for download.")
                        else:
                            st.caption("Output file path no longer exists on disk.")
