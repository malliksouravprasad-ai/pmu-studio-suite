"""BigQuery connector — credentials from UI (credentials_manager) or st.secrets fallback."""
import pandas as pd


def _get_sa_and_project() -> tuple[dict, str] | tuple[None, None]:
    """
    Return (service_account_dict, project_id) from the best available source.
    Priority: UI-saved → st.secrets → None
    """
    # Priority 1 — UI-saved via Integrations page
    try:
        from .credentials_manager import get_google_sa, get_bigquery_config
        sa = get_google_sa()
        bq = get_bigquery_config()
        if sa and bq and bq.get("project_id"):
            return sa, bq["project_id"]
    except Exception:
        pass

    # Priority 2 — st.secrets / secrets.toml
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets and "bigquery" in st.secrets:
            return dict(st.secrets["gcp_service_account"]), st.secrets["bigquery"]["project_id"]
    except Exception:
        pass

    return None, None


def bq_available() -> bool:
    """True if BigQuery credentials are available from any source."""
    sa, project = _get_sa_and_project()
    return sa is not None and bool(project)


def _get_client():
    from google.oauth2 import service_account
    from google.cloud import bigquery

    sa, project = _get_sa_and_project()
    if not sa:
        raise RuntimeError("BigQuery credentials not configured. Go to Integrations to set up.")
    creds = service_account.Credentials.from_service_account_info(
        sa, scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    return bigquery.Client(credentials=creds, project=project)


def _get_project() -> str:
    _, project = _get_sa_and_project()
    return project or ""


def bq_connection_info() -> dict:
    """Return {connected, project, error}."""
    try:
        if not bq_available():
            return {"connected": False, "project": None, "error": "Not configured. Use Integrations page to set up BigQuery."}
        client = _get_client()
        list(client.list_datasets(max_results=1))
        return {"connected": True, "project": _get_project(), "error": None}
    except Exception as exc:
        return {"connected": False, "project": None, "error": str(exc)}


def bq_list_datasets() -> list:
    """List all dataset IDs in the configured GCP project."""
    return [d.dataset_id for d in _get_client().list_datasets()]


def bq_list_tables(dataset_id: str) -> list:
    """List all table IDs in a dataset."""
    project = _get_project()
    return [t.table_id for t in _get_client().list_tables(f"{project}.{dataset_id}")]


def bq_table_to_df(dataset_id: str, table_id: str, limit: int = None) -> pd.DataFrame:
    """Load a BigQuery table into a DataFrame (optionally row-limited)."""
    project = _get_project()
    sql = f"SELECT * FROM `{project}.{dataset_id}.{table_id}`"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return _get_client().query(sql).to_dataframe()


def bq_query(sql: str) -> pd.DataFrame:
    """Run arbitrary BigQuery SQL and return results as a DataFrame."""
    return _get_client().query(sql).to_dataframe()


def bq_aggregate(
    dataset_id: str,
    table_id: str,
    group_cols: list,
    metrics: dict,
) -> pd.DataFrame:
    """
    Server-side GROUP BY aggregation — no raw data transferred to Streamlit.
    metrics = {column_name: 'SUM' | 'AVG' | 'COUNT' | 'MIN' | 'MAX'}
    """
    project     = _get_project()
    agg_exprs   = ", ".join(f"{func}(`{col}`) AS `{col}_{func}`" for col, func in metrics.items())
    group_exprs = ", ".join(f"`{c}`" for c in group_cols)
    sql = (
        f"SELECT {group_exprs}, {agg_exprs} "
        f"FROM `{project}.{dataset_id}.{table_id}` "
        f"GROUP BY {group_exprs} ORDER BY {group_exprs}"
    )
    return bq_query(sql)


def bq_push_df(
    df: pd.DataFrame,
    dataset_id: str,
    table_id: str,
    mode: str = "append",
) -> None:
    """Write a DataFrame to BigQuery. mode: 'append' or 'replace'."""
    from google.cloud import bigquery as bq

    project     = _get_project()
    client      = _get_client()
    disposition = (
        bq.WriteDisposition.WRITE_APPEND
        if mode == "append"
        else bq.WriteDisposition.WRITE_TRUNCATE
    )
    job_config = bq.LoadJobConfig(write_disposition=disposition)
    job = client.load_table_from_dataframe(
        df, f"{project}.{dataset_id}.{table_id}", job_config=job_config
    )
    job.result()
