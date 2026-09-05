# Output: `$TABLE` and `$SCATTERPLOT`

Distilled from NONMEM 7.6 Users Guide VIII (`$TABLE`/`$SCATTERPLOT`/format
reference).

## `$TABLE`

Optional; up to 10 `$TABLE` records per problem. Generates a table of
diagnostics and user items.

```
$TABLE [list1] [BY list2]
       [PRINT|NOPRINT] [FILE=filename]
       [NOHEADER|ONEHEADER] [ONEHEADERALL]
       [NOTITLE|NOLABEL]
       [FIRSTONLY|LASTONLY|FIRSTLASTONLY]
       [NOFORWARD|FORWARD] [APPEND|NOAPPEND]
       [FORMAT=s] [LFORMAT=s] [RFORMAT=s] [IDFORMAT=s]
       [NOSUB=[0|1]] [EXCLUDE_BY list3]
       [PARAFILE=[filename|ON|OFF]]
       [ESAMPLE=n] [WRESCHOL] [SEED=n] [CLOCKSEED=[0|1]]
       [RANMETHOD=[n|S|m]] [VARCALC=[0|1|2|3]]
       [FIXEDETAS=(list)] [NPDTYPE=[0|1]] [INTERPTYPE=[0|1]]
       [UNCONDITIONAL|CONDITIONAL] [OMITTED]
```

### Items for `list1`

- `$INPUT` data item labels.
- `DV`, plus automatic `PRED`, `RES`, `WRES` (appended unless `NOAPPEND`).
- Residual diagnostics: `NPRED/NRES/NWRES` (non-conditional, no interaction);
  `PREDI/RESI/WRESI` (non-conditional, interaction);
  `CPRED/CRES/CWRES` (conditional, no interaction);
  `CPREDI/CRESI/CWRESI` (conditional, interaction);
  `CIPRED/CIRES/CIWRES` and `CIPREDI/CIRESI/CIWRESI` (conditional individual);
  `EPRED/ERES/EWRES` and `ECWRES` (Monte-Carlo, non-linearized);
  `NPDE` (Monte-Carlo normalized prediction distribution error), `NPD`.
- `OBJI` (individual objective function values).
- `ETA(n)` / `ETAn`; ranges `ETAS(k:n)`, `ETAS(1 TO 10 BY 3)`, number lists
  `ETAS(1,5,12,4)` (NM74).
- `COM(k)` or `:kkkk` reserved NMPRD4 positions; PRED-defined item labels.
- `VECTRA(1..9)` / `VA_1..VA_9` etc.
- Derivative elements `Gk1`, `Hk1` (partials of F w.r.t. ETA(1)/EPS(1)).
- Synonyms: `WRES=RES1`, `IWRES=RES2`, `COM(3)=ABC`, etc.

`BY list2`: sort the table rows on one or more `list1` labels (only when
`list1` has <= 8 items).

### File / header / record selection

| Option | Meaning |
|---|---|
| `PRINT` (default) / `NOPRINT` | Table appears in NONMEM output / not. `FILE` required with NOPRINT. |
| `FILE=filename` | Write table to a file. |
| `NOHEADER` | No header lines. `ONEHEADER`: only first line is header. `ONEHEADERALL` (NM74): only first line of the whole file (with FORWARD). |
| `NOLABEL`, `NOTITLE` | Suppress column labels / title. `NOLABEL NOTITLE` = `NOHEADER`. |
| `FIRSTONLY`, `LASTONLY`, `FIRSTLASTONLY` | Only first / last / both records per individual. |
| `NOFORWARD` (default) / `FORWARD` | Reopen file at start / append to end (accumulate across subproblems). |
| `APPEND` (default) / `NOAPPEND` | Auto-append DV/PRED/RES/WRES / do not. NOAPPEND raises the label limit. |
| `EXCLUDE_BY list3` | Exclusion variables: rows where any listed item is nonzero are dropped from the file (not from printed tables). |

### Formatting

`FORMAT=s` sets delimiter + number format for table files (default
`s1PE11.4`; delimiter `,`, `s`=space, `t`=tab, then a Fortran format).
`LFORMAT` / `RFORMAT` give per-column label/numeric formats (use `="NONE"` to
revert). `IDFORMAT=s` (NM75) formats the ID column (e.g. `I`, `I6`, `F6.1`).

