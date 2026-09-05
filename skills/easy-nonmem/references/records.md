# NM-TRAN Control Records Reference

Complete reference for NONMEM control stream records. Records covered in
other files are not repeated here:

- `$INPUT`, `$DATA`, and data items → [data-items.md](data-items.md)
- `$ESTIMATION`, `$COVARIANCE`, `$SIMULATION` → [estimation.md](estimation.md)
- `$SUBROUTINES`, `$MODEL`, ADVAN/TRANS → [predpp.md](predpp.md)
- `$PK`, `$DES`, `$ERROR`, `$PRED`, `$AES`, `$AESINITIAL`, `$INFN`,
  `$ABBREVIATED` → [model-code.md](model-code.md)
- `$TABLE`, `$SCATTERPLOT` → [output.md](output.md)

Record names may be abbreviated to a unique prefix (e.g. `$PROB`, `$EST`,
`$COV`).

## Problem structure

### `$PROBLEM` (required)

```
$PROBLEM [text]
```

Marks the start of a problem specification; the first control record of the
stream must be `$PROBLEM` (unless `$SIZES`/`$SUPER` precede it). The text
(≤72 characters) becomes the heading in the NONMEM printout.

### `$SUPER` (optional)

```
$SUPER SCOPE=n1 ITERATIONS=n2 [NOPRINT|PRINT]
```

Groups a sequence of `$PROBLEM`s into a superproblem, repeated `ITERATIONS`
times. `SCOPE` = number of problems in the superproblem (≥1);
`ITERATIONS` ≥2. `NOPRINT` (default) prints input only on the first
iteration. Nesting depth at most 2, and each `$SUPER` must contain at least
one `$PROBLEM`.

### `$SIZES` (optional)

```
$SIZES LIM1=30000 MAXFCN=2000000 NO=500
```

Overrides NONMEM/PREDPP array-size constants. Must precede the first
`$PROBLEM`/`$SUPER`. Any non-zero value overrides the default; a *negative*
value (NM73) grants NM-TRAN permission up to that maximum while still
tailoring the executable to the problem (recommended over positive values,
which force a large executable). Commonly sized constants and defaults:
`LTH=100` (max thetas), `LVR=30` (max etas+eps), `NO=250` (max observations
per individual), `PD=50` (max data items), `PDT=50` (max PRED-defined
labels), `PC=30`, `MAXFCN=1000000`, `LIM1=10000`, `LIM2=100000`,
`MAXOMEG=70`, `MAXITER=210`.

Example granting generous limits: `$SIZES PD=-1000 LVR=-150 LTH=-200`.

### `INCLUDE`

```
INCLUDE filename [n]
```

Reads control-stream records from another file (`n` = number of copies,
default 1). The file may contain any portion of a control stream. Include
records may not be nested. `$INCLUDE`, `$include`, `include` are also
recognized.

## Parameter records

### `$THETA`

```
$THETA value1 [value2] ...
```

Initial estimates and bounds for thetas, numbered in definition order. Four
value forms:

1. `init [FIXED]` — initial estimate, optionally fixed.
2. `([low,] init [,up] [FIXED])` — with bounds; commas optional.
   `-INF`/`INF` are default bounds (sent as ±1000000). With `FIXED`, a
   bound must equal the initial estimate.
3. `([low,] init [,up]) [FIXED]` — as above but `FIXED` outside the
   parentheses; bounds need not equal the initial estimate.
4. `(low,,up)` — no initial estimate; NONMEM runs an Initial Estimates Step
   to find one (`NUMBERPOINTS=n` controls the search; `ABORT`/`NOABORT`/
   `NOABORTFIRST` control behavior on PRED errors).

Replication: `(value)xn` repeats the parenthesized value n times.

`label=value [FIXED]` (NM75) assigns a symbolic subscript usable in
abbreviated code (e.g. `$THETA CL=(0.0,7.0)` then `TVCL=THETA(CL)`);
the label appears in the NONMEM report. `$THETA` records must precede any
record that uses the label. `NAMES(label1,...)` followed by values is a
compact labelled form. `UNINT` (NM75) marks a theta uninteresting for the
Optimal Design step.

