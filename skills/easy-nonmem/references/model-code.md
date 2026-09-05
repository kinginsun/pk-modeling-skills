# Model Code: `$PK`, `$DES`, `$ERROR`, `$PRED`, and Abbreviated Code

Distilled from NONMEM 7.6 Users Guides IV and VIII (abbreviated-code and
reserved-variable reference).

Abbreviated code is FORTRAN-like model code. Blocks are started by `$PRED`,
`$PK`, `$ERROR`, `$DES`, `$AES`, `$AESINITIAL`, `$TOL`, `$MIX`, `$INFN` and
end at the next `$` record.

## Language rules

- One statement per line, starting anywhere; `;` starts a comment; `&`
  continues a line; lower or upper case; no statement numbers.
- Allowed statements: assignment; `IF (cond) ...`,
  `IF ... THEN / ELSEIF ... THEN / ELSE / ENDIF`; `DO WHILE(cond)` ... `ENDDO`;
  `CALL ...`; `WRITE`, `PRINT`; `RETURN`; `OPEN`, `CLOSE`, `REWIND`; `EXIT`.
  No GOTO, READ, FORMAT.
- Assignment right-hand side may use: previously defined quantities;
  constants (e.g. `1.1`, `3E-1`, `3D+1`, up to 30 chars); `THETA(n)`,
  `OMEGA(i,j)` (`OMEGA(i)` for diagonal), `SIGMA`; `$INPUT` labels;
  `ETA(n)`, `EPS(n)`/`ERR(n)` (mean 0, variances per OMEGA/SIGMA);
  operators `+ - * / **`; parentheses.
- Built-in functions: `LOG` (natural), `LOG10`, `EXP`, `SQRT`, `SIN`, `COS`,
  `TAN`, `ASIN`, `ACOS`, `ATAN`, `ABS`, `INT`, `MIN`, `MAX`, `MOD`; NONMEM
  functions `PHI` (no derivatives), `GAMLN`. Derivatives w.r.t. eta/eps are
  computed automatically for these (except INT/MOD/MIN/MAX, which are
  discontinuous — avoid them where they affect the objective function; use
  MTIME flags in `$PK` + tests in `$DES` instead).
- Everything is double precision (`K=.5` means 0.5, not 0).
- User-defined variable names: 1-20 chars (letters/digits/`_`, starting with
  a letter). `MU_1`, `MU_2`, ... are reserved for MU referencing.
- `$INPUT` labels may not be assigned to (except in simulation,
  initialization, finalization blocks).
- Random variables: anything defined (directly or indirectly) from ETA/EPS.
  Within one THEN/ELSE clause you may not define the same random variable
  twice; no random variables inside nested conditionals; if all conditions of
  a series defining a random variable are false, it is set to 0 (non-random
  variables keep their previous value — use `X=X` in ELSE for recursion).
- `EXIT n [k]`: immediate exit with PRED error return code n (1 or 2) and
  optional user code k (0-999; 1000-9999 allowed in Simulation Step, NM75+).
  n=1 allows theta/eta recovery during estimation (see NOABORT); n=2 aborts.
  Use EXIT to guard against bad parameter values (e.g. `IF (V.LE.0) EXIT 1 1`).
- `COM(k)`: the kth position of the NMPRD4 reserve storage; COM variables
  are not treated as random (no derivatives).
- Vectors/functions: `VECTRA..Z` / `FUNCA..Z` (extended `FUNCxy`, `FUNCxyz`)
  for user-supplied functions (`$SUBROUTINES OTHER=file`); declare custom
  names via `$ABBR FUNCTION name(vector,dim[,usage])` and `$ABBR VECTOR`.

## `$PK` — pharmacokinetic parameters (with PREDPP)

Left-hand quantities:

