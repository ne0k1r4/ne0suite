#!/usr/bin/env python3
"""ne0suite - one entry point for the toolchain.

Every tool i've written ends up in ~/dev/projects with its own way of being
invoked, its own version flag, and its own way of being installed. This
dispatcher exists so i don't have to remember any of that.
"""

import os
import shutil
import subprocess
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

TAGLINE = f"  {DIM}Unified Operator Suite · by Light (Neok1ra) · v{VERSION}{RESET}"
SEPARATOR = f"  {DIM}{'─' * 66}{RESET}"

# all tools live under ~/dev/projects/ - change this if your layout differs
PROJECTS = Path.home() / "dev" / "projects"

# run modes: "bin" = PATH binary (execvp), "cargo" = Rust project,
# "bash" = shell script project
TOOLS = {
    "grimoire": {
        "cmd":       "grimoire",
        "project":   "grimoire",
        "run":       "bin",
        "desc":      "Unified operator toolkit — recon, payloads, C2, stego, blue team",
        "install":   "pip install -e ~/dev/projects/grimoire",
    },
    "lightscan": {
        "cmd":       "lightscan",
        "project":   "Lightscan",  # capital L - that's how the repo is named
        "run":       "bin",
        "desc":      "Async network scanner — ports, CVEs, scripts, web, brute force",
        "install":   "pip install -e ~/dev/projects/Lightscan",
    },
    "wraith": {
        "cmd":       "wraith-net",  # binary name differs from the subcommand key
        "project":   "wraith-net",
        "run":       "bin",
        "desc":      "Attack surface intel — subdomains, ASN, DNS security, takeover",
        "install":   "pip install -e ~/dev/projects/wraith-net",
    },
    "shadowci": {
        "cmd":       "shadowci",
        "project":   "shadowci",
        "run":       "bin",
        "desc":      "CI/CD security scanner — secrets, CVEs, misconfigs",
        "install":   "pip install -e ~/dev/projects/shadowci",
    },
    "akame": {
        "cmd":       None,  # no PATH binary — invoked via cargo or target/release
        "project":   "akame",
        "run":       "cargo",
        "desc":      "C2 teamserver — operator comms, implant mgmt (Rust)",
        "install":   "cd ~/dev/projects/akame && cargo build --release",
    },
    "sigil": {
        "cmd":       None,
        "project":   "sigil",
        "run":       "cargo",
        "desc":      "Static PE/ELF binary analyzer — anti-debug, anti-cheat, YARA (Rust)",
        "install":   "cd ~/dev/projects/sigil && cargo build --release",
    },
    "kira-installer": {
        "cmd":       None,  # just runs install.sh, nothing lands on PATH
        "project":   "kira-installer",
        "run":       "bash",
        "desc":      "One-shot environment bootstrap for the full toolchain",
        "install":   "git clone https://github.com/ne0k1r4/kira-installer ~/dev/projects/kira-installer",
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
    "c2":      "akame",
    "analyze": "sigil",
    "install": "kira-installer",
}

HELP = f"""  {BOLD}ne0suite{RESET} {DIM}<tool> [args...]  |  status  |  help{RESET}

  {CYAN}grimoire{RESET}   {DIM}g{RESET}          Recon, C2, payloads, stego
  {CYAN}lightscan{RESET}  {DIM}ls  scan{RESET}   Network scanner
  {CYAN}wraith{RESET}     {DIM}wn  recon{RESET}  Attack surface intel
  {CYAN}shadowci{RESET}   {DIM}sh{RESET}         CI/CD security scanner
  {CYAN}akame{RESET}      {DIM}c2{RESET}         C2 teamserver {DIM}(Rust){RESET}
  {CYAN}sigil{RESET}      {DIM}analyze{RESET}    PE/ELF static analyzer {DIM}(Rust){RESET}
  {CYAN}kira-installer{RESET} {DIM}install{RESET} Env bootstrap
"""


def project_path(tool):
    return PROJECTS / TOOLS[tool]["project"]


def cargo_release_bin(tool):
    # check if the project has already been built - avoids triggering cargo
    pdir = project_path(tool)
    name = TOOLS[tool].get("cmd") or tool
    bin_path = pdir / "target" / "release" / name
    return bin_path if bin_path.exists() else None


def is_installed(tool):
    info = TOOLS[tool]
    if info["run"] == "bin":
        return bool(shutil.which(info["cmd"]))
    if info["run"] == "cargo":
        if cargo_release_bin(tool):
            return True
        # project dir alone counts - cargo run will build it on first dispatch
        return project_path(tool).exists()
    if info["run"] == "bash":
        return project_path(tool).exists()
    return False


def print_banner():
    print()
    for line in BANNER_ART:
        print(f"{BOLD}{line}{RESET}")
    print(TAGLINE)
    print(SEPARATOR)
    print()


def cmd_status():
    print_banner()
    print(f"  {BOLD}{'TOOL':<16} {'STATUS':<18} {'DESCRIPTION'}{RESET}")
    print(f"  {'─' * 66}")
    for name, info in TOOLS.items():
        ok = is_installed(name)
        raw = "✔ installed" if ok else "✗ missing"
        color = GREEN if ok else YELLOW
        padded = f"{color}{raw:<18}{RESET}"
        print(f"  {CYAN}{name:<16}{RESET} {padded} {DIM}{info['desc'][:40]}{RESET}")

    print(f"\n  {DIM}Config:{RESET}")
    for label, path in [("GRIMOIRE", "~/.grimoire/config.json"),
                        ("WRAITH-NET", "~/.wraith-net/config.json")]:
        full = Path(path.replace("~", str(Path.home())))
        color = GREEN if full.exists() else DIM
        mark = "✔" if full.exists() else "✗"
        print(f"  {color}{mark}{RESET}  {label:<14} {DIM}{path}{RESET}")
    print()


def cmd_dispatch(tool, args):
    # resolve aliases before anything else
    tool = ALIASES.get(tool, tool)

    if tool not in TOOLS:
        print(f"  {RED}[!]{RESET} Unknown tool: {tool}")
        print(f"  {DIM}Available: {', '.join(TOOLS.keys())}{RESET}")
        print(f"  {DIM}Aliases:   {', '.join(ALIASES.keys())}{RESET}")
        sys.exit(1)

    if not is_installed(tool):
        info = TOOLS[tool]
        print(f"\n  {RED}[!]{RESET} {BOLD}{tool}{RESET} is not installed\n")
        print(f"  {DIM}expected:  {project_path(tool)}{RESET}")
        print(f"\n  {BOLD}install:{RESET}")
        print(f"  {YELLOW}${RESET}  {info['install']}\n")
        sys.exit(1)

    info = TOOLS[tool]
    pdir = project_path(tool)

    if os.environ.get("NE0_DEBUG"):
        print(f"  {DIM}[debug] tool={tool} run={info['run']} dir={pdir} args={args}{RESET}",
              file=sys.stderr)

    if info["run"] == "bin":
        os.execvp(info["cmd"], [info["cmd"]] + args)

    elif info["run"] == "cargo":
        if tool == "sigil":
            # PATH first, then the release binary, then cargo run
            if shutil.which("sigil"):
                os.execvp("sigil", ["sigil"] + args)
            rbin = cargo_release_bin("sigil")
            if rbin:
                os.execvp(str(rbin), [str(rbin)] + args)
            print(f"  {YELLOW}[!]{RESET} sigil not built yet, running via cargo "
                  f"(this will take a minute)", file=sys.stderr)
            result = subprocess.run(["cargo", "run", "--release", "--"] + args, cwd=pdir)
            sys.exit(result.returncode)
        else:
            rbin = cargo_release_bin(tool)
            if rbin:
                os.execvp(str(rbin), [str(rbin)] + args)
            else:
                print(f"  {YELLOW}[!]{RESET} {tool} not built yet, running via cargo "
                      f"(this will take a minute)", file=sys.stderr)
                result = subprocess.run(["cargo", "run", "--release", "--"] + args, cwd=pdir)
                sys.exit(result.returncode)

    elif info["run"] == "bash":
        result = subprocess.run(["bash", str(pdir / "install.sh")] + args, cwd=pdir)
        sys.exit(result.returncode)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_banner()
        print(HELP)
        sys.exit(0)

    if args[0] in ("-v", "--version", "version"):
        print(f"ne0suite v{VERSION}")
        sys.exit(0)

    if args[0] == "status":
        cmd_status()
        sys.exit(0)

    cmd_dispatch(args[0].lower(), args[1:])


if __name__ == "__main__":
    main()
