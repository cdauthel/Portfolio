from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Prioritize local source code (src/) over potentially stale installed packages.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from portfolio_app.storage import build_duckdb, ensure_data_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate simulated portfolio datasets.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-stores", type=int, default=120)
    parser.add_argument("--n-customers", type=int, default=20000)
    parser.add_argument("--n-products", type=int, default=3000)
    parser.add_argument("--n-orders", type=int, default=120000)
    parser.add_argument("--n-assets", type=int, default=20)
    parser.add_argument(
        "--missing-rate",
        type=float,
        default=0.0,
        help="Taux de valeurs manquantes entre 0.0 et 0.4 (ex: 0.03 pour 3%%).",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--data-dir", type=str, default="data/processed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sim_kwargs = {
        "seed": args.seed,
        "n_stores": args.n_stores,
        "n_customers": args.n_customers,
        "n_products": args.n_products,
        "n_orders": args.n_orders,
        "n_assets": args.n_assets,
        "missing_rate": args.missing_rate,
        "start_date": "2022-01-01",
        "end_date": "2024-12-31",
    }
    data_dir = ensure_data_bundle(args.data_dir, force=args.force, sim_kwargs=sim_kwargs)
    db_path = build_duckdb(data_dir)
    print(f"Data bundle ready in: {data_dir}")
    print(f"DuckDB file: {db_path}")


if __name__ == "__main__":
    main()
