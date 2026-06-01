"""Studio Model — serialization for APP-001 Monitoring Builder."""
import dataclasses
from dataclasses import dataclass, field
from .monitoring_model import MonitoringJob, FieldDef, FormDef, FormSection


@dataclass
class MonitoringStudioJob:
    """Thin wrapper that adds workspace metadata and handles config save/load."""
    workspace_slug: str          = ""
    job:            MonitoringJob = field(default_factory=MonitoringJob)

    def to_config(self) -> dict:
        j = self.job
        return {
            "workspace_slug":  self.workspace_slug,
            "project_code":    j.project_code,
            "monitoring_name": j.monitoring_name,
            "entity_type":     j.entity_type,
            "entity_field":    j.entity_field,
            "fields":          [dataclasses.asdict(f) for f in j.fields],
            "form_def": {
                "title":       j.form_def.title,
                "description": j.form_def.description,
                "sections":    [dataclasses.asdict(s) for s in j.form_def.sections],
            },
            "rule_defs":       j.rule_defs,
            "kpi_defs":        j.kpi_defs,
            "agg_defs":        j.agg_defs,
        }

    @classmethod
    def from_config(cls, data: dict) -> "MonitoringStudioJob":
        ms = cls(workspace_slug=data.get("workspace_slug", ""))
        j  = ms.job
        j.project_code    = data.get("project_code", "PMU")
        j.monitoring_name = data.get("monitoring_name", "Monitoring Framework")
        j.entity_type     = data.get("entity_type", "School")
        j.entity_field    = data.get("entity_field", "")

        for f in data.get("fields", []):
            j.fields.append(FieldDef(**f))

        fd = data.get("form_def", {})
        j.form_def.title       = fd.get("title", "Data Collection Form")
        j.form_def.description = fd.get("description", "")
        for s in fd.get("sections", []):
            j.form_def.sections.append(FormSection(**s))

        j.rule_defs = data.get("rule_defs", [])
        j.kpi_defs  = data.get("kpi_defs", [])
        j.agg_defs  = data.get("agg_defs", [])
        return ms
