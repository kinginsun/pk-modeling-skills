# examples/nonmem-ivivc — level-A IVIVC with Hill-type dissolution link

In vitro–in vivo correlation (IVIVC) for **metformin** extended-release
tablets, data digitized from:

> Balan G, et al. *In vitro–in vivo correlation of a novel metformin
> extended-release formulation.* AAPS PharmSciTech, 2001.

| File | Purpose |
|------|---------|
| `balan_diss_hill.mod` | NONMEM `$PRED` model: Hill equation on dissolution time with formulation-specific T50/gamma and shared EMAX |
| `balan_dissolution_nm.csv` | In vitro dissolution data (3 formulations) |
| `balan_human_pk_data.csv` | Human PK data (for the in vivo side) |
| `balan_diss_hill.lst` / `.ext` | Reference NONMEM output / estimates |
| `balan_diss_hill_gof.R` | R GOF plots for the fitted dissolution model |

Run (requires NONMEM 7.6 + PsN):

```bash
execute balan_diss_hill.mod -directory=balan_execute
Rscript balan_diss_hill_gof.R
```

This example pairs with `examples/monolix-ivivc/`, which models the same
dataset headlessly in MonolixSuite.
