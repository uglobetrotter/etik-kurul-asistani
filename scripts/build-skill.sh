#!/usr/bin/env bash
# claude.ai / Claude Desktop'a yüklenecek .skill paketlerini (her skill için bir tane) dist/ altına üretir.
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$REPO_DIR/.claude-plugin/plugin.json")"
mkdir -p "$REPO_DIR/dist"
cd "$REPO_DIR/skills"
for dir in */; do
  name="${dir%/}"
  [ -f "$name/SKILL.md" ] || continue
  out="$REPO_DIR/dist/$name-v$VERSION.skill"
  rm -f "$out"
  zip -r -X -q "$out" "$name" -x '*.DS_Store' '*/__pycache__/*' '*.pyc'
  echo "$out"
done
