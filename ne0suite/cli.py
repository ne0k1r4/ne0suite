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
import time
from pathlib import Path

VERSION = "1.0.0"

# raw ANSI, zero deps, works in any terminal that isn't ancient
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GOLD = "\033[38;2;200;160;60m"  # 24-bit, matches the notebook cover
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

# deep crimson -> bright red, one stop per banner line
BANNER_GRADIENT = [
    "\033[38;2;120;20;20m",
    "\033[38;2;160;25;25m",
    "\033[38;2;200;35;35m",
    "\033[38;2;220;50;50m",
    "\033[38;2;240;70;70m",
    "\033[38;2;255;90;90m",
]

TAGLINE = f"  {DIM}Unified Operator Suite · by Light (Neok1ra) · v{VERSION}{RESET}"
SEPARATOR = f"  {DIM}{'─' * 66}{RESET}"


def print_banner(animate=True):
    """Line-by-line gradient reveal when stdout is a tty, plain dump otherwise."""
    print()
    if animate and sys.stdout.isatty():
        for i, line in enumerate(BANNER_ART):
            color = BANNER_GRADIENT[i]
            sys.stdout.write(f"{BOLD}{color}{line}{RESET}\n")
            sys.stdout.flush()
            time.sleep(0.04)
        time.sleep(0.08)
        # tagline typed out character by character
        tagline_raw = f"  Unified Operator Suite · by Light (Neok1ra) · v{VERSION}"
        for ch in tagline_raw:
            sys.stdout.write(f"{DIM}{ch}{RESET}")
            sys.stdout.flush()
            time.sleep(0.008)
        print()
    else:
        for i, line in enumerate(BANNER_ART):
            print(f"{BOLD}{BANNER_GRADIENT[i]}{line}{RESET}")
        print(TAGLINE)
    print(SEPARATOR)
    print()


# all tools live under ~/dev/projects/ - change this if your layout differs
PROJECTS = Path.home() / "dev" / "projects"

