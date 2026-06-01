"""
Studio Model — unified job container for Data Processing Studio.
Serializes/deserializes the complete pipeline config for workspace save/load.
"""
import dataclasses
from .transform_model import TransformStep, TransformJob
from .rule_model import Rule, RuleJob
from .mapping_model import ColumnMapping, MappingJob


@dataclasses.dataclass
class ProcessingJob:
    """Unified configuration for one Data Processing Studio session."""
    workspace_slug: str = ""
    project_code:   str = "PMU"
    source_filename: str = ""
    artifact_id:    str = ""
    transform_job:  TransformJob  = dataclasses.field(default_factory=TransformJob)
    rule_job:       RuleJob       = dataclasses.field(default_factory=RuleJob)
    mapping_job:    MappingJob    = dataclasses.field(default_factory=MappingJob)

    def to_config(self) -> dict:
        """Serialize to a JSON-safe dict for config_manager.save_config()."""
        return {
            "workspace_slug":  self.workspace_slug,
            "project_code":    self.project_code,
            "source_filename": self.source_filename,
            "artifact_id":     self.artifact_id,
            "transform_steps": [dataclasses.asdict(s) for s in self.transform_job.steps],
            "rules":           [dataclasses.asdict(r) for r in self.rule_job.rules],
            "column_mappings": [dataclasses.asdict(m) for m in self.mapping_job.column_mappings],
        }

    @classmethod
    def from_config(cls, data: dict) -> "ProcessingJob":
        """Reconstruct from a dict loaded by config_manager.load_config()."""
        job = cls(
            workspace_slug  = data.get("workspace_slug", ""),
            project_code    = data.get("project_code", "PMU"),
            source_filename = data.get("source_filename", ""),
            artifact_id     = data.get("artifact_id", ""),
        )
        for s in data.get("transform_steps", []):
            job.transform_job.steps.append(TransformStep(**s))
        for r in data.get("rules", []):
            job.rule_job.rules.append(Rule(**r))
        for m in data.get("column_mappings", []):
            job.mapping_job.column_mappings.append(ColumnMapping(**m))
        return job
