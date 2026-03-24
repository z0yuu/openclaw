#!/bin/sh

mkdir -p /etc/volcano/
echo "localhost" > /etc/volcano/ss.host
echo "localhost" > /etc/volcano/wc.host
echo "localhost" > /etc/volcano/worker.host

CONFIG_PATH=/workspace/data/
BIN_PATH=/workspace/ego-train-v1/bin/
LOG_DIR=$1
MAX_RUNTIME_TIMEOUT=$2

if [ -z "${LOG_DIR}" ] || [ -z "${MAX_RUNTIME_TIMEOUT}" ]; then
  echo "Error: log_dir and max_runtime_timeout are required."
  echo "Usage: sh container_run_local_job.sh <log_dir> <max_runtime_timeout_seconds>"
  exit 1
fi

case "${MAX_RUNTIME_TIMEOUT}" in
  ''|*[!0-9]*)
    echo "Error: max_runtime_timeout must be a positive integer, got '${MAX_RUNTIME_TIMEOUT}'."
    exit 1
    ;;
  0)
    echo "Error: max_runtime_timeout must be greater than 0."
    exit 1
    ;;
esac

TIMEOUT_EXIT_CODE=124
START_TIME=$(date +%s)

export VC_SS_NUM=1
export VC_WORKER_NUM=1
export VC_TASK_INDEX=0

export POD_NAME=pod-0
export COORDINATOR_RECOVER_PATH=${CONFIG_PATH}
export TRAIN_CONFIG_PATH=${CONFIG_PATH}
export EGO_MODEL_NAME=test_model
export EGO_PS_CLUSTER_NAME="1005-offline-cluster-1"
export EGO_CONTROLLER_URL="http://ego-portal.mlp.live-test.shopee.io/api/ego/portal"
export EGO_JOB_ID=1111
export EGO_TRAIN_MODE=${EGO_TRAIN_MODE:-train}
export ONLINE_EXPORT_PUBLISH_PATH="./"
export EGO_PS_PORT=9981
export CLASSPATH=$(hadoop classpath)
export HADOOP_HDFS_HOME=/usr/share/hadoop-2.10
ps -aux | grep "converter" | awk '{print $2}' | xargs -r kill -9
ps -aux | grep "worker" | awk '{print $2}' | xargs -r kill -9
ps -aux | grep "sample_server" | awk '{print $2}' | xargs -r kill -9
ps -aux | grep "coordinator" | awk '{print $2}' | xargs -r kill -9
sleep 10s
mkdir -p "${LOG_DIR}"
# Keep mount point intact; clear old log files only.
rm -f "${LOG_DIR}/coordinator.log" "${LOG_DIR}/sample_server.log" "${LOG_DIR}/worker.log"
${BIN_PATH}/coordinator --flagfile=${CONFIG_PATH}/flags.txt > "${LOG_DIR}/coordinator.log" 2>&1 &
COORDINATOR_PID=$!
${BIN_PATH}/sample_server --flagfile=${CONFIG_PATH}/flags.txt > "${LOG_DIR}/sample_server.log" 2>&1 &
SAMPLE_SERVER_PID=$!
${BIN_PATH}/worker --flagfile=${CONFIG_PATH}/flags.txt > "${LOG_DIR}/worker.log" 2>&1 &
WORKER_PID=$!

START_TRAINING_URL=127.0.0.1:23333/CoordinatorService/HttpStartTraining
START_SUCCESS_PATTERN='StartTraining success, TrainingBeginTime[[:space:]]+[0-9]+'
START_TIMEOUT_SECONDS=${START_TIMEOUT_SECONDS:-600}
SLEEP_SECONDS=${SLEEP_SECONDS:-2}
ELAPSED_SECONDS=0

is_alive() {
  kill -0 "$1" >/dev/null 2>&1
}

kill_all_training_processes() {
  is_alive "${COORDINATOR_PID}" && kill "${COORDINATOR_PID}" >/dev/null 2>&1 || true
  is_alive "${SAMPLE_SERVER_PID}" && kill "${SAMPLE_SERVER_PID}" >/dev/null 2>&1 || true
  is_alive "${WORKER_PID}" && kill "${WORKER_PID}" >/dev/null 2>&1 || true
  wait "${COORDINATOR_PID}" "${SAMPLE_SERVER_PID}" "${WORKER_PID}" >/dev/null 2>&1 || true
}

