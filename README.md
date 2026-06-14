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

The script performs an editable pip install and creates the template config
directories for the tools that need API keys.

## Usage

```bash
# check installation
ne0suite status

# dispatch
ne0suite wraith scan target.com
ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
ne0suite grimoire sentinel --ioc 1.2.3.4
ne0suite shadowci scan /path/to/repo
```

Short aliases are resolved before dispatch: `g` → grimoire, `ls`/`scan` →
lightscan, `wn`/`recon` → wraith, `sh`/`shadow` → shadowci, `c2` → akame,
`analyze` → sigil, `install` → kira-installer.

Set `NE0_DEBUG=1` to have ne0suite print the exact command it is about to run
instead of just running it — useful when something misbehaves.

## Configuration & API Keys

Configure credentials (Shodan, AbuseIPDB, VirusTotal, GitHub) in the template
files created during installation:

* `~/.grimoire/config.json`
* `~/.wraith-net/config.json`