- Basic PK parameters required (except general nonlinear ADVANs 6/8/9/13-18,
  where `P(n)` is explicit and any `$PK` variable used in `$DES`/`$AES` is an
  implicit parameter): `K`, `CL`, `V`, `KA`, `K12`, `K21`, `K23`, `K32`,
  `Q`, `VSS`, `V1..V4`, `ALPHA`, `BETA`, `GAMMA`, `AOB`, `Kij`, `VM`, `KM` —
  per the ADVAN/TRANS in use.
- Additional PK parameters (optional): `Sn` scales (`SC`, `S0`), `Fn`
  bioavailability, `F0`/`FO` output fraction, `Rn` rates, `Dn` durations,
  `ALAGn` lags, `TSCALE`/`XSCALE`, `MTIME(i)` model event times.
- `A_0(n)` initial compartment amounts (compartment initialization block).
- `I_SS` initial steady-state flag.
- PK-defined (PRED-defined) items.

Right-hand quantities: `$INPUT` labels, `THETA(n)`, `ETA(n)` (population
data), PK-defined items, plus:

- `NEWIND`: 0 = first record of data set (THETA may differ from last call);
  1 = first record of an individual record; 2 = subsequent record.
- `ICALL`: 1 initialization, 2 normal, 3 finalization, 4 simulation,
  5 expectation, 6 raw data averages. Special blocks run when ICALL != 2.
- Module variables: `DOSTIM` (time of a lagged/additional dose being
  processed; 0 otherwise), `DOSREC(n)` (copy of the initiating dose record),
  `A(n)` (latest compartment amounts), `TSTATE` (time of those amounts),
  `A_0FLG`.

Forbidden names in `$PK`: `IDEF IREV EVTREC NVNT INDXS IRGG GG NETAS DADT(n)
E(n) EPS(n)`.

Pseudo-statements (at the start of the block):

- `COMRES=-1` — keep block variables local (not in NMPRD4).
- `CALLFL=-2` call at every event record and additional/lagged dose times
  (default when DOSREC/DOSTIM/MTIME used explicitly); `-1` every event record
  (default otherwise); `0` first event record and new TIME values; `1` once
  per individual record. Phrases may be used instead: `$PK (ONCE PER IR)`,
  `(NEW TIME)`, `(EVERY EVENT)`, `(NONEVENT)`.

Record order: after `$SUBROUTINES` and `$INPUT`, after `$MODEL` (general
models); before `$ERROR`.

## `$DES` — differential equations (ADVAN6/8/9/13/14/15/16/17/18)

Left-hand: `DADT(n)` (required; derivative of compartment n amount) and
DES-defined items. PREDPP adds active infusion rates itself; endogenous drug
can be added as explicit terms (not counted into the output compartment).

Right-hand: `A(n)`, `P(n)`, PK-defined items, `T` (time, continuous over the
integration interval; may exceed the interval end), DES-defined items,
`$INPUT` labels (values of the record being advanced to), `THETA(n)`.
Continuous FORTRAN functions allowed (SIN, COS, ...); INT/MOD/ABS and other
discontinuous functions must be avoided (use MTIME flags).

Module variables of interest: `DOSTIM`, `DOSREC`, `ISFINL` (1 on the final
DES call at a time during simulation/copying), `DES_DER`, `MITER`, `METH`.

Forbidden names: `IR DA DP E(n) ETA(n) EPS(n) ERR(n)` — ETA/EPS may not
appear in `$DES`; introduce randomness via `$PK` parameters instead.

Pseudo-statement: `COMRES=-1`. Order: after `$SUBROUTINES $INPUT $MODEL $PK`.

Note: DES-defined items are computed only when event time increases;
displayed values at the first event of a subject come from the prior
individual's last advance (NM-TRAN WARNING 48).

## `$ERROR` — intra-individual error (with PREDPP)

Left-hand: `Y` (required; modeled value of the dependent variable) and
ERROR-defined items; also `$PK` left-hand quantities if they are non-random
and neither block uses `COMRES=-1`.

