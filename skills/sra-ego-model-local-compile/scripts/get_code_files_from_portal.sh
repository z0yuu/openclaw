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
  bash get_code_files_from_portal.sh \
    --cluster <sg|uat|us> \
    --model-id <model_id> \
    --model-version-id <model_version_id> \
    --user-id-openapi <USER_ID_OPENAPI> \
    --output-dir <output_dir>
USAGE
}

cluster=""
model_id=""
model_version_id=""
USER_ID_OPENAPI=""
output_dir=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cluster)
      cluster="${2:-}"
      shift 2
      ;;
    --model-id)
      model_id="${2:-}"
      shift 2
      ;;
    --model-version-id)
      model_version_id="${2:-}"
      shift 2
      ;;
    --user-id-openapi)
      USER_ID_OPENAPI="${2:-}"
      shift 2
      ;;
    --output-dir)
      output_dir="${2:-}"
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

if [[ -z "$cluster" || -z "$model_id" || -z "$model_version_id" || -z "$USER_ID_OPENAPI" || -z "$output_dir" ]]; then
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

mkdir -p "$output_dir"
api_resp_json="$output_dir/model_version_response.json"

auth_cookie="userID=${USER_ID_OPENAPI}"
api_url="https://${portal_url}/api/ego/portal/model/${model_id}/version/${model_version_id}"

log "Fetching model version metadata from $api_url"
curl -fsSL -X GET "$api_url" \
  -H "Content-Type: application/json" \
  -H "Cookie: ${auth_cookie}" > "$api_resp_json"

resp_code="$(jq -r '.code // empty' "$api_resp_json")"
entry_file="$(jq -r '.data.entry_file_name // empty' "$api_resp_json")"
code_file_len="$(jq -r '.data.code_file | length' "$api_resp_json")"

if [[ -z "$resp_code" || "$resp_code" != "9913100" ]]; then
  echo "API returned non-success code: ${resp_code:-<empty>}" >&2
  echo "Response saved at: $api_resp_json" >&2
  exit 1
fi

if [[ -z "$entry_file" || "$entry_file" == "null" ]]; then
  echo "entry_file_name not found in API response" >&2
  echo "Response saved at: $api_resp_json" >&2
  exit 1
fi

if [[ -z "$code_file_len" || "$code_file_len" == "null" || "$code_file_len" -eq 0 ]]; then
  echo "No code_file entries found in API response" >&2
  echo "Response saved at: $api_resp_json" >&2
  exit 1
fi

download_dir="$output_dir/downloads"
material_dir="$output_dir/material"
mkdir -p "$download_dir" "$material_dir"

log "Downloading $code_file_len code file(s)"
for idx in $(seq 0 $((code_file_len - 1))); do
  dump_url="$(jq -r ".data.code_file[$idx].dump_url // empty" "$api_resp_json")"
  file_name="$(jq -r ".data.code_file[$idx].file_name // empty" "$api_resp_json")"

  if [[ -z "$dump_url" || -z "$file_name" ]]; then
    echo "Missing dump_url/file_name at code_file[$idx]" >&2
    exit 1
  fi

  dest_file="$download_dir/$file_name"
  log "Downloading code_file[$idx]: $file_name"
  curl -fsSL "$dump_url" -o "$dest_file"

  if [[ "$file_name" == *.zip ]]; then
    log "Unzipping $file_name into $material_dir"
    unzip -oq "$dest_file" -d "$material_dir"
  else
    log "Non-zip file, keep downloaded copy: $file_name"
    cp -f "$dest_file" "$material_dir/"
  fi
done

resolved_entry_file="$entry_file"
if [[ ! -f "$material_dir/$resolved_entry_file" ]]; then
  found_entry="$(find "$material_dir" -type f -name "$entry_file" | head -n 1 || true)"
  if [[ -n "$found_entry" ]]; then
    resolved_entry_file="${found_entry#"$material_dir/"}"
  fi
fi

if [[ ! -f "$material_dir/$resolved_entry_file" ]]; then
  echo "entry file not found after download/unzip: $entry_file" >&2
  exit 1
fi

result_json="$output_dir/source_resolution.json"
jq -n \
  --arg cluster "$cluster" \
  --arg model_id "$model_id" \
  --arg model_version_id "$model_version_id" \
  --arg entry_file "$resolved_entry_file" \
  --arg material_dir "$material_dir" \
  --arg response_json "$api_resp_json" \
  --argjson uss_paths "$(jq '.data.code_file | map(.uss_path)' "$api_resp_json")" \
  '{cluster: $cluster, model_id: $model_id, model_version_id: $model_version_id, entry_file: $entry_file, material_dir: $material_dir, response_json: $response_json, uss_paths: $uss_paths}' > "$result_json"

log "Source resolution done"
log "entry_file=$resolved_entry_file"
log "material_dir=$material_dir"
log "result_json=$result_json"
