#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.streamlit_app.pid"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/streamlit.log"
PORT="${PORT:-8501}"
MODE="foreground"

if [[ "${1:-}" == "--background" ]]; then
  MODE="background"
fi

mkdir -p "$LOG_DIR"

if [[ "$MODE" == "background" ]]; then
  if [[ -f "$PID_FILE" ]]; then
    OLD_PID="$(cat "$PID_FILE" || true)"
    if [[ -n "${OLD_PID:-}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
      echo "Streamlit est déjà lancé (PID $OLD_PID)."
      echo "URL: http://localhost:$PORT"
      exit 0
    fi
    rm -f "$PID_FILE"
  fi
fi

cd "$ROOT_DIR"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

if command -v poetry >/dev/null 2>&1; then
  RUN_CMD=(poetry run streamlit run app/main.py --server.port="$PORT" --server.headless=true)
else
  RUN_CMD=(python -m streamlit run app/main.py --server.port="$PORT" --server.headless=true)
fi

# Ouvre automatiquement une nouvelle fenêtre Chrome (fallback navigateur par défaut).
(
  sleep 2
  open -na "Google Chrome" --args --new-window "http://localhost:$PORT" >/dev/null 2>&1 \
    || open "http://localhost:$PORT" >/dev/null 2>&1 \
    || true
) &

if [[ "$MODE" == "background" ]]; then
  nohup "${RUN_CMD[@]}" >"$LOG_FILE" 2>&1 &
  APP_PID=$!
  echo "$APP_PID" >"$PID_FILE"
  echo "Streamlit lancé en arrière-plan."
  echo "PID: $APP_PID"
  echo "URL: http://localhost:$PORT"
  echo "Logs: $LOG_FILE"
  exit 0
fi

echo "Streamlit lancé en mode normal (foreground)."
echo "URL: http://localhost:$PORT"
echo "Arrêt: Ctrl + C"
exec "${RUN_CMD[@]}"
