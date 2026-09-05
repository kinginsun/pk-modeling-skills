# examples/nonmem-pop-pk — minimal 1-compartment IV population PK

Smoke-test project for the `easy-nonmem` skill.

| File | Purpose |
|------|---------|
| `run1.mod` | 1-compartment IV model (ADVAN1 TRANS2), single subject, FOCE-I |
| `data.csv` | Dose + observation data (1 subject) |
| `run1.lst` | Reference NONMEM output (successful minimization) |
| `run1.ext` | Reference parameter estimates |

Run (requires NONMEM 7.6 + PsN):

```bash
execute run1.mod -directory=run1_execute
```

Expected: `run1.lst` ends with `MINIMIZATION SUCCESSFUL`; estimates in
`run1.ext` match the reference within estimation noise.
