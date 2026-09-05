# mlxtran file authoring reference (MonolixSuite 2024R1)

Distilled from the official MonolixSuite 2024R1 docs
(https://monolixsuite.slp-software.com/monolix/2024R1/) and verified against
the local demo projects (`~/lixoft/monolix/monolix2024R1/demos/`). Use this
to hand-write or patch `.mlxtran` project files for headless CLI runs.

## Big picture

A `.mlxtran` project file is plain text with 5 top-level sections, in this
order:

```text
<DATAFILE>    — dataset location, delimiter, column roles
<MODEL>       — [COVARIATE], [INDIVIDUAL], [LONGITUDINAL] (+ optional [POPULATION])
<FIT>         — maps observation columns/types to model outputs
<PARAMETER>   — initial values and estimation methods
<MONOLIX>     — [TASKS] workflow and [SETTINGS]
```

The structural model can live inline in `[LONGITUDINAL]` or be referenced
from the built-in library (`file = 'lib:xxx.txt'`) or a custom `.txt` file
(`file = 'path/model.txt'`). mlxtran is a *declarative* language: equations
are mathematical definitions, not sequential instructions. `;` starts a
comment. Reserved keywords cannot be reused as parameter names.

## `<DATAFILE>`

```text
<DATAFILE>

[FILEINFO]
file = 'data/mydata.txt'          # relative to the project file (or absolute)
delimiter = tab                   # tab | comma | space | semicolon
header = {ID, TIME, AMT, Y, WT, SEX}

[CONTENT]
ID   = {use=identifier}
TIME = {use=time}
AMT  = {use=amount}
Y    = {use=observation, name=Y, type=continuous}
WT   = {use=covariate, type=continuous}
SEX  = {use=covariate, type=categorical}
```

Column `use=` types (verified across demos; NONMEM-like column types):

| use | role |
| --- | --- |
| `identifier` | subject ID (mandatory) |
| `time` | time of dose/observation (mandatory) |
| `amount` | dose amount on dose rows, `.` on observation rows |
| `observation` | measurement column; add `type=` and (multi-Y) `yname=` |
| `observationtype` | DVID column distinguishing multiple observation types |
| `covariate` | `type=continuous` or `type=categorical` |
| `occasion` | occasion index for inter-occasion variability |
| `admid` | administration id (routes) |
| `censored` | BLQ/missing-data flag (1=censored) |
| `limit` | LOQ value for censored observations |
| `ss` | steady-state dose flag |
| `ii` | interdose interval |
| `addl` | number of additional doses |
| `rate` / `tinf` | infusion rate / infusion duration |
| `sort` | sort key |
| `regressor` | time-varying covariate read into the model |
| `evid` | event id |

### Data format rules

- Long format: one record = one individual at one time point. Each line holds
  a dose amount OR an observation (or both).
- Missing values are `.` (never blank or NA). Covariates must be present at
  least once per individual and are constant within an individual; time-varying
  covariates must be `use=regressor`.
- Dose rows: AMT filled, observation empty; observation rows: Y filled, AMT `.`.
- Multiple observation types share ONE observation column + an
  `observationtype` (DVID) column.
- Supported input files: txt/csv/tsv; 2024+ also xlsx and SAS (.sas7bdat/.xpt).

### Multiple observations (PK + PD example)

```text
[CONTENT]
dv   = {use=observation, yname={'1','2'}, type={continuous, continuous}}
dvid = {use=observationtype}

[SETTINGS]
dataType = {'1'=plasma, '2'=plasma}
```

Observation names in the GUI/results become `y1`, `y2`, … following the
yname/DVID values. Named alternative:
`OBS = {use=observation, name={y1_Cp, y2_Cm}, yname={'1_Cp','2_Cm'}, type={continuous, continuous}}`
(demo `parent_metabolite_project.mlxtran`).

### Censored data (BLQ)

Add `CENS = {use=censored}` and `LIMIT = {use=limit}` columns; set LOQ
per-observation in bootstrap config via `cens\<obs>\left=<LOQ>`.

## `<MODEL>`

### `[COVARIATE]`

```text
[COVARIATE]
input = {WT, SEX}
SEX = {type=categorical, categories={'F', 'M'}}

EQUATION:                      # optional covariate transformations
logtWT = log(WT/70)
```

Categories must be listed (strings or integers; quote strings containing
spaces/symbols). Transformations defined here (e.g. `logtWT`) let the
individual model express power-law covariate effects.

### `[INDIVIDUAL]` — parameter distributions

```text
[INDIVIDUAL]
input = {ka_pop, omega_ka, V_pop, omega_V, Cl_pop, omega_Cl}

DEFINITION:
ka = {distribution=logNormal, typical=ka_pop, sd=omega_ka}
V  = {distribution=logNormal, typical=V_pop,  sd=omega_V}
Cl = {distribution=logNormal, typical=Cl_pop, sd=omega_Cl}
```

- Distributions: `normal`, `logNormal`, `logitNormal` (bounded, add
  `min=`/`max=`, default 0/1), `probitNormal`.
- `typical=` (or `mean=`), `sd=` (or `var=`); no IIV → `no-variability`
  (distribution still stated, e.g. for bounds).
- Parameter names are free; Monolix convention: `xxx_pop`, `omega_xxx`.

**Covariate effects** (added linearly on the transformed parameter, e.g.
`log(V)` for logNormal; betas follow naming `beta_<param>_<cov>[_<cat>]`):

```text
input = {..., beta_V_logtWT, beta_Cl_SEX_F, WT, SEX}
V  = {distribution=logNormal, typical=V_pop, covariate=logtWT, coefficient=beta_V_logtWT, sd=omega_V}
Cl = {distribution=logNormal, typical=Cl_pop, covariate=SEX, coefficient={0, beta_Cl_SEX_F}, sd=omega_Cl}
```

Reference category gets coefficient `0`; order of betas matches the order of
`categories={...}` listed under input.

**Correlations between random effects** — every pair inside a correlation
group must be listed; parameters belong to one group only:

```text
correlation = {r(V, Cl)=corr_V_Cl, r(ka, Cl)=corr_ka_Cl, r(ka, V)=corr_ka_V}
```

**Inter-occasion variability** (requires an occasion column, `use=occasion`):

```text
ka = {distribution=logNormal, typical=ka_pop, varlevel={id, id*occ}, sd={omega_ka, gamma_ka}}
correlation = {level=id*occ, r(ka, Tlag)=corr2_ka_Tlag}
```

### `[POPULATION]` — priors for Bayesian (MAP) estimation

```text
[POPULATION]
DEFINITION:
ka_pop = {distribution=logNormal, typical=2, sd=0.1}
```

Used together with `ka_pop = {value=2, method=MAP}` in `<PARAMETER>`
(demo `7.miscellaneous/7.2.bayesian_estimation/theobayes2_project.mlxtran`).

### `[LONGITUDINAL]` — structural model + observation model

Either reference a library/custom model file…

```text
[LONGITUDINAL]
input = {a, b}                          # error model params (+ anything else needed)
file = 'lib:oral1_1cpt_kaVCl.txt'

DEFINITION:
CONC = {distribution=normal, prediction=Cc, errorModel=combined1(a, b)}
```

…or define the structural model inline (see "Structural model syntax" below).
When a library model is used, its internal PK parameters (e.g. `ka, V, Cl`)
are implicitly available and must match names defined in `[INDIVIDUAL]`.
Error-model parameters (`a, b, c`, or per-observation `a1, b1, a2, …`) MUST
be listed in the `input` of `[LONGITUDINAL]`.

**Observation (error) model**, inside `DEFINITION:` of `[LONGITUDINAL]`:

```text
y = {distribution=<dist>, prediction=<model output>, errorModel=<model>(params)}
```

- `distribution`: `normal`, `logNormal`, `logitNormal` (requires `min=`,
  `max=`). logNormal needs strictly positive observations; if data are
  already log-transformed, use `normal`.
- `errorModel`: `constant(a)` → sd=a; `proportional(b)` → sd=b·f;
  `combined1(a,b)` → sd=a+b·f^c; `combined2(a,b)` → sd=sqrt(a²+b²·f^(2c)).
  The exponent `c` exists and defaults FIXED at 1 (declare it FIXED in
  `<PARAMETER>` as seen in all demo projects). Arguments of `errorModel`
  must be parameters from the input list, not expressions.
- Custom sd: `y = {distribution=normal, prediction=E, sd=mySdVar}`.

### Library model naming

`lib:<admin>_<compartments>_<params>.txt`. Admin tokens seen in demos:
`bolus`, `infusion`, `oral1` (1st-order), `oral0` (zero-order),
`oral0_oral1_seqAbs`, `oral1_bolus`, `oral1_noFPE`. Examples verified on this
machine:

```text
lib:oral1_1cpt_kaVCl.txt
lib:oral1_1cpt_TlagkaVCl.txt
lib:oral1_1cpt_kaVk.txt
lib:oral0_1cpt_Tk0VCl.txt
lib:bolus_1cpt_Vk.txt
lib:infusion_2cpt_MM_VVmKmClQV2_outputL.txt
lib:oral1_1cpt_DirectEmaxWithBaseline_kaVkE0EmaxEC50.txt
lib:oral1_1cpt_IndirectModelInhibitionKin_TlagkaVClR0koutImaxIC50.txt
lib:oral1_noFPE_2cptP1cptM_uni_kaVkk12k21kmKpm.txt   # parent-metabolite
```

Libraries also cover PK/PD (direct effect, effect compartment, turnover),
TMDD, count, TGI models. When the output name isn't in the filename, open
the library model in the GUI editor or use `plotResult` to inspect.

## Structural model syntax (custom `.txt` file or inline)

A structural model file starts with `[LONGITUDINAL]` and contains blocks:

```text
DESCRIPTION:            # optional comments
[LONGITUDINAL]
input = {ka, V, Cl}     # mandatory: individual parameters (+ regressors)

PK:                     # optional: PK macros
EQUATION:               # optional: algebra + ODE/DDE
DEFINITION:             # optional: non-continuous observation models
OUTPUT:                 # mandatory
output = {Cc}           # outputs mapped to data observation types by order;
table = {Ac}            # optional extra variables exported to result tables
```

**Regressors** (time-varying covariates): list in `input`, mark each:

```text
input = {ka, V, Cl, E0}
E0 = {use=regressor}
```

Mapping to data regressor columns is by declaration order.

### `pkmodel` macro (PK: or EQUATION:)

One-line shortcut for standard PK models; only uses doses with adm=1.

```text
Cc = pkmodel(ka, V, Cl)                       # oral 1-cpt
{Cc, Ce} = pkmodel(ka, V, Cl, ke0)            # + effect compartment
```

Arguments (reserved names; mutually exclusive groups):

| Process | Arguments |
| --- | --- |
| Absorption | none → IV bolus (default); `Tk0` zero-order duration; `ka` first-order; `ka,Ktr,Mtt` transit compartments; optional `Tlag` (lag), `p` (bioavailability) |
| Volume | `V` (mandatory) |
| Elimination | `k` OR `Cl` OR `Vm,Km` (Michaelis–Menten) |
| Peripherals | `k12,k21` and/or `k13,k31` (or `k12=Q/V, k21=Q/V2`) |
| Effect | `ke0` → second output (effect compartment concentration) |

Rules: one administration type, one `pkmodel` per file, exact argument names,
cannot be combined with administration macros (`iv`, `oral`, …).

### Piecewise PK macros (PK:)

```text
PK:
compartment(cmt=1, amount=Ac, volume=V, concentration=Cc)   # define first!
absorption(adm=1, cmt=1, Tlag, ka, p=F)     # oral/adm = interchangeable; Tk0 for zero-order; Ktr,Mtt for transit
iv(adm=2, cmt=1)                            # bolus, or infusion if RATE/TINF column present
peripheral(k12, k21)                        # or peripheral(k12=Q/V, k21=Q/V2)
transfer(from=1, to=2, kt)                  # one-way transfer (no analytical solution)
effect(cmt=1, ke0, concentration=Ce)
elimination(cmt=1, Cl)                      # or k=, or Vm,Km; several eliminations per cmt allowed
depot(adm=1, target=Ad, ka)                 # links doses to an ODE variable
empty(adm=3, target=Ac)                     # zero a variable at adm times
reset(adm=2, target=all)                    # reset to initial value at adm times
```

Macro argument values must be input parameters or literals — no inline
calculations. Multi-route example (demo `ivOral2Macro_model.txt`):

```text
PK:
compartment(cmt=1, amount=Al)
compartment(cmt=2, amount=Ac)
peripheral(k23, k32)
oral(type=1, cmt=1, Tk0=Tk01, p=F1)
oral(type=2, cmt=2, ka=ka2, p=F2)
oral(type=3, cmt=2, ka=ka3, p=F3)
iv(type=4, cmt=2)
transfer(from=1, to=2, kt=kl)
elimination(cmt=2, k=Cl/V)
```

### `EQUATION:` — ODEs and algebra

```text
EQUATION:
t0 = 0                 # system start time
Ad_0 = 0               # initial conditions: <var>_0
Ac_0 = 0

ddt_Ad = -ka*Ad        # derivatives: ddt_<var>; first-order ODEs only
ddt_Ac = ka*Ad - (Cl/V)*Ac

Cc = Ac/V

if t <= 10             # conditionals: if / elseif / else / end
  kdeg = 1
else
  kdeg = 2
end
```

- `ddt_` lines cannot be placed inside if/else; compute conditional
  intermediate variables instead and use them in the derivative.
- DDE: `ddt_y = delay(x, tau) - y` — `delay()` must be called directly in a
  `ddt_` equation; delays are constant; prefer ODE reformulations for speed.
- PK macros and ODEs can be combined in one model.

### Non-continuous observation models (in the structural `DEFINITION:`)

Count/categorical/time-to-event models are defined in the model file
(continuous error models come from the GUI/project):

```text
DEFINITION:
Y = {type=count, P0=..., P1=..., P2=...}                  # probabilities per count
Y = {type=categorical, categories={...}, P1=..., P2=...}  # Pk for each category
h = {type=event, maxIterations=..., rightCensoring=...}   # hazard for TTE
```

## `<FIT>` — data ↔ model mapping

```text
<FIT>
data = 'CONC'         # observation column name or yname/DVID values
model = CONC          # model output (from DEFINITION: of [LONGITUDINAL])
```

Multiple observations — keep element order aligned:

```text
data = {'1', '2'}
model = {y1, y2}
```

Default mapping when omitted: first model output ↔ first observation type
(alphabetical).

## `<PARAMETER>`

```text
<PARAMETER>
V_pop = {value=7.7, method=MLE}      # estimate (default SAEM)
c = {value=1, method=FIXED}          # fixed
ka_pop = {value=2, method=MAP}       # Bayesian MAP; prior defined in [POPULATION]
```

Methods: `MLE`, `FIXED`, `MAP`. Every model input not fixed by construction
(population parameters, omegas, betas, error params) needs an entry here;
`c`/`c1`/`c2` (combined-model exponents) are conventionally present and
FIXED at 1.

## `<MONOLIX>`

```text
<MONOLIX>

[TASKS]
populationParameters()
individualParameters(method = {conditionalMean, conditionalMode})
fim(method = Linearization)            # or StochasticApproximation; run=false to skip
logLikelihood(method = ImportanceSampling)   # or Linearization; run=false to skip
plotResult(method = {indfits, obspred, vpc, residualsscatter, residualsdistribution, parameterdistribution, covariatemodeldiagnosis, covariancemodeldiagnosis, randomeffects, saemresults})

[SETTINGS]
GLOBAL:
exportpath = 'my_project'              # result folder next to the .mlxtran
```

Task notes: `fim` = Fisher information matrix → standard errors;
`logLikelihood` → -2LL, AIC, BIC. SAEM itself is configured via the GUI
defaults / `--config`; task methods above only affect post-estimation steps.

## Full worked example (hand-written project)

```text
<DATAFILE>

[FILEINFO]
file = 'data/pk_data.csv'
delimiter = comma
header = {ID, TIME, AMT, CONC, WT, SEX}

[CONTENT]
ID = {use=identifier}
TIME = {use=time}
AMT = {use=amount}
CONC = {use=observation, type=continuous}
WT = {use=covariate, type=continuous}
SEX = {use=covariate, type=categorical}

<MODEL>

[COVARIATE]
input = {WT, SEX}
SEX = {type=categorical, categories={'F', 'M'}}
EQUATION:
logtWT = log(WT/70)

[INDIVIDUAL]
input = {V_pop, omega_V, Cl_pop, omega_Cl, ka_pop, omega_ka, beta_V_logtWT}

DEFINITION:
V = {distribution=logNormal, typical=V_pop, covariate=logtWT, coefficient=beta_V_logtWT, sd=omega_V}
Cl = {distribution=logNormal, typical=Cl_pop, sd=omega_Cl}
ka = {distribution=logNormal, typical=ka_pop, sd=omega_ka}

[LONGITUDINAL]
input = {a, b}

PK:
Cc = pkmodel(ka, V, Cl)

DEFINITION:
CONC = {distribution=normal, prediction=Cc, errorModel=combined1(a, b)}

OUTPUT:
output = {Cc}

<FIT>
data = 'CONC'
model = CONC

<PARAMETER>
V_pop = {value=5, method=MLE}
Cl_pop = {value=0.5, method=MLE}
ka_pop = {value=1, method=MLE}
beta_V_logtWT = {value=0, method=MLE}
omega_V = {value=0.3, method=MLE}
omega_Cl = {value=0.3, method=MLE}
omega_ka = {value=0.5, method=MLE}
a = {value=1, method=MLE}
b = {value=0.3, method=MLE}
c = {value=1, method=FIXED}

<MONOLIX>

[TASKS]
populationParameters()
individualParameters(method = {conditionalMean, conditionalMode})
fim(method = Linearization)
logLikelihood(method = ImportanceSampling)
plotResult(method = {indfits, obspred, vpc, parameterdistribution, residualsscatter, randomeffects, saemresults})

[SETTINGS]
GLOBAL:
exportpath = 'my_project'
```

## Authoring gotchas (verified on this machine)

- `input = {}` lists are exhaustive: every parameter used in the section
  (including error-model `a,b,c`, betas, correlations, and covariates
  referenced in `[INDIVIDUAL]`) must appear there.
- `[LONGITUDINAL] input` of a `.mlxtran` project lists only the parameters
  NOT defined elsewhere (error params etc.); structural-model parameters come
  from `[INDIVIDUAL]`. In a standalone model `.txt` file, `input` lists the
  individual parameters themselves.
- Category order matters for `coefficient={0, beta_...}` vectors.
- `file = 'lib:...'` paths never need to exist on disk — they resolve inside
  the suite; custom model paths are relative to the project file.
- Observation names: single observation may reuse the data column name
  (`CONC`); multiple observations get `y1`, `y2` matching `yname`/DVID values.
- Run headless with the x86shim PATH prefix from SKILL.md; results land in
  `<exportpath>/` next to the project. Validate a new project quickly with
  `--mode complete` to watch SAEM output.

## Sources

- Model structure: /monolix/2024R1/introduction-model-structure-for-monolix
- Structural model setup: /monolix/2024R1/setting-the-structural-model
- Data format: /monolix/2024R1/data-format, /columns-used-to-define-observations,
  /columns-used-to-define-covariates
- pkmodel macro: /monolix/2024R1/pkmodel-macro; piecewise macros:
  /monolix/2024R1/piecewise-macros
- ODEs: /monolix/2024R1/ordinary-differential-equations-odes; DDEs:
  /monolix/2024R1/delay-differential-equations-ddes
- Error models: /monolix/2024R1/observation-error-model
- Distributions/covariates: /monolix/2024R1/distribution-of-individual-parameters-monolix,
  /monolix/2024R1/covariate-model, [INDIVIDUAL] (Simulx docs)
- MAP/priors: /monolix/2024R1/bayesian-estimation-or-fixed-population-parameters
- Local demos: `~/lixoft/monolix/monolix2024R1/demos/` (theophylline,
  warfarinPK/PD, parent_metabolite, iov1, theobayes2, ivOral2Macro models)
