from __future__ import annotations

import argparse
import importlib
import os
import platform
import sys
from dataclasses import dataclass


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("PREFECT_HOME", "/tmp/prefect")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/.cache")
os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp/numba_cache")
os.environ.setdefault("JOBLIB_TEMP_FOLDER", "/tmp/joblib")


@dataclass(frozen=True)
class Dependency:
    package: str
    import_name: str
    group: str
    required_on_cloud: bool = True


DEPENDENCIES = [
    Dependency("streamlit", "streamlit", "core"),
    Dependency("pandas", "pandas", "core"),
    Dependency("numpy", "numpy", "core"),
    Dependency("scipy", "scipy", "stats"),
    Dependency("scikit-learn", "sklearn", "ml"),
    Dependency("statsmodels", "statsmodels", "stats"),
    Dependency("plotly", "plotly", "viz"),
    Dependency("folium", "folium", "viz"),
    Dependency("duckdb", "duckdb", "storage"),
    Dependency("pyarrow", "pyarrow", "storage"),
    Dependency("xgboost", "xgboost", "boosting"),
    Dependency("lightgbm", "lightgbm", "boosting"),
    Dependency("catboost", "catboost", "boosting"),
    Dependency("shap", "shap", "explainability"),
    Dependency("hmmlearn", "hmmlearn", "ml"),
    Dependency("geopandas", "geopandas", "geospatial"),
    Dependency("shapely", "shapely", "geospatial"),
    Dependency("pyproj", "pyproj", "geospatial"),
    Dependency("pyogrio", "pyogrio", "geospatial"),
    Dependency("rasterio", "rasterio", "geospatial"),
    Dependency("rioxarray", "rioxarray", "geospatial"),
    Dependency("xarray", "xarray", "geospatial"),
    Dependency("libpysal", "libpysal", "spatial-modeling"),
    Dependency("esda", "esda", "spatial-modeling"),
    Dependency("spreg", "spreg", "spatial-modeling"),
    Dependency("mapclassify", "mapclassify", "spatial-modeling"),
    Dependency("pykrige", "pykrige", "geostatistics"),
    Dependency("gstools", "gstools", "geostatistics"),
    Dependency("scikit-gstat", "skgstat", "geostatistics"),
    Dependency("beautifulsoup4", "bs4", "scraping"),
    Dependency("lxml", "lxml", "scraping"),
    Dependency("scrapy", "scrapy", "scraping"),
    Dependency("yfinance", "yfinance", "api"),
    Dependency("fredapi", "fredapi", "api"),
    Dependency("geopy", "geopy", "api"),
    Dependency("pycountry", "pycountry", "api"),
    Dependency("praw", "praw", "api"),
    Dependency("google-api-python-client", "googleapiclient", "api"),
    Dependency("prefect", "prefect", "ops"),
    Dependency("mlflow", "mlflow", "ops"),
    Dependency("great-expectations", "great_expectations", "quality"),
    Dependency("optuna", "optuna", "optimization"),
    Dependency("scikit-optimize", "skopt", "optimization"),
    Dependency("weasyprint", "weasyprint", "exports"),
    Dependency("openpyxl", "openpyxl", "exports"),
    Dependency("XlsxWriter", "xlsxwriter", "exports"),
    Dependency("kaleido", "kaleido", "exports"),
    Dependency("nbformat", "nbformat", "notebooks"),
    Dependency("nbconvert", "nbconvert", "notebooks"),
]


def _import_status(dep: Dependency) -> tuple[bool, str]:
    try:
        module = importlib.import_module(dep.import_name)
        version = getattr(module, "__version__", "ok")
        return True, str(version)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check runtime dependencies for the Streamlit portfolio app.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when a cloud dependency is missing.")
    args = parser.parse_args()

    failures: list[tuple[Dependency, str]] = []
    print(f"Python: {sys.version.split()[0]} | Platform: {platform.platform()}")
    print("Checking runtime imports...\n")
    for dep in DEPENDENCIES:
        ok, detail = _import_status(dep)
        marker = "OK" if ok else "FAIL"
        print(f"{marker:4} {dep.group:16} {dep.package:28} {detail}")
        if not ok and dep.required_on_cloud:
            failures.append((dep, detail))

    if failures:
        print("\nMissing or broken cloud dependencies:")
        for dep, detail in failures:
            print(f"- {dep.package} ({dep.import_name}): {detail}")
        if platform.system() == "Darwin":
            print("\nNote macOS: XGBoost/LightGBM may need `brew install libomp` locally.")
        print("For Streamlit Cloud, Python packages are declared in requirements.txt and apt packages in packages.txt.")
    else:
        print("\nAll declared runtime imports are available.")

    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
