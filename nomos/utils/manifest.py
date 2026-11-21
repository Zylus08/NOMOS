"""
NOMOS Experiment Manifest & Telemetry Tracker
Agent H05
"""

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import platform
import time
from typing import Any, Dict, List, Optional
import psutil


@dataclass
class HardwareTelemetry:
    cpu_cores_physical: int
    cpu_cores_logical: int
    total_ram_gb: float
    platform_name: str
    python_version: str


@dataclass
class ExperimentManifest:
    manifest_id: str
    benchmark_name: str
    noise_level: float
    seed: int
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None
    telemetry: Optional[HardwareTelemetry] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    discovered_equations: Dict[str, str] = field(default_factory=dict)
    ground_truth_equations: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(cls, manifest_id: str, benchmark_name: str, noise_level: float, seed: int) -> "ExperimentManifest":
        tel = HardwareTelemetry(
            cpu_cores_physical=psutil.cpu_count(logical=False) or 1,
            cpu_cores_logical=psutil.cpu_count(logical=True) or 1,
            total_ram_gb=float(psutil.virtual_memory().total / (1024 ** 3)),
            platform_name=platform.platform(),
            python_version=platform.python_version(),
        )
        return cls(
            manifest_id=manifest_id,
            benchmark_name=benchmark_name,
            noise_level=noise_level,
            seed=seed,
            start_time=time.time(),
            telemetry=tel,
        )

    def finalize(self, metrics: Dict[str, Any], discovered: Dict[str, str], ground_truth: Dict[str, str]):
        self.end_time = time.time()
        self.duration_seconds = float(self.end_time - self.start_time)
        self.metrics = metrics
        self.discovered_equations = discovered
        self.ground_truth_equations = ground_truth

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
