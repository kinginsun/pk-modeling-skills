# PREDPP: ADVAN, TRANS, and `$MODEL`

Distilled from NONMEM 7.6 Users Guide VI (PREDPP) and VIII (record help).

PREDPP is NONMEM's PK library. Pick exactly one ADVAN (kinetic model) and one
TRANS (parameterization) on `$SUBROUTINES`:

```
$SUBROUTINES ADVAN2 TRANS2
```

## ADVAN catalog

| ADVAN | Model | Needs `$MODEL` | Needs `$DES` | TRANS choices |
|---|---|---|---|---|
| 1 | 1-compartment linear | no | no | 1, 2 |
| 2 | 1-compartment linear + first-order absorption | no | no | 1, 2 |
| 3 | 2-compartment linear | no | no | 1, 3, 4, 5, 6 |
| 4 | 2-compartment linear + first-order absorption | no | no | 1, 3, 4, 5, 6 |
| 5 | General linear | yes | no | 1 |
| 6 | General nonlinear (DVERK, nonstiff) | yes | yes | 1 |
| 7 | General linear, real eigenvalues (faster than 5) | yes | no | 1 |
| 8 | General nonlinear, stiff (DGEAR) | yes | yes | 1 |
| 9 | General nonlinear + equilibrium compartments (LSODI/DAE) | yes | yes (+`$AES`, `$AESINITIAL`) | 1 |
| 10 | 1-compartment Michaelis-Menten | no | only with SS doses (SS6; dummy DES ok otherwise) | 1 |
| 11 | 3-compartment linear | no | no | 1, 4 |
| 12 | 3-compartment linear + first-order absorption | no | no | 1, 4 |
| 13 | General nonlinear (LSODA; auto stiff/nonstiff) | yes | yes | 1 |
| 14 | General nonlinear (CVODES; root-finding) | yes | yes | 1 |
| 15 | General nonlinear + equilibrium (IDA) | yes | yes (+`$AES`, `$AESINITIAL`) | 1 |
| 16 | Delay differential equations (RADAR5) | yes | yes | 1 |
| 17 | DDE + equilibrium compartments (RADAR5) | yes | yes (+`$AES`, `$AESINITIAL`) | 1 |
| 18 | DDE (DDE_SOLVER) | yes | yes | 1 |

Solver notes:

- ADVAN6 for nonstiff, ADVAN8 for stiff, ADVAN13 for mixed; ADVAN14 is the
  modern LSODA/CVODES descendant. ADVAN9/15 also work for all-stiff systems
  without algebraic equations.
- TOL is required whenever `$DES` is required (ADVAN6, 8, 9, 13, 14, 15, 16,
  17, 18), with ADVAN10, and with steady-state routine SS6:
  `$SUBROUTINES ... TOL=n` (sets NRD), or `$TOL` record, or a TOL subroutine.
  Typical TOL values: 6-9; ADVAN9/13 may need NRD 7-8 or larger. ATOL
  (absolute tolerance) is available for ADVAN9, 13, 14, 15, 16, 17, 18
  (default 12, i.e. 1e-12; lowering to TOL can speed 3-4x).
- `MXSTEP` reserved variable limits integration steps (ADVAN13, 14, 16, 9,
  15, 17).
- ADVAN5/7 and ADVAN9/15/17 have no analytical second derivatives — Laplacian
  requires `NUMERICAL`.
- With ADVAN13/9: turn off compartments that should hold zero amount during a
  time period, else tiny amounts persist and cause problems.

## Compartment layouts (analytic ADVANs)

ADVAN1: (1) Central [on, dosable, default dose & obs], (2) Output [off].

ADVAN2: (1) Depot [off, dosable, default dose], (2) Central [on, default
obs], (3) Output.

ADVAN3: (1) Central [default dose & obs], (2) Peripheral, (3) Output.

ADVAN4: (1) Depot [default dose], (2) Central [default obs], (3) Peripheral,
(4) Output.

ADVAN10: (1) Central, (2) Output.

ADVAN11/12: central + two peripherals (+depot for 12); compartment numbering
follows the same convention (dose/observation defaults as ADVAN3/4).

## Basic PK parameters (with TRANS1)

| ADVAN | Parameters |
|---|---|
| 1 | `K` |
| 2 | `K`, `KA` |
| 3 | `K`, `K12`, `K21` |
| 4 | `K`, `K23`, `K32`, `KA` |
| 5, 7 | `Kij` (rate constant i->j; `Ki0` = Kim; use `T` separator when ambiguous, e.g. `K1T11`) |
| 6, 8, 9, 13-18 | `P(n)` explicitly; plus any `$PK` variable also used in `$DES`/`$AES` (implicit parameters) |
| 10 | `VM`, `KM` |
| 11 | `K`, `K12`, `K21`, `K13`, `K31` |
| 12 | `K`, `K23`, `K32`, `K24`, `K42`, `KA` |

ADVAN11/12: TRANS choices are 1, 4, 6; SS routines SS11/SS12 (or SS6) are
available; like ADVAN5/7, they lack analytical second derivatives (Laplacian
needs `NUMERICAL`). They can be greatly speeded up by limiting PK calls
(`CALLFL=1` in `$PK` plus the `CALL` data item for forced calls).

## TRANS reparameterizations

