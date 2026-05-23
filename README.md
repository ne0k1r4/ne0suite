# ne0suite

**Unified Operator CLI for ne0k1ra's security toolchain.**

One command to launch GRIMOIRE, LightScan, WRAITH-NET, and ShadowCI.

## Install

```bash
git clone https://github.com/ne0k1r4/ne0suite
cd ne0suite
pip install -e .
```

## Usage

```bash
ne0suite <tool> [args...]
ne0suite status
```

## Tools

| Command | Alias | Tool | Description |
|---------|-------|------|-------------|
| `ne0suite grimoire` | `g` | GRIMOIRE v2.1 | Operator toolkit — recon, payloads, C2, stego, blue team |
| `ne0suite lightscan` | `ls` | LightScan v2.0 | Network scanner — ports, CVEs, scripts, web, brute |
| `ne0suite wraith` | `wn` | WRAITH-NET v1.0 | Attack surface intel — subdomains, ASN, DNS, takeover |
| `ne0suite shadowci` | `sh` | ShadowCI v1.2 | CI/CD scanner — secrets, CVEs, misconfigs |

## Examples

```bash
# Attack surface intel
ne0suite wraith scan github.com
ne0suite wraith scan target.com --axfr --brute-subs

# Network scanning
ne0suite lightscan --scan -t 10.0.0.1 -p top100 --sv --cve
ne0suite lightscan --web-scan http://target.com

# GRIMOIRE modules
ne0suite grimoire sentinel --ioc 185.220.101.1
ne0suite grimoire sentinel --scan /var/log --report
ne0suite grimoire wraith target.com --report
ne0suite grimoire forge
ne0suite grimoire codex

# CI/CD security
ne0suite shadowci /path/to/repo

# Check all tools installed
ne0suite status
```

## Status

```
ne0suite status

  TOOL           STATUS       COMMAND          DESCRIPTION
  ────────────────────────────────────────────────────────
  grimoire       ✔ installed  grimoire         Unified operator toolkit
  lightscan      ✔ installed  lightscan        Async network scanner
  wraith         ✔ installed  wraith-net       Attack surface intel
  shadowci       ✔ installed  shadowci         CI/CD security scanner
```

---

*ne0suite v1.0.0 · Developer: Light (Neok1ra) · github.com/ne0k1r4*
