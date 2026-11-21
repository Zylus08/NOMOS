"""
NOMOS Bounded Resource-Aware Parallel Execution Pool
Agent H06
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import os
import psutil
from typing import Callable, Iterable, List, Optional, Any


def get_safe_worker_limit(task_type: str = "cpu_heavy") -> int:
    """
    Calculate safe concurrency limit based on physical cores and 16 GB workstation memory.
    Caps thread oversubscription from BLAS/LAPACK.
    """
    physical_cores = psutil.cpu_count(logical=False) or 4
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024 ** 3)

    if task_type == "cpu_heavy":
        # Leave 2 cores free for OS & orchestrator, memory ceiling
        return max(1, min(physical_cores - 2, int(available_gb // 2)))
    elif task_type == "light":
        return max(2, min(physical_cores, 8))
    else:
        return 2


def run_bounded_parallel(func: Callable, tasks: Iterable[Any], max_workers: Optional[int] = None) -> List[Any]:
    """Execute batch of independent tasks within safe hardware limits."""
    if max_workers is None:
        max_workers = get_safe_worker_limit()

    # Enforce OpenMP/MKL thread limits on worker processes
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for res in executor.map(func, tasks):
            results.append(res)
    return results
