# Architecture

## Couches
- `simulation`: génération retail + finance avec scénarios réalistes.
- `storage`: persistance Parquet/CSV + DuckDB.
- `features`: KPIs, RFM/CLV proxy, spatial metrics, finance metrics.
- `modeling`: churn classification, revenue regression, forecasting.
- `app`: interface Streamlit avec menu vertical + tabs horizontaux.
- `pipelines`: orchestration batch avec Prefect fallback.

## Flux
1. Simulation paramétrable (`seed`, tailles, période).
2. Contrôles qualité.
3. Feature engineering.
4. Entraînement modèles.
5. Exposition interactive via Streamlit.
6. Export QR et reporting.
