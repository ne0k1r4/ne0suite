#!/usr/bin/env python3
"""ne0suite - one entry point for the toolchain.

Every tool i've written ends up in ~/dev/projects with its own way of being
invoked. This routes to all of them.
"""

import os
import shutil
import sys
from pathlib import Path

VERSION = "0.0.1"

# raw ANSI, zero deps, works in any terminal that isn't ancient
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER_ART = [
    "  ███╗   ██╗███████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗",
    "  ████╗  ██║██╔════╝██╔═══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝",
    "  ██╔██╗ ██║█████╗  ██║   ██║███████╗██║   ██║██║   ██║   █████╗  ",
    "  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║   ██║██║   ██║   ██╔══╝  ",
    "  ██║ ╚████║███████╗╚██████╔╝███████║╚██████╔╝██║   ██║   ███████╗",
    "  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝",
]

SEPARATOR = f"  {DIM}{'─' * 66}{RESET}"

# all tools live under ~/dev/projects/ - change this if your layout differs
PROJECTS = Path.home() / "dev" / "projects"

TOOLS = {
    "grimoire": {
        "cmd":       "grimoire",
        "project":   "grimoire",
        "desc":      "Unified operator toolkit — recon, payloads, C2, stego, blue team",
    },
    "lightscan": {
        "cmd":       "lightscan",
        "project":   "Lightscan",  # capital L - that's how the repo is named
        "desc":      "Async network scanner — ports, CVEs, scripts, web, brute force",
    },
    "wraith": {
        "cmd":       "wraith",
        "project":   "wraith-net",
        "desc":      "Attack surface intel — subdomains, ASN, DNS security, takeover",
    },
    "shadowci": {
        "cmd":       "shadowci",
        "project":   "shadowci",
        "desc":      "CI/CD security scanner — secrets, CVEs, misconfigs",
    },
}

# short aliases so i don't have to type the full name every single time
ALIASES = {
    "ls":      "lightscan",
    "wn":      "wraith",
    "g":       "grimoire",
    "sh":      "shadowci",
    "scan":    "lightscan",  # muscle memory from nmap days
    "recon":   "wraith",
    "shadow":  "shadowci",
}


def project_path(tool):
    return PROJECTS / TOOLS[tool]["project"]


def print_banner():
    print()
    for line in BANNER_ART:
        print(f"{BOLD}{line}{RESET}")
    print(SEPARATOR)
    print()


def cmd_dispatch(tool, args):
    # resolve aliases before anything else
    tool = ALIASES.get(tool, tool)

    if tool not in TOOLS:
        print(f"  {RED}[!]{RESET} Unknown tool: {tool}")
        print(f"  {DIM}Available: {', '.join(TOOLS.keys())}{RESET}")
        print(f"  {DIM}Aliases:   {', '.join(ALIASES.keys())}{RESET}")
        sys.exit(1)

    if not shutil.which(TOOLS[tool]["cmd"]):
        print(f"  {RED}[!]{RESET} {BOLD}{tool}{RESET} is not installed")
        print(f"  {DIM}expected:  {project_path(tool)}{RESET}")
        sys.exit(1)

    os.execvp(TOOLS[tool]["cmd"], [TOOLS[tool]["cmd"]] + args)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_banner()
        print("usage: ne0suite <tool> [args...]")
        sys.exit(0)

    if args[0] in ("-v", "--version", "version"):
        print(f"ne0suite v{VERSION}")
        sys.exit(0)

    cmd_dispatch(args[0].lower(), args[1:])


if __name__ == "__main__":
    main()
