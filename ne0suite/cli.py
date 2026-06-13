#!/usr/bin/env python3
"""ne0suite - one entry point for the toolchain.

Every tool i've written ends up in ~/dev/projects with its own way of being
invoked. This is the start of something that routes to all of them.
"""

import sys

VERSION = "0.0.1"


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print("ne0suite - unified operator CLI")
        print("usage: ne0suite <tool> [args...]")
        sys.exit(0)

    if args[0] in ("-v", "--version", "version"):
        print(f"ne0suite v{VERSION}")
        sys.exit(0)

    print(f"ne0suite: unknown command '{args[0]}' (not wired up yet)")
    sys.exit(1)


if __name__ == "__main__":
    main()