| TRANS | With | Modeled parameters -> internal |
|---|---|---|
| TRANS1 | any | none (default, dummy) |
| TRANS2 | ADVAN1, 2 | `CL`, `V` (, `KA`) -> K=CL/V |
| TRANS3 | ADVAN3, 4 | `CL`, `V`, `Q`, `VSS` (, `KA`) -> K=CL/V, K12=Q/V, K21=Q/(VSS-V) |
| TRANS4 | ADVAN3, 4, 11, 12 | `CL`, `V1`/`V2`, `Q`/`Q2`/`Q3`, `V2`/`V3`/`V4` (, `KA`) -> K=CL/V1, K12=Q/V1, K21=Q/V2, ... |
| TRANS5 | ADVAN3, 4 | `AOB` (A/B), `ALPHA`, `BETA` (, `KA`) -> macro constants |
| TRANS6 | ADVAN3, 4, 11, 12 | `ALPHA`, `BETA` (, `GAMMA`), `K21`/`K32` (, `K31`/`K42`, `KA`) -> micro constants (constraint: ALPHA<K21<BETA etc.) |

TRANS4 is the usual choice for multi-compartment models (CL/V parameter
space). Typical pop-PK starter: `ADVAN2 TRANS2` (oral 1-cmt) or
`ADVAN4 TRANS4` (oral 2-cmt); IV bolus 1-cmt: `ADVAN1 TRANS2`.

## Additional PK parameters (all ADVANs)

For each compartment n (n = 1..m including output):

- `Sn` scale (S0 = output scale; `SC` = central scale alias)
- `Fn` bioavailability of a dosed compartment
- `Rn` modeled infusion rate (use with RATE=-1)
- `Dn` modeled infusion duration (use with RATE=-2)
- `ALAGn` absorption/dose lag time

Others: `F0` output fraction; `XSCALE` time scale; `MTIME(i)` model event
times; `TSCALE` (time scale for TIME data item).

Set these in `$PK`, e.g.:

```
$PK
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
KA=THETA(3)*EXP(ETA(3))
S2=V
ALAG1=THETA(4)
```

## `$MODEL` record (required with general ADVANs >= 5, except 10-12)

```
$MODEL NCOMPARTMENTS=n1 [NEQUILIBRIUM=n2] [NPARAMETERS=n3]
       COMPARTMENT=([name] [attr ...]) ...
       [LINK compnamea TO compnameb BY k [l]] [I_SS=n]
```

- Compartments numbered in definition order. Default name `COMPn`.
- Attributes: `INITIALOFF`, `NOOFF`, `NODOSE`, `EQUILIBRIUM` (ADVAN9/15/17;
  implies NODOSE), `EXCLUDE` (from output-amount accounting), `DEFOBSERVATION`
  (default obs compartment; otherwise first named CENTRAL, else first),
  `DEFDOSE` (default dose compartment; otherwise first dosable named DEPOT,
  else first dosable).
- `INITIALOFF + NODOSE` defines an "output-type" compartment (behaves like
  the output compartment but needs a DADT equation).
- `LINK` clauses only with ADVAN5/7 without `$PK` (rare).
- `I_SS=n`: initial steady state for general nonlinear models (0 none; 1
  initial SS; 2 SS added to current amounts; 3 SS using current amounts as
  initial estimates).
- NM75: compartment names are automatically usable in abbreviated code, e.g.
  `DADT(GUT)=...`, `A(CENTRAL)/S2` (implicit label substitution).

Example:

```
$SUBROUTINES ADVAN6 TRANS1 TOL=6
$MODEL NCOMP=3
COMP=(DEPOT DEFDOSE INITIALOFF) COMP=(CENTRAL DEFOBS NOOFF) COMP=(PERI)
$PK
KA=P(1); KCP=P(2); KC0=P(3); KPC=P(4)
$DES
DADT(1)=-KA*A(1)
DADT(2)=KA*A(1)-(KCP+KC0)*A(2)+KPC*A(3)
DADT(3)=KCP*A(2)-KPC*A(3)
$ERROR
IPRED=A(2)/S2
Y=IPRED*(1+EPS(1))
```

## `$SUBROUTINES` record

```
$SUBROUTINES [ADVAN=]ADVANn [TRANS=]TRANSn [SS=n] [TOL=n] [ATOL=n]
             [PK=...] [ERROR=...] [MODEL=...] [DES=...] [AES=...]
             [TOLR=...] [INFN=...] [CONTR=...] [CCONTR=...] [MIX=...]
             [OTHER=file.f90 ...]
```

- Selects user-supplied or PREDPP library routines; `ADVAN=`/`TRANS=` prefixes
  optional. `SS=6` or `SS=9` selects the steady-state routine for SS doses
  with general nonlinear models.
- TOL/ATOL (and `SSTOL`/`SSATOL` variants for steady state) set solver
  tolerances; `TOLC`/`ATOLC`/`SSTOLC`/`SSATOLC` apply to the covariance step.

## Steady-state doses with general models

- SS doses (SS=1/2/3 data item) with ADVAN6/8/13/14/16/18 use SS routines
  (SS6/SS9). A `$DES` block is then required (may be a dummy without SS
  infusions).
- Endogenous drug / nonzero initial conditions: compartment initialization
  block in `$PK` (`A_0(n)=...`), SS dose with AMT=0 RATE=0, or `I_SS`.
  Equilibrium compartments are only evaluated after TIME advances beyond the
  initial value; use `CALL=10` to force evaluation.
