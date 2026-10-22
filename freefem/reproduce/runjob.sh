#!/bin/bash
# runjob.sh WORK JOBFILE N : run line N of the job list (comments and blank lines removed) inside WORK.
# Resumable: a job that finished is marked in WORK/.done and skipped next time.
WORK=$1; LIST=$2; N=$3
cd "$WORK" || exit 1
cmd=$(sed -n "${N}p" "$LIST")
tag=$(basename "$LIST" .txt)_$N
mkdir -p .done .joblogs
[ -e ".done/$tag" ] && exit 0
echo "$(date '+%F %T') START $tag  $cmd" >> progress.log
if bash -c "$cmd" > ".joblogs/$tag.log" 2>&1; then
  touch ".done/$tag"; echo "$(date '+%F %T') END   $tag" >> progress.log
else
  echo "$(date '+%F %T') FAIL  $tag (see .joblogs/$tag.log)" >> progress.log
fi
exit 0
