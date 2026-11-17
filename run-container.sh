#!/bin/sh
set -eu
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 show|grade RUN_DIR" >&2
    exit 2
fi
action=$1
run_dir=$(cd "$2" && pwd -P)
case "$action" in
    show)
        docker run --rm --network none --read-only --cap-drop ALL \
            --security-opt no-new-privileges \
            --mount "type=bind,src=$run_dir/solver,dst=/task,readonly" \
            quality-record-bench:solver \
            python -c 'from pathlib import Path; print(Path("/task/instructions.txt").read_text()); print(Path("/task/cases.json").read_text())'
        ;;
    grade)
        docker run --rm --network none --read-only --cap-drop ALL \
            --security-opt no-new-privileges \
            --mount "type=bind,src=$run_dir/author/key.json,dst=/key.json,readonly" \
            --mount "type=bind,src=$run_dir/submission.json,dst=/submission.json,readonly" \
            quality-record-bench:verifier /key.json /submission.json
        ;;
    *)
        echo "Unknown action: $action" >&2
        exit 2
        ;;
esac