### `$OMEGA` and `$SIGMA`

```
$OMEGA  [DIAGONAL(n) | BLOCK(n) | BLOCK(n) SAME(m)] [values]
        [FIXED] [VARIANCE|STANDARD] [COVARIANCE|CORRELATON] [CHOLESKY]
        [SCALE(s)]
$SIGMA  ... (same forms, for eps)
```

Initial estimates of the eta (OMEGA) and eps (SIGMA) variance-covariance
blocks. Multiple records define multiple blocks in order. Seven forms:

1. `$OMEGA [DIAGONAL(n)] v11 v22 ...` — diagonal block. Per-element options
   may follow each estimate.
2. `$OMEGA BLOCK(n) v11 v21 v22 ...` — full (non-diagonal) block; values in
   lower-triangular row order. Block-wide options may appear anywhere.
3. `$OMEGA BLOCK(n) SAME(m)` — block constrained equal to the preceding
   block; `(m)` repeats this m times. No values may be given.
4. `$OMEGA BLOCK(n) VALUES(diag,odiag)` — all diagonals = `diag`, all
   off-diagonals = `odiag`.
5. `label=value` (NM75) — symbolic label for the element, usable as
   `ETA(label)`/`EPS(label)` in abbreviated code.
6. `BLOCK(n) NAMES(l1,...,ln) VALUES(diag,odiag)` (NM75) — labelled block;
   `VALUES()` must follow `NAMES()`.
7. `SCALE(s)` (NM760) — multiplies all subsequent values in the record by s
   (useful for scaling prior matrices, e.g. by `(df-p-1)/df`).

Options:
- `FIXED` constrains the estimate (or whole block) to its initial value. A
  `FIXED` anywhere splits a diagonal specification into separate 1x1 blocks.
- `VARIANCE` (default) / `STANDARD` (`SD`) interpret diagonal values as
  variances / standard deviations.
- `COVARIANCE` (default) / `CORRELATON` interpret off-diagonals. These may
  be combined with VARIANCE/STANDARD.
- `CHOLESKY` specifies the block in Cholesky form.
- `UNINT` (NM75) marks an eta/eps uninteresting for the design step.

NONMEM converts everything to variance/covariance internally and reports
those. `(value,value...)xn` replicates values. Block initial estimates must
be positive definite (a diagonal shift is applied and reported if rounding
prevents it); zeros off the diagonal are preserved only for band-symmetric
structures. A diagonal estimate may be 0 only if fixed.

Example equivalences (same 2x2 block):

```
$OMEGA BLOCK(2)
0.64
-0.24 0.58
$OMEGA STANDARD BLOCK(2)
0.8
-0.24 0.762
$OMEGA STANDARD CORRELATION BLOCK(2)
0.8
-0.394 0.762
```

### `$THETAI` and `$THETAR` (theta transformations)

```
$THETAI
THETA(1:NTHETA)=LOG(THETAI(1:NTHETA))   ; transform initial thetas
```

`$THETAI` (`$THI`) transforms initial `$THETA`/`$THETAP` values before the
estimation search (e.g. to estimate in log space while entering natural
values). `$THETAR` (`$THR`) transforms final values for the NONMEM report
and additional output files (`.cov`, `.coi`, `.cor`), typically the inverse
transformation. Statements are Fortran 95 array assignments, copied to
`THETAISUB`/`THETARSUB`. Available variables: `THETAI`, `THETAPI`, `THETA`,
`THETAP` (input), `THETA`, `THETAP`/`THETAR`, `THETAPR` (output), `NTHETA`,
`NTHP`, `NPROB`/`IPROB`. Bounds are transformed together with the initial
estimate. The transformation runs before estimation; the Initial Estimates
Step (if any) runs before `$THETAI`.