check_max_runtime_timeout() {
  NOW=$(date +%s)
  ELAPSED=$((NOW - START_TIME))
  if [ "${ELAPSED}" -ge "${MAX_RUNTIME_TIMEOUT}" ]; then
    echo "TimeOut: reached max_runtime_timeout=${MAX_RUNTIME_TIMEOUT}s, killing coordinator/sample_server/worker."
    kill_all_training_processes
    exit "${TIMEOUT_EXIT_CODE}"
  fi
}

while [ "${ELAPSED_SECONDS}" -lt "${START_TIMEOUT_SECONDS}" ]; do
  check_max_runtime_timeout

  if ! is_alive "${COORDINATOR_PID}"; then
    echo "Coordinator exited before training start."
    exit 1
  fi
  if ! is_alive "${SAMPLE_SERVER_PID}"; then
    echo "Sample_server exited before training start."
    exit 1
  fi
  if ! is_alive "${WORKER_PID}"; then
    echo "Worker exited before training start."
    exit 1
  fi

  curl -fsS "${START_TRAINING_URL}" >/dev/null 2>&1 || true

  if [ -f "${LOG_DIR}/coordinator.log" ] && grep -Eq "${START_SUCCESS_PATTERN}" "${LOG_DIR}/coordinator.log"; then
    echo "Training start confirmed in ${LOG_DIR}/coordinator.log"
    break
  fi

  sleep "${SLEEP_SECONDS}"
  ELAPSED_SECONDS=$((ELAPSED_SECONDS + SLEEP_SECONDS))
done

if [ "${ELAPSED_SECONDS}" -ge "${START_TIMEOUT_SECONDS}" ]; then
  echo "Timeout: training did not start within ${START_TIMEOUT_SECONDS}s, check ${LOG_DIR}/coordinator.log"
  exit 1
fi

echo "Monitoring worker/coordinator/sample_server; workflow will end when the first one exits."
while true; do
  check_max_runtime_timeout

  if ! is_alive "${COORDINATOR_PID}"; then
    wait "${COORDINATOR_PID}" >/dev/null 2>&1
    RC=$?
    echo "Coordinator exited first (pid=${COORDINATOR_PID}, exit_code=${RC}). Stopping remaining processes."
    if [ "${RC}" -ne 0 ]; then
      echo "Detected non-zero exit: coordinator pid=${COORDINATOR_PID}, exit_code=${RC}"
    fi
    is_alive "${SAMPLE_SERVER_PID}" && kill "${SAMPLE_SERVER_PID}" >/dev/null 2>&1 || true
    is_alive "${WORKER_PID}" && kill "${WORKER_PID}" >/dev/null 2>&1 || true
    wait "${SAMPLE_SERVER_PID}" "${WORKER_PID}" >/dev/null 2>&1 || true
    exit "${RC}"
  fi

  if ! is_alive "${SAMPLE_SERVER_PID}"; then
    wait "${SAMPLE_SERVER_PID}" >/dev/null 2>&1
    RC=$?
    echo "Sample_server exited first (pid=${SAMPLE_SERVER_PID}, exit_code=${RC}). Stopping remaining processes."
    if [ "${RC}" -ne 0 ]; then
      echo "Detected non-zero exit: sample_server pid=${SAMPLE_SERVER_PID}, exit_code=${RC}"
    fi
    is_alive "${COORDINATOR_PID}" && kill "${COORDINATOR_PID}" >/dev/null 2>&1 || true
    is_alive "${WORKER_PID}" && kill "${WORKER_PID}" >/dev/null 2>&1 || true
    wait "${COORDINATOR_PID}" "${WORKER_PID}" >/dev/null 2>&1 || true
    exit "${RC}"
  fi

  if ! is_alive "${WORKER_PID}"; then
    wait "${WORKER_PID}" >/dev/null 2>&1
    RC=$?
    echo "Worker exited first (pid=${WORKER_PID}, exit_code=${RC}). Stopping remaining processes."
    if [ "${RC}" -ne 0 ]; then
      echo "Detected non-zero exit: worker pid=${WORKER_PID}, exit_code=${RC}"
    fi
    is_alive "${COORDINATOR_PID}" && kill "${COORDINATOR_PID}" >/dev/null 2>&1 || true
    is_alive "${SAMPLE_SERVER_PID}" && kill "${SAMPLE_SERVER_PID}" >/dev/null 2>&1 || true
    wait "${COORDINATOR_PID}" "${SAMPLE_SERVER_PID}" >/dev/null 2>&1 || true
    exit "${RC}"
  fi

  sleep "${SLEEP_SECONDS}"
done
