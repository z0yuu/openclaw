#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(dirname "$SCRIPT_DIR")
REPO_ROOT=$(dirname "$(dirname "$SKILL_DIR")")

DEFAULT_CONFIG="${SCRIPT_DIR}/run_config.yaml"
RUNNER_SCRIPT_SRC="${SCRIPT_DIR}/container_run_local_job.sh"
FIXED_FLAGS="${SCRIPT_DIR}/flags.txt"
PORTAL_FETCH_SCRIPT="${SCRIPT_DIR}/get_run_files_by_job_id.sh"

usage() {
  cat <<'EOF'
Usage:
  Local mode:
    sh host_launch_local_job.sh \
      --model-dir <path> \
      --converter-dir <path> \
      --learner-config <path/to/ego-learner.yaml> \
      --runtime-image <image> \
      --log-dir <path> \
      [--run-config <path/to/run_config.yaml>]

  Portal mode:
    sh host_launch_local_job.sh \
      --model-dir <path> \
      --source-job-id <job_id> \
      --cluster <sg|us|uat> \
      --user-id-openapi <USER_ID_OPENAPI> \
      --runtime-image <image> \
      --log-dir <path> \
      [--portal-output-dir <path>] \
      [--run-config <path/to/run_config.yaml>]

Required common arguments:
  --model-dir         Directory containing ego-config.json and ego-config.pb
  --runtime-image     Docker runtime image (must contain tf1/tf2 and sg/us in tag)
  --log-dir           Host log directory path

Local-mode required arguments:
  --converter-dir     Directory containing converter files (for example .py or .lua)
  --learner-config    Path to ego-learner.yaml

Portal-mode required arguments:
  --source-job-id     Job id used to fetch converter/config files from portal
  --cluster           Portal cluster selector: sg/us/uat
  --user-id-openapi   OpenAPI user id for portal cookie auth

Optional arguments:
  --run-config        Explicit run config yaml; if missing, use default script config
  --portal-output-dir Directory used to store fetched ego-learner.yaml and converter files
EOF
}

MODEL_DIR=""
CONVERTER_DIR=""
LEARNER_CONFIG=""
RUNTIME_IMAGE=""
LOG_DIR=""
RUN_CONFIG_INPUT=""

SOURCE_JOB_ID=""
CLUSTER=""
USER_ID_OPENAPI=""
PORTAL_OUTPUT_DIR=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --model-dir)
      MODEL_DIR="${2:-}"
      shift 2
      ;;
    --converter-dir)
      CONVERTER_DIR="${2:-}"
      shift 2
      ;;
    --learner-config)
      LEARNER_CONFIG="${2:-}"
      shift 2
      ;;
    --runtime-image)
      RUNTIME_IMAGE="${2:-}"
      shift 2
      ;;
    --log-dir)
      LOG_DIR="${2:-}"
      shift 2
      ;;
    --run-config)
      RUN_CONFIG_INPUT="${2:-}"
      shift 2
      ;;
    --source-job-id)
      SOURCE_JOB_ID="${2:-}"
      shift 2
      ;;
    --cluster)
      CLUSTER="${2:-}"
      shift 2
      ;;
    --user-id-openapi)
      USER_ID_OPENAPI="${2:-}"
      shift 2
      ;;
    --portal-output-dir)
      PORTAL_OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "$MODEL_DIR" ] || [ -z "$RUNTIME_IMAGE" ] || [ -z "$LOG_DIR" ]; then
  echo "Error: --model-dir, --runtime-image, --log-dir are required." >&2
  usage >&2
  exit 1
fi

for f in ego-config.json ego-config.pb; do
  if [ ! -f "${MODEL_DIR}/${f}" ]; then
    echo "Error: missing required model file ${MODEL_DIR}/${f}" >&2
    exit 1
  fi
done

USE_PORTAL_MODE=0
if [ -n "$SOURCE_JOB_ID" ] || [ -n "$CLUSTER" ] || [ -n "$USER_ID_OPENAPI" ]; then
  USE_PORTAL_MODE=1
fi

