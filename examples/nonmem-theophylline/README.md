# examples/nonmem-theophylline — theophylline popPK (walkthrough)

Full worked example for the `easy-nonmem` skill — see
[`../../docs/walkthrough-theophylline.md`](../../docs/walkthrough-theophylline.md)
for the narrated session.

| File | Purpose |
|------|---------|
| `prep_data.R` | Monolix CSV → NONMEM event-record format (`theo_nm.csv`) |
| `run1.mod` | 1-cpt oral model, ADVAN2 TRANS2, FOCE-I, allometric WT scaling |
| `theo_nm.csv` | Generated NONMEM dataset (12 subjects, 12 doses, 120 obs) |
| `run1.lst` / `run1.ext` / `run1.cov` / `run1.coi` / `run1.cor` / `run1.phi` | Reference NONMEM outputs (minimization successful, covariance completed) |
| `sdtab1` | `$TABLE` output used by the plotting script |
| `gof_plots.R` | Individual fits + DV-vs-PRED/IPRED + CWRES panels |
| `gof_indfits.png` / `gof_diag.png` | Rendered GOF figures |

Reproduce:

```bash
Rscript prep_data.R
execute run1.mod -directory=theo_run -threads=4
Rscript gof_plots.R
```
