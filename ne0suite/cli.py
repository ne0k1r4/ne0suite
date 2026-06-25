import sys
import os
import shutil
import subprocess
import time
from pathlib import Path

VERSION = "1.2.0"

# raw ANSI — no deps, works everywhere, respects the terminal
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GOLD   = "\033[38;2;200;160;60m"  # 24-bit, matches the DN notebook cover
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# banner lines stored separately for the animated reveal
BANNER_ART = [
    "  ███╗   ██╗███████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗",
    "  ████╗  ██║██╔════╝██╔═══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝",
    "  ██╔██╗ ██║█████╗  ██║   ██║███████╗██║   ██║██║   ██║   █████╗  ",
    "  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║   ██║██║   ██║   ██╔══╝  ",
    "  ██║ ╚████║███████╗╚██████╔╝███████║╚██████╔╝██║   ██║   ███████╗",
    "  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝",
]

# red gradient — dark to bright across the 6 banner lines
BANNER_GRADIENT = [
    "\033[38;2;120;20;20m",  # deep crimson
    "\033[38;2;160;25;25m",
    "\033[38;2;200;35;35m",
    "\033[38;2;220;50;50m",
    "\033[38;2;240;70;70m",
    "\033[38;2;255;90;90m",  # bright red
]

TAGLINE = f"  {DIM}Unified Operator Suite · by Light (Neok1ra) · v{VERSION}{RESET}"
SEPARATOR = f"  {DIM}{'─' * 66}{RESET}"


def print_banner(animate=True):
    """Print the ne0suite ASCII banner with optional line-by-line gradient animation."""
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
        # non-interactive / piped — skip animation, just dump it
        for i, line in enumerate(BANNER_ART):
            print(f"{BOLD}{BANNER_GRADIENT[i]}{line}{RESET}")
        print(TAGLINE)
    print(SEPARATOR)
    print()

# all tools live under ~/dev/projects/ — change this if your layout differs
PROJECTS = Path.home() / "dev" / "projects"

# each tool entry drives both resolution and the status table.
# run modes: "bin" = PATH binary (execvp), "cargo" = Rust project, "bash" = shell script
# ver_probe: ("flag", <flag>) probes a PATH binary; ("cargo_meta",) reads Cargo.toml directly
# cmd: None for tools that don't produce a standalone PATH binary (cargo/bash tools)
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
        "project":   "Lightscan",  # capital L — that's how the repo is named
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
        "cmd":       None,  # no PATH binary — invoked via cargo or target/release/akame
        "project":   "akame",
        "run":       "cargo",
        "desc":      "C2 teamserver — operator comms, implant mgmt (Rust)",
        "ver_probe": ("cargo_meta",),
        "install":   "cd ~/dev/projects/akame && cargo build --release",
    },
    # sigil is a compiled Rust binary (target/release/sigil after cargo build --release).
    # it has a PATH-installable binary unlike akame, so cmd is set.
    # resolution order: PATH → target/release/sigil → cargo run --release (slow fallback)
    "sigil": {
        "cmd":       "sigil",
        "project":   "sigil",
        "run":       "cargo",
        "desc":      "Static PE/ELF binary analyzer — anti-debug, anti-cheat, YARA (Rust)",
        "ver_probe": ("cargo_meta",),
        "install":   "cd ~/dev/projects/sigil && cargo build --release",
    },
    "kira-installer": {
        "cmd":       None,  # just runs install.sh, nothing gets added to PATH
        "project":   "kira-installer",
        "run":       "bash",
        "desc":      "One-shot environment bootstrap for the full toolchain",
        "ver_probe": None,  # no version — it's a script, not a versioned binary
        "install":   "git clone https://github.com/ne0k1r4/kira-installer ~/dev/projects/kira-installer",
    },
}

# short aliases — so i don't have to type the full name every time
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

# pulled from sigil's clap subcommand definitions in src/main.rs
SIGIL_SUBCMDS = [
    "scan", "headers", "strings", "imports", "symbols", "tls",
    "hashes", "entropy", "antidebug", "anticheat", "disasm",
    "pattern", "diff", "report", "batch", "overlay", "resources",
    "clr", "full-disasm", "yara",
]

HELP = f"""
{BOLD}Usage:{RESET}
  ne0suite <tool> [args...]
  ne0suite status

{BOLD}Tools & Aliases:{RESET}
  {CYAN}grimoire{RESET}       {DIM}(g){RESET}        Operator toolkit (recon, C2, stego)
  {CYAN}lightscan{RESET}      {DIM}(ls, scan){RESET} Async network scanner
  {CYAN}wraith{RESET}         {DIM}(wn, recon){RESET} Attack surface intel
  {CYAN}shadowci{RESET}       {DIM}(sh){RESET}       CI/CD security scanner
  {CYAN}akame{RESET}          {DIM}(c2){RESET}       C2 teamserver (Rust)
  {CYAN}sigil{RESET}          {DIM}(analyze){RESET}  PE/ELF static analyzer (Rust)
  {CYAN}kira-installer{RESET} {DIM}(install){RESET}  Environment bootstrap

{BOLD}Examples:{RESET}
  {DIM}${RESET} ne0suite lightscan --scan -t 10.0.0.1
  {DIM}${RESET} ne0suite wraith scan target.com
  {DIM}${RESET} ne0suite sigil scan ./malware.exe
  {DIM}${RESET} ne0suite status

{DIM}Set NE0_DEBUG=1 to print the resolved command before exec.{RESET}
"""


