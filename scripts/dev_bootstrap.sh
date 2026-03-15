#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
SEED_DEMO="${SEED_DEMO:-1}"

log() {
  echo "[dev_bootstrap] $*"
}

warn() {
  echo "[dev_bootstrap][warn] $*" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    warn "missing command: $1"
    return 1
  fi
}

if ! require_cmd "$PYTHON_BIN"; then
  warn "请先安装 Python，或通过 PYTHON_BIN 指定解释器路径。"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  log "creating virtualenv at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log "upgrading pip"
if ! python -m pip install --upgrade pip; then
  warn "pip 升级失败，请检查网络/代理配置后重试。"
  exit 1
fi

log "installing project dependencies"
if ! pip install -e .[dev]; then
  warn "依赖安装失败，请检查网络、代理或 Python 版本兼容性。"
  warn "可先尝试：pip config list && env | grep -i proxy"
  exit 1
fi

if [ "$SEED_DEMO" = "1" ]; then
  if ! require_cmd curl; then
    warn "SEED_DEMO=1 需要 curl，请安装后重试，或设置 SEED_DEMO=0 跳过注入。"
    exit 1
  fi

  if ! command -v uvicorn >/dev/null 2>&1; then
    warn "未找到 uvicorn，可执行文件应位于虚拟环境。"
    warn "请确认依赖安装成功，或运行：python -m uvicorn app.main:app --host $HOST --port $PORT"
    exit 1
  fi

  log "starting temporary app server for demo bootstrap"
  uvicorn app.main:app --host "$HOST" --port "$PORT" >/tmp/trademanager_uvicorn.log 2>&1 &
  SERVER_PID=$!
  cleanup() {
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  }
  trap cleanup EXIT

  # wait app startup
  STARTED=0
  for _ in $(seq 1 30); do
    if curl -sf "http://$HOST:$PORT/health" >/dev/null; then
      STARTED=1
      break
    fi
    sleep 0.5
  done

  if [ "$STARTED" -ne 1 ]; then
    warn "应用启动超时，日志见 /tmp/trademanager_uvicorn.log"
    exit 1
  fi

  log "calling /demo/bootstrap"
  if ! curl -sf -X POST "http://$HOST:$PORT/demo/bootstrap" >/dev/null; then
    warn "调用 /demo/bootstrap 失败，日志见 /tmp/trademanager_uvicorn.log"
    exit 1
  fi

  kill "$SERVER_PID" >/dev/null 2>&1 || true
  trap - EXIT
fi

log "Bootstrap completed."
echo "Run app: source $VENV_DIR/bin/activate && uvicorn app.main:app --host $HOST --port $PORT --reload"
