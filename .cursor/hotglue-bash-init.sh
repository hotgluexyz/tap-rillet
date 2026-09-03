# Bash init for Cloud Agent shells (zsh plugin helpers run via zsh -lic).
[ -r "$HOME/.config/hotglue-cursor/env.sh" ] && source "$HOME/.config/hotglue-cursor/env.sh"

# Run any hotglue plugin shell helper. Usage: hg job-summary <url>
hg() {
    if [[ $# -eq 0 ]]; then
        zsh -lic plugin-help
        return
    fi
    zsh -lic "$*"
}

plugin-help() { zsh -lic plugin-help; }
