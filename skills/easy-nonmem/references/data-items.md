# Data Items, `$INPUT`, and `$DATA`

Distilled from the NONMEM 7.6 Users Guides (NM-TRAN data-item reference).
NONMEM reads a rectangular data set; `$INPUT` names
the columns and `$DATA` names the file and how to filter/translate it.

---

## `$INPUT` record

Required. Must precede any control record that refers to specific data items.
Multiple `$INPUT` records continue each other.

```
$INPUT item1 item2 ...        ; each item is B or A=B (A, B are labels)
```

Rules:

- Labels: 1-24 chars, letters/digits/`_`, starting with a letter. Case
  insensitive. `&` at end of line continues the record.
- `A=B` renames: at least one side must be a reserved label; the user label is
  used as the output label (e.g. `CP=DV`).
- `DROP` or `SKIP` as label/synonym removes the column from the NONMEM data
  set (may be used for many items).
- `DATE=DROP` removes the date column but NM-TRAN still uses it to adjust
  `TIME`.
- Do **not** use as labels: `ETA1`-`ETA9`, basic PK parameter names (`CL`,
  `V`, `K`, `KA`), additional PK parameter names (`S1`, `F1`, `R1`, `D1`, ...),
  `MU_` variables.

Reserved labels:

```
ID L1 L2 DV MDV RAW_ MRG_ RPT_ REPL_
TIME DATE DAT1 DAT2 DAT3 DROP SKIP EVID AMT RATE SS II ADDL
CMT PCMT CALL CONT
```

Semi-reserved: `XVID1`-`XVID5` (extra EVIDs for repeated PK/ERROR calls on one
record, used e.g. for stochastic differential equations).

---

## `$DATA` record

