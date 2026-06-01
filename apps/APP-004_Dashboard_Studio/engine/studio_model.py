"""Studio Model — unified job container for APP-004 Dashboard Studio."""
import dataclasses
from dataclasses import dataclass, field
from .viz_model import DashboardJob, KPIDef, ChartDef, TableDef


@dataclass
class DashboardStudioJob:
    workspace_slug:  str          = ""
    project_code:    str          = "PMU"
    source_filename: str          = ""
    artifact_id:     str          = ""
    layout_name:     str          = "Default Layout"
    dashboard_job:   DashboardJob = field(default_factory=DashboardJob)

    def to_config(self) -> dict:
        dj = self.dashboard_job
        return {
            "workspace_slug":  self.workspace_slug,
            "project_code":    self.project_code,
            "source_filename": self.source_filename,
            "artifact_id":     self.artifact_id,
            "layout_name":     self.layout_name,
            "dashboard_title": dj.dashboard_title,
            "kpis":            [dataclasses.asdict(k) for k in dj.kpis],
            "charts":          [dataclasses.asdict(c) for c in dj.charts],
            "tables":          [dataclasses.asdict(t) for t in dj.tables],
        }

    @classmethod
    def from_config(cls, data: dict) -> "DashboardStudioJob":
        job = cls(
            workspace_slug  = data.get("workspace_slug", ""),
            project_code    = data.get("project_code", "PMU"),
            source_filename = data.get("source_filename", ""),
            artifact_id     = data.get("artifact_id", ""),
            layout_name     = data.get("layout_name", "Default Layout"),
        )
        job.dashboard_job.dashboard_title = data.get("dashboard_title", "PMU Dashboard")
        for k in data.get("kpis",   []): job.dashboard_job.kpis.append(KPIDef(**k))
        for c in data.get("charts", []): job.dashboard_job.charts.append(ChartDef(**c))
        for t in data.get("tables", []): job.dashboard_job.tables.append(TableDef(**t))
        return job
