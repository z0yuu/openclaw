#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash skills/sra-ego-parquet-totxt/scripts/read_parquet_local.sh \
    --hdfs-path <hdfs://R2/...|hdfs://D2/...> \
    [--rows 10] \
    [--pipe-cmd "| python converter.py"] \
    [--script-path /path/to/converter.py_or_dir] \
    [--output-file /tmp/sra-ego-parquet-totxt-xxxx/sample_output.txt] \
    [--request-text "解析 hdfs://R2/xxx 前20条并用 python converter.py 转换"] \
    [--docker-bin "sudo docker"]

Arguments:
  --hdfs-path    Required. Must start with hdfs:// and use R2 or D2 namespace.
  --rows         Optional. Positive integer. Default: 10.
  --pipe-cmd     Optional. Pipeline fragment after reader, e.g. "| python converter.py".
  --script-path  Optional. Path to converter .py file or a script directory.
                 - If file: mount its parent directory and default to file-only usage.
                 - If directory: mount whole directory (recommended when dependencies exist).
  --output-file  Optional. Save parsed output to this file path.
                 If omitted, a temp file under /tmp is auto-generated.
  --request-text Optional. Natural language input. Used to auto-extract hdfs/rows/pipe/script
                 when explicit arguments are missing.
  --docker-bin   Optional. Docker launcher command. Default: "sudo docker".

Examples:
  bash skills/sra-ego-parquet-totxt/scripts/read_parquet_local.sh \
    --hdfs-path "hdfs://R2/XXX/parquet_file"

  bash skills/sra-ego-parquet-totxt/scripts/read_parquet_local.sh \
    --hdfs-path "hdfs://D2/YYY/parquet_file" \
    --pipe-cmd "| python converter.py" \
    --script-path "/home/me/converter"
USAGE
}

err() {
  echo "[sra-ego-parquet-totxt] $*" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "missing command: $1"
    exit 1
  fi
}

trim_leading_pipe() {
  local value="$1"
  value="${value#${value%%[![:space:]]*}}"
  if [[ "${value}" == \|* ]]; then
    value="${value#|}"
    value="${value#${value%%[![:space:]]*}}"
  fi
  printf '%s' "$value"
}

validate_positive_int() {
  local v="$1"
  [[ "$v" =~ ^[0-9]+$ ]] && [[ "$v" -gt 0 ]]
}

extract_from_request_text() {
  local text="$1"

  if [[ -z "$HDFS_PATH" ]]; then
    local extracted_hdfs
    extracted_hdfs="$(printf '%s' "$text" | grep -Eo 'hdfs://[^[:space:]|]+' | head -n 1 || true)"
    if [[ -n "$extracted_hdfs" ]]; then
      HDFS_PATH="$extracted_hdfs"
      err "auto-extracted hdfs path from request text: $HDFS_PATH"
    fi
  fi

  if [[ "$ROWS" == "10" ]] && [[ "$text" =~ ([0-9]+)[[:space:]]*(条|行) ]]; then
    ROWS="${BASH_REMATCH[1]}"
    err "auto-extracted rows from request text: $ROWS"
  fi

  if [[ -z "$PIPE_CMD" ]]; then
    if [[ "$text" == *"|"* ]]; then
      PIPE_CMD="| ${text#*|}"
      PIPE_CMD="${PIPE_CMD%%$'\n'*}"
      PIPE_CMD="${PIPE_CMD%%。*}"
      PIPE_CMD="${PIPE_CMD%%；*}"
      PIPE_CMD="${PIPE_CMD%%;*}"
      err "auto-extracted pipe command from request text: $PIPE_CMD"
    elif [[ "$text" =~ (python[[:space:]]+[^[:space:]]+\.py) ]]; then
      PIPE_CMD="| ${BASH_REMATCH[1]}"
      err "auto-extracted pipe command from request text: $PIPE_CMD"
    fi
  fi

  if [[ -z "$SCRIPT_PATH" ]]; then
    if [[ "$text" =~ (/[[:alnum:]_./-]+\.py) ]]; then
      SCRIPT_PATH="${BASH_REMATCH[1]}"
      err "auto-extracted script path from request text: $SCRIPT_PATH"
    fi
  fi
}

HDFS_PATH=""
ROWS="10"
PIPE_CMD=""
SCRIPT_PATH=""
OUTPUT_FILE=""
REQUEST_TEXT=""
DOCKER_BIN="sudo docker"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hdfs-path)
      HDFS_PATH="${2:-}"
      shift 2
      ;;
    --rows)
      ROWS="${2:-}"
      shift 2
      ;;
    --pipe-cmd)
      PIPE_CMD="${2:-}"
      shift 2
      ;;
    --script-path)
      SCRIPT_PATH="${2:-}"
      shift 2
      ;;
    --output-file)
      OUTPUT_FILE="${2:-}"
      shift 2
      ;;
    --request-text)
      REQUEST_TEXT="${2:-}"
      shift 2
      ;;
    --docker-bin)
      DOCKER_BIN="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      err "unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -n "$REQUEST_TEXT" ]]; then
  extract_from_request_text "$REQUEST_TEXT"
fi

if [[ -z "$HDFS_PATH" ]]; then
  err "--hdfs-path is required"
  if [[ -n "$REQUEST_TEXT" ]]; then
    err "request text was provided but no valid hdfs:// path was extracted"
  fi
  usage
  exit 1
fi

