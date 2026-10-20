#!/usr/bin/env bash
# Commit any changes and push to main (GitHub Pages serves from main /).
set -euo pipefail
cd "$(dirname "$0")"
git add -A
if git diff --cached --quiet; then
  echo "没有变化，无需发布。"
  exit 0
fi
git commit -q -m "更新热榜 $(TZ=Asia/Shanghai date +%F)"
git push -q origin main
echo "已发布：$(git log -1 --format='%h %s')"