### `$ANNEAL`

```
$ANNEAL 1-3,5:0.3 6,7:1.0
```

Sets starting diagonal OMEGA values for simulated annealing by subroutine
CONSTRAINT when `$ESTIMATION CONSTRAIN>=4`. Number-lists may be single
integers, ranges, or comma-separated groups; default value 0 (which becomes
0.3). Used especially with SAEM to anneal thetas that have zero omega; more
suitable than gradient methods for problems far from the solution.

## Prior information

### `$PRIOR`

```
$PRIOR subroutine [(conditional clause1), (clause2) ...]
      [DISPLAY[=ALL|CNT]] [ICMAX=n] [arguments...]
```

Enables prior distributions. `subroutine` is `TNPRI` (classical methods,
uses MSF file) or `NWPRI` (required for NONMEM 7 EM/Bayesian methods).
Conditional clauses (`AND`ed within, `OR`ed between) may use
`ESTIMATION`/`SIMULATION` (or `ICALL=n`) and `PROBLEM=n` with tests
`.EQ. .NE. .LT. .LE. .GT. .GE.`. Arguments (must be coded exactly; omitted
arguments default to 0): `ITYP, NSAM, ISS, PLEV, CNT` (both);
`NTHETA, NETA, NEPS, NTHP, NETP, NEPP, NPEXP` (NWPRI); `IFND, MODE, IVAR`
(TNPRI). `DISPLAY=ALL|CNT` prints checking information. At most 10 `$PRIOR`
records per problem; when a subroutine is listed more than once, all
specifications must be conditional and arguments reset each time.

### Informative prior records (NWPRI)

These "informative" forms describe prior information by name; when used,
`$PRIOR NWPRI` options need not be specified (but explicit options take
precedence). They may be located anywhere; NM-TRAN orders them correctly.
`FIXED` should be used; `BLOCK` and `VALUES` are appropriate.

- `$THETAP` — prior values for thetas; `$THETAPV` — prior variance matrix
  for thetas.
- `$OMEGAP` — prior OMEGA blocks; `$OMEGAPD` — prior degrees of freedom
  (dispersion), one per OMEGA block.
- `$SIGMAP` — prior SIGMA elements; `$SIGMAPD` — prior degrees of freedom
  per SIGMA block.

Example:

```
$PRIOR NWPRI
$THETAP (2.0 FIX) (2.0 FIX)
$THETAPV BLOCK(2) 10000 FIX 0.0 10000
$OMEGAP BLOCK(2) 0.2 FIX 0.0 0.2
$OMEGAPD (4 FIX)
$SIGMAP 0.05 FIX
$SIGMAPD (1 FIX)
```

### Prior/NUTS shape records (NM75)

These per-element/per-block records support t-distributed theta priors and
LKJ correlation priors; `$EST`/`$SIM` options of the same name override
them. `(value)xn` replication is allowed; default value is 0.

- `$TTDF value...` — t-distribution degrees of freedom for each theta
  (used with METHOD=NUTS and `$SIMULATION TRUE=PRIOR`; real values allowed
  for estimation, truncated integer for simulation).
- `$OLKJDF value...` — LKJ decorrelation degrees of freedom for each OMEGA
  block. A negative value `-n` uses n degrees of freedom with a
  user-defined standard-deviation prior (`OMEGA_STD_PRIORU.f90`, supplied
  via `$SUBROUTINES OTHER=`).
- `$SLKJDF value...` — same for SIGMA blocks (`SIGMA_STD_PRIORU.f90`).
- `$OVARF value...` — weighting (inverse variance) for OMEGA standard
  deviations (NUTS).
- `$SVARF value...` — same for SIGMA.

## Initial values and resumption

### `$MSFI`

```
$MSFI filename [NORESCALE|RESCALE] [NPOPETAS[=n]] [ONLYREAD]
      [NOMSFTEST|MSFTEST] [VERSION=n] [NEW]
```