if [ "${USE_PORTAL_MODE}" -eq 1 ]; then
  if [ -z "$SOURCE_JOB_ID" ] || [ -z "$CLUSTER" ] || [ -z "$USER_ID_OPENAPI" ]; then
    echo "Error: portal mode requires --source-job-id, --cluster and --user-id-openapi." >&2
    exit 1
  fi
  if [ -n "$CONVERTER_DIR" ] || [ -n "$LEARNER_CONFIG" ]; then
    echo "Error: do not provide --converter-dir/--learner-config in portal mode." >&2
    exit 1
  fi

  if [ -z "$PORTAL_OUTPUT_DIR" ]; then
    PORTAL_OUTPUT_DIR=$(mktemp -d "/tmp/model-local-run-portal.XXXXXX")
    CLEAN_PORTAL_DIR=1
  else
    mkdir -p "$PORTAL_OUTPUT_DIR"
    CLEAN_PORTAL_DIR=0
  fi

  PORTAL_LEARNER_CONFIG="${PORTAL_OUTPUT_DIR}/ego-learner.yaml"
  PORTAL_CONVERTER_DIR="${PORTAL_OUTPUT_DIR}/converter_dir"
  mkdir -p "$PORTAL_CONVERTER_DIR"

  bash "$PORTAL_FETCH_SCRIPT" \
    --cluster "$CLUSTER" \
    --job-id "$SOURCE_JOB_ID" \
    --user-id-openapi "$USER_ID_OPENAPI" \
    --output-ego-learner-path "$PORTAL_LEARNER_CONFIG" \
    --output-converter-dir "$PORTAL_CONVERTER_DIR"

  CONVERTER_DIR="$PORTAL_CONVERTER_DIR"
  LEARNER_CONFIG="$PORTAL_LEARNER_CONFIG"
else
  if [ -z "$CONVERTER_DIR" ] || [ -z "$LEARNER_CONFIG" ]; then
    echo "Error: local mode requires --converter-dir and --learner-config." >&2
    exit 1
  fi
  CLEAN_PORTAL_DIR=0
fi

if [ ! -d "$CONVERTER_DIR" ]; then
  echo "Error: converter_dir does not exist: $CONVERTER_DIR" >&2
  exit 1
fi
CONVERTER_FILE_COUNT=$(find "$CONVERTER_DIR" -type f \( -name '*.py' -o -name '*.lua' \) | wc -l | tr -d ' ')
if [ "${CONVERTER_FILE_COUNT}" -eq 0 ]; then
  echo "Error: converter_dir must contain at least one .py or .lua file: $CONVERTER_DIR" >&2
  exit 1
fi
if [ ! -f "$LEARNER_CONFIG" ]; then
  echo "Error: learner config file does not exist: $LEARNER_CONFIG" >&2
  exit 1
fi
if [ -n "$RUN_CONFIG_INPUT" ] && [ ! -f "$RUN_CONFIG_INPUT" ]; then
  echo "Error: run config file does not exist: $RUN_CONFIG_INPUT" >&2
  exit 1
fi

