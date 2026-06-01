"""Studio Model — unified job container for APP-006 Workflow Builder."""
import dataclasses
from dataclasses import dataclass, field
from .workflow_model import WorkflowJob, StageDef, TrackingEntry


@dataclass
class WorkflowStudioJob:
    workspace_slug: str         = ""
    workflow_job:   WorkflowJob = field(default_factory=WorkflowJob)

    def to_config(self) -> dict:
        wj = self.workflow_job
        return {
            "workspace_slug":  self.workspace_slug,
            "project_code":    wj.project_code,
            "workflow_name":   wj.workflow_name,
            "entity_type":     wj.entity_type,
            "entities":        wj.entities,
            "stages":          [dataclasses.asdict(s) for s in wj.stages],
            "tracking":        [dataclasses.asdict(t) for t in wj.tracking],
        }

    @classmethod
    def from_config(cls, data: dict) -> "WorkflowStudioJob":
        job = cls(workspace_slug=data.get("workspace_slug", ""))
        wj  = job.workflow_job
        wj.project_code  = data.get("project_code", "PMU")
        wj.workflow_name = data.get("workflow_name", "Workflow")
        wj.entity_type   = data.get("entity_type", "District")
        wj.entities      = data.get("entities", [])
        for s in data.get("stages",   []): wj.stages.append(StageDef(**s))
        for t in data.get("tracking", []): wj.tracking.append(TrackingEntry(**t))
        return job