Right-hand: `F` (required; scaled drug amount in the observation
compartment), `$INPUT` labels, `THETA(n)`, `ETA(n)` (required for
single-subject data; optional for population), `EPS(n)` (required for
population data; `ERR(n)` may code either), ERROR-defined items, `$PK`
quantities, `NEWIND`, `NEWL2` (1 = first record of an L2 record), `ICALL`,
and `A(n)`.

Common error models:

```
Y=F+F*EPS(1)                 ; proportional
Y=F+THETA(ERR)*EPS(1)        ; additive (with estimated SD)
Y=F*(1+EPS(1))               ; proportional, CV form
Y=F+F*EPS(1)+EPS(2)          ; combined
IPRED=F
Y=IPRED*(1+EPS(1))
```

Forbidden names: `IDEF IREV EVTREC NVNT INDXS G HH DADT(n) E(n) P(n)`.

Pseudo-statements: `COMRES=-1`; `CALLFL=-1` every event record (default),
`0` only observation records, `1` once per individual record, `2` once per
problem (implicit for simple one-line additive/proportional models only).
Phrases: `$ERROR (ONCE PER IR)`, `(ONLY OBSERVATIONS)`, `(EVERY EVENT)`.

Order: after `$SUBROUTINES`/`$INPUT`, after `$MODEL`, after `$PK`.

## `$PRED` — full model without PREDPP

Used instead of `$PK`+`$ERROR` when PREDPP is not selected (no `$SUBROUTINES`
ADVAN). Left-hand: `Y` (required). Right-hand: `$INPUT` labels, `THETA(n)`,
`ETA(n)`, `EPS(n)`/`ERR(n)`, `NEWIND`, `NEWL2`, `ICALL`, PRED-defined items.
Single-subject data need no ID. Recursion across records is allowed
(see examples in the abbreviated-code rules).

## `$AES` / `$AESINITIAL` — algebraic (equilibrium) expressions

With ADVAN9/15/17. `$AES` defines algebraic equations `E(ncm1+i)=...` for
equilibrium compartments (right-hand: `A(n)`, `P(n)`, `T`, `THETA(n)`,
`DOSTIM`, `DOSREC`, `ISFINL`). `$AESINITIAL` computes initial equilibrium
amounts `A(ncm1+i)` at the start of an integration interval (`INIT`
left-hand; `CALLFL` options control calling).

## `$INFN` — initialization/finalization code

Abbreviated code executed at ICALL=1 (initialization) and ICALL=3
(finalization); with PREDPP, mainly for setting up arrays or reading files.
Supports `CALL PASS(MODE)`, `CALL SUPP(ie,ic)`, `DO WHILE(DATA)`.

## `$ABBREVIATED` record options

```
$ABBREVIATED [COMRES=n1] [COMSAV=n2] [DERIV1=NO] [DERIV2=NO|NOCOMMON]
             [FASTDER|NOFASTDER] [CHECKMU|NOCHECKMU]
             [DES=COMPACT|DES=FULL]
             [REPLACE left=right]... [DECLARE ...] [PROTECT]
             [FUNCTION name(vec,dim[,usage])] [VECTOR name(dim)]
```

- `COMRES=n1`: reserve first n1 NMPRD4 positions (`-1` stores nothing; 0
  default). `COMSAV=n2`: SAVE-region size for copying passes (`-1` = none).
- `DERIV2=NO`: skip second derivatives (no Laplacian); `DERIV2=NOCOMMON`:
  compute but don't store (no display in tables; no `$PK`->`$ERROR` variable
  passing). `DERIV1=NO`: skip first derivatives (NM74; SAEM/BAYES only).
- `DES=COMPACT` (default; required for Laplacian) / `DES=FULL` (default for
  ADVAN9/15/17; with Laplacian also needs `NUMERICAL`).
- `PROTECT` (NM74): auto-replace math functions with protected versions
  (PLOG, PEXP, ...) guarding domain errors and divide-by-zero.
