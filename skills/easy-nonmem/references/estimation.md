# Estimation, Covariance, and Simulation Methods

Distilled from NONMEM 7.6 Users Guides VII (Conditional Estimation Methods)
and VIII (the `$ESTIMATION`, `$COVARIANCE`, `$SIMULATION` record help).

---

## Choosing an estimation method

Classical methods: FO (`METHOD=0`), FOCE (`METHOD=1`), Laplacian, Hybrid, and
Centering variants. NONMEM 7 EM/Bayesian methods: ITS, IMP, IMPMAP, SAEM,
BAYES, DIRECT, NUTS, CHAIN.

Hierarchy and guidance (Guide VII):

- Laplacian should perform no worse than FOCE, FOCE no worse than FO.
- Need for conditional methods increases as models become more nonlinear in
  eta, with multiple dosing, and with rich data per individual.
- FO is often adequate for linear pop-PK (especially simple bolus dosing);
  FOCE is frequently needed even there — check bias in DV vs PRED plots.
- For categorical / discrete-ordinal data, use Laplacian.
- Conditional methods differ less from FO when inter-individual variability
  (OMEGA) is small or data per individual are sparse (eta shrinkage to 0).
- FOCE with INTERACTION should be tried when residual variance is
  eta-dependent and data are rich; without interaction it can be biased.
- Objective function values are comparable only within the same method.

Typical workflows:

```
$ESTIMATION METHOD=1 INTERACTION MAXEVAL=9999        ; FOCE-I (workhorse)
$ESTIMATION METHOD=1 LAPLACIAN MAXEVAL=9999          ; Laplace (nonlinear/likelihood)
$ESTIMATION METHOD=COND INTERACTION NOABORT          ; with theta-recovery
$ESTIMATION METHOD=SAEM NBURN=3000 NITER=1000        ; SAEM
$ESTIMATION METHOD=BAYES NBURN=4000 NITER=10000      ; MCMC Bayesian
$ESTIMATION METHOD=1 INTERACTION AUTO=3              ; NUTS setup helper (NM74+)
```

Method-specific model-building advice:

- Prefer multiplicative IIV (e.g. `CL=THETA(1)*EXP(ETA(1))`) so conditional
  exploration of eta never yields impossible values (negative CL, flip-flop
  KA/KE). With FO both forms are equivalent; with FOCE they are not.
- If FOCE terminates on a PRED error (negative rate constant etc.), fix the
  parameterization first; add `NOABORT` only after inspecting the error. With
  PREDPP, never start with NOABORT — it masks PREDPP error detection.
- Lag-time models can hit undefined derivatives (change-point problem);
  `METHOD=HYBRID ZERO=(k)` zeroing the lag-time eta reduces the risk.

## `$ESTIMATION` record essentials

Optional record; may repeat — options carry over to the next `$ESTIMATION`
unless restated, and final estimates become the next step's initial estimates.
May also be coded `$ESTM`/`$ESTIMATE`.