Required with the first problem; may be omitted later (NONMEM re-uses the
previous problem's data). May also be coded `$INFILE`.

```
$DATA filename [(format)] [IGNORE=c1] [IGNORE=(list)...|ACCEPT=(list)...]
      [NULL=c2] [RECORDS=n1|RECORDS=label] [LRECL=n2]
      [NOWIDE|WIDE] [CHECKOUT] [NOREWIND|REWIND] [NOOPEN]
      [LAST20=n3] [TRANSLATE=(list)] [BLANKOK] [MISDAT=r...]
      [REPL=n...] [NOFDATACSV] [PRED_IGNORE_DATA]
```

Key options:

| Option | Meaning |
|---|---|
| `filename` | Data file; quote it if it contains commas/semicolons/parens/`=`/spaces. `*` in a later problem re-uses the previous data set. |
| `(format)` | FORTRAN read format (F, E, X codes; no I). When given, `DROP` on `$INPUT` and `WIDE`/`NULL` may not be used. If omitted, NM-TRAN generates one. |
| `IGNORE=c1` | Records with character `c1` in column 1 are comments. Default `IGNORE=#`. `IGNORE=@` drops records whose first non-blank char is alphabetic or `@` (lets table files with headers be read). |
| `IGNORE=(list)` | Drop records matching conditions: `label=value`, `.EQ.`, `.NE.`, `.GT.`, `.GE.`, `.LT.`, `.LE.` (or Fortran-90 `==`, `/=`, `<`, ...); `.NEN.`/`.EQN.` force numeric compare. Multiple conditions in one list are OR-ed; up to 100 conditions. With `=`, `.EQ.`, `.NE.` values compare as strings. |
| `ACCEPT=(list)` | Same syntax, but keeps matching records (drops the rest). Cannot combine with `IGNORE=(list)`; may combine with `IGNORE=c`. To drop an AND of conditions, use ACCEPT with negated conditions. |
| `NULL=c2` | Replace null items (single `.`, consecutive commas/tabs) with `c2` (default: space). |
| `RECORDS=n1` | Number of records to read. `RECORDS=ID` (or any label) reads only the first contiguous block of records sharing the first record's value of that item. |
| `NOWIDE` / `WIDE` | FDATA record layout; `NOWIDE` is default. `WIDE` writes single-line records (max 300 chars) and suppresses the FINISH record. |
| `CHECKOUT` | Data checkout mode: no PRED calls, no predictions/objective function; only `$TABLE`/`$SCAT` tasks run. Writes `FDATA.csv` so you can inspect parsed data. |
| `NOREWIND` / `REWIND` | For a later problem re-using the same file: keep position (read next data set) vs reposition to start. Default `NOREWIND`. |
| `NOOPEN` | Data file created by an earlier problem in the same run; requires an explicit format. |
| `LAST20=n3` | Two-digit-year century cutoff (default 50: 00-50 -> 2000s, 51-99 -> 1900s; `-1` = all same century). |
| `TRANSLATE=(TIME/F[/D], II/F[/D])` | Divide TIME and/or II by factor F (e.g. `/24` hours->days), writing D digits after the decimal. |
| `BLANKOK` | Permit blank lines in the data set (default: error). |
| `MISDAT=r` | Numeric missing-data sentinel shown in tables but read as 0 elsewhere (up to 20 values). |
| `REPL=n` | Treat data as template; NONMEM replicates it n times (for `$SIMULATION`/`$DESIGN`). |
| `NOFDATACSV` | Suppress creation of `FDATA.csv` (useful for large data sets). |
| `PRED_IGNORE_DATA` | Enables dropping records via abbreviated code (NM75+). |

Notes:

- Tab characters are field delimiters in data, converted to spaces in control
  streams.
- `:` in TIME or II values triggers clock-time translation (`hh:mm` or
  `hh:mm:ss` -> fractional hours relative to the first record of the
  individual).

---

## Required vs optional items

| Item | Required? | Purpose |
|---|---|---|
| `ID` | Required for population data (PREDPP) | Groups records into individual (L1) records; a change in ID starts a new individual. |
| `TIME` | Required with PREDPP (except ADVAN9/15/17 with only equilibrium compartments) | Event time; must be non-decreasing within an individual (reset events exempt). Negative times allowed since NM 7.4. |
| `DV` | Required by NONMEM | Observed value on observation records. |
| `MDV` | Optional (ID required if present) | 0 = observed; 1 = DV missing/ignored; 100/101 = like 0/1 but also ignored in Estimation/Covariance steps. With PREDPP, dose/other/reset records must have MDV=1 (NM-TRAN appends MDV if missing). |
| `EVID` | Required (NM-TRAN can supply it if only dose/observation events exist) | Event type: 0 observation, 1 dose, 2 other-type, 3 reset, 4 reset-and-dose. |
| `AMT` | Optional | Dose amount; must be 0 on non-dose records; must be 0 for steady-state constant infusions; positive otherwise. |
| `RATE` | Optional | Dose rate: 0 = bolus; >0 = infusion at that rate; -1 = zero-order with rate modeled in `$PK` (`Rn`); -2 = zero-order with duration modeled (`Dn`). |
| `SS` | Optional | Steady-state flag: 0 no; 1 reset amounts to SS from this dose; 2 add SS amounts to current amounts (linear kinetics); 3 like 1 but uses existing state as initial estimate (SS6/SS9). When SS is used, AMT, RATE, and/or II must define the dosing pattern. |
| `II` | Optional | Interdose interval. SS infusion (AMT=0, RATE>0): II=0. Other SS doses: II>0 (period of implied doses). Non-SS: II>0 only if ADDL>0. Units must match TIME. |
| `ADDL` | Optional | Number of additional doses identical to this one, spaced by II. NM75: negative ADDL requests the empirical steady-state method (no SS item). |
| `CMT` / `PCMT` | Optional | Compartment number; see below. |
| `L2` | Optional | Level-two grouping: records sharing the same L2 within an individual share one realization of level-two random effects. |
| `CALL` | Optional | Force calls to PK/ERROR on records that would not normally invoke them: 1 = ERROR, 2 = PK, 3 = both, 10 = call ADVAN9/15/17 (addable, e.g. 11). |
| `CONT` | Optional | Continuation: 0 = last/only record of the event; 1 = event spans to next record (MDV must be 1). |
| `DATE`, `DAT1`-`DAT3` | Optional | Calendar date used to translate TIME to relative times. Formats: DATE = month day year; DAT1 = day month year; DAT2 = year month day; DAT3 = year day month. Components separated by any non-numeric char. |
| `RAW_` | Optional | Raw-data averaging: 0 = normal; 1 (with MDV=1) = template record; displayed DV/RES become the two-stage raw-data-average over matching user-data items. |
| `MRG_` | Optional | Marginal expectation: 0 = typical value of F; 1/2 (with MDV=1) = expectation of F (simulation or posterior, per-individual deletion adjustment with 2). |
| `RPT_` | Optional | Repetition base marker: 0 = none; n (1-5) = first of a series of contiguous records that may be repeated. |
| `REPL_` | Optional (NM75) | Per-subject replication number when the data set is a template; 0 deletes the subject. Applied before `$DATA REPL=n`. |

---

## `EVID` event types

| EVID | Event | Requirements |
|---|---|---|
| 0 | Observation | DV is the observation; CMT names the observed compartment; AMT, RATE, II, ADDL, SS must be 0. |
| 1 | Dose | CMT names the dosed compartment; DV ignored; at least one of AMT, RATE, II, ADDL, SS non-zero. |
| 2 | Other-type | DV ignored; dose items 0. Uses: turn compartments on/off (CMT sign), obtain predictions at chosen times (PCMT), covariate changes, interventions. |
| 3 | Reset | Re-initialize system: time resets, amounts zeroed, compartment on/off statuses restored. DV ignored; dose items 0. |
| 4 | Reset-and-dose | Reset first, then dose. DV ignored. |

NM7 note: when NM-TRAN appends EVID, the record is non-dose, and the user
supplied MDV (1 or 101), NM-TRAN sets EVID=2 instead of 0. Supply both EVID
and MDV yourself to avoid surprises (especially with `RAW_`/`MRG_`).

`XVID1`-`XVID5`: on a single data record, PK/ERROR is called repeatedly with
EVID taken from XVID1, then XVID2, ... (MDV forced to 1 when EVID != 0). An
XVID of -1 stops further calls. If an EVID column exists, its value is used
only when XVID1=-1.

---

## `CMT` and `PCMT`

Behavior depends on event type:

- **Observation**: CMT = number of the observation compartment (its scaled
  amount becomes F in `$ERROR`). Negative CMT for the output compartment turns
  it off after observing. CMT = 1000 (or 100 for <= 99 compartments) denotes
  the output compartment. CMT = 0 uses the default observation compartment.
- **Dose**: CMT = dosed compartment (turned on if off); 0 = default dose
  compartment. PCMT = compartment for which F is computed (0 = default).
- **Other-type**: positive CMT turns a compartment on, negative turns off, 0 =
  no change. PCMT as for dose events.
- **Reset**: CMT ignored; PCMT as for dose events.
- **Reset-and-dose**: same as dose events.

Urine collections are typically modeled with the output compartment (see Guide
V, section 6.9).

---

## TIME and clock times

- If any TIME contains `:`, all times are treated as clock times (`hh:mm`) and
  converted to relative times starting at 0 for the first record of each
  individual (population data) or of the data set (single-subject).
- `$DATA ... TRANSLATE=(TIME/24)` divides converted times by 24 (hours -> days);
  same for `II/24`.

## DATE translation example

```
NM-TRAN data set                 NONMEM data set
ID   DATE      TIME              ID   TIME
1    10-1-86   9:15              1    0.00
1    10-1-86   14:40             1    5.42
1    10-2-86   8:30              1    23.25
```

One component = day; two components = day and month (<= 31 and <= 12).
