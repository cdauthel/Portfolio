#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.streamlit_app.pid"
PORT="${PORT:-8501}"

stopped=0

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE" || true)"
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    sleep 1
    if kill -0 "$PID" 2>/dev/null; then
      kill -9 "$PID" 2>/dev/null || true
    fi
    echo "Processus Streamlit arrêté (PID $PID)."
    stopped=1
  fi
  rm -f "$PID_FILE"
fi

if command -v lsof >/dev/null 2>&1; then
  PIDS_ON_PORT="$(lsof -ti tcp:"$PORT" || true)"
  if [[ -n "${PIDS_ON_PORT:-}" ]]; then
    echo "$PIDS_ON_PORT" | xargs kill -9 2>/dev/null || true
    echo "Processus restants arrêtés sur le port $PORT."
    stopped=1
  fi
fi

if [[ "$stopped" -eq 0 ]]; then
  echo "Aucun processus Streamlit actif détecté."
fi
