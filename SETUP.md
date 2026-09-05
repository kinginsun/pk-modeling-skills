# SETUP — pk-modeling-skills: agent installation & verification guide

> **Audience**: an AI coding agent that was handed this document (or its URL).
> Follow the steps **in order**. Do not skip verification commands — they are
> the acceptance criteria for each step. At the end, report the summary table
> from Step 6 to the user.
>
> **Platform**: macOS 13+ (Apple Silicon or Intel). Other platforms: the
> skills themselves are portable text, but the automated steps below target
> macOS.

---

## Step 0 — Obtain the repository

If you do not already have a local clone:

```bash
git clone https://github.com/kinginsun/pk-modeling-skills.git
cd pk-modeling-skills
```

If the user pointed you at an existing local directory instead, use it and
`cd` into it.

Set a variable for later steps:

```bash
REPO="$PWD"   # must be the repository root containing skills/ and scripts/
```

**Verify**: `ls "$REPO"` shows `README.md SETUP.md LICENSE skills scripts examples`.

---

## Step 1 — Environment report

```bash
"$REPO/scripts/doctor.sh"
```

`doctor.sh` prints a table of detected tools and `[OK]` / `[MISSING]` /
`[WARN]` markers. It never modifies the system. Read its output; the missing
items determine which sub-steps of Steps 2–4 you must run. Anything already
`[OK]` can be skipped.

---

## Step 2 — Install the skills

```bash
"$REPO/scripts/install.sh"            # auto-detects the agent skills directory
```

Or explicitly:

```bash
"$REPO/scripts/install.sh" --target ~/.claude/skills --link     # symlinks (recommended while developing)
"$REPO/scripts/install.sh" --target "$PWD/.cursor/skills" --copy  # copies into a Cursor project
```

**Verify**: the script prints one `installed: <skill>` line per skill and
exits 0. The installed tree must keep `SKILL.md` at
`<target>/<skill-name>/SKILL.md`.

Supported targets (auto-detected in this order): `~/.claude/skills`,
`~/.codex/skills`, `~/.agents/skills`, and `./.cursor/skills` inside a git
repository. Use `--list` to show what was detected.

---

## Step 3 — Base toolchain (skip items doctor.sh already marked OK)

### 3.1 Homebrew, gfortran, R, Python

```bash
command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install gcc python        # gcc provides gfortran
brew install --cask r          # R >= 4.3; skip if `R --version` already works
```

R packages used by the examples:

```r
install.packages("ggplot2")   # from R: install.packages("ggplot2")
```

**Verify**: `gfortran --version` and `R --version` both print versions.

### 3.2 Rosetta 2 (Apple Silicon only)

MonolixSuite binaries are x86_64. Check arch with `uname -m`; if it prints
`arm64`:

```bash
/usr/sbin/softwareupdate --install-rosetta --agree-to-license
arch -x86_64 /usr/bin/true && echo "rosetta OK"
```

**Verify**: `arch -x86_64 /usr/bin/true` exits 0.

---

## Step 4 — Modeling engines

> These are **licensed commercial tools**. This repository distributes no
> NONMEM or MonolixSuite binaries or license files. Wherever a step needs a
> download link, installer, or license file that you cannot obtain, **stop
> and ask the user to provide it**; do not fabricate licenses.

### 4.1 NONMEM 7.6

**Check first**: `which nmfe76`. If found, NONMEM is already reachable — go
to the verify box below.

Otherwise ask the user for:

