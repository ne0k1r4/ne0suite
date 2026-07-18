# ne0suite

One entry point for the whole security toolchain. `ne0suite` routes subcommands
to their respective tools, resolves aliases, and checks whether a tool is
actually installed before dispatching.

## Tools

* **GRIMOIRE** — Operator toolkit (recon, C2, payloads, stego)
* **LightScan** — Async network scanning engine
* **WRAITH-NET** — Attack surface intel
* **ShadowCI** — CI/CD pipeline security scanner
* **akame** — C2 teamserver (Rust)
* **sigil** — PE/ELF static analyzer (Rust)
* **kira-installer** — environment bootstrap

## Installation

Ensure system dependencies (`python`, `git`, `curl`, `bind`, `nmap`) are
installed, then run:

```bash
git clone https://github.com/ne0k1r4/ne0suite
cd ne0suite
./install.sh
```

The script performs an editable pip install, creates the template config
directories, and wires up shell aliases (`g`, `ls`, `wn`, `sh`, `n0s`).

## Usage

```bash
# check installation and versions
ne0suite status

# dispatch
ne0suite wraith scan target.com
ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
ne0suite grimoire sentinel --ioc 1.2.3.4
ne0suite shadowci scan /path/to/repo

# interactive shell with tab completion
ne0suite console
```

`status` probes each tool for its version (via its version flag, or straight
out of `Cargo.toml` for the Rust tools) instead of just reporting
installed/missing.

### Console

`ne0suite console` drops into an interactive shell. `target <host>` sets a
target that gets substituted into `$TARGET`/`$t` in later commands, so you can
run several tools against the same host without retyping it. `history` shows
the last 20 dispatches (tool, duration, exit status); `check` verifies system
binaries and config file validity.

Set `NE0_DEBUG=1` to have ne0suite print the exact command it is about to run
instead of just running it — useful when something misbehaves.

## Configuration & API Keys

Configure credentials (Shodan, AbuseIPDB, VirusTotal, GitHub) in the template
files created during installation:

* `~/.grimoire/config.json`
* `~/.wraith-net/config.json`

## Release notes

**v1.2.0** — `ne0suite console` (readline tab completion, `target` variable),
`ne0suite history`, `ne0suite check`. All dispatches are logged to
`~/.ne0suite/history.json`.

**v1.0.0** — animated gradient banner, `ne0suite status` with per-tool version
probing and a spinner, sigil/akame cargo resolution, kira-installer bash
dispatch.

**v0.1.0** — first working dispatcher: tool registry, alias resolution,
subprocess passthrough, `ne0suite status`.
