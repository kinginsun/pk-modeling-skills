# easy-nonmem — reference

## Skeleton population PK `.mod` (adjust ADVAN/TRANS and records)

```text
$PROBLEM  base PK model
$INPUT   ID TIME AMT DV CMT EVID MDV ; + covariates as needed
$DATA    data.csv IGNORE=@

$SUBROUTINES ADVAN2 TRANS2

$PK
  TVCL = THETA(1)
  TVV  = THETA(2)
  CL   = TVCL * EXP(ETA(1))
  V    = TVV  * EXP(ETA(2))
  S2   = V/1000

$ERROR
  IPRED = F
  Y     = IPRED * (1 + EPS(1)) + EPS(2)

$THETA
  (0, 5, 100)   ; CL
  (0, 50, 500)  ; V

$OMEGA
  0.09 ; IIV CL
  0.09 ; IIV V

$SIGMA
  0.01 ; prop
  0   ; add fix

$ESTIMATION METHOD=1 INTERACTION MAXEVAL=9999 SIGDIG=3 PRINT=5 POSTHOC
$COVARIANCE PRINT=E UNCONDITIONAL
$TABLE ID TIME MDV AMT DV PRED IPRED RES WRES CWRES CL V NOAPPEND
       FILE=sdtab1.dta FORMAT=s1PE23.15
```

Notes:

- **`METHOD=0`** ≈ FO, **`METHOD=1` + `INTERACTION`** ≈ FOCE interaction—always confirm in `references/help/$estimat.ctl` (under the skill’s `references/` tree) for your NONMEM version.  
- For other ADVAN/TRANS pairs, see `references/guides/VI.md` and `references/help/$model.ctl`.

## PsN run

```bash
execute run1.mod -directory=run1_execute -threads=4
```

Inspect `run1_execute/NM_run1/psn.lst` or the generated `.lst` path PsN reports.

## R: DV vs PRED / IPRED (after `$TABLE`)

Assume `sdtab1.dta` is space-delimited scientific notation from NONMEM:

```r
# utils::read.table handles FORMAT=s1PE23.15 reasonably if default white space
df <- read.table("sdtab1.dta", header = TRUE, comment.char = "")

library(ggplot2)
ggplot(subset(df, MDV == 0 | is.na(MDV)), aes(IPRED, DV)) +
  geom_point(alpha = 0.4) +
  geom_abline(slope = 1, intercept = 0, linetype = 2) +
  scale_x_log10() + scale_y_log10() +
  labs(title = "DV vs IPRED", x = "IPRED", y = "DV")

ggplot(subset(df, MDV == 0 | is.na(MDV)), aes(TIME, DV)) +
  geom_point() +
  geom_line(aes(y = IPRED), color = "steelblue") +
  facet_wrap(~ID, scales = "free_x") +
  labs(title = "Individual fits")
```

Use **CWRES vs PRED** or **NPDE** only if those columns were requested in `$TABLE` and the estimation method supports them.

## Documentation paths (bundled in `easy-nonmem`)

Paths are relative to **this skill's folder** (the directory containing `SKILL.md`).

| Need | Path |
|------|------|
| `$INPUT` help | `references/help/$input.ctl` |
| `$DATA` / `IGNORE` | `references/help/$data.ctl` |
| `$DES` | `references/help/$des.ctl` |
| `$ERROR` | `references/help/$error.ctl` |
| `$ESTIMATION` | `references/help/$estimat.ctl` |
| NM-TRAN guide | `references/guides/IV.md` |
| PREDPP guide | `references/guides/VI.md` |
