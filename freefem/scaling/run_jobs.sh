#!/usr/bin/env bash
# usage: bash run_jobs.sh JOBFILE [NPROC]
# Runs every non-comment line of JOBFILE from this folder, NPROC at a time (default 4).
# A job whose log already ends with a "# SUMMARY" line is skipped, so the command can be repeated after an interruption.
# Each command is passed to bash as one argument: macOS xargs limits -I replacements to 255 characters.
set -u
cd "$(dirname "$0")"
jobs="$1"
np="${2:-4}"
mkdir -p scaling
for f in nsb.edp mms.idp; do [ -f "$f" ] || cp "../$f" .; done
grep -v '^#' "$jobs" | grep -v '^[[:space:]]*$' | while IFS= read -r cmd; do
    out="${cmd##*-out }"
    out="${out%% *}"
    if [ -f "$out" ] && grep -q '^# SUMMARY' "$out"; then
        continue
    fi
    printf '%s\0' "$cmd"
done | xargs -0 -n 1 -P "$np" bash -c '[ -n "$1" ] || exit 0; eval "$1" > /dev/null 2>&1; o="${1##*-out }"; echo "done: ${o%% *}"' _
echo "finished $jobs"
