#!/usr/bin/env bash
set -euo pipefail

# Scoped to: gitlab@git.garena.com:shopee/MLP/EGO/ego-train-v1.git
GITLAB_API="https://git.garena.com/api/v4"
PROJECT_ID="shopee%2FMLP%2FEGO%2Fego-train-v1"

VALID_JOBS="deploy-tf-all-job deploy-tf1-job deploy-tf2-job deploy-torch-job"
DEFAULT_JOBS="deploy-tf-all-job"
DEFAULT_MAX_RETRIES=3
POLL_INTERVAL=5
POLL_MAX_WAIT=60
JOB_POLL_INTERVAL=60
JOB_POLL_MAX_WAIT=5400

usage() {
    cat <<EOF
Usage: $(basename "$0") --branch <branch> [--jobs <job1,job2,...>] [--max-retries <n>] [--wait]

Trigger GitLab CI deploy jobs for ego-train-v1 on a specified branch.
Target repo: gitlab@git.garena.com:shopee/MLP/EGO/ego-train-v1.git

Options:
  --branch       Branch name (required, cannot be master/main)
  --jobs         Comma-separated job names (default: deploy-tf-all-job)
                 Valid: deploy-tf-all-job, deploy-tf1-job, deploy-tf2-job, deploy-torch-job
  --max-retries  Max retry attempts per failed job (default: $DEFAULT_MAX_RETRIES)
  --wait         Wait for jobs to complete instead of exiting after trigger
                 (applies to both new and existing in-progress pipelines)

Environment:
  GITLAB_PRIVATE_TOKEN   GitLab Personal Access Token with api scope (required)
EOF
    exit 1
}

log()  { echo "[INFO]  $(date '+%H:%M:%S') $*"; }
warn() { echo "[WARN]  $(date '+%H:%M:%S') $*" >&2; }
err()  { echo "[ERROR] $(date '+%H:%M:%S') $*" >&2; exit 1; }

api_get() {
    local endpoint="$1"
    curl -sS -f -H "PRIVATE-TOKEN: ${GITLAB_PRIVATE_TOKEN}" \
        "${GITLAB_API}/projects/${PROJECT_ID}${endpoint}"
}

api_post() {
    local endpoint="$1"
    curl -sS -f -X POST -H "PRIVATE-TOKEN: ${GITLAB_PRIVATE_TOKEN}" \
        "${GITLAB_API}/projects/${PROJECT_ID}${endpoint}"
}

json_val() {
    python3 -c "import sys,json; print(json.load(sys.stdin)$1)"
}

extract_images_from_job() {
    local job_id="$1" base_image="$2" short_sha="${3:-}"
    api_get "/jobs/${job_id}/trace" 2>/dev/null | \
        grep -oE 'harbor\.shopeemobile\.com/mlp-ego/ego-train-runtime:[A-Za-z0-9._-]+' | \
        grep -v "^${base_image}$" | \
        ( [[ -n "$short_sha" ]] && grep -F "$short_sha" || cat ) | \
        sort -u
}

wait_for_job() {
    local job_name="$1" job_id="$2"
    local elapsed=0
    while [[ $elapsed -lt $JOB_POLL_MAX_WAIT ]]; do
        sleep "$JOB_POLL_INTERVAL"
        elapsed=$((elapsed + JOB_POLL_INTERVAL))

        local status
        status=$(api_get "/jobs/${job_id}" | json_val "['status']" 2>/dev/null || echo "unknown")

        case "$status" in
            success)
                log "[$job_name] Succeeded!"
                return 0
                ;;
            failed|canceled)
                warn "[$job_name] Status: $status"
                return 1
                ;;
            *)
                log "[$job_name] Status: $status (${elapsed}s elapsed)"
                ;;
        esac
    done

    warn "[$job_name] Timed out after ${JOB_POLL_MAX_WAIT}s"
    return 1
}

ALL_IMAGES=()

# --- Argument parsing ---
BRANCH=""
JOBS=""
MAX_RETRIES="$DEFAULT_MAX_RETRIES"
WAIT_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --branch)      BRANCH="$2"; shift 2 ;;
        --jobs)        JOBS="$2"; shift 2 ;;
        --max-retries) MAX_RETRIES="$2"; shift 2 ;;
        --wait)        WAIT_MODE=true; shift ;;
        -h|--help) usage ;;
        *) err "Unknown option: $1" ;;
    esac
done

[[ -z "$BRANCH" ]] && err "Missing required option: --branch"
[[ "$BRANCH" == "master" || "$BRANCH" == "main" ]] && err "Operating on '$BRANCH' branch is forbidden. Use a feature/dev branch instead."
[[ -z "${GITLAB_PRIVATE_TOKEN:-}" ]] && err "Environment variable GITLAB_PRIVATE_TOKEN is not set"

