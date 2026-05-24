<div align="center">

```
  ███╗   ██╗███████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗
  ████╗  ██║██╔════╝██╔═══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝
  ██╔██╗ ██║█████╗  ██║   ██║███████╗██║   ██║██║   ██║   █████╗
  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║   ██║██║   ██║   ██╔══╝
  ██║ ╚████║███████╗╚██████╔╝███████║╚██████╔╝██║   ██║   ███████╗
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝
```

[![Version](https://img.shields.io/badge/version-1.0.0-cc0000?style=for-the-badge&labelColor=0a0000)](https://github.com/ne0k1r4/ne0suite)
[![Python](https://img.shields.io/badge/python-3.10+-cc0000?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0000)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-cc0000?style=for-the-badge&labelColor=0a0000)](LICENSE)
[![Author](https://img.shields.io/badge/author-ne0k1r4-cc0000?style=for-the-badge&labelColor=0a0000)](https://github.com/ne0k1r4)

**Unified Operator CLI**  
One command to launch the full ne0k1ra security toolchain

</div>

---

## Overview

ne0suite is a unified CLI dispatcher that ties together GRIMOIRE, LightScan, WRAITH-NET, and ShadowCI under a single command. No more remembering different tool names — just `ne0suite <tool> [args]`.

```bash
ne0suite status                              # check all tools
ne0suite wraith scan target.com             # attack surface intel
ne0suite lightscan --scan -t 10.0.0.1      # network scan
ne0suite grimoire sentinel --ioc 1.2.3.4   # threat intel
ne0suite shadowci /path/to/repo            # CI security scan
```

---

## Install

```bash
git clone https://github.com/ne0k1r4/ne0suite
cd ne0suite
pip install -e .
```

Or use the full toolchain installer:

```bash
bash install.sh
```

This installs all 5 tools, creates config directories, and adds shell aliases.

---

## Tools

| Tool | Command | Alias | Description |
|------|---------|-------|-------------|
| **GRIMOIRE v2.1** | `grimoire` | `g` | Operator toolkit — recon, payloads, C2, stego, blue team |
| **LightScan v2.0** | `lightscan` | `ls` | Network scanner — ports, CVEs, scripts, web, brute |
| **WRAITH-NET v1.0** | `wraith-net` | `wn` | Attack surface intel — subdomains, ASN, DNS, takeover |
| **ShadowCI v2.0** | `shadowci` | `sh` | CI/CD scanner — secrets, SAST, supply chain |

---

## Usage

```bash
# Full status check
ne0suite status

# WRAITH-NET
ne0suite wraith scan github.com
ne0suite wraith scan target.com --axfr --brute-subs
ne0suite wn scan target.com --modules subdomains intel dns_security

# LightScan
ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
ne0suite lightscan --web-scan http://target.com
ne0suite lightscan --brute ssh -t 10.0.0.1 -U root -W passwords.txt
ne0suite ls --list-templates

# GRIMOIRE
ne0suite grimoire sentinel --ioc 185.220.101.1
ne0suite grimoire sentinel --scan /var/log --report
ne0suite grimoire wraith target.com --report
ne0suite grimoire forge
ne0suite grimoire codex
ne0suite g phantom

# ShadowCI
ne0suite shadowci scan /path/to/repo
ne0suite shadowci scan . --format html
ne0suite sh scan . --only secrets sast
```

---

## Status Output

```
  TOOL           STATUS        COMMAND          DESCRIPTION
  ────────────────────────────────────────────────────────
  grimoire       ✔ installed   grimoire         Unified operator toolkit
  lightscan      ✔ installed   lightscan        Async network scanner
  wraith         ✔ installed   wraith-net       Attack surface intel
  shadowci       ✔ installed   shadowci         CI/CD security scanner

  Config locations:
  ✔  GRIMOIRE     ~/.grimoire/config.json
  ✔  WRAITH-NET   ~/.wraith-net/config.json
```

---

## Aliases

After running `install.sh`, these shell aliases are available:

```bash
g    → ne0suite grimoire
ls   → ne0suite lightscan   # careful: shadows ls command
wn   → ne0suite wraith
sh   → ne0suite shadowci
n0s  → ne0suite
```

---

## Arch Linux Installer

`install.sh` automates the full setup on a fresh Arch Linux system:

```bash
bash install.sh
```

What it does:
- Installs system packages (python, git, curl, bind, nmap)
- Clones and pip-installs all 5 tools
- Creates config directories with template API key files
- Adds shell aliases to `.zshrc` / `.bashrc`
- Verifies all installations

---

## API Keys

Add keys to unlock full functionality:

```bash
# GRIMOIRE — Shodan, AbuseIPDB, VirusTotal
~/.grimoire/config.json

# WRAITH-NET — VirusTotal, GitHub
~/.wraith-net/config.json
```

Free keys:
- **Shodan** — account.shodan.io
- **AbuseIPDB** — abuseipdb.com/account/api
- **VirusTotal** — virustotal.com/gui/my-apikey
- **GitHub PAT** — github.com/settings/tokens

---

<div align="center">
<br>
<i>ne0suite v1.0.0 · Developer: Light (Neok1ra)</i>
<br><br>

[![GitHub](https://img.shields.io/badge/github.com%2Fne0k1r4-cc0000?style=flat-square&labelColor=0a0000&logo=github&logoColor=white)](https://github.com/ne0k1r4)

</div>
