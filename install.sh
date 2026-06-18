#!/bin/bash
# install.sh — Setup script for ne0suite toolchain

set -e

RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
RESET="\033[0m"

# 1. System Package Check (Arch)
if [ -f /etc/arch-release ]; then
    echo -e "${GREEN}[*] Arch Linux detected. Verifying/installing system dependencies...${RESET}"
    SUDO=""
    [ "$EUID" -ne 0 ] && SUDO="sudo"
    $SUDO pacman -Sy --needed --noconfirm python git curl bind nmap rust cargo
else
    echo -e "${YELLOW}[!] Non-Arch system detected. Ensure python, git, curl, bind, nmap, and cargo are installed.${RESET}"
fi

# 2. Install ne0suite itself
echo -e "${GREEN}[*] Installing ne0suite...${RESET}"
pip install -e .

# 3. Config dirs
echo -e "${GREEN}[*] Creating configuration directories...${RESET}"
mkdir -p ~/.grimoire ~/.wraith-net

if [ ! -f ~/.grimoire/config.json ]; then
    echo '{"shodan": "", "abuseipdb": "", "virustotal": ""}' > ~/.grimoire/config.json
    echo -e "${GREEN}[+] Created ~/.grimoire/config.json${RESET}"
fi

if [ ! -f ~/.wraith-net/config.json ]; then
    echo '{"virustotal": "", "github": ""}' > ~/.wraith-net/config.json
    echo -e "${GREEN}[+] Created ~/.wraith-net/config.json${RESET}"
fi

# 4. Shell aliases
SHELL_RC=""
[ -f "$HOME/.zshrc" ]  && SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"

if [ -n "$SHELL_RC" ]; then
    echo -e "${GREEN}[*] Checking shell aliases in $SHELL_RC...${RESET}"

    ALIASES=(
        "alias ne0='ne0suite'"
        "alias n0s='ne0suite'"
        "alias g='ne0suite grimoire'"
        "alias wn='ne0suite wraith'"
        "alias sh='ne0suite shadowci'"
        "alias c2='ne0suite akame'"
        "alias analyze='ne0suite sigil'"
    )

    for alias_line in "${ALIASES[@]}"; do
        if ! grep -qF "$alias_line" "$SHELL_RC"; then
            echo "$alias_line" >> "$SHELL_RC"
            echo -e "${GREEN}[+] Added: $alias_line${RESET}"
        fi
    done
    echo -e "${YELLOW}[!] Run 'source $SHELL_RC' to load aliases.${RESET}"
fi

# 5. Verify
echo -e "${GREEN}[*] Verifying installation...${RESET}"
if command -v ne0suite >/dev/null 2>&1; then
    ne0suite status
else
    python -m ne0suite.cli status
fi
