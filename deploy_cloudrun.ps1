# PMU Tools — Cloud Run Deployment Script (PowerShell)
# Deploys the 6 studio apps to Google Cloud Run.
#
# Prerequisites:
#   1. Google Cloud SDK installed (cloud.google.com/sdk)
#   2. Run once: gcloud auth login
#   3. Run once: gcloud auth configure-docker
#
# Usage — deploy all 6 apps:
#   .\deploy_cloudrun.ps1 -Project "your-gcp-project-id"
#
# Usage — deploy a single app after a change:
#   .\deploy_cloudrun.ps1 -Project "your-gcp-project-id" -App "APP-003_Analytics_Studio"

param(
    [Parameter(Mandatory=$true)]
    [string]$Project,

    [string]$Region = "asia-south1",

    # Leave empty to deploy all 6 apps
    [string]$App = ""
)

$IMAGE = "gcr.io/$Project/pmu-studio-suite"

$APPS = @(
    @{ Name = "APP-001_Monitoring_Builder";     Service = "pmu-001-monitoring-builder"      },
    @{ Name = "APP-002_Data_Processing_Studio"; Service = "pmu-002-data-processing-studio"  },
    @{ Name = "APP-003_Analytics_Studio";       Service = "pmu-003-analytics-studio"        },
    @{ Name = "APP-004_Dashboard_Studio";       Service = "pmu-004-dashboard-studio"        },
    @{ Name = "APP-005_Deliverable_Studio";     Service = "pmu-005-deliverable-studio"      },
    @{ Name = "APP-006_Workflow_Builder";       Service = "pmu-006-workflow-builder"        }
)

# Filter to single app if -App is specified
if ($App) {
    $APPS = $APPS | Where-Object { $_.Name -eq $App }
    if (-not $APPS) {
        Write-Error "App '$App' not recognised. Valid names:`n$($APPS.Name -join "`n")"
        exit 1
    }
}

# ── Step 1: Build image on Cloud Build ───────────────────────────────────────
Write-Host "`n[1/2] Building Docker image on Cloud Build: $IMAGE" -ForegroundColor Cyan
gcloud builds submit --tag $IMAGE --project $Project
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed. Check Cloud Build logs."; exit 1 }
Write-Host "Image built." -ForegroundColor Green

# ── Step 2: Deploy each studio as a separate Cloud Run service ────────────────
Write-Host "`n[2/2] Deploying $($APPS.Count) studio(s) to Cloud Run ($Region)..." -ForegroundColor Cyan

foreach ($entry in $APPS) {
    Write-Host "`n  Deploying $($entry.Name)..." -ForegroundColor Yellow

    gcloud run deploy $entry.Service `
        --image $IMAGE `
        --region $Region `
        --set-env-vars "APP_NAME=$($entry.Name)" `
        --port 8080 `
        --memory 2Gi `
        --cpu 1 `
        --min-instances 1 `
        --max-instances 3 `
        --allow-unauthenticated `
        --project $Project

    if ($LASTEXITCODE -ne 0) {
        Write-Warning "  $($entry.Name) failed. Check Cloud Run logs."
    } else {
        Write-Host "  $($entry.Name) deployed." -ForegroundColor Green
    }
}

# ── Print live URLs ───────────────────────────────────────────────────────────
Write-Host "`nLive URLs:" -ForegroundColor Cyan
foreach ($entry in $APPS) {
    $url = gcloud run services describe $entry.Service `
        --region $Region --project $Project `
        --format "value(status.url)" 2>$null
    Write-Host "  $($entry.Name)`n    $url"
}

Write-Host "`nAll done." -ForegroundColor Green