1. The NONMEM 7.6 installer (the `nm760CD` folder / zip from
   https://nonmem.iconplc.com/nonmem760 — ICON account + license required), and
2. A valid `nonmem.lic` license file (or permission to reuse an existing one).

Native install (gfortran backend; answers: `y` to recompile, `q` for quiet):

```bash
/bin/bash SETUP76 /path/to/nm760CD "$HOME/nm76" gfortran y ar same rec q
cp /path/to/nonmem.lic "$HOME/nm76/license/nonmem.lic"
ln -sf "$HOME/nm76/util/nmfe76" /usr/local/bin/nmfe76   # may need sudo
```

Alternative: if the user runs NONMEM via Docker, keep their existing `nmfe76`
wrapper script on `PATH` (it typically `docker run`s a NONMEM image with the
license mounted). Nothing else to do in that case.

**Verify**:

```bash
which nmfe76 && nmfe76 -licfile=... # only if a license check is quick on this install
```

Minimal acceptance: `which nmfe76` prints a path. The full functional check
happens in Step 5.

### 4.2 PsN (Perl-speaks-NONMEM)

**Check first**: `which execute` (and `psn -version`). If found, skip ahead.

Install the latest PsN from source:

```bash
brew install cpanm
sudo cpanm Math::Random::Free Math::MatrixReal Mouse MouseX::Params::Validate \
           Archive::Zip YAML Capture::Tiny File::Copy::Recursive File::HomeDir \
           Math::SigFigs Statistics::Distributions

# Download the latest release (5.7.1+), e.g.:
curl -sL https://api.github.com/repos/UUPharmacometrics/PsN/releases/latest
# download the PsN-*.tar.gz asset, then:
tar xzf PsN-*.tar.gz && cd PsN-Source
sudo perl setup.pl
```

`setup.pl` is interactive. Accept defaults, **except**: on recent macOS, when
prompted for the *PsN Utilities installation directory*, type
`/usr/local/bin`. When asked for the NONMEM directory, point it at the nm76
root (e.g. `~/nm76`); let it create a fresh `psn.conf`.

**Verify**: `execute -version` prints the PsN version.

### 4.3 MonolixSuite (optional — for the monolix-cli skill)

**Check first**: `ls /Applications | grep -i monolix`. If absent, ask the
user to install MonolixSuite 2024R1 from the Lixoft download portal (license
required) and to activate the license once via the GUI. The agent cannot
activate licenses unattended.

If the app bundle exists but the user is on Apple Silicon, also verify
`arch -x86_64 /usr/bin/true` (Rosetta, Step 3.2).

**Verify**: the `monolix.sh` entry point exists:

```bash
ls /Applications/MonolixSuite*/Contents/Resources/monolixSuite/bin/monolix.sh
```

---

## Step 5 — End-to-end smoke tests

```bash
"$REPO/scripts/doctor.sh" --run-examples
```

This runs, in order, only the tests whose engines are present:

1. **NONMEM smoke test** (`examples/nonmem-pop-pk/run1.mod`): PsN `execute`
   on the 1-compartment IV example. Pass criteria: exit 0, `run1.lst` contains
   `#ESTIMATION STEP OMNIPROCESSING SUCCESSFUL` (or `MINIMIZATION SUCCESSFUL`),
   and `run1.ext` has a final estimate row.
2. **R plotting smoke test**: renders a small ggplot2 figure from the example
   tables. Pass criteria: a `.png` is written without error.
3. **Monolix smoke test** (`examples/monolix-theophylline/theophylline_project.mlxtran`,
   only if MonolixSuite is installed): headless estimation run with the
   skill's `x86shim`. Pass criteria: result folder contains
   `populationParameters.txt` with finite estimates.

Run times: ~10–60 s for the NONMEM example, ~2–4 min for the Monolix example.
If a test fails, read the emitted log path before retrying; common causes are
listed in Troubleshooting below.

---

## Step 6 — Report

Report to the user exactly this table filled with results:

```text
| Item                    | Status | Notes                        |
|-------------------------|--------|------------------------------|
| Skills installed        |        | target directory used        |
| gfortran                |        | version                      |
| R + ggplot2             |        | version                      |
| Rosetta (Apple Silicon) |        | n/a on Intel                 |
| NONMEM 7.6 (nmfe76)     |        | path / wrapper type          |
| PsN (execute)           |        | version                      |
| MonolixSuite            |        | version or "not installed"   |
| NONMEM smoke test       |        | pass/fail + example used     |
| Monolix smoke test      |        | pass/fail/skipped            |
```

Rules: mark `SKIPPED (no license)` rather than failing when the user declined
to provide a commercial tool; never claim a test passed without having run the
verify command.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `execute: command not found` | PsN utilities dir not on PATH | `export PATH="/usr/local/bin:$PATH"`; re-run `perl setup.pl` choosing `/usr/local/bin` |
| `execute` fails: "no NONMEM found" | `psn.conf` has no `[nm_versions]` entry | add `nm76=<nmfe76 path>` to `~/.PsN/psn.conf` (or the printed conf path) under `[nm_versions]`, and `default_nm_version=nm76` under `[defaults]` |
| `nmfe76` errors on license | missing/expired `nonmem.lic` | ask the user for a valid license; place it in `<nm76>/license/nonmem.lic` |
| `cannot load Mlxtran plugin` (Monolix) | arm64 compiler used for the model plugin | prepend the skill's shim: `PATH="<skills>/monolix-cli/x86shim:$PATH"`; delete stale plugins in `~/lixoft/monolix/monolix2024R1/modules/` |
| Monolix killed with exit 137 | invalid code signature on modified suite file | `codesign -v <file>`; re-sign ad-hoc: `codesign --remove-signature <file> && codesign --force --sign - <file>` |
| Monolix hangs at startup headless | license not activated | activate once via the GUI (cannot be automated) |
| `ggplot2` missing | package not installed | `Rscript -e 'install.packages("ggplot2", repos="https://cloud.r-project.org")'` |
| Perl module errors during PsN install | missing CPAN deps | re-run the `cpanm` line in Step 4.2, then `perl setup.pl` again |

## Re-running / updating

The scripts are idempotent: re-run `install.sh` after `git pull` to refresh
copied skills (symlinked installs update automatically). `doctor.sh` is
read-only and safe to run any time.