Reads a Model Specification File (MSF) from a previous run to continue or
repeat the estimation. When `$MSFI` is used, `$THETA`/`$OMEGA`/`$SIGMA`
records should not appear in that problem.

- `NORESCALE` (default) continues the search as the previous run would;
  `RESCALE` restarts the search from the previous final estimates (only if
  the previous search terminated successfully with identical `$ESTIMATION`
  options except MAXEVAL).
- `NPOPETAS[=n]` declares population data with n population etas; required
  in some cases (see help).
- `ONLYREAD` reads the MSF only to convey prior information (TNPRI); no
  task records may follow.
- `VERSION=n` reads MSF files from older NONMEM versions (7.4.4 down to
  6.1). `MSFTEST` (default) / `NOMSFTEST` control strict error checking.
- `NEW` allows resuming from the MSF final parameters even when the
  originating run completed (FO/FOCE/Laplace).

With `MSFO=` on `$ESTIMATION`, extra files `*_ETAS.msf`, `*_RMAT.msf`,
`*_SMAT.msf` are produced to support `$MSFI`/`$COV ... RESUME` later.

### `$CHAIN`

```
$CHAIN FILE=filename [FORMAT=s] [ORDER=xxxf] [ISAMPLE=n] [NSAMPLE=n]
       [SEED=n] [CLOCKSEED] [SELECT=n] [RANMETHOD=...] [CTYPE=...]
       [DF=n] [DFS=n] [IACCEPT=x] [TBLN=n]
```

Loads initial thetas/omegas/sigmas (and, unlike `$EST METHOD=CHAIN`, also
the parameters used by the Simulation step) for the entire problem from an
output file of a previous run (e.g. a `.ext` file). Options have the same
meanings as for `$ESTIMATION`; seeds/methods set here do not propagate to
`$EST` records.

### `$ETAS` and `$PHIS`

```
$ETAS value1 value2 ...                       ; same initial etas for all subjects
$ETAS FILE=myprevious.phi FORMAT=... TBLN=n [ITERATION=n]
$PHIS ...                                     ; phi values: eta(i)=phi(i)-mu(i)
```

Sets non-zero initial eta (or phi) values. With `FILE=`, values are loaded
per subject from a `.phi`/`.phm`/`.iph` file, matching by ID when an ID
column exists; `TBLN` selects the table, `ITERATION` the `.iph` iteration.
Usage by method: ignored for FO; used for FOCE only when `MCETA>0`; used as
starting etas for BAYES/SAEM/IMP `MAPITER=0`; tested among initial eta
positions (best OBJ selected) for ITS/IMP `MAPITER>0`/IMPMAP with
`MCETA>0`; with `FNLETA=2` the loaded etas are treated as final.

### `$RCOV` and `$RCOVI`

```
$RCOV  FILE=filename [FORMAT|DELIM=s1] [TBLN=n]
$RCOVI FILE=filename [FORMAT|DELIM=s1] [TBLN=n]
```

Loads the variance-covariance of estimates (`.cov`) or its inverse (`.coi`)
from a previous problem so `$TABLE` can compute total standard errors
without re-running `$COVARIANCE`. `FILE` is required; `FORMAT` should match
the one used when the file was written. Can be combined with `$CHAIN`.

## Data-related records

### `$BIND`

```
$BIND [value1] [value2] ...
```

Overrides the default data-item values seen by `$PK`/`$DES`/`$AES` when PK
is called at additional or lagged dose times (`CALLFL=-2`). Positions map
1-to-1 onto `$INPUT`. Each value: `DOSE` (from the dose record), `NEXT`
(next event record), `LAST` (last event record ≤ dose time), `SKIP`/`DROP`
(ignore), `-` (default). Defaults: `TIME` → NEXT; NONMEM/PREDPP items
(DV MDV ID L2 MRG_ RAW_ REPL_ EVID AMT RATE SS II CMT PCMT CALL CONT ADDL
DATE DAT1-3) → DOSE; user items → NEXT. Only applies when a dose is
additional/lagged, PK parameters depend on time-varying data, and
`CALLFL=-2` is set.

