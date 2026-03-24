#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash ensure_smart_tune_done.sh \
    --job-id <job_id> \
    [--cluster <sg|us|uat>] \
    [--base-url <https://ego-portal...>] \
    [--user-id-openapi <USER_ID_OPENAPI>] \
    [--debug-input <0|1>] \
    [--enable-auto-restart <0|1>] \
    [--poll-interval-sec <20>] \
    [--max-polls <180>] \
    [--work-dir </tmp/smart_tune_xxx>]
USAGE
}

log() {
  echo "[INFO] $*" >&2
}

die() {
  echo "[ERROR] $*" >&2
  exit 1
}

cluster="sg"
base_url=""
job_id=""
user_id_openapi="${USER_ID_OPENAPI:-}"
debug_input="0"
enable_auto_restart="0"
poll_interval_sec="20"
max_polls="180"
work_dir=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cluster)
      cluster="${2:-}"
      shift 2
      ;;
    --base-url)
      base_url="${2:-}"
      shift 2
      ;;
    --job-id)
      job_id="${2:-}"
      shift 2
      ;;
    --user-id-openapi)
      user_id_openapi="${2:-}"
      shift 2
      ;;
    --debug-input)
      debug_input="${2:-}"
      shift 2
      ;;
    --enable-auto-restart)
      enable_auto_restart="${2:-}"
      shift 2
      ;;
    --poll-interval-sec)
      poll_interval_sec="${2:-}"
      shift 2
      ;;
    --max-polls)
      max_polls="${2:-}"
      shift 2
      ;;
    --work-dir)
      work_dir="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$job_id" ]]; then
  die "Missing required argument: --job-id"
fi
if [[ -z "$user_id_openapi" ]]; then
  die "USER_ID_OPENAPI is required (use --user-id-openapi or env USER_ID_OPENAPI)."
fi
if ! [[ "$poll_interval_sec" =~ ^[0-9]+$ ]] || (( poll_interval_sec <= 0 )); then
  die "--poll-interval-sec must be a positive integer."
fi
if ! [[ "$max_polls" =~ ^[0-9]+$ ]] || (( max_polls <= 0 )); then
  die "--max-polls must be a positive integer."
fi
if ! command -v jq >/dev/null 2>&1; then
  die "jq command not found"
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "$work_dir" ]]; then
  work_dir="$(mktemp -d "/tmp/smart_tune_${job_id}.XXXXXX")"
else
  mkdir -p "$work_dir"
fi
log "work_dir=$work_dir"
base_url_args=()
if [[ -n "$base_url" ]]; then
  base_url_args+=(--base-url "$base_url")
fi

run_summary() {
  local smart_tune_id="$1"
  local summary_out="$work_dir/smart_tune_summary_result.json"
  local py_args=(
    --job-id "$job_id"
    --smart-tune-job-id "$smart_tune_id"
    --cluster "$cluster"
    --work-dir "$work_dir"
  )
  if [[ -n "$base_url" ]]; then
    py_args+=(--base-url "$base_url")
  fi
  python3 "$script_dir/smart_tune_summary.py" "${py_args[@]}" > "$summary_out"
  echo "$summary_out"
}

job_status_json="$work_dir/source_job_status.json"
bash "$script_dir/get_job_status.sh" \
  --job-id "$job_id" \
  --cluster "$cluster" \
  "${base_url_args[@]}" \
  --user-id-openapi "$user_id_openapi" \
  --output-json "$job_status_json" >/dev/null

source_job_status="$(jq -r '.data.status // ""' "$job_status_json")"
if [[ "${source_job_status,,}" == "deleted" ]]; then
  echo "任务已删除，无法启动smart tune任务" >&2
  jq -n \
    --arg job_id "$job_id" \
    --arg source_job_status "$source_job_status" \
    --arg message "任务已删除，无法启动smart tune任务" \
    '{job_id:$job_id, source_job_status:$source_job_status, message:$message}'
  exit 1
fi
if [[ "${source_job_status,,}" == "running" ]]; then
  echo "任务正在训练，无法启动smart tune任务，请等待任务结束(Success/Killed/Failed)，在重试命令" >&2
  jq -n \
    --arg job_id "$job_id" \
    --arg source_job_status "$source_job_status" \
    --arg message "任务正在训练，无法启动smart tune任务，请等待任务结束(Success/Killed/Failed)，在重试命令" \
    '{job_id:$job_id, source_job_status:$source_job_status, message:$message}'
  exit 1
fi

sub_jobs_json="$work_dir/sub_jobs.json"
bash "$script_dir/get_smart_tune_sub_jobs.sh" \
  --job-id "$job_id" \
  --cluster "$cluster" \
  "${base_url_args[@]}" \
  --user-id-openapi "$user_id_openapi" \
  --output-json "$sub_jobs_json" >/dev/null

