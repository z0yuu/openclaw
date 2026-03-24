#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash launch_smart_tune_job.sh \
    --original-job-id <job_id> \
    [--cluster <sg|us|uat>] \
    [--base-url <https://ego-portal...>] \
    [--user-id-openapi <USER_ID_OPENAPI>] \
    [--debug-input <0|1>] \
    [--enable-auto-restart <0|1>] \
    [--output-json <path>]
USAGE
}

log() {
  echo "[INFO] $*" >&2
}

cluster="sg"
base_url=""
original_job_id=""
debug_input="0"
enable_auto_restart="0"
user_id_openapi="${USER_ID_OPENAPI:-}"
output_json=""

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
    --original-job-id)
      original_job_id="${2:-}"
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
    --output-json)
      output_json="${2:-}"
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

if [[ -z "$original_job_id" ]]; then
  echo "Missing required argument: --original-job-id" >&2
  usage
  exit 2
fi
if [[ ! "$original_job_id" =~ ^[0-9]+$ ]]; then
  echo "original_job_id must be numeric: '$original_job_id'" >&2
  exit 2
fi
if [[ -z "$user_id_openapi" ]]; then
  echo "USER_ID_OPENAPI is required (use --user-id-openapi or env USER_ID_OPENAPI)." >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq command not found" >&2
  exit 1
fi

resolve_base_url() {
  local c="$1"
  local raw="${2:-}"
  local b=""
  if [[ -n "$raw" ]]; then
    b="$raw"
  else
    case "$c" in
      sg) b="https://ego-portal.mlp.shopee.io" ;;
      us) b="https://ego-portal.mlp.us.shopee.io" ;;
      uat|live-test|lt) b="https://ego-portal.mlp.live-test.shopee.io" ;;
      *)
        echo "invalid cluster: '$c' (must be sg/us/uat)" >&2
        exit 3
        ;;
    esac
  fi
  if [[ "$b" != http://* && "$b" != https://* ]]; then
    b="https://${b}"
  fi
  b="${b%/}"
  b="${b%/api/ego/portal}"
  echo "$b"
}

normalize_bool() {
  local v="${1:-0}"
  case "$v" in
    1|true|TRUE|True|yes|YES|on|ON) echo "true" ;;
    0|false|FALSE|False|no|NO|off|OFF|"") echo "false" ;;
    *)
      echo "invalid boolean value: '$v' (accepted: 0/1/true/false)" >&2
      exit 2
      ;;
  esac
}

portal_root="$(resolve_base_url "$cluster" "$base_url")"
api_url="${portal_root}/api/ego/portal/job/smart-tuning-analysis"
is_debug_mode="$(normalize_bool "$debug_input")"
is_auto_restart="$(normalize_bool "$enable_auto_restart")"

payload="$(jq -n \
  --argjson original_job_id "$original_job_id" \
  --argjson is_debug_mode "$is_debug_mode" \
  --argjson enable_auto_restart "$is_auto_restart" \
  '{original_job_id: $original_job_id, is_debug_mode: $is_debug_mode, enable_auto_restart: $enable_auto_restart}')"

log "Submitting smart tune job for original_job_id=${original_job_id}"
resp="$(curl -fsSL -X POST "$api_url" \
  -H "Content-Type: application/json" \
  -H "Cookie: userID=${user_id_openapi}" \
  -d "$payload")"

if [[ -n "$output_json" ]]; then
  mkdir -p "$(dirname "$output_json")"
  echo "$resp" | jq '.' > "$output_json"
  log "Saved response json: ${output_json}"
fi

echo "$resp" | jq '.'