### `$CONTR`

```
$CONTR DATA=([label1|0] [label2|0] [label3|0])
```

Makes up to three `$INPUT` data items available to user-supplied routines
(MIX, CONTR, CCONTR) through the `DATA` array (in module `ROCM_REAL`),
where `DATA(I,J)` is item J on observation record I. `0` is a placeholder.

### `$INDEX`

```
$INDEX [label1|value1] [label2|value2] ...
```

Stores data-item indices (positions in the data record) into the `INDXS`
array for user-supplied FORTRAN routines. Rarely needed. May also be coded
`$INDXS`/`$INDEXES`.

### `$OMIT`

```
$OMIT item1 item2 ...
```

Excludes the named `$INPUT` data items from template matching when raw-data
averages are computed. Rarely needed.

## Nested random levels

### `$LEVEL`

```
$LEVEL item=(n1[m1], n2[m2], ...)
```

Declares "super ID" data items defining random nesting levels above subject
ID (e.g. site, country). Each listed item is a super ID from `$INPUT`;
`nk[mk]` associates ETA(nk) with the level, with ETA(mk) nested within it.
Order of items on `$LEVEL` defines nesting depth; NM74 shorthand
`start TO end BY interval` (`:` may replace `TO`).

Example (country > site > subject):

```
$LEVEL
SID=(5[1],6[2])
CID=(9[5],10[6])
```

With FOCE, the `SLOW` option is required on `$ESTIMATION` and
`MATRIX=R` on `$COVARIANCE`. See also `LEVWT` on `$ESTIMATION`. If several
problems are present, restate `$LEVEL` in each relevant problem.

## Special code blocks and steps

### `$MIX`

```
$MIX
NSPOP=2
P(1)=THETA(5)
P(2)=1-THETA(5)
```

Defines mixture-model subpopulation probabilities. Left-hand: `NSPOP`
(number of subpopulations; must be set when `ICALL=1`) and `P(i)`/`MIXP(i)`
(fractions summing to 1). Right-hand: `THETA(n)`, `ICALL`, MIX-defined
items, and data items declared via `$CONTR DATA=`. May not contain
`EXIT`/`CALL`/`DO WHILE`, COMRES/CALLFL; forbidden names include
`NEWIND`, `ETA(i)`, `EPS(i)`, `ERR(i)`, `COM(i)`. MIX variables are not
available in `$TABLE`/`$SCATTERPLOT`. Follows `$SUBROUTINES`.

### `$TOL`

```
$TOL
NRD(1)=6
ANRD(1)=12
```

Specifies compartment-specific solver tolerances for general nonlinear
ADVANs (6, 8, 9, 13–18) and SS6/SS9. Equivalent to `$SUBROUTINES TOL=n`.
Left-hand quantities: `NRD(i)` (relative tolerance digits; `NRD(0)` for
steady state, NM74), `ANRD(i)` (absolute tolerance, default 12),
`NRDC(i)`/`ANRDC(i)` (FOCE/Laplace covariance step variants). Only
ADVAN 9, 13, 14, 15, 16, 17, 18 use per-compartment values; others use
`NRD(1)` only. Right-hand: integers only. Follows `$SUBROUTINES`/`$MODEL`.

### `$NONPARAMETRIC`

```
$NONPARAMETRIC [MARGINALS|ETAS] [MSFO=filename] [RECOMPUTE] [EXPAND]
               [NPSUPP=n | NPSUPPE=n] [BOOTSTRAP [STRAT=label] [STRATF=label]]
               [PARAFILE=...] [NPESTIM=[0|1]] [NPMAXITER=n]
               [UNCONDITIONAL|CONDITIONAL] [OMITTED]
```

