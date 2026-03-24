#!/usr/bin/env bash
set -Eeuo pipefail

log() {
  echo "[INFO] $*"
}

err_report() {
  local rc=$?
  echo "[ERROR] command failed" >&2
  echo "[ERROR] exit_code=$rc line=${BASH_LINENO[0]} cmd=${BASH_COMMAND}" >&2
}
trap err_report ERR

usage() {
  cat <<'USAGE'
Usage:
  bash get_run_files_by_job_id.sh \
    --cluster <sg|uat|us> \
    --job-id <job_id> \
    --user-id-openapi <USER_ID_OPENAPI> \
    --output-ego-learner-path <path/to/ego-learner.yaml> \
    --output-converter-dir <path/to/converter_dir>
USAGE
}

cluster=""
job_id=""
USER_ID_OPENAPI=""
output_ego_learner_path=""
output_converter_dir=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cluster)
      cluster="${2:-}"
      shift 2
      ;;
    --job-id)
      job_id="${2:-}"
      shift 2
      ;;
    --user-id-openapi)
      USER_ID_OPENAPI="${2:-}"
      shift 2
      ;;
    --output-ego-learner-path)
      output_ego_learner_path="${2:-}"
      shift 2
      ;;
    --output-converter-dir)
      output_converter_dir="${2:-}"
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

if [[ -z "$cluster" || -z "$job_id" || -z "$USER_ID_OPENAPI" || -z "$output_ego_learner_path" || -z "$output_converter_dir" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 2
fi

case "$cluster" in
  sg)
    portal_url="ego-portal.mlp.shopee.io"
    ;;
  us)
    portal_url="ego-portal.mlp.us.shopee.io"
    ;;
  uat)
    portal_url="ego-portal.mlp.live-test.shopee.io"
    ;;
  *)
    echo "invalid cluster: '$cluster' (must be sg/uat/us)" >&2
    exit 3
    ;;
esac

if ! command -v jq >/dev/null 2>&1; then
  echo "jq command not found" >&2
  exit 1
fi

mkdir -p "$(dirname "$output_ego_learner_path")" "$output_converter_dir"
work_dir="$(mktemp -d "/tmp/get-run-files-by-job-id.XXXXXX")"
downloads_dir="$work_dir/downloads"
mkdir -p "$downloads_dir"
cleanup() {
  rm -rf "$work_dir"
}
trap cleanup EXIT INT TERM

api_resp_json="$work_dir/job_response.json"
api_url="https://${portal_url}/api/ego/portal/job/${job_id}"
auth_cookie="userID=${USER_ID_OPENAPI}"

# Fixed portal query contract:
#   GET https://<cluster-domain>/api/ego/portal/job/<JOB_ID>
#   Header: Cookie: userID=<USER_ID_OPENAPI>
log "Fetching job metadata from $api_url"
curl -fsSL -X GET "$api_url" \
  -H "Content-Type: application/json" \
  -H "Cookie: ${auth_cookie}" > "$api_resp_json"

resp_code="$(jq -r '.code // empty' "$api_resp_json")"
if [[ -z "$resp_code" || "$resp_code" != "9914100" ]]; then
  echo "API returned non-success code: ${resp_code:-<empty>}" >&2
  echo "Response saved at: $api_resp_json" >&2
  exit 1
fi

learner_dump_url="$(jq -r '.data.config_files[]? | select(.file_name=="ego-learner.yaml") | .dump_url' "$api_resp_json" | head -n1)"
if [[ -z "$learner_dump_url" || "$learner_dump_url" == "null" ]]; then
  learner_dump_url="$(jq -r '.data.config_files[0].dump_url // empty' "$api_resp_json")"
fi
if [[ -z "$learner_dump_url" ]]; then
  echo "Cannot resolve config_files dump_url for ego-learner.yaml." >&2
  exit 1
fi

log "Downloading ego-learner.yaml from config_files dump_url"
curl -fsSL "$learner_dump_url" -o "$output_ego_learner_path"

converter_len="$(jq -r '(.data.data_converter // .data.converter // []) | length' "$api_resp_json")"
if [[ -z "$converter_len" || "$converter_len" == "null" || "$converter_len" -eq 0 ]]; then
  echo "No data_converter entries found for job ${job_id}" >&2
  exit 1
fi

for idx in $(seq 0 $((converter_len - 1))); do
  dump_url="$(jq -r "(.data.data_converter // .data.converter // [])[${idx}].dump_url // empty" "$api_resp_json")"
  file_name="$(jq -r "(.data.data_converter // .data.converter // [])[${idx}].file_name // empty" "$api_resp_json")"
  if [[ -z "$dump_url" || -z "$file_name" ]]; then
    echo "Missing dump_url/file_name at data_converter[$idx]" >&2
    exit 1
  fi

  dest_file="${downloads_dir}/${file_name}"
  log "Downloading converter file: ${file_name}"
  curl -fsSL "$dump_url" -o "$dest_file"

  if [[ "$file_name" == *.zip ]]; then
    log "Unzipping converter zip: ${file_name} -> ${output_converter_dir}"
    unzip -oq "$dest_file" -d "$output_converter_dir"
  else
    cp -f "$dest_file" "${output_converter_dir}/"
  fi
done

if [[ -z "$(find "$output_converter_dir" -type f \( -name '*.py' -o -name '*.lua' \) | head -n 1 || true)" ]]; then
  echo "No converter .py/.lua files downloaded from job ${job_id}" >&2
  exit 1
fi

log "Run files fetched by job id"
log "ego_learner_path=$output_ego_learner_path"
log "converter_dir=$output_converter_dir"
