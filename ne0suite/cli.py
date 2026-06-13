#!/usr/bin/env python3
"""ne0suite - one entry point for the toolchain.

Every tool i've written ends up in ~/dev/projects with its own way of being
invoked. This is the start of something that routes to all of them.
"""

import sys

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


def print_banner():
    print()
    for line in BANNER_ART:
        print(f"{BOLD}{line}{RESET}")
    print(SEPARATOR)
    print()


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_banner()
        print("usage: ne0suite <tool> [args...]")
        sys.exit(0)

    if args[0] in ("-v", "--version", "version"):
        print(f"ne0suite v{VERSION}")
        sys.exit(0)

    print(f"ne0suite: unknown command '{args[0]}' (not wired up yet)")
    sys.exit(1)


if __name__ == "__main__":
    main()
