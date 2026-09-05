---
name: monolix-cli
description: >-
  Run MonolixSuite 2024R1 headless through the command line: estimation runs,
  model building (covariate search), convergence assessment and bootstrap on
  .mlxtran projects, plus lixoftConnectors R automation. Analysis only —
  plotting follows plotting.md, which maps result files to hand-crafted charts.
  Use when the user wants to run Monolix/PKanalix/Simulx without the GUI, batch
  .mlxtran projects, or script SAEM runs. Trigger terms: Monolix, mlxtran,
  mlxSuite, --no-gui, SAEM, modelBuilding, convergenceAssessment, bootstrap,
  lixoftConnectors.
---

# monolix-cli (headless MonolixSuite workflow)

> Skill directory = the folder that contains this `SKILL.md`. All relative
> paths below are relative to it (notably the `x86shim/` compiler shim).
> Environment setup (MonolixSuite on macOS, Rosetta): see `SETUP.md` at the
> repository root.
>
> Authoring `.mlxtran` files by hand (sections, mlxtran model syntax, PK
> macros, error models, worked example): see `references.md` in this folder.
> Plotting results: monolix-cli does **not** plot — after a run, follow the
> result-feature mapping in `plotting.md`.

## Installation layout (macOS, Apple Silicon via Rosetta)

- App bundle: `/Applications/MonolixSuite2024R1.app` (adapt the version tag if yours differs)
- Suite root (`lixoft.ini`): `/Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite`
- CLI entry points (`monolixSuite/bin/`): `monolix.sh`, `pkanalix.sh`, `simulx.sh`, `datxplore.sh`, `mlxEditor.sh`
- User data: `~/lixoft/` (license/, preferences/, monolix/monolix2024R1/{config,demos,tmp})
- Binaries are x86_64 → require Rosetta on Apple Silicon (`/usr/bin/pgrep oahd`).

## Basic command

On Apple Silicon, **prepend the x86_64 compiler shim to PATH** (see Gotchas →
model plugin architecture). The shim lives in this skill's `x86shim/` folder;
resolve it from this skill's own directory:

```bash
# SKILL_DIR = directory containing this SKILL.md
PATH="$SKILL_DIR/x86shim:$PATH" \
/Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite/bin/monolix.sh \
  --no-gui -p /absolute/path/project.mlxtran
```

- `-p, --project` — **absolute** path to the `.mlxtran` project (relative paths fail).
- `--no-gui` — mandatory for headless runs.
- `-t, --tool` — `monolix` (default, runs the estimation scenario), `modelBuilding`,
  `assessment`, or `bootstrap`. Note: the docs/help text sometimes say
  "convergenceAssessment" but the 2024R1 binary only accepts `assessment`
  (anything else aborts with "not a valid monolix perspective").
- `--config <file>` — settings file for the selected tool (blocks below).
- `-o, --output-dir` — output directory.
- `--thread N` — number of threads.
- `--mode none|basic|complete` — console verbosity. Since 2023R1 the console is
  silent by default; use `--mode complete` to watch progress.

Demo projects (good smoke tests): `~/lixoft/monolix/monolix2024R1/demos/`,
e.g. `1.creating_and_using_models/1.1.libraries_of_models/theophylline_project.mlxtran`.

## Tool config file (`--config`)

