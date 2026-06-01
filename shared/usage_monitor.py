"""
Usage Monitor — tracks Cloud Run request counts and shows billing alerts.
Compares usage against Google Cloud Run free tier limits.
"""
import json
import datetime
from pathlib import Path

_USAGE_FILE = Path(__file__).parent.parent / "config" / "usage.json"

# Cloud Run free tier (per month, per region, for the first 2 million requests)
FREE_TIER = {
    "requests":          2_000_000,   # per month
    "compute_gb_sec":    360_000,     # GB-seconds per month
    "vcpu_sec":          180_000,     # vCPU-seconds per month
}

# Estimated cost per unit beyond free tier (USD)
PRICE_PER = {
    "requests":          0.40 / 1_000_000,  # $0.40 per million
    "compute_gb_sec":    0.000016,
    "vcpu_sec":          0.000024,
}


def _load() -> dict:
    if _USAGE_FILE.exists():
        try:
            return json.loads(_USAGE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    _USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _USAGE_FILE.write_text(json.dumps(data, indent=2))


def _current_month() -> str:
    return datetime.datetime.now().strftime("%Y-%m")


def increment_request() -> None:
    """Call once per page load to track request count."""
    data  = _load()
    month = _current_month()
    if month not in data:
        data[month] = {"requests": 0, "last_updated": ""}
    data[month]["requests"] += 1
    data[month]["last_updated"] = datetime.datetime.now().isoformat()
    _save(data)


def get_current_usage() -> dict:
    """Return usage stats for the current month."""
    data  = _load()
    month = _current_month()
    month_data = data.get(month, {"requests": 0})
    requests   = month_data.get("requests", 0)

    req_pct  = round(requests / FREE_TIER["requests"] * 100, 1)
    req_remaining = FREE_TIER["requests"] - requests
    req_overage   = max(0, requests - FREE_TIER["requests"])
    est_cost_usd  = req_overage * PRICE_PER["requests"]

    return {
        "month":           month,
        "requests":        requests,
        "requests_limit":  FREE_TIER["requests"],
        "requests_pct":    req_pct,
        "requests_remaining": max(0, req_remaining),
        "in_free_tier":    requests <= FREE_TIER["requests"],
        "est_cost_usd":    round(est_cost_usd, 4),
        "alert_level":     _alert_level(req_pct),
    }


def _alert_level(pct: float) -> str:
    if pct >= 100:
        return "billing"   # beyond free tier — being billed
    if pct >= 80:
        return "warning"   # approaching limit
    if pct >= 50:
        return "info"      # halfway through
    return "ok"


def render_usage_banner() -> None:
    """Show a usage alert banner at the top of each page if approaching limits."""
    import streamlit as st

    try:
        increment_request()
        usage = get_current_usage()
        level = usage["alert_level"]

        if level == "billing":
            st.error(
                f"⚠️ **Free tier exhausted** — Cloud Run is now billing. "
                f"This month: **{usage['requests']:,} requests** "
                f"({usage['requests_pct']}% of {usage['requests_limit']:,} free). "
                f"Estimated extra charge: **${usage['est_cost_usd']:.4f} USD**. "
                "Go to [console.cloud.google.com/billing](https://console.cloud.google.com/billing) to review.",
                icon="🔴",
            )
        elif level == "warning":
            st.warning(
                f"⚠️ **Approaching free tier limit** — {usage['requests_pct']}% used this month "
                f"({usage['requests']:,} / {usage['requests_limit']:,} requests). "
                f"{usage['requests_remaining']:,} requests remaining before billing starts.",
                icon="🟡",
            )
    except Exception:
        pass  # Usage tracking should never crash the app


def render_usage_dashboard() -> None:
    """Full usage dashboard page."""
    import streamlit as st

    try:
        from .theme import page_header, kpi_row
        page_header("Usage & Billing Monitor",
                    subtitle="Cloud Run request tracking against Google free tier · refreshes on each page visit",
                    icon="📊")
    except Exception:
        st.markdown("# 📊 Usage & Billing Monitor")

    usage = get_current_usage()
    level = usage["alert_level"]

    status_map = {"billing": "red", "warning": "amber", "info": "blue", "ok": "green"}
    kpi_status = status_map.get(level, "green")

    try:
        from .theme import kpi_row
        kpi_row([
            {
                "label": "Requests This Month",
                "value": f"{usage['requests']:,}",
                "delta": f"{usage['requests_pct']}% of {usage['requests_limit']:,} free",
                "status": kpi_status,
                "icon": "📨",
            },
            {
                "label": "Remaining Free Requests",
                "value": f"{usage['requests_remaining']:,}" if usage["in_free_tier"] else "0",
                "delta": "Resets 1st of each month",
                "status": "slate",
                "icon": "🎯",
            },
            {
                "label": "Estimated Extra Charge",
                "value": f"${usage['est_cost_usd']:.4f}" if not usage["in_free_tier"] else "$0.00",
                "delta": "USD · beyond free tier only",
                "status": "red" if not usage["in_free_tier"] else "green",
                "icon": "💳",
            },
        ])
    except Exception:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Requests This Month", f"{usage['requests']:,}",
                      delta=f"{usage['requests_pct']}% of free tier")
        with col2:
            st.metric("Remaining Free",
                      f"{usage['requests_remaining']:,}" if usage["in_free_tier"] else "0")
        with col3:
            st.metric("Estimated Charge",
                      f"${usage['est_cost_usd']:.4f} USD" if not usage["in_free_tier"] else "$0.00 USD")

    # Progress bar
    st.markdown("---")
    st.markdown("### Free Tier Usage")
    pct = min(usage["requests_pct"], 100)
    bar_color = "red" if level == "billing" else ("orange" if level == "warning" else "green")
    st.progress(pct / 100, text=f"Cloud Run Requests: {pct}% of free tier used")

    # Free tier reference
    with st.expander("📋 Google Cloud Run Free Tier Limits (per month, per region)"):
        st.markdown("""
| Resource | Free Tier Limit | Price After |
|---|---|---|
| **Requests** | 2,000,000 requests | $0.40 per million |
| **Compute** | 360,000 GB-seconds | $0.000016 per GB-second |
| **vCPU** | 180,000 vCPU-seconds | $0.000024 per vCPU-second |
| **Networking** | 1 GB outbound | $0.12 per GB |

With 4 concurrent users and typical PMU workloads (10–50 requests/session, 3–5 sessions/day),
expected monthly usage is approximately **6,000–15,000 requests** — well within the 2 million free tier.
        """)

    # Historical usage
    data = _load()
    if len(data) > 1:
        st.markdown("---")
        st.markdown("### Historical Usage")
        hist = []
        for month, v in sorted(data.items()):
            hist.append({"Month": month, "Requests": v.get("requests", 0)})
        import pandas as pd
        hist_df = pd.DataFrame(hist)
        st.bar_chart(hist_df.set_index("Month"))

    # Links
    st.markdown("---")
    st.markdown("### Billing Management")
    st.markdown("""
- 🔗 [Cloud Run Console](https://console.cloud.google.com/run) — view running services and metrics
- 🔗 [Billing Dashboard](https://console.cloud.google.com/billing) — view current charges
- 🔗 [Set Budget Alerts](https://console.cloud.google.com/billing/budgets) — get email when charges exceed a threshold
    """)
    st.info("**Tip:** Set a billing budget alert at $1 USD in the GCP Billing console. You will receive an email before any significant charge accumulates.")