if [[ -z "$JOBS" ]]; then
    JOBS="$DEFAULT_JOBS"
fi

IFS=',' read -ra JOB_ARRAY <<< "$JOBS"
for job in "${JOB_ARRAY[@]}"; do
    if ! echo "$VALID_JOBS" | grep -qw "$job"; then
        err "Invalid job name: $job (valid: $VALID_JOBS)"
    fi
done

log "Target repo: git.garena.com:shopee/MLP/EGO/ego-train-v1"
log "Branch: $BRANCH"
log "Jobs to trigger: ${JOB_ARRAY[*]}"
log "Max retries per job: $MAX_RETRIES"

# --- Phase 1: Get latest commit SHA ---
log "Fetching latest commit for branch '$BRANCH'..."
branch_info=$(api_get "/repository/branches/$(echo "$BRANCH" | sed 's|/|%2F|g')") || \
    err "Failed to fetch branch info. Does branch '$BRANCH' exist on remote?"

commit_sha=$(echo "$branch_info" | json_val "['commit']['id']")
short_sha=$(echo "$branch_info" | json_val "['commit']['short_id']")
log "Latest commit: $short_sha ($commit_sha)"

cur_version=$(api_get "/repository/files/.gitlab-ci.yml/raw?ref=${BRANCH}" | \
    python3 -c "import sys,re; m=re.search(r'cur_version:\s*\"([^\"]+)\"', sys.stdin.read()); print(m.group(1)) if m else sys.exit(1)") || \
    err "Failed to parse cur_version from .gitlab-ci.yml on branch '$BRANCH'"
IMAGE="harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V${cur_version}-dev-${short_sha}"
log "Base image prefix: $IMAGE"

# --- Phase 2: Check existing pipelines for this commit ---
# Three possible outcomes:
#   1. All target jobs succeeded → output images, exit 0
#   2. Target jobs running/pending → report in-progress, exit 0
#   3. Neither → proceed to create new pipeline
log "Checking existing pipelines for commit $short_sha..."
existing_pipelines=$(api_get "/pipelines?sha=${commit_sha}&order_by=id&sort=desc&per_page=10") || true

target_jobs_str="${JOB_ARRAY[*]}"
existing_result="none"
existing_pipeline_id=""
existing_pipeline_url=""