One file can hold several blocks; unspecified settings fall back to GUI defaults
(or the last saved settings in the project's result folder).

```text
[modelBuilding]
strategy=COSSAC            # COSSAC | SAMBA | covSAMBA | SCM
lin=true                   # linearization
copyData=false
stoppingCriterion=LRT      # LRT | bicc
LRTThreshold=0.01, 0.01    # forward, backward
correlationThreshold=0.3, 0.01
locked\<parameter>\<covariate>=in|out
selectedParameters=V, Cl, Tlag
selectedCovariates=sex, wt

[assessment]
nbruns=5
SEandLL=false
linearization=false
parameter\<pop_param>\interval=<lo>, <hi>

[bootstrap]
nbruns=200
sampling=nonparametric     # parametric | nonparametric
initialValues=initial      # initial | final
# runLikelihood/runSE: omit to skip; only value 'true' is accepted (2024R1)
#runLikelihood=true
#runSE=true
lin=false
sampleSize=<n>             # default = original n
stratifiedResampling=sex, wt
confidenceInterval=95
saveBootResults=false
saveBootData=false
replaceFailedConv=false
maxNbFailedRuns=20
cens\<obs>\left=<LOQ>
```

Examples:

```bash
# covariate search
monolix.sh --no-gui -t modelBuilding -p $PWD/warfarinPK_project.mlxtran --config mb.txt
# bootstrap
monolix.sh --no-gui -t bootstrap -p $PWD/warfarinPK_project.mlxtran --config bs.txt
```

Note for ≤2023R1: model building uses flat flags (`-s cossac -c lrt -a 0.01 -r 0.01 --lin true`);
assessment/bootstrap are not available from the CLI.

### Tested config gotchas

- `selectedCovariates` must match the **exact** covariate names in the
  `[CONTENT]` block (case-sensitive, e.g. `WEIGHT`, `SEX` for the theophylline
  demo); wrong names silently yield "No valid covariate found".
- `[bootstrap]`: `runLikelihood` and `runSE` are only accepted with value
  `true` (2024R1 quirk); omit them to skip SE/LL. `saveBootResults`,
  `saveBootData`, `replaceFailedConv`, `maxNbFailedRuns` work as documented.
- Bootstrap requires a prior SAEM run in the project's result folder; run the
  plain estimation task first (or `initialValues=final` won't help a fresh
  project). Output goes to `<result folder>/Bootstrap/`.

## Outputs

- Results go to the project's result folder (or `-o` dir): population/individual
  estimates (`populationParameters.txt`, `individualParameters.txt`, …), standard
  errors, correlation matrix, convergence chains.
- Charts data: enable "Export charts data" in preferences
  (`~/lixoft/monolix/monolix2024R1/config/config.ini`, `exportChartsData=true`)
  to get plot datasets in the result folder.

## Plotting results

monolix-cli stops at analysis: it produces the result folder, nothing more.
After any successful run, follow `plotting.md` in this skill: inspect which
output files exist, then build only the charts those features justify using
the result feature → chart mapping (self-contained ECharts HTML, or R +
ggplot2/lixoftConnectors when the user wants R figures). Do not use a
one-size-fits-all auto-reporter; e.g. SAEM chains only if convergence data is
available, bootstrap boxplots only if `Bootstrap/` exists.

## lixoftConnectors (R API — the better automation path)

```r
install.packages(
  "/Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite/connectors/lixoftConnectors.tar.gz",
  repos = NULL, type = "source", INSTALL_opts = "--no-multiarch")
library(lixoftConnectors)
initializeLixoftConnectors(software = "monolix",
  path = "/Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite")
loadProject("/abs/path/project.mlxtran")
runPopulationParameterEstimation()
getEstimatedPopulationParameters()
saveProject()
```

- On Apple Silicon you must use the **x86_64 build of R** for the connectors
  (e.g. `arch -x86_64 R`), and the x86shim PATH prefix above.
- Requires the `RJSONIO` dependency (`install.packages("RJSONIO")`).
- 2024R1 has **no `exitLixoftConnectors()`**; the connection lives for the R
  session and you quit by ending the session. Tested function names:
  `getEstimatedPopulationParameters`, `getEstimatedIndividualParameters`,
  `getEstimatedStandardErrors`, `getEstimatedLogLikelihood`, `runBootstrap`,
  `runAssessment`, `runModelBuilding`, `getChartsData`, `plotSaem`, etc.
- Full scripting (verified names in 2024R1): `runScenario`/`getScenario`/
  `setScenario` for scenario tasks, `getChartsData` for plot datasets,
  `plotSaem`/`plotIndividualFits`/`plotObservationsVsPredictions`/`plotVpc`/…
  for figures, `runSimulation` for simulations, `runEstimation` to run all
  estimation tasks at once.

## Validation / health check

```bash
cd /Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite
mkdir -p /tmp/mlx_validation_out   # output dir must exist
PATH="$SKILL_DIR/x86shim:$PATH" \
./lib/validationSuite --no-gui -s monolix \
  -i ./resources/validationSuite/maci64_x86/monolix -o /tmp/mlx_validation_out
```

Verified 2026-08: all reference projects report `OK` (≈5–6 min on a typical machine).

## Tested / verified (2026-08, MonolixSuite 2024R1, Apple Silicon)

- Estimation (`-t monolix`, default), modelBuilding (COSSAC), assessment,
  bootstrap, and validationSuite all run headless with the x86shim PATH prefix.
- lixoftConnectors runs end-to-end in x86_64 R after re-signing `libxl.dylib`.

## Examples

Runnable example projects live at the repository root under `examples/`:

- `examples/monolix-theophylline/` — theophylline pop-PK with covariate search
  (allometric scaling), including reference result folders.
- `examples/monolix-ivivc/` — level-A IVIVC `.mlxtran` project (metformin,
  Balan et al. data) plus a reference ECharts HTML report.

## Gotchas

- **Apple Silicon model-plugin architecture**: Monolix compiles each mlxtran
  model into a plugin dylib by invoking the first `g++` on `PATH`. The system
  compiler defaults to arm64, but the suite runs x86_64 under Rosetta, so the
  plugin fails to load (`Cannot load the Mlxtran plugin at ...`). Fix: prepend
  a shim dir containing `g++`/`clang++` that exec
  `/usr/bin/clang++ -arch x86_64 "$@"` (this skill ships one in `x86shim/`).
  Compiled plugins are cached under `~/lixoft/monolix/monolix2024R1/modules/`;
  delete that folder after architecture changes.
- **Code signing**: modified suite files (e.g. a patched `libxl.dylib`) get an
  invalid signature and macOS SIGKILLs any process that loads them (exit 137,
  `CODESIGNING Invalid Page` in crash reports). Check with
  `codesign -v <file>` and re-sign ad-hoc:
  `codesign --remove-signature <file>; codesign --force --sign - <file>`.

- All paths in CLI args must be absolute.
- The activation/license check runs before any task; without a valid license the
  CLI blocks (it may spawn the interactive `licenseActivate` GUI dialog even with
  `--no-gui`). Activate once via GUI or a valid `.lic` first.
- Diagnostic logs: `~/lixoft/monolix/monolix2024R1/tmp/Monolix.log`;
  RLM diagnostics via `RLM_DIAGNOSTICS=/tmp/rlm.log RLM_DEBUG=1`.
- Kill stray headless runs: `pkill -f "monolixSuite/lib/monolix"`.
