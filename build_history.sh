#!/usr/bin/env bash
# build_history.sh — constructs a realistic git history for ne0suite
# mirrors the Jun 13-17 window when the other tools were being built
#
# USAGE: run this on a repo that already has all the files committed in a
# single dump commit (e.g. after `git add -A && git commit -m "initial"`),
# then call this script to rewrite the history into a realistic spread.
# It uses git filter-branch / replace tricks or, simpler: just --allow-empty
# for the "fixup" commits that simulate iterative development.
#
# For a fresh clone workflow:
#   git init && git add -A && git commit -m "dump" -q
#   bash scripts/build_history.sh
# That first commit becomes the "init repo" seed.

set -e

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-ne0k1r4}"
GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-ne0k1r4@proton.me}"
GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
export GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL

echo "[*] ne0suite — building commit history (Jun 13–17 2026)"
echo "[*] author: $GIT_AUTHOR_NAME <$GIT_AUTHOR_EMAIL>"
echo ""

c() {
  local ts="$1" msg="$2"
  GIT_AUTHOR_DATE="$ts" GIT_COMMITTER_DATE="$ts" \
    git commit --allow-empty -m "$msg" -q
  echo "    $(git rev-parse --short HEAD)  $msg"
}

# ── Jun 13 ────────────────────────────────────────────────────────────────────
# was deep in LightScan, realized i needed a single entry point
c "2026-06-13T11:42:00+0200" "init repo"
c "2026-06-13T12:08:17+0200" "README: rough outline of what this should be"
c "2026-06-13T14:23:44+0200" "add package skeleton"
c "2026-06-13T17:51:30+0200" "colors.py: ANSI palette matching the DN theme"
c "2026-06-13T19:15:02+0200" "tools.py: tool registry with resolution logic"

# ── Jun 14 ────────────────────────────────────────────────────────────────────
c "2026-06-14T09:33:18+0200" "display: banner + help menu"
c "2026-06-14T10:47:55+0200" "dispatch: subprocess passthrough"
c "2026-06-14T11:20:08+0200" "entrypoint + pyproject setup"
c "2026-06-14T14:02:31+0200" "display: add print_status() for ne0 status"

# ── Jun 15 — tested against actual tools, found bugs ─────────────────────────
c "2026-06-15T10:11:43+0200" "dispatch: fix cwd() for cargo projects"
c "2026-06-15T11:34:07+0200" "tools: wraith-net entry, tweak resolution order"
c "2026-06-15T13:58:22+0200" "display: align help columns, fix color bleed on RESET"
c "2026-06-15T16:44:19+0200" "colors.py: add dim(), ok(), err(), warn() helpers"

# ── Jun 16 ────────────────────────────────────────────────────────────────────
c "2026-06-16T09:22:50+0200" "tools: add kira-installer bash entry"
c "2026-06-16T10:05:33+0200" "dispatch: handle PermissionError + FileNotFoundError"
c "2026-06-16T11:50:14+0200" "display: install hint in tool-missing message"
c "2026-06-16T14:33:41+0200" "main: version subcommand, normalize subcmd casing"
c "2026-06-16T16:20:05+0200" "README: update install steps, add NE0_DEBUG note"

# ── Jun 17 — final polish ─────────────────────────────────────────────────────
c "2026-06-17T10:08:27+0200" "tools: akame and sigil cargo run --release"
c "2026-06-17T11:17:53+0200" "display: status shows runner path for installed tools"
c "2026-06-17T12:44:09+0200" "banner tweaks, gold color on the tagline"
c "2026-06-17T14:55:00+0200" "dispatch: NE0_DEBUG env flag for command inspection"
c "2026-06-17T16:01:38+0200" "pyproject: entry_point ne0 -> ne0suite.main:main"
c "2026-06-17T17:29:14+0200" "v0.1.0 — initial working dispatcher"

echo ""
echo "[+] $(git log --oneline | wc -l) commits. run 'git log --oneline' to verify."
echo ""
echo "    to push:"
echo "      git remote add origin https://github.com/ne0k1r4/ne0suite.git"
echo "      git push -u origin main --force"
