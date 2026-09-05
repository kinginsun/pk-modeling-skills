# Plotting Monolix results — hand-crafted charts from result files

monolix-cli is analysis-only: it produces the result folder, nothing more.
After a run finishes, build the figures yourself with the features the run
actually produced — no auto-reporter script. The quality bar is a hand-crafted
dashboard (KPI strip, numbered cards with descriptions, dark theme, rich
tooltips, parameter tables) as a single self-contained ECharts HTML page, not
a generic dump.

## Workflow

1. Inspect the result folder: list files (top level, `IndividualParameters/`,
   `FisherInformation/`, `LogLikelihood/`, `Tests/`, `Bootstrap/`,
   `ModelBuilding/`).
2. Parse each existing output into chart-ready data (read the txt directly;
   they are small comma/tab tables — see anatomy below).
3. Pick charts using the **result feature → chart** table below; skip rows
   whose source files are missing.
4. Compose a single self-contained HTML (ECharts CDN, no build step):
   header with project/toolchain info → KPI stat cards → 2-column chart grid
   with numbered cards + one-line interpretation under each title →
   parameter summary table → footer with caveats.
5. Open the HTML in the browser to verify (serve via `python3 -m http.server`
   if the harness blocks `file://`).

## Result-folder anatomy

Result folder = `<exportpath>/` next to the `.mlxtran` (or the `-o` dir):

```text
populationParameters.txt        parameter,value,CV,se_lin,rse_lin,P2.5_lin,P97.5_lin
summary.txt                     estimates, SE/RSE/CI, iterations, OFV/AIC/BIC, dataset recap
predictions.txt                 id,time,<OBS>,popPred_medianCOV,popPred,indivPred_SAEM,indivPred_mode,indWRes_SAEM,indWRes_mode
IndividualParameters/
  estimatedIndividualParameters.txt   id,<param>_SAEM,...,<param>_mode,...,<covariates>
  estimatedRandomEffects.txt          id,eta_<param>_SAEM,...
  shrinkage.txt                       shrinkage per parameter (nan when no IIV)
FisherInformation/
  correlationEstimatesLin.txt   lower-triangular correlation matrix (+ rows/cols)
  covarianceEstimatesLin.txt    covariance matrix
LogLikelihood/logLikelihood.txt OFV / AIC / BIC / BICc
Tests/fixedEffects.txt          Wald test stat + p-value per covariate effect
Tests/normalityResiduals.txt    Shapiro-Wilk etc. on residuals
Bootstrap/                      Bootstrap_NNN/populationParameters.txt per replicate
ModelBuilding/                  modelBuilding.txt (COSSAC/SAMBA history)
ChartsData/                     binary chart blobs (not parseable; ignore)
.Internals/results.dat          binary (not parseable; ignore)
```

Multi-observation projects name predictions `y1`, `y2` and error params
`a1,b1,a2`; any predictions column that is not id/time/prediction/wres is
treated as an observation.

## Result feature → chart mapping

| Result feature present | Chart | Rationale / notes |
| --- | --- | --- |
| `predictions.txt` (fits exist) | ① Obs + IPRED per subject: scatter (obs) + lines (indivPred), subject selector or small multiples | The core deliverable; wide card, `dataZoom` for large data |
| `predictions.txt` popPred ≠ indivPred | ② GOF: obs vs popPred + obs vs indivPred with dashed y=x identity | Equal axes (`max` shared); use `type:'log'` for PK conc. spanning decades |
| `predictions.txt` indWRes column | ③ IWRES vs time scatter + zero markLine | Random scatter around 0 ⇒ structural + error model OK; color-split by sign |
| Multiple subjects, few parameters | η/EBE grouped bar per subject (from `estimatedRandomEffects.txt`) | Reveals IIV structure; skip when no IIV (all zeros) |
| `estimatedIndividualParameters.txt` with covariate columns | Individual parameters by category (e.g. bar of T50 per FORM) | For categorical covariates; scatter η-vs-covariate for continuous |
| `populationParameters.txt` with se/rse/CI | Parameter forest plot (value + 95% CI) and/or summary table (value, SE, RSE%, CI, CV%) | Prefer table + forest plot over a plain bar chart of raw values |
| `Tests/fixedEffects.txt` | Covariate effect significance bars (−log10 p or Wald stat) | Only when covariate effects were estimated |
| `FisherInformation/correlationEstimatesLin.txt` | Correlation heatmap (visualMap or matrix coords) | Flags overparameterization (|r|>0.95); ECharts 6 matrix system |
| `LogLikelihood/logLikelihood.txt` | KPI card: OFV / AIC / BIC | Put in the stat strip, not a chart |
| `ModelBuilding/` history | Criterion bars (OFV/AIC/BIC per model) with best-model markPoint | Only if a modelBuilding run exists |
| `Bootstrap/` replicates | Boxplots of estimates relative to reference (100% line) | Use relative % so parameters of different scales fit one chart |
| SAEM convergence chains (ChartsData or connectors `getChartsData`) | convergenceIndicator vs iteration, log y-axis, exploratory/smoothing markArea split | Only if the chain is actually available; `.Internals/results.dat` is binary |
| `summary.txt` | KPI strip: individuals/obs/doses, iterations (autostop), elapsed time, OFV/AIC/BIC | Parse the text sections; drives the header stats |

Rules of thumb:

- Number every card (①②③…) and add a one-line `desc` under the title that
  states what a good result looks like (e.g. "IWRES 随机分布于 0 线附近 →
  结构/误差模型设定合理").
- KPI strip first (grid of stat cards), then the chart grid; parameter table
  near the end; footer lists source files and caveats (e.g. bootstrap n small).
- Dark theme is the default deliverable style; keep axes/tooltip/legend
  consistent (single `baseAxis`/palette constants in the generated JS).
- Large datasets: cap scatter series at ~5k points or enable
  `sampling: 'lttb'` for lines; use `dataZoom` on fits plots.
- Single self-contained HTML with the CDN script tag; for offline use, drop
  `echarts.min.js` next to the HTML and swap the src.
- `plotResult(...)` in `<MONOLIX>` `[TASKS]` only controls the GUI's chart
  set; headless runs produce data only — which is why plotting happens here.

## Reference implementations

Two in-repo examples show the target quality (dark theme, KPI strip, numbered
cards, source-file footers):

- `examples/monolix-ivivc/echarts_report.html` (repository root): ①–⑥ numbered
  cards (fits with FORM legend, GOF, IWRES, T50-by-formulation bars,
  correlation heatmap, parameter table with SE/RSE/CI + Wald p-values), built
  from the txt outputs above with stdlib parsing only.
- `examples/monolix-theophylline/theophylline_monolix_report.html`: covariate
  model comparison report for the theophylline example.
