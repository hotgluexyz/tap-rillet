#!/usr/bin/env bash
# Idempotent Cloud Agent setup for the Hotglue Cursor plugin shell helpers.
set -euo pipefail

if ! command -v zsh >/dev/null 2>&1; then
    sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq zsh
fi

PLUGIN_INSTALL=""
while IFS= read -r candidate; do
    if [[ -f "$candidate" ]]; then
        PLUGIN_INSTALL="$candidate"
        break
    fi
done < <(find "${HOME}/.cursor/plugins/cache/hotglue" -path '*/shell/install.sh' 2>/dev/null)

if [[ -n "$PLUGIN_INSTALL" ]]; then
    bash "$PLUGIN_INSTALL" --non-interactive
else
    echo "hotglue plugin install.sh not found under ~/.cursor/plugins/cache/hotglue" >&2
    exit 1
fi

mkdir -p "${HOME}/.config/hotglue-cursor"
cp -f "$(dirname "$0")/hotglue-bash-init.sh" "${HOME}/.config/hotglue-cursor/bash-init.sh"

BASHRC="${HOME}/.bashrc"
MARKER="# Hotglue Cursor plugin (bash shells / Cloud Agent)"
if [[ ! -f "$BASHRC" ]] || ! grep -qF "$MARKER" "$BASHRC"; then
    {
        echo ""
        echo "$MARKER"
        echo '[[ -r "$HOME/.config/hotglue-cursor/bash-init.sh" ]] && source "$HOME/.config/hotglue-cursor/bash-init.sh"'
    } >> "$BASHRC"
fi