| Option | Meaning |
|---|---|
| `METHOD=0` / `METHOD=1` | FO / conditional (FOCE). Also `METHOD=HYBRID` (requires `ZERO=(list)` of eta indices fixed to 0). EM/Bayes: `METHOD=ITS`, `IMP`, `IMPMAP`, `SAEM`, `BAYES`, `DIRECT`, `NUTS`, `CHAIN`. Any EM/Bayes method implies `METHOD=1` and population data. |
| `INTERACTION` / `NOINTERACTION` | Preserve (or ignore) eta-dependence of the residual-error model. NM7.3+: INTERACTION defaults on for EM/Bayes; default off for classical methods. |
| `LAPLACIAN` / `NOLAPLACIAN` | Second-order (in eta) Laplace approximation. Not allowed with `METHOD=0`. With EM methods it is used in MAP phases (IMP/IMPMAP/ITS) or ignored (SAEM/BAYES). Cannot combine with `$ABBREVIATED DERIV2=NO` unless `NUMERICAL`. |
| `CENTERING` / `NOCENTERING` | Constrain average conditional eta estimates near 0. `METHOD=1` only; not with INTERACTION. Use only after bias persists despite good modeling — not routinely. |
| `FO` / `NOFO` | Use (or not) the first-order model with `METHOD=1 CENTERING`. |
| `NUMERICAL` / `NONUMERICAL` | Numeric vs PRED-computed second eta derivatives for Laplacian. |
| `MAXEVALS=n` | Max objective-function evaluations (each = one data pass). Default generous; `MAXEVALS=0` omits the step (e.g. POSTHOC only); `-1` re-uses prior value with `$MSFI`. |
| `PRINT=n` | Iteration summaries at 0th, every nth, and last iteration (0 = none; default 9999). |
| `SIGDIGITS=n` (`NSIGDIGITS`) | Significant digits required in final estimates (default 3). Not used by Monte-Carlo methods. |
| `SIGL=n`, `SIGLO=n` | Finite-difference step-size control; recommended `SIGLO<=TOL`, `SIGL<=SIGLO`, `NSIG<=SIGL/3`. Classical methods often need stricter SIGL/TOL (e.g. 12) in `$COVARIANCE` than in `$ESTIMATION`. |
| `NOABORT` / `ABORT` / `NOHABORT` | Theta-recovery from PRED error code 1 / default abort / positive-definite correction at all levels (use NOHABORT with care). |
| `SLOW` / `NOSLOW` / `FAST` | Slower-but-safer vs faster computation. SLOW required with mixture+CENTERING or NUMERICAL. |
| `POSTHOC` / `NOPOSTHOC` | Estimate individual etas after estimation (with `MAXEVALS=0`, etas come from the initial estimates). Default off with METHOD=0; not allowed with METHOD=1. |
| `MSFO=filename` | Write a model specification file. |
| `FILE=filename`, `FORMAT`/`DELIM=s`, `NOTITLE`, `NOLABEL`, `ORDER=xxxf` | Raw/additional output file controls (default format `s1PE12.5`; ORDER default `TSOL`). |
| `MSFO`, `NOPRIOR=[0|1]` | Suppress prior information for one step (e.g. maximize without priors, then BAYES with them). |
| `THETABOUNDTEST`, `OMEGABOUNDTEST`, `SIGMABOUNDTEST` | Boundary tests (classical). |
| `AUTO=0|1|2|3` | Let NONMEM choose good settings (ignored by FO/FOCE/Laplace). AUTO=2: NUTS "Matt trick"; AUTO=3: NUTS eta sampling. |
| `SEED=n`, `CLOCKSEED=[0|1]` | RNG seed (default 14455); CLOCKSEED=1 adds 10000*seconds-after-midnight. |
| `RANMETHOD=[n|S|m|P]` | RNG choice: n = 0..4 (3 = Knuth ran3, default); S = Sobol quasi-random (with optional scrambling m=0..3); P = per-subject seed paths (NM74). Propagates to later `$EST` records, not to `$CHAIN`/`$TABLE`. |
| `PARAFILE=[filename|ON|OFF]`, `PARAFPRINT=n` | Parallelization controls. |
| `LNTWOPI`, `OLNTWOPI`, `PRIORC` | Include N*log(2pi) / per-observation constant / prior constant in reported objective. |

### EM/Bayesian method knobs

