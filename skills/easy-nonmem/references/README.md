# easy-nonmem references

Curated NONMEM 7.6 reference extracted from the official Users Guides. All
paths are relative to this `references/` directory.

| File | Contents |
|------|----------|
| [data-items.md](data-items.md) | `$INPUT`, `$DATA`, and all reserved data items (`ID`, `TIME`, `DV`, `MDV`, `EVID`, `AMT`, `RATE`, `SS`, `II`, `ADDL`, `CMT`, `PCMT`, `L2`, `CALL`, `CONT`, `DATE`, `RAW_`, `MRG_`, `RPT_`, `REPL_`, `XVID`) — usage, options, event semantics. |
| [records.md](records.md) | All other NM-TRAN control records: `$PROBLEM`, `$SUPER`, `$SIZES`, `INCLUDE`, `$THETA`, `$OMEGA`, `$SIGMA`, `$THETAI`/`$THETAR`, `$PRIOR` and informative prior records, `$MSFI`, `$CHAIN`, `$ETAS`/`$PHIS`, `$BIND`, `$CONTR`, `$LEVEL`, `$MIX`, `$TOL`, `$NONPARAMETRIC`, `$WARNINGS`, etc., plus record-order summary. |
| [predpp.md](predpp.md) | PREDPP: ADVAN catalog with compartment layouts, basic PK parameters per ADVAN, TRANS1–6 reparameterizations, additional PK parameters (`Sn`, `Fn`, `ALAGn`, `MTIME`…), `$MODEL` record, `$SUBROUTINES`. |
| [model-code.md](model-code.md) | Abbreviated code: `$PK`, `$DES`, `$ERROR`, `$PRED`, `$AES`/`$AESINITIAL`, `$INFN`; language rules, left/right-hand quantities, forbidden names, pseudo-statements (`COMRES`, `CALLFL`), `$ABBREVIATED` options, special `CALL` statements, reserved module variables. |
| [estimation.md](estimation.md) | Estimation methods guidance (FO/FOCE/Laplace vs ITS/IMP/SAEM/BAYES/NUTS), full `$ESTIMATION` option reference, `$COVARIANCE` (incl. SIR), `$SIMULATION`. |
| [output.md](output.md) | `$TABLE` (items, diagnostics, SEs, file/format options) and `$SCATTERPLOT`; output file formats. |

## How to use

1. Drafting a control stream → start from the skeleton in `../reference.md`,
   then consult `predpp.md` (ADVAN/TRANS choice) and `data-items.md`.
2. Writing `$PK`/`$DES`/`$ERROR` → `model-code.md`.
3. Setting up `$THETA`/`$OMEGA`/`$SIGMA`, priors, `$MSFI`, or any other
   record → `records.md`.
4. Choosing/setting the estimation method → `estimation.md`.
5. Diagnostics tables and plots → `output.md`.