first_job_name="$(jq -r '.data.data[0].job_name // ""' "$sub_jobs_json")"
first_training_type="$(jq -r '.data.data[0].training_job_type // ""' "$sub_jobs_json")"
first_status="$(jq -r '.data.data[0].status // ""' "$sub_jobs_json")"
first_smart_tune_job_id="$(jq -r '.data.data[0].job_id // .data.data[0].id // ""' "$sub_jobs_json")"

smart_tune_job_id=""

first_is_smart_tune="0"
if [[ "${first_training_type,,}" == "smart tuning analysis" ]]; then
  first_is_smart_tune="1"
elif [[ "$first_job_name" == smart_tune_* || "$first_job_name" == smart_tuning_* ]]; then
  first_is_smart_tune="1"
fi

if [[ "$first_is_smart_tune" == "1" ]]; then
  log "First sub job is smart tune: job_name=$first_job_name training_type=$first_training_type status=$first_status"
  case "$first_status" in
    succeeded)
      summary_result_json="$(run_summary "$first_smart_tune_job_id")"
      jq -n --arg smart_tune_job_id "$first_smart_tune_job_id" --arg smart_tune_status "succeeded" --arg action "skip launch, go summary" \
        --arg summary_result_json "$summary_result_json" \
        '{smart_tune_job_id:$smart_tune_job_id, smart_tune_status:$smart_tune_status, action:$action, summary_result_json:$summary_result_json}'
      exit 0
      ;;
    running)
      smart_tune_job_id="$first_smart_tune_job_id"
      ;;
    failed|failed_archived)
      echo "smart_tune任务失败，请联系EGO同学" >&2
      jq -n --arg smart_tune_job_id "$first_smart_tune_job_id" --arg smart_tune_status "$first_status" --arg message "smart_tune任务失败，请联系EGO同学" \
        '{smart_tune_job_id:$smart_tune_job_id, smart_tune_status:$smart_tune_status, message:$message}'
      exit 1
      ;;
    *)
      die "Unsupported existing smart tune status: '$first_status'"
      ;;
  esac
else
  log "First sub job is not smart tune, launching new smart tune job via launch_smart_tune_job.sh"
  log "launch params: original_job_id=$job_id cluster=$cluster debug_input=$debug_input enable_auto_restart=$enable_auto_restart base_url=${base_url:-<auto>}"
  launch_json="$work_dir/launch_response.json"
  bash "$script_dir/launch_smart_tune_job.sh" \
    --original-job-id "$job_id" \
    --cluster "$cluster" \
    "${base_url_args[@]}" \
    --user-id-openapi "$user_id_openapi" \
    --debug-input "$debug_input" \
    --enable-auto-restart "$enable_auto_restart" \
    --output-json "$launch_json" >/dev/null

  smart_tune_job_id="$(jq -r '.data.sub_job_id // .data.job_id // .data.id // .sub_job_id // .job_id // .id // empty' "$launch_json")"
  if [[ -z "$smart_tune_job_id" ]]; then
    die "Cannot extract smart_tune_job_id from launch response: $launch_json"
  fi
fi

log "smart_tune_job_id=$smart_tune_job_id"
if [[ -z "$smart_tune_job_id" ]]; then
  die "smart_tune_job_id is empty, cannot start polling."
fi

for ((i=1; i<=max_polls; i++)); do
  status_json="$work_dir/status_${i}.json"
  bash "$script_dir/get_job_status.sh" \
    --job-id "$smart_tune_job_id" \
    --cluster "$cluster" \
    "${base_url_args[@]}" \
    --user-id-openapi "$user_id_openapi" \
    --output-json "$status_json" >/dev/null

  status="$(jq -r '.data.status // ""' "$status_json")"
  log "poll#${i}: status=${status:-<empty>}"

  case "$status" in
    succeeded)
      summary_result_json="$(run_summary "$smart_tune_job_id")"
      jq -n \
        --arg smart_tune_job_id "$smart_tune_job_id" \
        --arg smart_tune_status "$status" \
        --arg action "launched_or_reused_and_succeeded" \
        --arg work_dir "$work_dir" \
        --arg summary_result_json "$summary_result_json" \
        '{smart_tune_job_id:$smart_tune_job_id, smart_tune_status:$smart_tune_status, action:$action, work_dir:$work_dir, summary_result_json:$summary_result_json}'
      exit 0
      ;;
    running)
      if (( i == max_polls )); then
        die "Polling timeout reached (${max_polls} polls). Last status=running"
      fi
      sleep "$poll_interval_sec"
      ;;
    failed|failed_archived)
      echo "smart_tune任务失败，请联系EGO同学" >&2
      jq -n \
        --arg smart_tune_job_id "$smart_tune_job_id" \
        --arg smart_tune_status "$status" \
        --arg message "smart_tune任务失败，请联系EGO同学" \
        --arg work_dir "$work_dir" \
        '{smart_tune_job_id:$smart_tune_job_id, smart_tune_status:$smart_tune_status, message:$message, work_dir:$work_dir}'
      exit 1
      ;;
    *)
      die "Unsupported polled status: '${status:-<empty>}'"
      ;;
  esac
done

die "Unexpected polling exit"