def project_path(tool):
    return PROJECTS / TOOLS[tool]["project"]


def cargo_release_bin(tool):
    # check if the project has already been built — avoids triggering cargo unnecessarily
    pdir = project_path(tool)
    name = TOOLS[tool].get("cmd") or tool  # fall back to tool name if cmd is None
    bin_path = pdir / "target" / "release" / name
    return bin_path if bin_path.exists() else None


def is_installed(tool):
    info = TOOLS[tool]

    if info["run"] == "bin":
        # for Python tools, just check if the entry_point landed on PATH
        return bool(shutil.which(info["cmd"]))

    if info["run"] == "cargo":
        # prefer PATH or compiled binary over just "project dir exists"
        # project dir existing without a build isn't really "installed"
        if info.get("cmd") and shutil.which(info["cmd"]):
            return True
        if cargo_release_bin(tool):
            return True
        # project dir alone counts — cargo run will build it on first dispatch
        return project_path(tool).exists()

    if info["run"] == "bash":
        # kira-installer just needs the repo cloned — install.sh does the rest
        return project_path(tool).exists()

    return False


def check_tool(name):
    if not is_installed(name):
        return False, "not installed"

    info = TOOLS[name]
    probe = info.get("ver_probe")

    if probe is None:
        # bash tools don't have a version — just confirm presence
        return True, "project found"

    if probe[0] == "cargo_meta":
        # read from Cargo.toml — avoids invoking cargo just for a version string
        toml = project_path(name) / "Cargo.toml"
        try:
            for line in toml.read_text().splitlines():
                if line.strip().startswith("version"):
                    v = line.split("=")[1].strip().strip('"')
                    return True, f"v{v}"
        except Exception:
            pass
        # Cargo.toml missing or unparseable — try the binary directly if it exists
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
        # Python tools — run the binary with its version flag and scrape the output
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
    """Quick inline spinner — gives visual feedback while probing tools."""
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
            # fade-in each row
            sys.stdout.write(f"{line}\n")
            sys.stdout.flush()
            time.sleep(0.05)
        else:
            print(line)

    # config file check
    print(f"\n  {DIM}Config:{RESET}")
    for label, path in [("GRIMOIRE", "~/.grimoire/config.json"),
                        ("WRAITH-NET", "~/.wraith-net/config.json")]:
        full = Path(path.replace("~", str(Path.home())))
        color = GREEN if full.exists() else DIM
        mark = "✔" if full.exists() else "✗"
        print(f"  {color}{mark}{RESET}  {label:<14} {DIM}{path}{RESET}")
    print()


def resolve_sigil():
    # PATH first — if someone did `cargo install` or symlinked the binary manually
    if shutil.which("sigil"):
        return ["sigil"]
    rbin = cargo_release_bin("sigil")
    if rbin:
        return [str(rbin)]
    return None  # caller falls back to cargo run --release


def cmd_dispatch(tool, args):
    # resolve alias before anything else
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
            # show available subcommands so the user knows what they're missing
            print(f"  {DIM}subcommands: {', '.join(SIGIL_SUBCMDS)}{RESET}\n")
        sys.exit(1)

    info = TOOLS[tool]
    pdir = project_path(tool)

    if os.environ.get("NE0_DEBUG"):
        print(f"  {DIM}[debug] tool={tool} run={info['run']} dir={pdir} args={args}{RESET}",
              file=sys.stderr)

    if info["run"] == "bin":
        # execvp replaces this process entirely — tool owns the terminal from here
        # no subprocess overhead, signals propagate correctly, exit code is the tool's
        os.execvp(info["cmd"], [info["cmd"]] + args)

    elif info["run"] == "cargo":
        if tool == "sigil":
            resolved = resolve_sigil()
            if resolved:
                if os.environ.get("NE0_DEBUG"):
                    print(f"  {DIM}[debug] sigil binary: {resolved[0]}{RESET}", file=sys.stderr)
                # same clean execvp behavior as bin tools once we have the binary path
                os.execvp(resolved[0], resolved + args)
            else:
                # project dir exists but no compiled binary yet — trigger a build via cargo
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
            # akame + any future Rust tools follow the same pattern
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

    # no args at all — just show the help, don't error
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