TAG=${RUNTIME_IMAGE##*:}
TF_VERSION=$(echo "$TAG" | grep -oE 'tf[12]' | head -n1 || true)
ZONE=$(echo "$TAG" | grep -oE '(^|-)us(-|$)|(^|-)sg(-|$)' | head -n1 | tr -d '-' || true)
if [ -z "$TF_VERSION" ] || [ -z "$ZONE" ]; then
  echo "Error: cannot parse tf_version/zone from image tag: ${TAG}" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# Stage a temporary job_dir mounted to /workspace/data in container.
TEMP_JOB_DIR=$(mktemp -d "/tmp/model-local-run-jobdir.XXXXXX")
cleanup() {
  rm -rf "$TEMP_JOB_DIR"
  if [ "${CLEAN_PORTAL_DIR:-0}" -eq 1 ]; then
    rm -rf "${PORTAL_OUTPUT_DIR:-}"
  fi
}
trap cleanup EXIT INT TERM

cp -f "${MODEL_DIR}/ego-config.json" "${TEMP_JOB_DIR}/ego-config.json"
cp -f "${MODEL_DIR}/ego-config.pb" "${TEMP_JOB_DIR}/ego-config.pb"
if [ -f "${MODEL_DIR}/graph.pb" ]; then
  cp -f "${MODEL_DIR}/graph.pb" "${TEMP_JOB_DIR}/graph.pb"
fi
if [ -f "${MODEL_DIR}/graph.readable" ]; then
  cp -f "${MODEL_DIR}/graph.readable" "${TEMP_JOB_DIR}/graph.readable"
fi
cp -f "${LEARNER_CONFIG}" "${TEMP_JOB_DIR}/ego-learner.yaml"
cp -a "${CONVERTER_DIR}/." "${TEMP_JOB_DIR}/"

RUN_CONFIG_FOR_PARSE=""
if [ -n "$RUN_CONFIG_INPUT" ]; then
  cp -f "${RUN_CONFIG_INPUT}" "${TEMP_JOB_DIR}/run_config.yaml"
  RUN_CONFIG_FOR_PARSE="${TEMP_JOB_DIR}/run_config.yaml"
else
  RUN_CONFIG_FOR_PARSE="${DEFAULT_CONFIG}"
fi

cp "$FIXED_FLAGS" "${TEMP_JOB_DIR}/flags.txt"
cp "$RUNNER_SCRIPT_SRC" "${TEMP_JOB_DIR}/container_run_local_job.sh"
chmod +x "${TEMP_JOB_DIR}/container_run_local_job.sh"

# Validate assembled temporary job_dir completeness before docker run.
for f in ego-config.json ego-config.pb ego-learner.yaml flags.txt container_run_local_job.sh; do
  if [ ! -f "${TEMP_JOB_DIR}/${f}" ]; then
    echo "Error: assembled temp_job_dir missing required file ${TEMP_JOB_DIR}/${f}" >&2
    exit 1
  fi
done

MAX_RUNTIME_SECONDS=$(awk -F': *' '/^max_runtime_seconds:/ {gsub(/"/, "", $2); print $2; exit}' "$RUN_CONFIG_FOR_PARSE")
MEMORY=$(awk -F': *' '/^[[:space:]]*memory:/ {gsub(/"/, "", $2); print $2; exit}' "$RUN_CONFIG_FOR_PARSE")
CPU=$(awk -F': *' '/^[[:space:]]*cpu:/ {gsub(/"/, "", $2); print $2; exit}' "$RUN_CONFIG_FOR_PARSE")
GPU=$(awk -F': *' '/^[[:space:]]*gpu:/ {gsub(/"/, "", $2); print $2; exit}' "$RUN_CONFIG_FOR_PARSE")

if [ -z "$MAX_RUNTIME_SECONDS" ] || [ -z "$MEMORY" ] || [ -z "$CPU" ] || [ -z "$GPU" ]; then
  echo "Error: invalid run config file: ${RUN_CONFIG_FOR_PARSE}" >&2
  exit 1
fi

echo "Resolved inputs:"
echo "  model_dir=${MODEL_DIR}"
echo "  converter_dir=${CONVERTER_DIR}"
echo "  learner_config=${LEARNER_CONFIG}"
echo "  runtime_image=${RUNTIME_IMAGE}"
echo "  log_dir=${LOG_DIR}"
echo "  tf_version=${TF_VERSION}"
echo "  zone=${ZONE}"
echo "  run_config=${RUN_CONFIG_FOR_PARSE}"
echo "  temp_job_dir=${TEMP_JOB_DIR}"
echo "  max_runtime_seconds=${MAX_RUNTIME_SECONDS}"
echo "  memory=${MEMORY}"
echo "  cpu=${CPU}"
echo "  gpu=${GPU}"
if [ "${USE_PORTAL_MODE}" -eq 1 ]; then
  echo "  source_job_id=${SOURCE_JOB_ID}"
  echo "  cluster=${CLUSTER}"
  echo "  portal_output_dir=${PORTAL_OUTPUT_DIR}"
fi

GPU_ARGS=""
if [ "${GPU}" -gt 0 ] 2>/dev/null; then
  GPU_ARGS="--gpus ${GPU}"
fi

# Fixed by skill contract: sample Docker stats every 5 seconds.
MONITOR_INTERVAL_SECONDS=5
CID_FILE="${TEMP_JOB_DIR}/.model-local-run-cid.$$.tmp"
rm -f "${CID_FILE}"
RUN_NAME="model-local-run-$(date +%s)-$$"

MAX_CPU_PERCENT=0
MAX_MEM_PERCENT=0
LAST_MEM_USAGE="N/A"
LAST_MEM_PERCENT="N/A"
LAST_PIDS="N/A"
STATS_SAMPLES=0
CONTAINER_ID=""
STATS_COLLECTION_NOTE=""

resolve_container_ref() {
  if [ -n "${CONTAINER_ID}" ]; then
    echo "${CONTAINER_ID}"
    return 0
  fi

  if [ -s "${CID_FILE}" ]; then
    CID_FROM_FILE=$(cat "${CID_FILE}" 2>/dev/null || true)
    if [ -n "${CID_FROM_FILE}" ]; then
      CONTAINER_ID="${CID_FROM_FILE}"
      echo "${CONTAINER_ID}"
      return 0
    fi
  fi

  CID_FROM_NAME=$(sudo docker ps -aq --filter "name=^/${RUN_NAME}$" | head -n1 || true)
  if [ -n "${CID_FROM_NAME}" ]; then
    CONTAINER_ID="${CID_FROM_NAME}"
    echo "${CONTAINER_ID}"
    return 0
  fi

  echo "${RUN_NAME}"
  return 0
}

if [ -n "$GPU_ARGS" ]; then
  sudo docker run --name "${RUN_NAME}" --cidfile "${CID_FILE}" --network host \
    --memory "${MEMORY}" --cpus "${CPU}" ${GPU_ARGS} \
    -v "${TEMP_JOB_DIR}:/workspace/data" \
    -v "${LOG_DIR}:${LOG_DIR}" \
    "${RUNTIME_IMAGE}" \
    sh -lc "sh /workspace/data/container_run_local_job.sh '${LOG_DIR}' '${MAX_RUNTIME_SECONDS}'" &
else
  sudo docker run --name "${RUN_NAME}" --cidfile "${CID_FILE}" --network host \
    --memory "${MEMORY}" --cpus "${CPU}" \
    -v "${TEMP_JOB_DIR}:/workspace/data" \
    -v "${LOG_DIR}:${LOG_DIR}" \
    "${RUNTIME_IMAGE}" \
    sh -lc "sh /workspace/data/container_run_local_job.sh '${LOG_DIR}' '${MAX_RUNTIME_SECONDS}'" &
fi
RUN_CMD_PID=$!

echo "Monitoring container CPU/MEM every ${MONITOR_INTERVAL_SECONDS}s..."
while kill -0 "${RUN_CMD_PID}" >/dev/null 2>&1; do
  CONTAINER_REF=$(resolve_container_ref)
  STATS_LINE=$(sudo docker stats --no-stream --format '{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.PIDs}}' "${CONTAINER_REF}" 2>/dev/null || true)
  if [ -n "${STATS_LINE}" ]; then
    STATS_SAMPLES=$((STATS_SAMPLES + 1))
    CPU_P=$(echo "${STATS_LINE}" | awk -F'|' '{print $1}')
    MEM_U=$(echo "${STATS_LINE}" | awk -F'|' '{print $2}')
    MEM_P=$(echo "${STATS_LINE}" | awk -F'|' '{print $3}')
    PIDS=$(echo "${STATS_LINE}" | awk -F'|' '{print $4}')

    LAST_MEM_USAGE="${MEM_U}"
    LAST_MEM_PERCENT="${MEM_P}"
    LAST_PIDS="${PIDS}"

    CPU_V=$(echo "${CPU_P}" | tr -d '%')
    MEM_V=$(echo "${MEM_P}" | tr -d '%')
    if [ -n "${CPU_V}" ] && awk "BEGIN {exit !(${CPU_V} > ${MAX_CPU_PERCENT})}"; then
      MAX_CPU_PERCENT="${CPU_V}"
    fi
    if [ -n "${MEM_V}" ] && awk "BEGIN {exit !(${MEM_V} > ${MAX_MEM_PERCENT})}"; then
      MAX_MEM_PERCENT="${MEM_V}"
    fi
  fi
  sleep "${MONITOR_INTERVAL_SECONDS}"
done

set +e
wait "${RUN_CMD_PID}"
RC=$?
set -e

CONTAINER_REF=$(resolve_container_ref)
if [ -z "${CONTAINER_ID}" ] && [ "${CONTAINER_REF}" != "${RUN_NAME}" ]; then
  CONTAINER_ID="${CONTAINER_REF}"
fi
rm -f "${CID_FILE}" >/dev/null 2>&1 || true

if [ "${STATS_SAMPLES}" -eq 0 ]; then
  FINAL_STATS_LINE=$(sudo docker stats --no-stream --format '{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.PIDs}}' "${CONTAINER_REF}" 2>/dev/null || true)
  if [ -n "${FINAL_STATS_LINE}" ]; then
    STATS_SAMPLES=1
    CPU_P=$(echo "${FINAL_STATS_LINE}" | awk -F'|' '{print $1}')
    MEM_U=$(echo "${FINAL_STATS_LINE}" | awk -F'|' '{print $2}')
    MEM_P=$(echo "${FINAL_STATS_LINE}" | awk -F'|' '{print $3}')
    PIDS=$(echo "${FINAL_STATS_LINE}" | awk -F'|' '{print $4}')

    LAST_MEM_USAGE="${MEM_U}"
    LAST_MEM_PERCENT="${MEM_P}"
    LAST_PIDS="${PIDS}"

    CPU_V=$(echo "${CPU_P}" | tr -d '%')
    MEM_V=$(echo "${MEM_P}" | tr -d '%')
    if [ -n "${CPU_V}" ]; then
      MAX_CPU_PERCENT="${CPU_V}"
    fi
    if [ -n "${MEM_V}" ]; then
      MAX_MEM_PERCENT="${MEM_V}"
    fi
  else
    STATS_COLLECTION_NOTE="stats_unavailable(container may have exited before sampling)"
  fi
fi

OOM_KILLED="unknown"
STATE_EXIT_CODE="unknown"
STATE_ERROR=""
STATE_FINISHED_AT=""
if [ -n "${CONTAINER_ID}" ]; then
  INSPECT_LINE=$(sudo docker inspect --format '{{.State.OOMKilled}}|{{.State.ExitCode}}|{{.State.Error}}|{{.State.FinishedAt}}' "${CONTAINER_ID}" 2>/dev/null || true)
  if [ -n "${INSPECT_LINE}" ]; then
    OOM_KILLED=$(echo "${INSPECT_LINE}" | awk -F'|' '{print $1}')
    STATE_EXIT_CODE=$(echo "${INSPECT_LINE}" | awk -F'|' '{print $2}')
    STATE_ERROR=$(echo "${INSPECT_LINE}" | awk -F'|' '{print $3}')
    STATE_FINISHED_AT=$(echo "${INSPECT_LINE}" | awk -F'|' '{print $4}')
  fi
fi

echo "===== Docker Resource Summary ====="
echo "monitor_interval_seconds=${MONITOR_INTERVAL_SECONDS}"
echo "stats_samples=${STATS_SAMPLES}"
echo "peak_cpu_percent=${MAX_CPU_PERCENT}%"
echo "peak_memory_percent=${MAX_MEM_PERCENT}%"
echo "last_memory_usage=${LAST_MEM_USAGE}"
echo "last_memory_percent=${LAST_MEM_PERCENT}"
echo "last_pids=${LAST_PIDS}"
if [ -n "${STATS_COLLECTION_NOTE}" ]; then
  echo "stats_collection_note=${STATS_COLLECTION_NOTE}"
fi
echo "oom_killed=${OOM_KILLED}"
echo "container_state_exit_code=${STATE_EXIT_CODE}"
echo "container_state_error=${STATE_ERROR}"
echo "container_finished_at=${STATE_FINISHED_AT}"
if [ "${RC}" -eq 124 ]; then
  echo "run_termination_reason=TimeOut(max_runtime_timeout)"
fi
if [ "${RC}" -eq 137 ] && [ "${OOM_KILLED}" = "true" ]; then
  echo "hint=exit_code_137_and_oom_killed_true_likely_memory_pressure"
fi

if [ -n "${CONTAINER_ID}" ]; then
  sudo docker rm "${CONTAINER_ID}" >/dev/null 2>&1 || true
fi

echo "docker_exit_code=${RC}"
exit "${RC}"