# run modes: "bin" = PATH binary (execvp), "cargo" = Rust project,
# "bash" = shell script project.
# ver_probe: ("flag", <flag>) probes a PATH binary; ("cargo_meta",) reads
# Cargo.toml directly; None for tools without a version.
TOOLS = {
    "grimoire": {
        "cmd":       "grimoire",
        "project":   "grimoire",
        "run":       "bin",
        "desc":      "Unified operator toolkit — recon, payloads, C2, stego, blue team",
        "ver_probe": ("flag", "--version"),
        "install":   "pip install -e ~/dev/projects/grimoire",
    },
    "lightscan": {
        "cmd":       "lightscan",
        "project":   "Lightscan",  # capital L - that's how the repo is named
        "run":       "bin",
        "desc":      "Async network scanner — ports, CVEs, scripts, web, brute force",
        "ver_probe": ("flag", "-v"),
        "install":   "pip install -e ~/dev/projects/Lightscan",
    },
    "wraith": {
        "cmd":       "wraith",
        "project":   "wraith-net",
        "run":       "bin",
        "desc":      "Attack surface intel — subdomains, ASN, DNS security, takeover",
        "ver_probe": ("flag", "version"),
        "install":   "pip install -e ~/dev/projects/wraith-net",
    },
    "shadowci": {
        "cmd":       "shadowci",
        "project":   "shadowci",
        "run":       "bin",
        "desc":      "CI/CD security scanner — secrets, CVEs, misconfigs",
        "ver_probe": ("flag", "version"),
        "install":   "pip install -e ~/dev/projects/shadowci",
    },
    "akame": {
        "cmd":       None,  # no PATH binary — invoked via cargo or target/release
        "project":   "akame",
        "run":       "cargo",
        "desc":      "C2 teamserver — operator comms, implant mgmt (Rust)",
        "ver_probe": ("cargo_meta",),
        "install":   "cd ~/dev/projects/akame && cargo build --release",
    },
    "sigil": {
        "cmd":       "sigil",
        "project":   "sigil",
        "run":       "cargo",
        "desc":      "Static PE/ELF binary analyzer — anti-debug, anti-cheat, YARA (Rust)",
        "ver_probe": ("cargo_meta",),
        "install":   "cd ~/dev/projects/sigil && cargo build --release",
    },
    "kira-installer": {
        "cmd":       None,  # just runs install.sh, nothing lands on PATH
        "project":   "kira-installer",
        "run":       "bash",
        "desc":      "One-shot environment bootstrap for the full toolchain",
        "ver_probe": None,  # a script, not a versioned binary
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

# pulled from sigil's clap subcommands in src/main.rs
SIGIL_SUBCMDS = [
    "scan", "headers", "strings", "imports", "symbols", "tls",
    "hashes", "entropy", "antidebug", "anticheat", "disasm",
    "pattern", "diff", "report", "batch", "overlay", "resources",
    "clr", "full-disasm", "yara",
]

HELP = f"""  {BOLD}ne0suite{RESET} {DIM}<tool> [args...]  |  status  |  help{RESET}

  {CYAN}grimoire{RESET} {DIM}g{RESET}          ·  {CYAN}lightscan{RESET} {DIM}ls  scan{RESET}
  {CYAN}wraith{RESET} {DIM}wn  recon{RESET}    ·  {CYAN}shadowci{RESET} {DIM}sh{RESET}
  {CYAN}akame{RESET} {DIM}c2{RESET}            ·  {CYAN}sigil{RESET} {DIM}analyze{RESET}
  {CYAN}kira-installer{RESET} {DIM}install{RESET}
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
        if info.get("cmd") and shutil.which(info["cmd"]):
            return True
        if cargo_release_bin(tool):
            return True
        return project_path(tool).exists()
    if info["run"] == "bash":
        return project_path(tool).exists()
    return False


def check_tool(name):
    """Return (ok, version_string) for one tool."""
    if not is_installed(name):
        return False, "not installed"

    info = TOOLS[name]
    probe = info.get("ver_probe")

    if probe is None:
        return True, "project found"

    if probe[0] == "cargo_meta":
        # read Cargo.toml directly instead of invoking cargo for a version
        toml = project_path(name) / "Cargo.toml"
        try:
            for line in toml.read_text().splitlines():
                if line.strip().startswith("version"):
                    v = line.split("=")[1].strip().strip('"')
                    return True, f"v{v}"
        except Exception:
            pass
        rbin = cargo_release_bin(name)
        if rbin:
            try:
                r = subprocess.run([str(rbin), "--version"],
                                   capture_output=True, text=True, timeout=5)
                out = (r.stdout + r.stderr).strip()
                for word in out.split():
                    if word.startswith("v") and any(c.isdigit() for c in word):
                        return True, word[:12]
            except Exception:
                pass
        return True, "built"

    if probe[0] == "flag":
        try:
            r = subprocess.run([info["cmd"], probe[1]],
                               capture_output=True, text=True, timeout=5)
            out = (r.stdout + r.stderr).strip()
            for line in out.splitlines():
                for word in line.split():
                    if word.startswith("v") and any(c.isdigit() for c in word):
                        return True, word[:12]
            return True, "installed"
        except Exception:
            return True, "installed"

    return True, "installed"


def _spinner(msg, duration=0.6):
    """Quick inline spinner while probing the toolchain."""
    if not sys.stdout.isatty():
        print(f"  {msg}")
        return
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.monotonic() + duration
    i = 0
    while time.monotonic() < end_time:
        sys.stdout.write(f"\r  {RED}{frames[i % len(frames)]}{RESET} {msg}")
        sys.stdout.flush()
        time.sleep(0.06)
        i += 1
    sys.stdout.write(f"\r  {GREEN}✔{RESET} {msg}\n")
    sys.stdout.flush()


def cmd_status():
    print_banner()

    _spinner("Scanning toolchain...", 0.5)
    print()

    print(f"  {BOLD}{'TOOL':<16} {'STATUS':<18} {'DESCRIPTION'}{RESET}")
    print(f"  {'─' * 66}")

    for name, info in TOOLS.items():
        ok, ver = check_tool(name)
        raw = f"✔ {ver}" if ok else "✗ missing"
        color = GREEN if ok else YELLOW
        padded = f"{color}{raw:<18}{RESET}"
        print(f"  {CYAN}{name:<16}{RESET} {padded} {DIM}{info['desc'][:40]}{RESET}")

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
        if info.get("cmd"):
            print(f"  {DIM}or PATH:   {info['cmd']}{RESET}")
        print(f"\n  {BOLD}install:{RESET}")
        print(f"  {GOLD}${RESET}  {info['install']}\n")
        if tool == "sigil":
            print(f"  {DIM}subcommands: {', '.join(SIGIL_SUBCMDS)}{RESET}\n")
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