Requests the Nonparametric Step; requires `$ESTIMATION METHOD=1` or
`POSTHOC`. `MARGINALS` (default) obtains marginal cumulatives; `ETAS`
obtains conditional nonparametric eta estimates (CNPE). Support points are
the posthoc eta estimates across individuals. `EXPAND` evaluates support
points using initial OMEGAs; `NPSUPP`/`NPSUPPE` fix the number of support
points (extra points simulated from final/initial omegas). `BOOTSTRAP`
re-samples subjects (with `STRAT`/`STRATF` stratification). `NPESTIM=1`
selects non-negative least squares instead of EM. `CONDITIONAL` (default)
runs only if estimation succeeded or had `MAXEVAL=0`.

### `$DESIGN` / `$OPTDES` (NM75)

Requests clinical-trial design evaluation or optimal design (modeled after
POPED/PFIM). Key options: `APPROX=FO|FOI|FOCE|LAPLACE|LAPLACEI`,
`OFVTYPE=n`, `FIMTYPE=n`, `FIMDIAG=n`, `GROUPSIZE=n`, `MODE=0|1|2|3`,
plus algorithm selectors (`NELDER`, `FEDOROV`, `RS`, `STGR`, `DISCRETE`,
...) and design-selection labels (`DESEL`, `STRAT`, `NMIN`, `NMAX`, ...).
Consult the NONMEM 7.5 design documentation for details.

## Miscellaneous records

### `$FORMAT`

```
$FORMAT FMTN=n
```

Sets significant digits (3–23; default 3) for thetas/omegas/sigmas and
variance-covariance in the report file and `$TABLE` report output. Negative
values select G-field format. Place right after `$PROBLEM`; applies to all
subsequent problems until another `$FORMAT`.

### `$WARNINGS`

```
$WARNINGS [NONE] [n] [RESET|NORESET]
          [WARNINGMAXIMUM=[NONE|n|(list)]]
          [DATAMAXIMUM=[NONE|n|(list)]]
          [ERRORMAXIMUM=n]
```

Controls display of NM-TRAN warning/data-warning/data-error messages for
the current and subsequent problems. `NONE` suppresses warnings; `n` sets
all three maximums. Defaults: 20 per message type. Data errors can never be
fully suppressed (`ERRORMAXIMUM=0` or `1` terminates after the first).
Abbreviations allowed: `WMAX`, `DMAX`, `EMAX`. `$WARNING LIST` prints all
possible warnings. A bare `$WARNING` restores defaults.

### `$DEFAULT`

```
$DEFAULT NOSUB=[-1|0|1]
```

Sets label-substitution default: `NOSUB=0` (default) performs symbolic label
substitution for all tasks; `NOSUB=1` disables it; `-1` reverts to NONMEM
default. Options on `$TABLE`/`$SCATTER`/`$EST` override for that task.

### `$LDFOLD` (NM751)

```
$LDFOLD
```

Reverts to pre-7.5.1 handling of loss of degrees of freedom (LDF); affects
only ITS/IMP/SAEM/BAYES. Insert after the first `$PROBLEM`.

## Record order summary

```
$SIZES                          (first, if present)
$SUPER                          (optional)
$PROBLEM
$DATA                           (often before $INPUT is fine; see data-items.md)
$INPUT
$SUBROUTINES / $MODEL
$PK / $DES / $ERROR / $PRED / $AES / $TOL / $MIX
$BIND / $CONTR / $INDEX / $OMIT / $LEVEL
$THETA / $OMEGA / $SIGMA        (before any use of symbolic labels)
$TTDF / $OLKJDF / $SLKJDF / $OVARF / $SVARF
$THETAP / $THETAPV / $OMEGAP / $OMEGAPD / $SIGMAP / $SIGMAPD / $PRIOR
$THETAI / $THETAR / $ANNEAL
$MSFI / $CHAIN / $ETAS / $PHIS / $RCOV / $RCOVI
$ESTIMATION
$COVARIANCE
$NONPARAMETRIC
$SIMULATION
$TABLE / $SCATTERPLOT
```