if [[ "$HDFS_PATH" != hdfs://* ]]; then
  err "hdfs path must start with hdfs://"
  exit 1
fi

IMAGE=""
if [[ "$HDFS_PATH" == hdfs://R2* ]]; then
  IMAGE="harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.4.2-tf1-sg-20251118063218"
elif [[ "$HDFS_PATH" == hdfs://D2* ]]; then
  IMAGE="harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.4.2-tf1-us-20251118063218"
else
  err "unsupported hdfs namespace. Only hdfs://R2 and hdfs://D2 are supported"
  exit 1
fi

if ! validate_positive_int "$ROWS"; then
  err "--rows must be a positive integer"
  exit 1
fi

require_cmd realpath

HOST_SCRIPT_MOUNT_DIR=""
CONTAINER_SCRIPT_DIR=""
if [[ -n "$SCRIPT_PATH" ]]; then
  SCRIPT_PATH_ABS="$(realpath "$SCRIPT_PATH")"
  if [[ ! -e "$SCRIPT_PATH_ABS" ]]; then
    err "--script-path does not exist: $SCRIPT_PATH"
    exit 1
  fi

  CONTAINER_SCRIPT_DIR="/workspace/sra-ego-parquet-totxt-user"
  if [[ -d "$SCRIPT_PATH_ABS" ]]; then
    HOST_SCRIPT_MOUNT_DIR="$SCRIPT_PATH_ABS"
    err "script path mode: directory (dependencies supported)"
  else
    HOST_SCRIPT_MOUNT_DIR="$(dirname "$SCRIPT_PATH_ABS")"
    err "script path mode: single file (assume no extra dependencies)"
  fi
fi

PIPE_BODY="$(trim_leading_pipe "$PIPE_CMD")"
if [[ -z "$PIPE_BODY" && -n "$SCRIPT_PATH" ]]; then
  SCRIPT_PATH_ABS="$(realpath "$SCRIPT_PATH")"
  if [[ -f "$SCRIPT_PATH_ABS" ]]; then
    PIPE_BODY="python $(basename "$SCRIPT_PATH_ABS")"
    err "--pipe-cmd not provided, auto using: | $PIPE_BODY"
  elif [[ -d "$SCRIPT_PATH_ABS" ]]; then
    if [[ -f "$SCRIPT_PATH_ABS/converter.py" ]]; then
      PIPE_BODY="python converter.py"
      err "--pipe-cmd not provided, auto using: | $PIPE_BODY (from directory converter.py)"
    else
      err "script directory has no converter.py, fallback to plain parquet text output"
    fi
  fi
fi

if [[ -z "$PIPE_BODY" ]]; then
  err "no converter pipeline resolved, will parse parquet to plain text only"
fi

if [[ -z "$OUTPUT_FILE" ]]; then
  TMP_DIR="$(mktemp -d /tmp/sra-ego-parquet-totxt-XXXXXX)"
  OUTPUT_FILE="${TMP_DIR}/sample_output.txt"
  STDERR_FILE="${TMP_DIR}/stderr.log"
else
  OUTPUT_FILE="$(realpath -m "$OUTPUT_FILE")"
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  STDERR_FILE="${OUTPUT_FILE}.stderr.log"
fi

INNER_CMD="set -o pipefail; "
if [[ -n "$CONTAINER_SCRIPT_DIR" ]]; then
  INNER_CMD+="cd ${CONTAINER_SCRIPT_DIR@Q}; "
fi
INNER_CMD+="export HADOOP_HOME=/usr/share/hadoop-client; "
INNER_CMD+="export CLASSPATH=\$(hadoop classpath); "
INNER_CMD+="export HADOOP_HDFS_HOME=/usr/share/hadoop-2.10; "
READER_CMD="/workspace/ego-train-v1/bin/parquet-message-reader-printer --hdfs_file_path=${HDFS_PATH@Q}"
PIPELINE_CMD="$READER_CMD"
if [[ -n "$PIPE_BODY" ]]; then
  PIPELINE_CMD+=" | $PIPE_BODY"
fi
INNER_CMD+="ROWS=${ROWS}; "
INNER_CMD+="STREAM_CMD=${PIPELINE_CMD@Q}; "
INNER_CMD+='coproc PARQUET_STREAM { bash -lc "$STREAM_CMD"; }; '
INNER_CMD+='count=0; '
INNER_CMD+='while IFS= read -r line <&"${PARQUET_STREAM[0]}"; do '
INNER_CMD+='  printf "%s\n" "$line"; '
INNER_CMD+='  count=$((count + 1)); '
INNER_CMD+='  if [[ "$count" -ge "$ROWS" ]]; then break; fi; '
INNER_CMD+='done; '
INNER_CMD+='kill "$PARQUET_STREAM_PID" >/dev/null 2>&1 || true; '
INNER_CMD+='wait "$PARQUET_STREAM_PID" >/dev/null 2>&1 || true'

DOCKER_RUN_CMD=(
  run --rm
)

if [[ -n "$HOST_SCRIPT_MOUNT_DIR" ]]; then
  DOCKER_RUN_CMD+=( -v "${HOST_SCRIPT_MOUNT_DIR}:${CONTAINER_SCRIPT_DIR}" )
fi

DOCKER_RUN_CMD+=("$IMAGE" bash -lc "$INNER_CMD")

err "using image: $IMAGE"
err "execute command: $PIPELINE_CMD"
err "output file: $OUTPUT_FILE"

read -r -a DOCKER_BIN_ARR <<<"$DOCKER_BIN"
if [[ "${#DOCKER_BIN_ARR[@]}" -eq 0 ]]; then
  err "invalid --docker-bin"
  exit 1
fi

set +e
"${DOCKER_BIN_ARR[@]}" "${DOCKER_RUN_CMD[@]}" >"$OUTPUT_FILE" 2>"$STDERR_FILE"
EXIT_CODE=$?
set -e

err "stderr log: $STDERR_FILE"
if [[ $EXIT_CODE -ne 0 ]]; then
  err "docker command failed with exit code: $EXIT_CODE"
  exit "$EXIT_CODE"
fi
