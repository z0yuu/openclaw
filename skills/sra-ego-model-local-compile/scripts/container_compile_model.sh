#!/usr/bin/env bash
set -Eeuo pipefail

log() {
  echo "[INFO] $*"
}

err_report() {
  local rc=$?
  echo "[ERROR] command failed" >&2
  echo "[ERROR] exit_code=$rc line=${BASH_LINENO[0]} cmd=${BASH_COMMAND}" >&2
  echo "[ERROR] context: tf_version=${tf_version:-unknown} ego_mode=${ego_mode:-unknown} compile_dir=${compile_dir:-unknown}" >&2
}

trap err_report ERR

usage() {
  cat <<'USAGE'
Usage:
  bash container_compile_model.sh \
    --material-dir <material_dir> \
    --compile-image <compile_image> \
    --ego-mode <TRAINING|SERVING> \
    --entry-file <entry_file.py> \
    --output-path <output_path> \
    [--workspace-root /workspace]
USAGE
}

material_dir=""
compile_image=""
ego_mode=""
entry_file=""
output_path=""
workspace_root="/workspace"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --compile-image)
      compile_image="${2:-}"
      shift 2
      ;;
    --ego-mode)
      ego_mode="${2:-}"
      shift 2
      ;;
    --material-dir)
      material_dir="${2:-}"
      shift 2
      ;;
    --entry-file)
      entry_file="${2:-}"
      shift 2
      ;;
    --output-path)
      output_path="${2:-}"
      shift 2
      ;;
    --workspace-root)
      workspace_root="${2:-}"
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

if [[ -z "$material_dir" || -z "$compile_image" || -z "$ego_mode" || -z "$entry_file" || -z "$output_path" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 2
fi

if [[ ! -d "$material_dir" ]]; then
  echo "Material directory not found: $material_dir" >&2
  exit 1
fi

if [[ ! -d "$workspace_root" ]]; then
  echo "Workspace root not found: $workspace_root" >&2
  exit 1
fi

if ! command -v python >/dev/null 2>&1; then
  echo "python command not found in environment" >&2
  exit 1
fi

case "$ego_mode" in
  TRAINING|SERVING)
    ;;
  *)
    echo "Invalid ego_mode: $ego_mode (must be TRAINING or SERVING)" >&2
    exit 2
    ;;
esac

case "$compile_image" in
  *tf2*)
    tf_version="tf2"
    ;;
  *tf1*)
    tf_version="tf1"
    ;;
  *)
    echo "Cannot infer tf version from compile_image: $compile_image" >&2
    exit 2
    ;;
esac

log "Detected tf_version=$tf_version from compile_image=$compile_image"

compile_dir="$workspace_root"

if [[ "$tf_version" == "tf2" ]]; then
  tf1_rel="ego_tf1_dir"
  tf2_rel="ego_tf2_dir"
  tf1_dir="$workspace_root/$tf1_rel"
  tf2_dir="$workspace_root/$tf2_rel"
  common_sh="$workspace_root/ego-api-v1/scripts/common.sh"

  log "Preparing tf2 upgrade workspace under $workspace_root"
  # Stage source materials into tf1 working directory before upgrading.
  rm -rf "$tf1_dir"
  rm -rf "$tf2_dir"
  mkdir -p "$tf1_dir"
  mkdir -p "$tf2_dir"
  cp -a "$material_dir"/. "$tf1_dir"/

  if [[ ! -f "$common_sh" ]]; then
    echo "Required script not found: $common_sh" >&2
    exit 1
  fi

  # Load shared functions, then run model definition upgrade.
  # shellcheck source=/dev/null
  source "$common_sh"

  (
    cd "$workspace_root"
    upgrade_model_def "$tf1_rel" "$tf2_rel"
  )

  log "Upgrade finished, compile directory set to $tf2_dir"
  compile_dir="$tf2_dir"
else
  log "Preparing tf1 compile workspace under $workspace_root"
  # For tf1, place code files directly under /workspace.
  cp -a "$material_dir"/. "$workspace_root"/
fi

entry_path="$compile_dir/$entry_file"
if [[ ! -f "$entry_path" ]]; then
  echo "Entry file not found in compile directory: $entry_path" >&2
  exit 1
fi

log "Running compile entry: EGO_MODE=$ego_mode python $entry_file"
(
  cd "$compile_dir"
  EGO_MODE="$ego_mode" python "$entry_file"
)

mkdir -p "$output_path"

artifact_dir="$compile_dir"
if [[ "$ego_mode" == "SERVING" ]]; then
  artifact_dir="$compile_dir/serving"
fi

if [[ ! -d "$artifact_dir" ]]; then
  echo "Artifact directory not found: $artifact_dir" >&2
  exit 1
fi

for artifact in ego-config.json ego-config.pb graph.pb graph.readable; do
  src="$artifact_dir/$artifact"
  if [[ ! -f "$src" ]]; then
    echo "Missing compile artifact: $src" >&2
    exit 1
  fi
  cp -f "$src" "$output_path/"
done

log "Compile finished. Artifacts copied to: $output_path"
