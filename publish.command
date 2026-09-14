#!/bin/bash
# macOS convenience launcher. Does not install tools, print tokens, overwrite a repository, or force-push.
set -euo pipefail
cd "$(dirname "$0")"
for executable in python3 git gh; do
  if ! command -v "$executable" >/dev/null 2>&1; then
    echo "缺少 $executable。请先安装本地 Python、Git 和 GitHub CLI。"
    echo "已使用 Homebrew 的 Mac：brew install gh；本脚本不会自动安装。"
    read -r -p "按回车退出…" _ || true
    exit 1
  fi
done
python3 scripts/check_release.py
if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  gh auth login --hostname github.com --git-protocol https --web
fi
python3 scripts/publish_github.py --owner wz20 --repo explain-motion --public
read -r -p "查看上方真实发布结果；按回车关闭…" _ || true
