#!/usr/bin/env bash
# macOS / Linux kurulumu: skills/ altındaki her skill'i ~/.claude/skills altına
# bağlar ya da kopyalar.
#   ./scripts/install.sh              sembolik bağ (git pull ile kendiliğinden güncellenir)
#   ./scripts/install.sh --copy       bağımsız kopya
#   ./scripts/install.sh --uninstall  bu repodan kurulan skill'leri kaldırır
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_ROOT="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
MODE="link"

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --uninstall) MODE="uninstall" ;;
    *) echo "Bilinmeyen seçenek: $arg" >&2; exit 2 ;;
  esac
done

install_skill() {
  local src="$1" name dest backup
  name="$(basename "$src")"
  dest="$SKILLS_ROOT/$name"
  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ]; then
    backup="$dest.bak-$(date +%Y%m%d-%H%M%S)"
    mv "$dest" "$backup"
    echo "Var olan kurulum yedeklendi: $backup"
  fi
  if [ "$MODE" = "uninstall" ]; then
    echo "Kaldırıldı: $dest"
  elif [ "$MODE" = "link" ]; then
    ln -s "$src" "$dest"
    echo "Bağlandı:   $dest"
  else
    cp -R "$src" "$dest"
    echo "Kopyalandı: $dest"
  fi
}

mkdir -p "$SKILLS_ROOT"
for src in "$REPO_DIR"/skills/*/; do
  src="${src%/}"
  [ -f "$src/SKILL.md" ] && install_skill "$src"
done


[ "$MODE" = "uninstall" ] || echo "Claude Code'u yeniden başlatın; /skills listesinde görünmeliler."
