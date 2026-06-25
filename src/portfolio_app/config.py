from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SimulationConfig:
    seed: int = 42
    n_stores: int = 120
    n_customers: int = 20000
    n_products: int = 3000
    n_orders: int = 120000
    n_assets: int = 20
    start_date: str = "2022-01-01"
    end_date: str = "2024-12-31"


@dataclass(frozen=True)
class AppPaths:
    root: Path = Path(".")
    data_dir: Path = Path("data/processed")
    docs_dir: Path = Path("docs")
    qr_dir: Path = Path("docs/assets")


DEFAULT_SIM_CONFIG = SimulationConfig()
DEFAULT_PATHS = AppPaths()
