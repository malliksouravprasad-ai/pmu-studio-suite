"""BigQuery connector for PMU Tool Suite — authenticates from st.secrets."""
import pandas as pd


def bq_available() -> bool:
    """True if BigQuery credentials are configured in st.secrets."""
    try:
        import streamlit as st
        return "gcp_service_account" in st.secrets and "bigquery" in st.secrets
    except Exception:
        return False


def _get_client():
    import streamlit as st
    from google.oauth2 import service_account
    from google.cloud import bigquery

    creds = service_account.Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    project = st.secrets["bigquery"]["project_id"]
    return bigquery.Client(credentials=creds, project=project)


def bq_connection_info() -> dict:
    """Return {connected, project, error}."""
    try:
        if not bq_available():
            return {"connected": False, "project": None, "error": "Not configured in secrets.toml"}
        import streamlit as st
        client = _get_client()
        list(client.list_datasets(max_results=1))
        return {"connected": True, "project": st.secrets["bigquery"]["project_id"], "error": None}
    except Exception as exc:
        return {"connected": False, "project": None, "error": str(exc)}


def bq_list_datasets() -> list:
    """List all dataset IDs in the configured GCP project."""
    return [d.dataset_id for d in _get_client().list_datasets()]


def bq_list_tables(dataset_id: str) -> list:
    """List all table IDs in a dataset."""
    import streamlit as st
    project = st.secrets["bigquery"]["project_id"]
    return [t.table_id for t in _get_client().list_tables(f"{project}.{dataset_id}")]


def bq_table_to_df(dataset_id: str, table_id: str, limit: int = None) -> pd.DataFrame:
    """Load a BigQuery table into a DataFrame (optionally row-limited)."""
    import streamlit as st
    project = st.secrets["bigquery"]["project_id"]
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
    Server-side GROUP BY aggregation — no data transferred to Streamlit until aggregated.
    metrics = {column_name: 'SUM' | 'AVG' | 'COUNT' | 'MIN' | 'MAX'}
    """
    import streamlit as st
    project = st.secrets["bigquery"]["project_id"]
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
    import streamlit as st
    from google.cloud import bigquery as bq

    project = st.secrets["bigquery"]["project_id"]
    client  = _get_client()
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
