# PMU Tools — Cloud Run Dockerfile
# One image, 6 studio apps. APP_NAME env var selects which app runs.
# Default: APP-001_Monitoring_Builder

FROM python:3.11-slim

ENV APP_NAME=APP-001_Monitoring_Builder

WORKDIR /pmu

# System libraries for PDF generation and font rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install all Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Shared utilities — used by all 6 apps via sys.path
COPY shared/ ./shared/

# The 6 studio apps
COPY apps/APP-001_Monitoring_Builder/    ./apps/APP-001_Monitoring_Builder/
COPY apps/APP-002_Data_Processing_Studio/ ./apps/APP-002_Data_Processing_Studio/
COPY apps/APP-003_Analytics_Studio/     ./apps/APP-003_Analytics_Studio/
COPY apps/APP-004_Dashboard_Studio/     ./apps/APP-004_Dashboard_Studio/
COPY apps/APP-005_Deliverable_Studio/   ./apps/APP-005_Deliverable_Studio/
COPY apps/APP-006_Workflow_Builder/     ./apps/APP-006_Workflow_Builder/

# Report templates
COPY templates/ ./templates/

# Streamlit secrets — credentials for Google, BigQuery, Apps Script
COPY .streamlit/ ./.streamlit/

# Runtime directories (ephemeral) + config dir for UI-saved credentials
RUN mkdir -p workspaces outputs inputs config

EXPOSE 8080

# APP_NAME is set at deploy time via --set-env-vars
CMD streamlit run apps/${APP_NAME}/app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.fileWatcherType=none \
    --server.enableXsrfProtection=false
