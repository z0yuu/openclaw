#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash get_smart_tune_sub_jobs.sh \
    --job-id <job_id> \
    [--cluster <sg|us|uat>] \
    [--base-url <https://ego-portal...>] \
    [--user-id-openapi <USER_ID_OPENAPI>] \
    [--output-json <path>]
USAGE
}

log() {
  echo "[INFO] $*" >&2
}

cluster="sg"
base_url=""
job_id=""
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
    --job-id)
      job_id="${2:-}"
      shift 2
      ;;
    --user-id-openapi)
      user_id_openapi="${2:-}"
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

if [[ -z "$job_id" ]]; then
  echo "Missing required argument: --job-id" >&2
  usage
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

portal_root="$(resolve_base_url "$cluster" "$base_url")"
api_url="${portal_root}/api/ego/portal/job/${job_id}/sub_jobs"

log "Querying smart tune sub jobs: ${api_url}"
resp="$(curl -fsSL -X GET "$api_url" \
  -H "Content-Type: application/json" \
  -H "Cookie: userID=${user_id_openapi}")"

if [[ -n "$output_json" ]]; then
  mkdir -p "$(dirname "$output_json")"
  echo "$resp" | jq '.' > "$output_json"
  log "Saved response json: ${output_json}"
fi

echo "$resp" | jq '.'
