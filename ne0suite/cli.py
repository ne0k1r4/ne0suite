#!/usr/bin/env python3
"""ne0suite - one entry point for the whole toolchain.

Every security tool I've written lives in ~/dev/projects, each with its own
invocation, its own version flag, and its own way of being installed. After a
while I stopped remembering which one needed `--version` and which one needed
`version`, so this dispatcher exists to forget all of that for me.

    ne0suite <tool> [args...]     run a tool
    ne0suite status               show what's installed and what isn't
    ne0suite console              interactive shell with tab completion
    ne0suite history              last tool invocations, timings and exits
    ne0suite check                dependency / config diagnostics

Tools that don't land on PATH (the Rust ones, mostly) get resolved through
their release binaries or a cargo run fallback, so dispatching never depends
on how a tool happened to be installed.
"""

import sys
import os
import shutil
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

try:
    import readline
except ImportError:  # windows / minimal pythons
    readline = None

VERSION = "1.2.0"

# runtime state lives under ~/.ne0suite so uninstalling leaves nothing behind
NE0_DIR = Path.home() / ".ne0suite"
HISTORY_FILE = NE0_DIR / "history.json"
CONFIG_FILE = NE0_DIR / "config.json"


class HistoryManager:
    """Tiny json-backed log of everything dispatched through ne0suite."""

    @staticmethod
    def init_db():
        """Make sure the state directory and history file exist."""
        NE0_DIR.mkdir(parents=True, exist_ok=True)
        if not HISTORY_FILE.exists():
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)

    @staticmethod
    def log_event(tool, args, duration, exit_code):
        """Append one run to the history file.

        Best effort - if the file is corrupt or unreadable we just don't
        record this one, no point crashing a dispatch over bookkeeping.
        """
        HistoryManager.init_db()
        event = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "args": args,
            "duration_seconds": round(duration, 3),
            "exit_code": exit_code,
        }
        try:
            with open(HISTORY_FILE, "r+") as f:
                data = json.load(f)
                data.append(event)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except Exception:
            pass


# raw ANSI, zero deps, works in any terminal that isn't ancient
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GOLD = "\033[38;2;200;160;60m"  # 24-bit color, matches the notebook cover
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# banner lines live separately so the animated reveal can print them one at a time
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
    """Print the banner. When stdout is a tty, reveal it line by line and
    type the tagline out - it's stupid, but it's *our* stupid."""
    print()
    if animate and sys.stdout.isatty():
        for i, line in enumerate(BANNER_ART):
            color = BANNER_GRADIENT[i]
            sys.stdout.write(f"{BOLD}{color}{line}{RESET}\n")
            sys.stdout.flush()
            time.sleep(0.04)
        time.sleep(0.08)
        tagline_raw = f"  Unified Operator Suite · by Light (Neok1ra) · v{VERSION}"
        for ch in tagline_raw:
            sys.stdout.write(f"{DIM}{ch}{RESET}")
            sys.stdout.flush()
            time.sleep(0.008)
        print()
    else:
        # piped output - skip the theatrics, just dump it
        for i, line in enumerate(BANNER_ART):
            print(f"{BOLD}{BANNER_GRADIENT[i]}{line}{RESET}")
        print(TAGLINE)
    print(SEPARATOR)
    print()


# everything lives under ~/dev/projects - change this if your layout differs
PROJECTS = Path.home() / "dev" / "projects"

