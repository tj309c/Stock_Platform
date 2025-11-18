#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR"

STREAMLIT_PORT=${STREAMLIT_PORT:-8501}
SETTINGS_SERVER_PORT=${SETTINGS_SERVER_PORT:-5001}

# Default to local project venv python if present
if [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
elif [ -x "$ROOT/venv/bin/python" ]; then
  PY="$ROOT/venv/bin/python"
else
  PY="python3"
fi

WITH_REDIS=0
CLEAN_CACHE=0

usage() {
  echo "Usage: $0 [--with-redis] [--clean-cache]"
  echo "  --with-redis  Start a local redis container (docker must be installed)"
  echo "  --clean-cache  Clears local caches before starting"
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --with-redis)
      WITH_REDIS=1
      shift
      ;;
    --clean-cache)
      CLEAN_CACHE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      exit 1
      ;;
  esac
done

if [ "$CLEAN_CACHE" -eq 1 ]; then
  echo "Clearing caches..."
  "$PY" -c "from src.core.cache_manager import CacheManager; CacheManager.clear_all_cache(); print('Caches cleared')"
fi

if [ "$WITH_REDIS" -eq 1 ]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required to start Redis via --with-redis. Please install Docker or run Redis separately."
  else
    # start a redis container if not already running
    if [ -z "$(docker ps -q -f name=stockplatform_redis)" ]; then
      echo "Starting Redis container..."
      docker run -d --name stockplatform_redis -p 6379:6379 redis:7 || echo "Redis container may already be running"
    else
      echo "Redis container already running."
    fi
  fi
fi

echo "Starting Streamlit (port $STREAMLIT_PORT)..."
nohup "$PY" -m streamlit run main.py --server.port $STREAMLIT_PORT > "$LOG_DIR/streamlit.log" 2>&1 &
STREAMLIT_PID=$!
sleep 1
echo "Streamlit started (PID: $STREAMLIT_PID). Logs: $LOG_DIR/streamlit.log"

echo "Starting Settings Server (port $SETTINGS_SERVER_PORT)..."
nohup "$PY" -m src.server.settings_server > "$LOG_DIR/settings_server.log" 2>&1 &
SERVER_PID=$!
sleep 1
echo "Server started (PID: $SERVER_PID). Logs: $LOG_DIR/settings_server.log"

echo "Starting LLM worker (background)..."
nohup "$PY" scripts/run_llm_worker.py > "$LOG_DIR/llm_worker.log" 2>&1 &
WORKER_PID=$!
sleep 1
echo "LLM worker started (PID: $WORKER_PID). Logs: $LOG_DIR/llm_worker.log"

echo "Dev environment started. Use 'tail -f $LOG_DIR/*.log' to follow logs or 'ps aux | grep python' to find processes."

exit 0
