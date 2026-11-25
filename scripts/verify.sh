#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
"${PYTHON:-python}" -m unittest discover -s tests -v
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
node examples/video/render.mjs examples/video/sample.json "$stage/sample.mp4"
printf '{"title":"%048d","subtitle":"%096d"}\n' 0 0 | tr 0 W > "$stage/bounds.json"
node examples/video/render.mjs "$stage/bounds.json" "$stage/bounds.mp4"
printf '{"title":"%060d","subtitle":"Overflow"}\n' 0 > "$stage/invalid.json"
if node examples/video/render.mjs "$stage/invalid.json" "$stage/rejected.mp4" > "$stage/errors" 2>&1; then
  echo 'Invalid video props were accepted' >&2
  exit 1
fi
grep -q 'Expected an ASCII title' "$stage/errors"
test ! -e "$stage/rejected.mp4"
echo 'Remotion render, FFmpeg decode, and invalid props checks passed'
