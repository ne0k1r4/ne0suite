<div align="center">

```
  ███╗   ██╗███████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗
  ████╗  ██║██╔════╝██╔═══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝
  ██╔██╗ ██║█████╗  ██║   ██║███████╗██║   ██║██║   ██║   █████╗
  ██║╚██╗██║██╔══╝  ██║   ██║╚════██║██║   ██║██║   ██║   ██╔══╝
  ██║ ╚████║███████╗╚██████╔╝███████║╚██████╔╝██║   ██║   ███████╗
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝
```

[![Version](https://img.shields.io/badge/version-1.0.0-cc0000?style=for-the-badge&labelColor=0a0000)](https://github.com/ne0k1ra/ne0suite)
[![Python](https://img.shields.io/badge/python-3.10+-cc0000?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0000)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-cc0000?style=for-the-badge&labelColor=0a0000)](LICENSE)

**Unified Operator Command Line Interface**  
One entry point to run the entire security toolchain.

</div>

---

## Overview

`ne0suite` acts as a central dispatcher for the security suite, routing subcommands to their respective tools:

* **GRIMOIRE** (v2.1) — Operator toolkit (recon, C2, payloads, stego)
* **LightScan** (v2.0) — Async network scanning engine
* **WRAITH-NET** (v1.0) — Attack surface intel
* **ShadowCI** (v2.0) — CI/CD pipeline security scanner

---

## Installation & Setup

Ensure system dependencies (`python`, `git`, `curl`, `bind`, `nmap`) are installed, then run:

```bash
git clone https://github.com/ne0k1ra/ne0suite
cd ne0suite
./install.sh
```

The script performs editable pip installation, creates template config directories, and configures shell aliases (`g`, `ls`, `wn`, `sh`, `n0s`).

---

## Usage

```bash
# Check installation and versions
ne0suite status

# Dispatch subcommands directly
ne0suite wraith scan target.com
ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
ne0suite grimoire sentinel --ioc 1.2.3.4
ne0suite shadowci scan /path/to/repo
```

### Configuration & API Keys
Configure credentials (Shodan, AbuseIPDB, VirusTotal, GitHub) in the template files created during installation:
* `~/.grimoire/config.json`
* `~/.wraith-net/config.json`
