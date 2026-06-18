import sys
import os
import shutil
import subprocess
from pathlib import Path

VERSION = "1.2.0"

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GOLD   = "\033[38;2;200;160;60m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BANNER = f"""
{RED}{BOLD}  ███╗   ██╗███████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗
  ████╗  ██║██╔════╝██╔═══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝
  ██╔██╗ ██║█████╗  ██║   ██║███████╗██║   ██║██║   ██║   █████╗
  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║   ██║██║   ██║   ██╔══╝
  ██║ ╚████║███████╗╚██████╔╝███████║╚██████╔╝██║   ██║   ███████╗
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝{RESET}
  {DIM}Unified Operator Suite · by Light (Neok1ra) · v{VERSION}{RESET}
  {DIM}GRIMOIRE · LightScan · WRAITH-NET · ShadowCI · akame · sigil{RESET}
"""

PROJECTS = Path.home() / "dev" / "projects"

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
        "project":   "Lightscan",
        "run":       "bin",
        "desc":      "Async network scanner — ports, CVEs, scripts, web, brute force",
        "ver_probe": ("flag", "-v"),
        "install":   "pip install -e ~/dev/projects/Lightscan",
    },
    "wraith": {
        "cmd":       "wraith-net",
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
        "cmd":       None,
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
        "cmd":       None,
        "project":   "kira-installer",
        "run":       "bash",
        "desc":      "One-shot environment bootstrap for the full toolchain",
        "ver_probe": None,
        "install":   "git clone https://github.com/ne0k1r4/kira-installer ~/dev/projects/kira-installer",
    },
}

ALIASES = {
    "ls":      "lightscan",
    "wn":      "wraith",
    "g":       "grimoire",
    "sh":      "shadowci",
    "scan":    "lightscan",
    "recon":   "wraith",
    "shadow":  "shadowci",
    "c2":      "akame",
    "analyze": "sigil",
    "install": "kira-installer",
}

SIGIL_SUBCMDS = [
    "scan", "headers", "strings", "imports", "symbols", "tls",
    "hashes", "entropy", "antidebug", "anticheat", "disasm",
    "pattern", "diff", "report", "batch", "overlay", "resources",
    "clr", "full-disasm", "yara",
]

HELP = f"""
{RED}{BOLD}ne0suite{RESET} — Unified Operator CLI  {DIM}v{VERSION}{RESET}

{BOLD}Usage:{RESET}
  ne0suite <tool> [args...]
  ne0suite status
  ne0suite help

{BOLD}Tools:{RESET}
  {CYAN}grimoire{RESET}        {DIM}GRIMOIRE — full operator toolkit{RESET}
  {CYAN}lightscan{RESET}       {DIM}LightScan — async network scanner{RESET}
  {CYAN}wraith{RESET}          {DIM}WRAITH-NET — attack surface intel{RESET}
  {CYAN}shadowci{RESET}        {DIM}ShadowCI — CI/CD security scanner{RESET}
  {CYAN}akame{RESET}           {DIM}akame — C2 teamserver (Rust){RESET}
  {CYAN}sigil{RESET}           {DIM}sigil — static PE/ELF analyzer, anti-debug/cheat (Rust){RESET}
  {CYAN}kira-installer{RESET}  {DIM}kira-installer — full env bootstrap{RESET}

{BOLD}Aliases:{RESET}
  {CYAN}analyze{RESET}  → sigil          {CYAN}c2{RESET}      → akame
  {CYAN}install{RESET}  → kira-installer {CYAN}g{RESET}       → grimoire
  {CYAN}ls{RESET}       → lightscan      {CYAN}wn{RESET}      → wraith
  {CYAN}scan{RESET}     → lightscan      {CYAN}recon{RESET}   → wraith

{BOLD}Examples:{RESET}
  ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
  ne0suite wraith scan target.com --axfr --brute-subs
  ne0suite akame
  ne0suite sigil scan ./malware.exe
  ne0suite sigil anticheat ./game.exe
  ne0suite sigil antidebug ./sample.exe
  ne0suite sigil diff ./v1.exe ./v2.exe
  ne0suite sigil report ./sample.exe --html -o report.html
  ne0suite sigil yara ./sample.exe -r ./rules/
  ne0suite grimoire sentinel --ioc 185.220.101.1
  ne0suite shadowci /path/to/repo
  ne0suite kira-installer
  ne0suite status

{BOLD}sigil subcommands:{RESET}
  {DIM}{', '.join(SIGIL_SUBCMDS)}{RESET}

{DIM}Set NE0_DEBUG=1 to print the resolved command before exec.{RESET}
"""


def project_path(tool):
    return PROJECTS / TOOLS[tool]["project"]


def cargo_release_bin(tool):
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
    if not is_installed(name):
        return False, "not installed"

    info = TOOLS[name]
    probe = info.get("ver_probe")

    if probe is None:
        return True, "project found"

    if probe[0] == "cargo_meta":
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


def cmd_status():
    print(BANNER)
    print(f"  {BOLD}Tool Status{RESET}\n")
    print(f"  {'TOOL':<16} {'STATUS':<20} {'DESCRIPTION'}")
    print(f"  {'─' * 70}")

    for name, info in TOOLS.items():
        ok, ver = check_tool(name)
        raw = f"✔ {ver}" if ok else "✗ missing"
        color = GREEN if ok else YELLOW
        padded = f"{color}{raw:<18}{RESET}"
        print(f"  {CYAN}{name:<16}{RESET} {padded} {DIM}{info['desc'][:44]}{RESET}")

    print(f"\n  {DIM}Config locations:{RESET}")
    for label, path in [("GRIMOIRE", "~/.grimoire/config.json"),
                        ("WRAITH-NET", "~/.wraith-net/config.json")]:
        full = Path(path.replace("~", str(Path.home())))
        color = GREEN if full.exists() else DIM
        mark = "✔" if full.exists() else "✗"
        print(f"  {color}{mark}{RESET}  {label:<14} {DIM}{path}{RESET}")
    print()


def resolve_sigil():
    if shutil.which("sigil"):
        return ["sigil"]
    rbin = cargo_release_bin("sigil")
    if rbin:
        return [str(rbin)]
    return None


def cmd_dispatch(tool, args):
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
            resolved = resolve_sigil()
            if resolved:
                if os.environ.get("NE0_DEBUG"):
                    print(f"  {DIM}[debug] sigil binary: {resolved[0]}{RESET}", file=sys.stderr)
                os.execvp(resolved[0], resolved + args)
            else:
                print(f"  {YELLOW}[!]{RESET} sigil not built yet, running via cargo (this will take a minute)",
                      file=sys.stderr)
                print(f"  {DIM}run `cd {pdir} && cargo build --release` to avoid this next time{RESET}",
                      file=sys.stderr)
                try:
                    result = subprocess.run(["cargo", "run", "--release", "--"] + args, cwd=pdir)
                    sys.exit(result.returncode)
                except KeyboardInterrupt:
                    sys.exit(130)
        else:
            rbin = cargo_release_bin(tool)
            if rbin:
                os.execvp(str(rbin), [str(rbin)] + args)
            else:
                try:
                    result = subprocess.run(["cargo", "run", "--release", "--"] + args, cwd=pdir)
                    sys.exit(result.returncode)
                except KeyboardInterrupt:
                    sys.exit(130)

    elif info["run"] == "bash":
        try:
            result = subprocess.run(["bash", str(pdir / "install.sh")] + args, cwd=pdir)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            sys.exit(130)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(BANNER)
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
