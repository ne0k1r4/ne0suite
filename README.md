<div align="center">

```
  ███╗   ██╗███████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗
  ████╗  ██║██╔════╝██╔═══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝
  ██╔██╗ ██║█████╗  ██║   ██║███████╗██║   ██║██║   ██║   █████╗
  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║   ██║██║   ██║   ██╔══╝
  ██║ ╚████║███████╗╚██████╔╝███████║╚██████╔╝██║   ██║   ███████╗
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝
```

[![Version](https://img.shields.io/badge/version-1.3.0-cc0000?style=for-the-badge&labelColor=0a0000)](https://github.com/ne0k1r4/ne0suite)
[![Python](https://img.shields.io/badge/python-3.10+-cc0000?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0000)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-cc0000?style=for-the-badge&labelColor=0a0000)](LICENSE)

**Unified Operator Command Line Interface**
One entry point to run the entire security toolchain.

</div>

---

## Overview

`ne0suite` is a central dispatcher for the suite, routing subcommands to their
respective tools. It resolves aliases, checks whether a tool is actually
installed (and offers the install command if it isn't), and handles the three
different ways the tools get run: PATH binaries, Rust release binaries (with a
`cargo run --release` fallback), and plain shell scripts.

* **GRIMOIRE** — Operator toolkit (recon, C2, payloads, stego)
* **LightScan** — Async network scanning engine
* **WRAITH-NET** — Attack surface intel
* **ShadowCI** — CI/CD pipeline security scanner
* **akame** — C2 teamserver (Rust)
* **sigil** — PE/ELF static analyzer (Rust)
* **kira-installer** — environment bootstrap
* **ADCS** (ne0adcs) — AD Certificate Services attack toolkit (ESC1/3/4/6, shadow credentials, autopwn)

`ne0suite adcs <command>` dispatches straight into the toolkit (`enum`, `esc1`,
`esc3`, `esc4`, `esc6`, `shadow`, `list`, `audit`, `autopwn`).

akame is a teamserver, so `ne0suite akame` shortcuts its operator API instead
of spawning a second server:

```bash
# list implants currently checked in
ne0suite akame sessions

# queue a task on a session (type from server/src/task.rs)
ne0suite akame task <session_id> logins

# block until the implant reports back, then print the output
ne0suite akame task <session_id> shell cmd=id --wait
```

The API base defaults to `http://127.0.0.1:8443` (override with `AKAME_API`)
and the bearer token comes from `AKAME_API_TOKEN` or the `akame_token` key in
`~/.ne0suite/config.json`.

---

## Installation & Setup

Ensure system dependencies (`python`, `git`, `curl`, `bind`, `nmap`) are
installed, then run:

```bash
git clone https://github.com/ne0k1r4/ne0suite
cd ne0suite
./install.sh
```

The script performs an editable pip install, pulls in the AD CS toolkit, creates
template config directories, and configures shell aliases (`g`, `ls`, `wn`,
`sh`, `n0s`, `adcs`).

---

## Usage

```bash
# check installation and versions
ne0suite status

# dispatch subcommands directly
ne0suite wraith scan target.com
ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
ne0suite grimoire sentinel --ioc 1.2.3.4
ne0suite shadowci scan /path/to/repo
ne0suite akame task <session_id> logins   # queue a logins task on a live c2

# interactive shell with tab completion
ne0suite console
```

### Console

`ne0suite console` drops into an interactive shell. `target <host>` sets a
target that gets substituted into `$TARGET`/`$t` in later commands, so you can
run several tools against the same host without retyping it. `history` shows
the last 20 dispatches (tool, duration, exit status); `check` verifies system
binaries and config file validity.

### Configuration & API Keys

Configure credentials (Shodan, AbuseIPDB, VirusTotal, GitHub) in the template
files created during installation:

* `~/.grimoire/config.json`
* `~/.wraith-net/config.json`

---

## Release notes

**v1.3.0** — AD CS toolkit integrated as a first-class tool (`ne0suite adcs`,
alias `cert`). ne0adcs is installed by `install.sh` and reports its version in
`ne0suite status`.

**v1.2.0** — `ne0suite console` (readline tab completion, `target` variable),
`ne0suite history`, `ne0suite check`. All dispatches are logged to
`~/.ne0suite/history.json`.

**v1.0.0** — animated banner, `ne0suite status` with per-tool version probing
and a spinner, sigil/akame cargo resolution, kira-installer bash dispatch.

**v0.1.0** — first working dispatcher: tool registry, alias resolution,
subprocess passthrough, help output.
