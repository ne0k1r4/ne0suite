#!/bin/bash
# install.sh — Setup script for ne0suite toolchain

set -e

RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
RESET="\033[0m"

# 1. System Package Check / Install (if on Arch Linux)
if [ -f /etc/arch-release ]; then
    echo -e "${GREEN}[*] Arch Linux detected. Verifying/installing system dependencies...${RESET}"
    if [ "$EUID" -ne 0 ]; then
        SUDO="sudo"
    else
        SUDO=""
    fi
    $SUDO pacman -Sy --needed --noconfirm python git curl bind nmap
else
    echo -e "${YELLOW}[!] Non-Arch system detected. Skipping system package installation. Ensure python, git, curl, bind, and nmap are installed.${RESET}"
fi

# 2. Install ne0suite itself
echo -e "${GREEN}[*] Installing ne0suite...${RESET}"
pip install -e .

# 3. Create config directories and templates
echo -e "${GREEN}[*] Creating configuration directories...${RESET}"
mkdir -p ~/.grimoire ~/.wraith-net

if [ ! -f ~/.grimoire/config.json ]; then
    echo '{"shodan": "", "abuseipdb": "", "virustotal": ""}' > ~/.grimoire/config.json
    echo -e "${GREEN}[+] Created ~/.grimoire/config.json template${RESET}"
fi

if [ ! -f ~/.wraith-net/config.json ]; then
    echo '{"virustotal": "", "github": ""}' > ~/.wraith-net/config.json
    echo -e "${GREEN}[+] Created ~/.wraith-net/config.json template${RESET}"
fi

# 4. Add aliases to shell config
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo -e "${GREEN}[*] Checking shell aliases in $SHELL_RC...${RESET}"
    
    ALIASES=(
        "alias g='ne0suite grimoire'"
        "alias ls='ne0suite lightscan'"
        "alias wn='ne0suite wraith'"
        "alias sh='ne0suite shadowci'"
        "alias n0s='ne0suite'"
    )
    
    for alias_line in "${ALIASES[@]}"; do
        if ! grep -qF "$alias_line" "$SHELL_RC"; then
            echo "$alias_line" >> "$SHELL_RC"
            echo -e "${GREEN}[+] Added: $alias_line${RESET}"
        fi
    done
    echo -e "${YELLOW}[!] Shell aliases added. Please run 'source $SHELL_RC' to load them.${RESET}"
fi

# 5. Verify installation
echo -e "${GREEN}[*] Verifying toolchain installation status...${RESET}"
if command -v ne0suite >/dev/null 2>&1; then
    ne0suite status
else
    python -m ne0suite.cli status
fi
