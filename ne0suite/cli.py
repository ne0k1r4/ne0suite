"""
ne0suite/cli.py — Unified Operator CLI
Dispatches to GRIMOIRE, LightScan, and WRAITH-NET.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

VERSION = "1.0.0"

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
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
  {DIM}GRIMOIRE · LightScan · WRAITH-NET · ShadowCI{RESET}
"""

TOOLS = {
    "grimoire":  {"cmd": "grimoire",   "desc": "Unified operator toolkit — recon, payloads, C2, stego, blue team"},
    "lightscan": {"cmd": "lightscan",  "desc": "Async network scanner — ports, CVEs, scripts, web, brute force"},
    "wraith":    {"cmd": "wraith-net", "desc": "Attack surface intel — subdomains, ASN, DNS security, takeover"},
    "shadowci":  {"cmd": "shadowci",   "desc": "CI/CD security scanner — secrets, CVEs, misconfigs"},
}

ALIASES = {
    "ls": "lightscan", "wn": "wraith",
    "g":  "grimoire",  "sh": "shadowci",
    "scan": "lightscan", "recon": "wraith",
    "shadow": "shadowci",
}

HELP = f"""
{RED}{BOLD}ne0suite{RESET} — Unified Operator CLI

{BOLD}Usage:{RESET}
  ne0suite <tool> [args...]
  ne0suite status
  ne0suite help

{BOLD}Tools:{RESET}
  {CYAN}grimoire{RESET}   GRIMOIRE v2.1 — full operator toolkit
  {CYAN}lightscan{RESET}  LightScan v2.0 PHANTOM — network scanner
  {CYAN}wraith{RESET}     WRAITH-NET v1.0 — attack surface intel
  {CYAN}shadowci{RESET}   ShadowCI v1.2 — CI/CD security scanner

{BOLD}Aliases:{RESET}
  {CYAN}g{RESET}  → grimoire    {CYAN}ls{RESET}  → lightscan
  {CYAN}wn{RESET} → wraith      {CYAN}sh{RESET}  → shadowci

{BOLD}Examples:{RESET}
  ne0suite wraith scan github.com
  ne0suite wraith scan target.com --axfr --brute-subs
  ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
  ne0suite lightscan --web-scan http://target.com
  ne0suite grimoire sentinel --ioc 185.220.101.1
  ne0suite grimoire sentinel --scan /var/log
  ne0suite grimoire wraith target.com --report
  ne0suite grimoire forge
  ne0suite shadowci /path/to/repo
  ne0suite status
"""


def _check_tool(name: str) -> tuple:
    cmd = TOOLS[name]["cmd"]
    if not shutil.which(cmd):
        return False, "not installed"
    try:
        r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
        ver = (r.stdout + r.stderr).strip().splitlines()
        ver = next((l for l in ver if any(c.isdigit() for c in l)), "installed")
        return True, ver[:50]
    except Exception:
        return True, "installed"


def cmd_status():
    print(BANNER)
    print(f"  {BOLD}Tool Status{RESET}\n")
    print(f"  {'TOOL':<14} {'STATUS':<12} {'COMMAND':<16} {'DESCRIPTION'}")
    print(f"  {'─'*72}")
    for name, info in TOOLS.items():
        ok, _ = _check_tool(name)
        status = f"{GREEN}✔ installed{RESET}" if ok else f"{YELLOW}✗ missing{RESET}"
        print(f"  {CYAN}{name:<14}{RESET} {status:<22} {DIM}{info['cmd']:<16}{RESET} {DIM}{info['desc'][:38]}{RESET}")

    print(f"\n  {DIM}Config locations:{RESET}")
    for tool, path in [("GRIMOIRE","~/.grimoire/config.json"),
                       ("WRAITH-NET","~/.wraith-net/config.json")]:
        full = Path(path.replace("~", str(Path.home())))
        c = GREEN if full.exists() else DIM
        print(f"  {c}{'✔' if full.exists() else '✗'}{RESET}  {tool:<12} {DIM}{path}{RESET}")
    print()


def cmd_dispatch(tool: str, args: list):
    tool = ALIASES.get(tool, tool)
    if tool not in TOOLS:
        print(f"  {RED}[!]{RESET} Unknown tool: {tool}")
        print(f"  {DIM}Available: {', '.join(TOOLS.keys())} | Aliases: {', '.join(ALIASES.keys())}{RESET}")
        sys.exit(1)
    cmd = TOOLS[tool]["cmd"]
    if not shutil.which(cmd):
        print(f"  {RED}[!]{RESET} {tool} not installed — '{cmd}' not found in PATH")
        print(f"  {DIM}Install: pip install -e ~/dev/projects/{tool}{RESET}")
        sys.exit(1)
    os.execvp(cmd, [cmd] + args)


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