| Option | Used with | Meaning (defaults) |
|---|---|---|
| `NBURN=n` | SAEM, BAYES | Max stochastic/burn-in iterations (2000 SAEM, 4000 BAYES). |
| `NITER=n` (`NSAMPLE`) | ITS/IMP/IMPMAP, SAEM, BAYES | Max iterations (50 ITS-family; 1000 SAEM accumulation; 10000 BAYES stationary). |
| `ISAMPLE=n` | IMP/IMPMAP, SAEM, BAYES | Samples per subject for E-step (300); M-H chains (2 SAEM, 1 BAYES). |
| `ISAMPLE_M1/M1A/M1B/M2/M3=n` | SAEM, BAYES | Metropolis-Hastings kernel iteration counts (default 2,0,2,2,2). |
| `IACCEPT=x` | IMP, SAEM, BAYES | Target acceptance fraction; SAEM/BAYES OMEGA scaling (0.4); IMP proposal variance expansion (0.4; 0 lets NONMEM choose per subject, possibly with t densities). Lower (0.1-0.3) for sparse/categorical data. |
| `CTYPE=0..4` | EM/Bayes burn-in & ITS/IMP/IMPMAP estimation termination | Which parameters the linear-regression convergence test covers (CTYPE=4 applies to classical: objective stable to NSIG digits over 10 iterations). |
| `CITER=n`, `CINTERVAL=n` | EM/Bayes | Iterations used for / interval of the convergence test (10 default). |
| `EONLY=[0|1]` | IMP | Evaluate IMP objective with expectation step only, no parameter advance (useful as `$EST METHOD=IMP EONLY=1` after SAEM for an OBJ). |
| `CONSTRAIN=n` | SAEM (annealing) | Simulated annealing pattern for OMEGA/SIGMA during burn-in: 0/4 none, 1/5 omega, 2/6 sigma, 3/7 both (default 1); >=4 also anneals omega diagonals fixed to 0. Via subroutine CONSTRAINT; see `$ANNEAL`. |
| `MAPITER`, `MAPITERS`, `MAPCOV`, `MAPINTER`, `OPTMAP` | IMP, IMPMAP | MAP optimization controls. |
| `DF=n` | IMP, IMPMAP | t-distribution proposal density degrees of freedom (0 = normal). |
| `STDOBJ=x`, `ISAMPEND=n` | IMP/DIRECT | Vary sample count between ISAMPLE and ISAMPEND until OBJ stochastic SD < STDOBJ; ISAMPEND alone preprocesses to pick ISAMPLE. |
| `THIN=n` | BAYES, NUTS | Keep every nth iteration in the raw output file (default 1). |
| `GRD=s`, `MUM=s` | BAYES / MU-referencing | Per-theta Gibbs/MH/default designations; MU-modeling designations (M/N/D/X). |
| `TTDF=n`, `OLKJDF`, `SLKJDF`, `OVARF`, `SVARF` | NUTS (also BAYES) | Prior choices: t-density thetas, LKJ decorrelation for omega/sigma blocks, log-normal or half-t (use -1 for half-Cauchy) variance priors. Per-parameter records: `$TTDF`, `$OLKJDF`, `$SLKJDF`, `$OVARF`, `$SVARF`. |
| `NUTS_*` | NUTS | Tuning: `NUTS_MASS` (default B), `NUTS_MAXDEPTH` (10), `NUTS_DELTA` (0.8), `NUTS_INIT` (0.075), `NUTS_BASE` (0.025), `NUTS_GAMMA` (0.05), etc. `AUTO=2/3` set alternative sampling strategies. |
| `BIONLY=[0|1]`, `BAYES_PHI_STORE=[0|1]` | BAYES | Sample individual parameters only (population fixed); store phi/eta per iteration in root.iph. |
| `PHITYPE=n` | EM/Bayes | root.phi contains conditional-mean parameters (0) or etas (1). |
| `SELECT=[0..3]`, `TBLN=n` | `METHOD=CHAIN` with `$CHAIN` | Sample selection scheme; table within a raw output file. |
| `MCETA=n` | IMP/IMPMAP/ITS/classical | Initial eta setting for MAP optimization (0; 1; or >1 = test MCETA-1 random eta samples). |
| `NONINFETA=[0|1]` | Classical | Fix bad gradients when some etas are unused by some subjects (e.g. KA eta with IV-only subjects). |

