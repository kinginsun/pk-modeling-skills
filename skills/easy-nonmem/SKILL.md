---
name: easy-nonmem
description: >-
  Conversational NM-TRAN/NONMEM control-stream authoring, PsN execute-based runs,
  and quick R plots from $TABLE output. Bundles NONMEM 7.6 reference manuals under
  references/ next to this file. Use when the user builds or edits NONMEM models
  (.mod/.ctl), runs execute/nmfe, wants IVIVC/PKPD control files tested, or asks
  for DV–PRED diagnostics and figures. Trigger terms: NONMEM, NM-TRAN, PsN,
  execute, $INPUT, $ESTIMATION, FOCE, SAEM, VPC, gof plots.
---

# easy-nonmem (easy NONMEM workflow)

> Skill directory = the folder that contains this `SKILL.md`. All relative
> paths below are relative to it. Environment setup (NONMEM 7.6, PsN, R on
> macOS): see `SETUP.md` at the repository root.

## Requirements

- **NONMEM 7.6** is installed and the **`nmfe76`** driver is on your `PATH` (verify with `which nmfe76`).
- **PsN** is installed and **`execute`** (and other PsN commands such as `vpc`, `bootstrap`, etc.) are on your `PATH` as needed.
- **R** with `ggplot2` for figures (see `reference.md`).

## When to read local docs

Official NONMEM 7.6 help ships **inside this skill** under `references/` (sibling of this `SKILL.md`):

| Kind                           | Path (relative to this skill folder) |
| ------------------------------ | ------------------------------------ |
| NM-TRAN `$` record, plain text | `references/help/$<RECORD>.ctl`      |
| User guides (Markdown)         | `references/guides/I.md`, `IV.md`, … |

Always read the relevant `references/help/$*.ctl` **before** inventing options.

**Suggested manuals**: `references/guides/IV.md` (NM-TRAN), `references/guides/VI.md` (PREDPP), `references/guides/VII.md` (estimation), `references/guides/VIII_part1_p1-500.md` + `VIII_part2_p501-876.md` (Help), `references/guides/useful_variables.md`.

## Conversation-first control stream

1. **Clarify**: population vs single-subject; route; dosing; ADVAN/TRANS (or `$DES`); residual error model; estimation method (FO/FOCE/Laplace/SAEM/IMPORTANCE/BAYES etc.); data columns and ignore rules (`IGNORE=@`, `IGNORE=(...)`).
2. **Data**: confirm delimiter, `$DATA` path (relative to run directory or copied with PsN), and **required** items for the ADVAN (e.g. `EVID`, `CMT`, `AMT`, `RATE`, `MDV`, `DV`).
3. **Draft** a minimal runnable skeleton, then add `$TABLE` for diagnostics (see [reference.md](reference.md)).
4. **Naming**: PsN convention is **`run1.mod`** (can reference `foo.csv`). `execute` accepts multiple models.

## Run (PsN)

Use **PsN `execute`** so retries, directories, and nmtran checks are consistent.

```bash
# From the folder that contains the model and data (or use absolute paths in $DATA)
execute run1.mod -directory=run1_execute
```

Useful flags (see `execute -h`):

- `-threads=N` — parallel, if configured
- `-clean=2` — tidy intermediates after success
- `-check_nmtran` — stop early on NM-TRAN issues

**NONMEM driver**: if `nmfe76` fails (e.g. Docker-based wrapper/socket issues), fix the local NONMEM installation or point PsN at a working `nmfe`.

## Test checklist

- [ ] NM-TRAN: no typos in records; `$INPUT` matches data columns; `$SUBROUTINES` matches `$MODEL`.
- [ ] `$THETA` / `$OMEGA` / `$SIGMA` sizes match `$PK`–`$ERROR` (and `#THETA` in abbreviated code if used).
- [ ] `execute` completes; inspect `*.lst` for termination and errors.
- [ ] Tables exist where `$TABLE` requested (e.g. `sdtab1`, `patab1`).

## Figures (minimal path)

1. Ensure `$TABLE` outputs **ID, TIME, DV, PRED, IPRED** (and **WRES** or **CWRES** if needed).
2. Use **R + ggplot2** on the merged table (see [reference.md](reference.md) for snippets).

For publication VPC or bootstrap workflows, use additional PsN tools (`vpc`, `bootstrap`, etc.) only when the user asks—keep the default loop to **execute + tables + R plots**.

## What not to do

- Do not guess rare `$ESTIMATION` / `$COVARIANCE` options without checking `references/help/$estimat.ctl` and `references/help/$covar.ctl`.
- Do not strip required items or ignore `EVID` semantics when using PREDPP.
- Do not assume `nmfe*` works without verifying (wrapper/Docker/permissions).

## Examples

Runnable example projects live at the repository root under `examples/`:

- `examples/nonmem-pop-pk/` — minimal one-compartment IV population PK run (`run1.mod` + `data.csv`, with reference `.lst`/`.ext`).
- `examples/nonmem-ivivc/` — level-A IVIVC with Hill-type dissolution link (metformin, Balan et al. data) plus an R GOF script.

## More detail

- Control templates, `$TABLE` block, and R plotting snippet: [reference.md](reference.md)
