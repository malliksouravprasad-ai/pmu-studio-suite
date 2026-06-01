"""
Studio Model — unified job container for APP-003 Analytics Studio.
Serializes/deserializes the complete analysis config for workspace save/load.
"""
import dataclasses
from dataclasses import dataclass, field
from typing import List

from .agg_model import AggJob, AggConfig, MetricDef
from .analytics_model import AnalyticsJob, RankDef, VarianceDef, TrendDef
from .kpi_engine import KPIDef


@dataclass
class AnalyticsStudioJob:
    """Unified configuration for one Analytics Studio session."""
    workspace_slug:  str          = ""
    project_code:    str          = "PMU"
    source_filename: str          = ""
    artifact_id:     str          = ""
    agg_job:         AggJob       = field(default_factory=AggJob)
    kpi_defs:        List[KPIDef] = field(default_factory=list)
    analytics_job:   AnalyticsJob = field(default_factory=AnalyticsJob)

    def to_config(self) -> dict:
        """Serialize to a JSON-safe dict for config_manager.save_config()."""
        agg_configs_raw = []
        for cfg in self.agg_job.configs:
            d = dataclasses.asdict(cfg)
            agg_configs_raw.append(d)

        return {
            "workspace_slug":  self.workspace_slug,
            "project_code":    self.project_code,
            "source_filename": self.source_filename,
            "artifact_id":     self.artifact_id,
            "agg_configs":     agg_configs_raw,
            "kpi_defs":        [dataclasses.asdict(k) for k in self.kpi_defs],
            "rankings":        [dataclasses.asdict(r) for r in self.analytics_job.rankings],
            "variances":       [dataclasses.asdict(v) for v in self.analytics_job.variances],
            "trends":          [dataclasses.asdict(t) for t in self.analytics_job.trends],
        }

    @classmethod
    def from_config(cls, data: dict) -> "AnalyticsStudioJob":
        """Reconstruct from a saved config dict."""
        job = cls(
            workspace_slug  = data.get("workspace_slug", ""),
            project_code    = data.get("project_code", "PMU"),
            source_filename = data.get("source_filename", ""),
            artifact_id     = data.get("artifact_id", ""),
        )
        for c in data.get("agg_configs", []):
            metrics_raw = c.pop("metrics", [])
            agg_cfg = AggConfig(**c)
            for m in metrics_raw:
                agg_cfg.metrics.append(MetricDef(**m))
            job.agg_job.configs.append(agg_cfg)
        for k in data.get("kpi_defs", []):
            job.kpi_defs.append(KPIDef(**k))
        for r in data.get("rankings", []):
            job.analytics_job.rankings.append(RankDef(**r))
        for v in data.get("variances", []):
            job.analytics_job.variances.append(VarianceDef(**v))
        for t in data.get("trends", []):
            job.analytics_job.trends.append(TrendDef(**t))
        return job