Reserved speed variables (NM74): set `MUFIRSTREC=1` and `OBJQUICK=1|2` in
`$PRED`/`$PK` (after `include nonmem_reserved_general`) to speed NUTS/BAYES/
FOCE/ITS/EM. OBJQUICK=2 is incompatible with `$LEVEL`/`$MIX`.

### Option availability by method (abridged; X = relevant)

| Option | Classical | ITS | DIRECT | IMP | IMPMAP | SAEM | BAYES | NUTS |
|---|---|---|---|---|---|---|---|---|
| MAXEVALS | X | | | | | | | |
| CENTERING | X | | | | | | | |
| LAPLACIAN | X | X | * | * | X | * | * | * |
| NUMERICAL | X | X | * | * | X | * | * | * |
| NBURN | | | | | | X | X | X |
| NITER/NSAMPLE | | X | X | X | X | X | X | X |
| ISAMPLE | | | | | | X | X | X |
| IACCEPT | | | | X | X | X | X | X |
| EONLY | | | X | X | X | X | | |
| CONSTRAIN | | X | X | X | X | X | X | X |
| CTYPE | (4) | X | X | X | X | X | X | X |
| SLOW/FAST | X | X | | | | | | |
| THETABOUNDTEST etc. | X | | | | | | | |
| TTDF/OLKJDF/SLKJDF/NUTS_* | | | | | | | | X |

(From `estopts.ctl`; `*` = may be needed to suppress NMTRAN/NONMEM messages.)

---

## `$COVARIANCE` record

Optional; outputs standard errors, covariance, inverse covariance, and
correlation matrices. May also be coded `$COVR`.

Key options:

| Option | Meaning |
|---|---|
| `MATRIX=R` / `MATRIX=S` | Use 2*R^-1 (Hessian-based; SEs closer to other regression software) or 4*S^-1 (gradient cross-product) instead of default R^-1 S R^-1. `MATRIX=R` not with SPECIAL. |
| `SPECIAL` | Computation for recursive PRED (default when PREDPP is used). |
| `PRINT=[E][R][S]` | Extra output: eigenvalues of correlation matrix, .5*R, .25*S. |
| `COMPRESS` | Print arrays in compressed format. |
| `SLOW` / `NOSLOW` / `FAST` | As for `$ESTIMATION`; SLOW required with mixture+CENTERING or NUMERICAL. |
| `TOL=n`, `ATOL=n`, `SIGL=n`, `SIGLO=n` | Override estimation-step tolerances for this step; classical methods often need stricter values here. |
| `NOFCOV` | Skip covariance for classical steps (e.g. when FOCE is last but only EM SEs are wanted). |
| `THBND=n` | 1 (default) keeps logistic transformation of bounded thetas; set 0 with narrow bounds to assess derivatives w.r.t. thetas themselves. |
| `PARAFILE`, `PARAFPRINT` | Parallelization. |
| SIR options: `SIRSAMPLE=[list]` (300-10000), `SIRNITER=n` (1), `SIRCENTER=n` (0), `SIRDF=n` (0), `SIRPRINT=n`, `FILE`, `FORMAT`, `SIRTHBND`, `SIRMINWT`/`SIRMAXWT` (0.001/1000), `SIR_CAPCORR`, `SIRSEED` (11456), `SIRCLOCKSEED`, `SIRPARAFILE`, `SIRPARAFPRINT`, `IACCEPT` (1), `IACCEPTL` (0), `RANMETHOD` | Sampling-Importance-Resampling (SIR) for parameter uncertainty (NM74+). Analyze with `table_quant` / `table_resample` utilities. |
| `PRECOND`, `PRECONDS`, `PFCOND`, `PRETYPE`, `FPOSDEF`, `CHOLROFF`, `KNUTHSUMOFF`, `POSDEF`, `RESUME` | Positive-definiteness / Cholesky handling for the covariance estimate. |
| `CONDITIONAL` / `UNCONDITIONAL` / `OMITTED` | Control when the step executes relative to `$ESTIMATION` options. |

