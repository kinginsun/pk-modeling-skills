# pk-modeling-skills

Agent skills for **population PK/PD modeling** on macOS. Give these skills to
an AI coding agent (Cursor, Claude Code, Codex, …) and it can author NONMEM
control streams, run PsN and headless MonolixSuite, and produce diagnostic
plots — with the official manuals bundled for offline lookup.

> **One URL for an agent to self-install**: hand your agent
> [`SETUP.md`](SETUP.md) (or its raw GitHub URL) and it will follow the
> instructions to install, configure, and test this skills collection.

## Skills

| Skill | Path | What it does |
|-------|------|--------------|
| **easy-nonmem** | [`skills/easy-nonmem`](skills/easy-nonmem/SKILL.md) | Conversational NM-TRAN control-stream authoring, PsN `execute` runs, R/ggplot2 diagnostics. Ships NONMEM 7.6 Users Guides as markdown (`references/guides/`) plus all `$record` help files (`references/help/`). |
| **monolix-cli** | [`skills/monolix-cli`](skills/monolix-cli/SKILL.md) | Headless MonolixSuite 2024R1: estimation, model building (COSSAC/SAMBA), convergence assessment, bootstrap, and `lixoftConnectors` R automation. Ships the Apple-Silicon x86_64 compiler shim and an `.mlxtran` authoring reference. |

Tool integrations are modular: more tools (e.g. Phoenix NLME, nlmixr, Stan)
can be added as new `skills/<tool>` folders without touching existing ones.

## Repository layout

```text
pk-modeling-skills/
├── README.md            ← this file (for humans)
├── SETUP.md             ← agent-facing install/config/test instructions
├── LICENSE
├── skills/              ← agent skills (tool-agnostic location)
│   ├── easy-nonmem/     ← NONMEM 7.6 + PsN workflow + bundled manuals
│   └── monolix-cli/     ← headless MonolixSuite workflow + x86shim
├── scripts/
│   ├── install.sh       ← copy/symlink skills into .cursor/skills or ~/.claude/skills
│   └── doctor.sh        ← environment checks + smoke tests
└── examples/            ← small, runnable example projects
    ├── nonmem-pop-pk/        1-cpt IV popPK (run1.mod + data.csv, reference .lst)
    ├── nonmem-ivivc/         level-A IVIVC, Hill dissolution link (Balan et al. metformin)
    ├── monolix-theophylline/ theophylline popPK + covariate search + reference outputs
    └── monolix-ivivc/        IVIVC .mlxtran project + reference ECharts report
```

## Requirements (macOS)

- **macOS 13+**, Apple Silicon or Intel. Apple Silicon needs Rosetta 2 for MonolixSuite.
- **NONMEM 7.6** (licensed) with `nmfe76` on `PATH` — native install or Docker wrapper.
- **PsN** (Perl-speaks-NONMEM) with `execute` on `PATH`.
- **gfortran** (Homebrew `gcc`), **R ≥ 4.3** with `ggplot2`, **Python 3.10+**.
- **MonolixSuite 2024R1** (licensed) for the `monolix-cli` skill.

Step-by-step installation and verification: [`SETUP.md`](SETUP.md).

## Quick start

```bash
git clone https://github.com/kinginsun/pk-modeling-skills.git
cd pk-modeling-skills

# 1. Check what is already installed / what is missing
./scripts/doctor.sh

# 2. Install skills into your agent's skills directory
./scripts/install.sh            # auto-detects (~/.claude/skills, .cursor/skills, …)
./scripts/install.sh --target ~/.claude/skills --link   # or pick explicitly

# 3. Smoke-test the toolchain end-to-end (needs NONMEM + PsN installed)
./scripts/doctor.sh --run-examples
```

Then ask your agent something like:

- “Using the easy-nonmem skill, write a 2-compartment oral PK model for my data and run it with PsN.”
- “Run a bootstrap on this .mlxtran project headlessly with Monolix.”

## Legal notes

- **NONMEM** is commercial software from ICON plc; you need a valid license.
  This repo distributes **no NONMEM binaries, installers, or license files** —
  only documentation converted from the PDF manuals that ship with licensed
  NONMEM installations.
- **MonolixSuite** is commercial software from Lixoft/Inria; you need a valid
  license. No MonolixSuite binaries are distributed here.
- Example datasets derive from published literature (theophylline demo data;
  metformin PK/dissolution data from Balan et al., AAPS PharmSciTech 2001).

## License

MIT — see [LICENSE](LICENSE).