# one entry per tool. run modes:
#   "bin"    - a PATH binary (execvp)
#   "cargo"  - a Rust project, resolved via release binary or cargo run
#   "bash"   - a shell script project
# ver_probe tells status how to scrape a version string:
#   ("flag", <flag>)   run the binary with this flag and scan the output
#   ("cargo_meta",)    read version straight out of Cargo.toml (no build)
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
        "cmd":       "wraith-net",  # binary name differs from the subcommand key
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
    # sigil ships a release binary like akame, but it's PATH-installable so
    # cmd is set. resolution order: PATH -> target/release/sigil -> cargo run.
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
    "adcs": {
        "cmd":       "ne0adcs",
        "project":   "ne0adcs",
        "run":       "bin",
        "desc":      "AD CS attack toolkit — ESC1/3/4/6, shadow creds, autopwn",
        "ver_probe": ("flag", "--version"),
        "install":   "pip install -e ~/dev/projects/ne0adcs",
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

HELP = f"""  {BOLD}ne0suite{RESET} {DIM}<tool> [args...]  |  status  |  console  |  history  |  check  |  help{RESET}

  {CYAN}grimoire{RESET}   {DIM}g{RESET}          Recon, C2, payloads, stego
  {CYAN}lightscan{RESET}  {DIM}ls  scan{RESET}   Network scanner
  {CYAN}wraith{RESET}     {DIM}wn  recon{RESET}  Attack surface intel
  {CYAN}shadowci{RESET}   {DIM}sh{RESET}         CI/CD security scanner
  {CYAN}akame{RESET}      {DIM}c2{RESET}         C2 teamserver {DIM}(Rust){RESET}
  {CYAN}sigil{RESET}      {DIM}analyze{RESET}    PE/ELF static analyzer {DIM}(Rust){RESET}
  {CYAN}kira-installer{RESET} {DIM}install{RESET} Env bootstrap
  {CYAN}adcs{RESET}      {DIM}cert{RESET}      AD CS attack toolkit — ESC1/3/4/6, shadow, autopwn
"""


def project_path(tool):
    return PROJECTS / TOOLS[tool]["project"]


def cargo_release_bin(tool):
    """Existing release binary for a cargo tool, if any.

    Checking first avoids triggering a cargo build every time you dispatch.
    """
    pdir = project_path(tool)
    name = TOOLS[tool].get("cmd") or tool
    bin_path = pdir / "target" / "release" / name
    return bin_path if bin_path.exists() else None


def is_installed(tool):
    info = TOOLS[tool]

    if info["run"] == "bin":
        # for the python tools this is just "did the entry point land on PATH"
        return bool(shutil.which(info["cmd"]))

    if info["run"] == "cargo":
        # a project dir alone doesn't mean installed - it has to be buildable
        if info.get("cmd") and shutil.which(info["cmd"]):
            return True
        if cargo_release_bin(tool):
            return True
        # last resort: dir exists, cargo run will build it on first dispatch
        return project_path(tool).exists()

    if info["run"] == "bash":
        # kira-installer just needs the repo cloned; install.sh does the rest
        return project_path(tool).exists()

    return False


def check_tool(name):
    """Return (ok, version_string) for one tool."""
    if not is_installed(name):
        return False, "not installed"

    info = TOOLS[name]
    probe = info.get("ver_probe")

    if probe is None:
        # bash tools have no version to speak of - presence is enough
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
        # no Cargo.toml, or it didn't parse - fall back to the binary itself
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
        # run the binary with its version flag and scrape the output
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
        line = f"  {CYAN}{name:<16}{RESET} {padded} {DIM}{info['desc'][:40]}{RESET}"
        if sys.stdout.isatty():
            # fade each row in one at a time, feels less like a wall of text
            sys.stdout.write(f"{line}\n")
            sys.stdout.flush()
            time.sleep(0.05)
        else:
            print(line)

    print(f"\n  {DIM}Config:{RESET}")
    for label, path in [("GRIMOIRE", "~/.grimoire/config.json"),
                        ("WRAITH-NET", "~/.wraith-net/config.json")]:
        full = Path(path.replace("~", str(Path.home())))
        color = GREEN if full.exists() else DIM
        mark = "✔" if full.exists() else "✗"
        print(f"  {color}{mark}{RESET}  {label:<14} {DIM}{path}{RESET}")
    print()


def cmd_history():
    """Show the last few dispatched runs from ~/.ne0suite/history.json."""
    HistoryManager.init_db()
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        if not data:
            print(f"  {YELLOW}No execution history found.{RESET}")
            return
        print(f"\n  {BOLD}Execution History (Last 20 Runs){RESET}\n")
        print(f"  {'TIME':<20} {'TOOL':<12} {'DURATION':<10} {'STATUS':<10} {'ARGUMENTS'}")
        print(f"  {'─' * 76}")
        for event in reversed(data[-20:]):
            dt = datetime.fromisoformat(event["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            status = f"{GREEN}✔ OK{RESET}" if event["exit_code"] == 0 else f"{RED}✗ ERR{RESET}"
            args_str = " ".join(event["args"])[:35]
            print(f"  {dt:<20} {CYAN}{event['tool']:<12}{RESET} "
                  f"{event['duration_seconds']:<10.2f}s {status:<18} {DIM}{args_str}{RESET}")
        print()
    except Exception as e:
        print(f"  {RED}[!]{RESET} Error reading history: {e}")


def cmd_check():
    """Diagnostics: required binaries present, config files valid JSON."""
    print_banner()
    print(f"  {BOLD}System Status & Diagnostics{RESET}\n")

    dependencies = {
        "git": "Cloning and tracking repositories",
        "python3": "Running Python tool pipelines",
        "nmap": "Active scanning (LightScan)",
        "cargo": "Compiling Rust applications",
        "docker": "Running isolated environments",
        "dig": "DNS queries (WRAITH-NET)",
        "curl": "Raw HTTP connectivity probes",
    }

    print(f"  {BOLD}{'DEPENDENCY':<16} {'STATUS':<15} {'DESCRIPTION'}{RESET}")
    print(f"  {'─' * 66}")
    for binary, desc in dependencies.items():
        path = shutil.which(binary)
        status = f"{GREEN}✔ found{RESET}" if path else f"{YELLOW}✗ missing{RESET}"
        line = f"  {CYAN}{binary:<16}{RESET} {status:<24} {DIM}{desc}{RESET}"
        print(line)

    print(f"\n  {BOLD}{'CONFIGURATION FILE':<32} {'STATUS'}{RESET}")
    print(f"  {'─' * 66}")
    for label, path in [("GRIMOIRE", "~/.grimoire/config.json"),
                        ("WRAITH-NET", "~/.wraith-net/config.json")]:
        full = Path(path.replace("~", str(Path.home())))
        if not full.exists():
            status = f"{YELLOW}✗ missing{RESET}"
        else:
            try:
                with open(full, "r") as f:
                    json.load(f)
                status = f"{GREEN}✔ valid{RESET}"
            except Exception:
                status = f"{RED}✗ invalid JSON{RESET}"
        print(f"  {label:<32} {status}")
    print()


class Ne0Console:
    """Interactive shell around the dispatcher.

    Tab-completes tool names, aliases and builtin commands, and keeps a
    `target` variable that gets substituted into $TARGET / $t in arguments
    so you can run several tools against the same host without retyping it.
    """

    def __init__(self):
        self.target = ""
        self.prompt = f"{RED}ne0suite{RESET} > "
        self.commands = sorted(list(TOOLS.keys()) + list(ALIASES.keys()) + [
            "status", "history", "check", "target", "help", "exit", "quit"
        ])
        if readline:
            readline.set_completer(self.complete)
            readline.parse_and_bind("tab: complete")

    def complete(self, text, state):
        options = [cmd for cmd in self.commands if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    def run(self):
        print_banner(animate=False)
        print(f"  {BOLD}Console Session Started.{RESET} Type {CYAN}help{RESET} or {CYAN}exit{RESET} to close.\n")
        while True:
            prefix = f" [{GOLD}{self.target}{RESET}]" if self.target else ""
            self.prompt = f"{RED}ne0suite{prefix}{RESET} > "
            try:
                line = input(self.prompt).strip()
            except (KeyboardInterrupt, EOFError):
                print("\n  Closing console session.")
                break
            if not line:
                continue
            parts = line.split()
            cmd, args = parts[0].lower(), parts[1:]
            self.execute(cmd, args)

    def execute(self, cmd, args):
        if cmd in ("exit", "quit"):
            raise KeyboardInterrupt
        elif cmd == "help":
            print(HELP)
        elif cmd == "status":
            cmd_status()
        elif cmd == "history":
            cmd_history()
        elif cmd == "check":
            cmd_check()
        elif cmd == "target":
            if not args:
                if self.target:
                    print(f"  Active target: {GOLD}{self.target}{RESET}")
                else:
                    print("  No active target set. Use: target <host>")
            else:
                self.target = args[0]
                print(f"  Target set to: {GOLD}{self.target}{RESET}")
        else:
            if self.target:
                args = [a.replace("$TARGET", self.target).replace("$t", self.target) for a in args]
            try:
                cmd_dispatch(cmd, args, in_console=True)
            except SystemExit:
                pass
            except Exception as e:
                print(f"  {RED}[!]{RESET} Command failed: {e}")


def resolve_sigil():
    """PATH first (cargo install / manual symlink), then release binary."""
    if shutil.which("sigil"):
        return ["sigil"]
    rbin = cargo_release_bin("sigil")
    if rbin:
        return [str(rbin)]
    return None  # caller falls back to cargo run --release


def cmd_dispatch(tool, args, in_console=False):
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
            # show what they're missing out on
            print(f"  {DIM}subcommands: {', '.join(SIGIL_SUBCMDS)}{RESET}\n")
        sys.exit(1)

    info = TOOLS[tool]
    pdir = project_path(tool)

    if os.environ.get("NE0_DEBUG"):
        print(f"  {DIM}[debug] tool={tool} run={info['run']} dir={pdir} args={args}{RESET}",
              file=sys.stderr)

    if info["run"] == "bin":
        if in_console:
            start_time = time.monotonic()
            try:
                result = subprocess.run([info["cmd"]] + args)
                duration = time.monotonic() - start_time
                HistoryManager.log_event(tool, args, duration, result.returncode)
            except KeyboardInterrupt:
                duration = time.monotonic() - start_time
                HistoryManager.log_event(tool, args, duration, 130)
        else:
            HistoryManager.log_event(tool, args, 0.0, 0)
            os.execvp(info["cmd"], [info["cmd"]] + args)

    elif info["run"] == "cargo":
        if tool == "sigil":
            resolved = resolve_sigil()
            if resolved:
                if os.environ.get("NE0_DEBUG"):
                    print(f"  {DIM}[debug] sigil binary: {resolved[0]}{RESET}", file=sys.stderr)
                if in_console:
                    start_time = time.monotonic()
                    try:
                        result = subprocess.run(resolved + args)
                        duration = time.monotonic() - start_time
                        HistoryManager.log_event(tool, args, duration, result.returncode)
                    except KeyboardInterrupt:
                        duration = time.monotonic() - start_time
                        HistoryManager.log_event(tool, args, duration, 130)
                else:
                    HistoryManager.log_event(tool, args, 0.0, 0)
                    os.execvp(resolved[0], resolved + args)
            else:
                # no built binary yet - build and run via cargo (slow first time)
                print(f"  {YELLOW}[!]{RESET} sigil not built yet, running via cargo (this will take a minute)",
                      file=sys.stderr)
                print(f"  {DIM}run `cd {pdir} && cargo build --release` to avoid this next time{RESET}",
                      file=sys.stderr)
                start_time = time.monotonic()
                try:
                    result = subprocess.run(["cargo", "run", "--release", "--"] + args, cwd=pdir)
                    duration = time.monotonic() - start_time
                    HistoryManager.log_event(tool, args, duration, result.returncode)
                    if not in_console:
                        sys.exit(result.returncode)
                except KeyboardInterrupt:
                    duration = time.monotonic() - start_time
                    HistoryManager.log_event(tool, args, duration, 130)
                    if not in_console:
                        sys.exit(130)
        else:
            # akame and any future rust tool follows the same pattern
            rbin = cargo_release_bin(tool)
            if rbin:
                if in_console:
                    start_time = time.monotonic()
                    try:
                        result = subprocess.run([str(rbin)] + args)
                        duration = time.monotonic() - start_time
                        HistoryManager.log_event(tool, args, duration, result.returncode)
                    except KeyboardInterrupt:
                        duration = time.monotonic() - start_time
                        HistoryManager.log_event(tool, args, duration, 130)
                else:
                    HistoryManager.log_event(tool, args, 0.0, 0)
                    os.execvp(str(rbin), [str(rbin)] + args)
            else:
                start_time = time.monotonic()
                try:
                    result = subprocess.run(["cargo", "run", "--release", "--"] + args, cwd=pdir)
                    duration = time.monotonic() - start_time
                    HistoryManager.log_event(tool, args, duration, result.returncode)
                    if not in_console:
                        sys.exit(result.returncode)
                except KeyboardInterrupt:
                    duration = time.monotonic() - start_time
                    HistoryManager.log_event(tool, args, duration, 130)
                    if not in_console:
                        sys.exit(130)

    elif info["run"] == "bash":
        start_time = time.monotonic()
        try:
            result = subprocess.run(["bash", str(pdir / "install.sh")] + args, cwd=pdir)
            duration = time.monotonic() - start_time
            HistoryManager.log_event(tool, args, duration, result.returncode)
            if not in_console:
                sys.exit(result.returncode)
        except KeyboardInterrupt:
            duration = time.monotonic() - start_time
            HistoryManager.log_event(tool, args, duration, 130)
            if not in_console:
                sys.exit(130)


def main():
    args = sys.argv[1:]

    # no args at all - just show the help, don't error out
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

    if args[0] == "console":
        shell = Ne0Console()
        shell.run()
        sys.exit(0)

    if args[0] == "history":
        cmd_history()
        sys.exit(0)

    if args[0] == "check":
        cmd_check()
        sys.exit(0)

    cmd_dispatch(args[0].lower(), args[1:])


if __name__ == "__main__":
    main()