With `$COV` present, IMP/IMPMAP/ITS get SEs for every `$EST`; classical
methods get SEs only if they are the last estimation step and NOFCOV is not
set.

---

## `$SIMULATION` record

Optional; may also be coded `$SIMULATE`/`$SIML`. Each parenthesized group
defines one random source; by default source 1 simulates etas and epsilons.

```
$SIMULATION (seed1 [seed2] [NORMAL|UNIFORM|NONPARAMETRIC] [NEW]) ...
            [CLOCKSEED=[0|1]] [SOURCE_EPS=n]
            [SUBPROBLEMS=n] [ONLYSIMULATION] [OMITTED]
            [PREDICTION|NOPREDICTION] [TRUE=INITIAL|FINAL|PRIOR] [TTDF=n]
            [BOOTSTRAP=n [REPLACE|NOREPLACE] [STRAT=label] [STRATF=label]]
            [NOREWIND|REWIND] [SUPRESET|NOSUPRESET]
            [RANMETHOD=[n|S|m|P]] [PARAFILE=[filename|ON|OFF]]
```

| Option | Meaning |
|---|---|
| `seed1`, `seed2` | Integer seeds 0..2147483647; seed1=-1 continues the source from the previous problem. |
| `NORMAL` (default) / `UNIFORM` | Pseudo-normal (0,1) or uniform [0,1] source. For the eta/epsilon source, OMEGA/SIGMA define the variance-covariance. |
| `NONPARAMETRIC` | Simulate etas from the nonparametric distribution of an earlier problem (requires input MSF). Only for the 2nd+ source. |
| `NEW` | New eta (epsilon) vector on every SIMETA (SIMEPS) call, not only at new ID (L2). |
| `CLOCKSEED=[0|1]` | Seed offset by clock for automated replications. |
| `SOURCE_EPS=n` | Use source n for epsilon simulation instead of source 1 (NM75). |
| `SUBPROBLEMS=n` | Repeat the whole problem n times; each subproblem continues the random sources and re-uses (possibly transgenerated) data. |
| `ONLYSIMULATION` | Simulate without evaluating an objective function; WRES = 0; no `$ESTIM`/`$COV`/`$NONP`. |
| `PREDICTION` (default) / `NOPREDICTION` | Simulated observation is Y/F (set DV too in simulation blocks, then `Y=DV`) vs DV directly (also set `DV=Y`; etas are population etas). Both ONLYSIM-only. |
| `TRUE=INITIAL|FINAL|PRIOR` | Parameter values used as "true" values. |
| `TTDF=n` | t-distribution degrees of freedom for simulated thetas. |
| `BOOTSTRAP=n` | Resample subjects n times, `REPLACE`/`NOREPLACE`, optionally stratified by `STRAT=label` / `STRATF=label`. |
| `REWIND`/`NOREWIND` | Reposition/re-use data files across subproblems (NM74+). |
| `REQUESTFIRST`, `REQUESTSECOND` | Ask PRED for first/second eta derivatives of PRED-defined items during simulation (do not compute such items inside a simulation block). |
| `SUPRESET`/`NOSUPRESET`, `RANMETHOD`, `PARAFILE` | Superproblem reset behavior; RNG choice; parallelization. |

Notes:

- With `$ESTIMATION` present (and no LIKELIHOOD option), etas are
  single-subject etas unless epsilons also appear; with `$SIMULATION` only
  and `NOPREDICTION`, etas are population etas.
- A "simulation block" in abbreviated code runs only during simulation
  (see ICALL).
- To simulate with estimated parameters, combine `$ESTIMATION` (or `$MSFI`)
  with `$SIMULATION TRUE=FINAL`.