### Monte-Carlo diagnostics & SEs

| Option | Meaning |
|---|---|
| `ESAMPLE=n` | Random samples for Monte-Carlo diagnostics (default 300; first `$TABLE` only). |
| `WRESCHOL` | Cholesky (vs eigenvalue) sqrt of variance for weighted residuals (speedup). |
| `SEED=n`, `CLOCKSEED` | Seed for Monte-Carlo diagnostics (default 11456). |
| `RANMETHOD=[n|S|m]` | RNG / Sobol + scrambling for weighted residuals. |
| `VARCALC=[0|1|2|3]` | Standard errors for user-defined variables: 1 appends `item_SE`; 2 only writes `.vpd`/`.vpt`; 3 total SEs; 0 none (default). |
| `FIXEDETAS=(list)` | Treat listed etas as fixed effects for population diagnostics (super-ID `$LEVEL` etas). |
| `NPDTYPE=[0|1]` | 0 asymptotic residual variability (default); 1 strict stochastic Monte-Carlo NPD. |
| `INTERPTYPE=[0|1]` | NPDE quantile interpolation/extrapolation (NM751). |

`UNCONDITIONAL` (default) always runs the Table Step; `CONDITIONAL` only if
estimation succeeded/was omitted; `OMITTED` skips it.

`PARAFILE=[filename|ON|OFF]`: parallelize the weighted-residual computation.

## `$SCATTERPLOT`

Optional; generates families of scatterplots; up to 20 families per problem.
May also be coded `$SCATTERS` or `$SCATTERGRAMS`.

```
$SCATTERPLOT list1 VS list2 [BY list3]
             [FROM n1] [TO n2] [UNIT]
             [ORD0|NOORD0] [ABS0|NOABS0] [FIRSTONLY] [OBSONLY]
             [NOSUB=[0|1]]
             [UNCONDITIONAL|CONDITIONAL] [OMITTED]
```

Example: `$SCATTERPLOT (RES WRES) VS TIME BY ID`

- `list1` = ordinate items (may be parenthesized list); `list2` = abscissa.
  Items: data item labels, `PRED`, `RES`, `WRES`, all diagnostic variants
  (NPRED/CPRED/CWRES/EWRES/NPDE/... as for `$TABLE`), `OBJI`, `ETA(n)`/
  `ETAn` (ranges `ETAS(k:n)`, `TO`/`BY` syntax NM74; `ETAS(1:LAST)` is
  ignored — only the first eta is used), `COM(k)`/`:kkkk`, PRED-defined
  labels, `$ABBR REPLACE` symbolic labels (NM74).
- `BY list3`: a separate scatter family for each distinct value of the
  `list3` item (e.g. `BY ID`, `BY DOSE`).
- `FROM=n1 TO=n2`: restrict to a sub-range of the abscissa. `UNIT`: unit
  square plot.
- `ORD0`/`NOORD0`, `ABS0`/`NOABS0`: force (or not) ordinate/abscissa to
  include 0.
- `FIRSTONLY`: only first record of each individual. `OBSONLY`: only
  observation records.
- Repeated points are overstruck with symbols.

`UNCONDITIONAL`/`CONDITIONAL`/`OMITTED` behave as for `$TABLE`.

## Output file formats (`FORMAT` option)

Shared by `$TABLE`, `$ESTIMATION`, `$COVARIANCE`, `$CHAIN`, `$ETAS`, `$PHIS`.

`FORMAT=s` where `s` = delimiter (`,`, `s`=space, `t`=tab) followed by a
Fortran-like format. Examples:

```
FORMAT=s1PE11.4      ; space-delimited, E11.4 (default for $TABLE)
FORMAT=,E12.5        ; comma-delimited
FORMAT=t1PE12.5      ; tab-delimited (default for $ESTIMATION raw file)
```

The raw output file (from `$ESTIMATION`) uses `.ext`; standard errors come
from `$COVARIANCE` (`.cov`, `.cor`, `.coi`, `.cov` inverse); individual
parameters from `.phi` / `.iph`.
