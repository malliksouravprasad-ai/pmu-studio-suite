"""Studio Model — unified job container for APP-005 Deliverable Studio."""
import dataclasses
from dataclasses import dataclass, field
from .deliverable_model import ReportConfig, SectionDef


@dataclass
class DeliverableStudioJob:
    workspace_slug:  str          = ""
    source_filename: str          = ""
    report_config:   ReportConfig = field(default_factory=ReportConfig)

    def to_config(self) -> dict:
        rc = self.report_config
        return {
            "workspace_slug":  self.workspace_slug,
            "source_filename": self.source_filename,
            "project_code":    rc.project_code,
            "report_title":    rc.report_title,
            "programme":       rc.programme,
            "organization":    rc.organization,
            "author":          rc.author,
            "report_date":     rc.report_date,
            "description":     rc.description,
            "selected_formats": rc.selected_formats,
            "sections":        [dataclasses.asdict(s) for s in rc.sections],
        }

    @classmethod
    def from_config(cls, data: dict) -> "DeliverableStudioJob":
        job = cls(
            workspace_slug  = data.get("workspace_slug", ""),
            source_filename = data.get("source_filename", ""),
        )
        rc = job.report_config
        rc.project_code    = data.get("project_code", "PMU")
        rc.report_title    = data.get("report_title", "Programme Report")
        rc.programme       = data.get("programme", "")
        rc.organization    = data.get("organization", "OSEPA")
        rc.author          = data.get("author", "")
        rc.report_date     = data.get("report_date", "")
        rc.description     = data.get("description", "")
        rc.selected_formats = data.get("selected_formats", ["excel"])
        for s in data.get("sections", []):
            rc.sections.append(SectionDef(**s))
        return job