if [[ -n "$existing_pipelines" && "$existing_pipelines" != "[]" ]]; then
    pipeline_ids=$(echo "$existing_pipelines" | python3 -c "
import sys, json
for p in json.load(sys.stdin):
    print(p['id'])
")
    for pid in $pipeline_ids; do
        pipeline_jobs=$(api_get "/pipelines/${pid}/jobs?per_page=100") || continue
        result=$(echo "$pipeline_jobs" | python3 -c "
import sys, json
jobs = json.load(sys.stdin)
targets = set('${target_jobs_str}'.split())
job_map = {}
for j in jobs:
    if j['name'] in targets:
        job_map[j['name']] = j['status']
if len(job_map) < len(targets):
    print('none')
elif all(s == 'success' for s in job_map.values()):
    print('success')
elif any(s in ('running', 'pending', 'created') for s in job_map.values()):
    print('in_progress')
else:
    print('none')
" 2>/dev/null || echo "none")

        if [[ "$result" == "success" || "$result" == "in_progress" ]]; then
            existing_result="$result"
            existing_pipeline_id="$pid"
            existing_pipeline_url=$(echo "$existing_pipelines" | python3 -c "
import sys, json
for p in json.load(sys.stdin):
    if p['id'] == ${pid}:
        print(p['web_url']); break
")
            break
        fi
    done
fi

if [[ "$existing_result" == "success" ]]; then
    log "All requested jobs already succeeded for commit $short_sha!"
    log "Extracting built images from job logs..."
    existing_job_ids=$(echo "$pipeline_jobs" | python3 -c "
import sys, json
targets = set('${target_jobs_str}'.split())
for j in json.load(sys.stdin):
    if j['name'] in targets and j['status'] == 'success':
        print(j['id'])
")
    for jid in $existing_job_ids; do
        while IFS= read -r img; do
            [[ -n "$img" ]] && ALL_IMAGES+=("$img")
        done < <(extract_images_from_job "$jid" "$IMAGE" "$short_sha")
    done
    echo ""
    echo "=========================================="
    echo "  IMAGE ALREADY BUILT"
    echo "=========================================="
    echo "  Pipeline: #${existing_pipeline_id}"
    echo "  URL:      $existing_pipeline_url"
    echo "  Commit:   $short_sha"
    if [[ ${#ALL_IMAGES[@]} -gt 0 ]]; then
        echo "  Images:"
        for img in "${ALL_IMAGES[@]}"; do
            echo "    - $img"
        done
    fi
    echo "=========================================="
    exit 0
fi

if [[ "$existing_result" == "in_progress" ]]; then
    log "Target jobs are already running/pending for commit $short_sha."
    echo ""
    echo "=========================================="
    echo "  BUILD ALREADY IN PROGRESS"
    echo "=========================================="
    echo "  Pipeline: #${existing_pipeline_id}"
    echo "  URL:      $existing_pipeline_url"
    echo "  Commit:   $short_sha"
    echo "=========================================="

    if [[ "$WAIT_MODE" == "true" ]]; then
        log "Waiting for existing pipeline jobs to complete (--wait)..."
        echo ""

        pipeline_jobs=$(api_get "/pipelines/${existing_pipeline_id}/jobs?per_page=100")
        succeeded_jobs=()
        failed_jobs=()

        for job_name in "${JOB_ARRAY[@]}"; do
            current_job_id=$(echo "$pipeline_jobs" | python3 -c "
import sys, json
for j in json.load(sys.stdin):
    if j['name'] == '${job_name}':
        print(j['id']); break
")
            current_job_status=$(echo "$pipeline_jobs" | python3 -c "
import sys, json
for j in json.load(sys.stdin):
    if j['name'] == '${job_name}':
        print(j['status']); break
")

            if [[ "$current_job_status" == "success" ]]; then
                log "[$job_name] Already succeeded."
                succeeded_jobs+=("$job_name")
            elif [[ "$current_job_status" == "failed" || "$current_job_status" == "canceled" ]]; then
                warn "[$job_name] Already $current_job_status."
                failed_jobs+=("$job_name")
                break
            else
                log "[$job_name] Status: $current_job_status — waiting..."
                if wait_for_job "$job_name" "$current_job_id"; then
                    succeeded_jobs+=("$job_name")
                else
                    failed_jobs+=("$job_name")
                    warn "Job '$job_name' failed. Aborting remaining jobs."
                    break
                fi
            fi

            log "[$job_name] Extracting built images from job log..."
            while IFS= read -r img; do
                [[ -n "$img" ]] && ALL_IMAGES+=("$img")
            done < <(extract_images_from_job "$current_job_id" "$IMAGE" "$short_sha")
        done

        echo ""
        echo "=========================================="
        if [[ ${#failed_jobs[@]} -eq 0 ]]; then
            echo "  CI COMPLETED SUCCESSFULLY"
        else
            echo "  CI COMPLETED WITH FAILURES"
        fi
        echo "=========================================="
        echo "  Pipeline:  #${existing_pipeline_id}"
        echo "  URL:       $existing_pipeline_url"
        echo "  Branch:    $BRANCH"
        echo "  Commit:    $short_sha"
        [[ ${#succeeded_jobs[@]} -gt 0 ]] && echo "  Succeeded: ${succeeded_jobs[*]}"
        [[ ${#failed_jobs[@]} -gt 0 ]]    && echo "  Failed:    ${failed_jobs[*]}"
        if [[ ${#ALL_IMAGES[@]} -gt 0 ]]; then
            echo "  Images:"
            for img in "${ALL_IMAGES[@]}"; do
                echo "    - $img"
            done
        fi
        echo "=========================================="

        [[ ${#failed_jobs[@]} -gt 0 ]] && exit 1
        exit 0
    fi

    echo ""
    echo "A build for this commit is already running. Not creating a duplicate pipeline."
    exit 0
fi

log "No existing successful or in-progress build found. Triggering new pipeline..."

# --- Phase 3: Create new pipeline ---
log "Creating pipeline for branch '$BRANCH'..."
pipeline_resp=$(api_post "/pipeline?ref=${BRANCH}") || \
    err "Failed to create pipeline. Check branch permissions and CI config."

pipeline_id=$(echo "$pipeline_resp" | json_val "['id']")
pipeline_url=$(echo "$pipeline_resp" | json_val "['web_url']")
log "Pipeline created: #${pipeline_id}"
log "URL: $pipeline_url"

# --- Phase 4: Wait for manual jobs to appear ---
log "Waiting for jobs to appear in pipeline..."
elapsed=0
jobs_json=""
found_count=0
while [[ $elapsed -lt $POLL_MAX_WAIT ]]; do
    jobs_json=$(api_get "/pipelines/${pipeline_id}/jobs?per_page=100") || true
    found_count=$(echo "$jobs_json" | python3 -c "
import sys, json
target = set('${JOB_ARRAY[*]}'.split())
print(len([j for j in json.load(sys.stdin) if j['name'] in target]))
" 2>/dev/null || echo "0")

    if [[ "$found_count" -ge "${#JOB_ARRAY[@]}" ]]; then break; fi
    sleep "$POLL_INTERVAL"
    elapsed=$((elapsed + POLL_INTERVAL))
done

if [[ "$found_count" -lt "${#JOB_ARRAY[@]}" ]]; then
    err "Timed out waiting for jobs. Found $found_count/${#JOB_ARRAY[@]}. Check CI rules include CI_PIPELINE_SOURCE=api."
fi

# --- Phase 5: Trigger manual jobs ---
log "All target jobs found. Triggering..."
echo ""

for job_name in "${JOB_ARRAY[@]}"; do
    current_job_id=$(echo "$jobs_json" | python3 -c "
import sys, json
for j in json.load(sys.stdin):
    if j['name'] == '${job_name}':
        print(j['id']); break
")
    log "[$job_name] Playing manual job (job #${current_job_id})..."
    play_resp=$(api_post "/jobs/${current_job_id}/play") || {
        warn "[$job_name] Failed to play job #${current_job_id}"
        continue
    }
    job_url=$(echo "$play_resp" | json_val "['web_url']")
    log "[$job_name] Triggered. URL: $job_url"
done

if [[ "$WAIT_MODE" != "true" ]]; then
    echo ""
    echo "=========================================="
    echo "  JOBS TRIGGERED"
    echo "=========================================="
    echo "  Pipeline:  #${pipeline_id}"
    echo "  URL:       $pipeline_url"
    echo "  Branch:    $BRANCH"
    echo "  Commit:    $short_sha"
    echo "  Jobs:      ${JOB_ARRAY[*]}"
    echo "=========================================="
    exit 0
fi

# --- Phase 6: Wait for triggered jobs with retry ---
log "Waiting for triggered jobs to complete..."

jobs_json=$(api_get "/pipelines/${pipeline_id}/jobs?per_page=100") || \
    err "Failed to fetch pipeline jobs"

succeeded_jobs=()
failed_jobs=()

for job_name in "${JOB_ARRAY[@]}"; do
    current_job_id=$(echo "$jobs_json" | python3 -c "
import sys, json
for j in json.load(sys.stdin):
    if j['name'] == '${job_name}':
        print(j['id']); break
")

    job_ok=false
    for attempt in $(seq 1 $((MAX_RETRIES + 1))); do
        if [[ $attempt -gt 1 ]]; then
            log "[$job_name] Retrying (attempt $attempt/$((MAX_RETRIES + 1)), retry $((attempt - 1))/$MAX_RETRIES)..."
            retry_resp=$(api_post "/jobs/${current_job_id}/retry") || {
                warn "[$job_name] Retry API call failed"
                break
            }
            current_job_id=$(echo "$retry_resp" | json_val "['id']")
            job_url=$(echo "$retry_resp" | json_val "['web_url']")
            log "[$job_name] Retried as job #${current_job_id}, URL: $job_url"
        fi

        if wait_for_job "$job_name" "$current_job_id"; then
            job_ok=true
            break
        fi
    done

    if [[ "$job_ok" == "true" ]]; then
        succeeded_jobs+=("$job_name")
        log "[$job_name] Extracting built images from job log..."
        while IFS= read -r img; do
            [[ -n "$img" ]] && ALL_IMAGES+=("$img")
        done < <(extract_images_from_job "$current_job_id" "$IMAGE" "$short_sha")
    else
        failed_jobs+=("$job_name")
        warn "Job '$job_name' failed after all retries. Aborting remaining jobs."
        break
    fi
done

echo ""
echo "=========================================="
if [[ ${#failed_jobs[@]} -eq 0 ]]; then
    echo "  CI COMPLETED SUCCESSFULLY"
else
    echo "  CI COMPLETED WITH FAILURES"
fi
echo "=========================================="
echo "  Pipeline:  #${pipeline_id}"
echo "  URL:       $pipeline_url"
echo "  Branch:    $BRANCH"
echo "  Commit:    $short_sha"
[[ ${#succeeded_jobs[@]} -gt 0 ]] && echo "  Succeeded: ${succeeded_jobs[*]}"
[[ ${#failed_jobs[@]} -gt 0 ]]    && echo "  Failed:    ${failed_jobs[*]}"
if [[ ${#ALL_IMAGES[@]} -gt 0 ]]; then
    echo "  Images:"
    for img in "${ALL_IMAGES[@]}"; do
        echo "    - $img"
    done
fi
echo "=========================================="

[[ ${#failed_jobs[@]} -gt 0 ]] && exit 1
exit 0