- `DECLARE [INTEGER] [DOWHILE] name[(dim...)] ...`: global declared variables
  (auto-initialized to 0); DOWHILE loop indices must be declared DOWHILE.
  Array elements can appear in WRITE/PRINT but not `$TABLE` (copy to scalars).
- `REPLACE` forms:
  1. Simple: `$ABBR REPLACE THETA(CL)=THETA(4)` — symbolic parameter names;
     NM74+ also substitutes labels in the report/table files.
  2. Data-item selection: `$ABBR REPLACE THETA(OCC)=THETA(4,7)` — picks
     THETA(4) when OCC==1, THETA(7) when OCC==2 (VAR must be THETA/ETA/EPS).
  3. Data-item + parameter: `$ABBR REPLACE THETA(SID_KA)=THETA(4,6)`.
  4. Multiple: `$ABBR REPLACE THETA(CL,V1,Q,V2)=THETA(1,2,3,4)` (NM74).
  Shorthand lists: `THETA(,4 TO 13 BY 3)` or `THETA(10:4)` (NM74, `:` and
  negative BY allowed). Produces FORIG/FREPL files for debugging.
  Explicit compartment substitution: `$ABBR REPLACE A(DEPOT)=A(1)`; NM75
  `$MODEL` names give implicit substitution.
- Label substitution can be disabled globally (`$DEFAULT NOSUB=1`) or per
  task (`$TABLE/$SCAT/$ESTIMATION NOSUB=1`). Never applied to `.ext`, `.phi`,
  etc.

## Special CALL statements

- `CALL PASS(MODE)` — initialization/finalization blocks and `$INFN` only.
- `CALL SUPP(ie,ic)` — suppress estimation/covariance output (1/0).
- `CALL RANDOM(n,R)` — random number from source n (1-10); simulation and
  expectation blocks only.
- `CALL SIMETA(ETA)` / `CALL SIMEPS(EPS)` — obtain new simulated eta/eps
  (e.g. truncation via `DO WHILE (ETA(1).GT.5) CALL SIMETA(ETA) ENDDO`);
  simulation blocks only.

## Useful reserved module variables

Accessible in abbreviated code via `include nonmem_reserved_general` (copy
the file from the NONMEM util directory to the run directory). Selected:

| Variable | Meaning |
|---|---|
| `NTHETA` | Number of thetas. |
| `NPROB`, `IPROB` | Number of problems / current problem number. |
| `NIND` | Total number of individuals. |
| `NINDREC` | Current individual record number. |
| `NDATINDR` | Data record number within the individual record. |
| `NOBSIND` | Number of observation records in the individual record. |
| `NINDOBS` | Number of individual records containing observations. |
| `ITERATION`, `ITER_REPORT` | Current EM/Bayes iteration (reported value can be negative during burn-in). |
| `OBJI` | Individual objective function value, `OBJI(NIREC,1)`. |
| `SAEM_MODE` | 0 BAYES, 1 stochastic period, 2 accumulation period. |
| `ITS_MODE` / `IMP_MODE` | MAP/importance-sampling mode indicators. |
| `PI`, `ISEED`, `IRANM` | Constants and RNG state. |
| `IKEY_TERM` | 5 = end run (ctrl-E / stop.sig), 11 = end mode (next.sig). |
| `MUFIRSTREC`, `OBJQUICK` | Speed options for MU-referenced models (NM74). |
| `ETABAR` etc. | Diagnostic statistics (see etabar output). |

Changing reserved variables can crash NONMEM — read before writing.

## Record order summary

```
$PROBLEM
$INPUT / $DATA
$SUBROUTINES
$MODEL          (general ADVANs)
$PK             (PREDPP)
$DES            (general nonlinear ADVANs)
$AES, $AESINITIAL (ADVAN9/15/17)
$ERROR          (PREDPP)   -- or $PRED (no PREDPP)
$THETA $OMEGA $SIGMA
$ESTIMATION $COVARIANCE $SIMULATION
$TABLE $SCATTERPLOT
```
