from sip_bench.adapters.base import BenchmarkAdapter, SplitManifest, TaskDescriptor
from sip_bench.adapters.skillsbench import SkillsBenchAdapter
from sip_bench.adapters.mock_bench import MockBenchAdapter
from sip_bench.adapters.tau_bench import TauBenchAdapter
try:
    from sip_bench.adapters.evoagentbench import EvoAgentBenchAdapter
except ModuleNotFoundError as exc:
    if exc.name != "sip_bench.adapters.evoagentbench":
        raise
    EvoAgentBenchAdapter = None  # type: ignore[assignment]
    EVOAGENTBENCH_AVAILABLE = False
else:
    EVOAGENTBENCH_AVAILABLE = True
from sip_bench.adapters.medical import MedicalAdapter


def require_evoagentbench_adapter():
    """Return the optional adapter or raise an actionable installation error."""
    if EvoAgentBenchAdapter is None:
        raise RuntimeError(
            "EvoAgentBench support is not installed in this SIP-Bench release. "
            "Install the optional adapter package before using evoagentbench suites."
        )
    return EvoAgentBenchAdapter

__all__ = [
    "BenchmarkAdapter",
    "SplitManifest",
    "TaskDescriptor",
    "MockBenchAdapter",
    "SkillsBenchAdapter",
    "TauBenchAdapter",
    "MedicalAdapter",
    "EVOAGENTBENCH_AVAILABLE",
    "require_evoagentbench_adapter",
]
