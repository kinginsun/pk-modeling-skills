;; Theophylline population PK — one-compartment oral model (walkthrough demo)
;; Data: classic theophylline dataset, 12 subjects, single oral dose 4.02 mg/kg
;; AMT is in mg/kg, so CL and V are in per-kg units (L/h/kg, L/kg).
;; ADVAN2 TRANS2: KA (absorption), K = CL/V (elimination), S2 = V
;; Covariate: allometric weight on CL (0.75) and V (1.0), reference 70 kg

$PROBLEM  Theophylline 1-cpt oral popPK (easy-nonmem walkthrough)
$INPUT  ID TIME AMT DV WT SEX EVID CMT MDV
$DATA   theo_nm.csv IGNORE=@

$SUBROUTINES ADVAN2 TRANS2

$PK
  TVKA = THETA(1)
  TVCL = THETA(2)
  TVV  = THETA(3)
  KA   = TVKA * EXP(ETA(1))
  CL   = TVCL * (WT/70)**0.75 * EXP(ETA(2))
  V    = TVV  * (WT/70)       * EXP(ETA(3))
  S2   = V
  K    = CL/V

$ERROR
  IPRED = F
  Y     = IPRED * (1 + EPS(1)) + EPS(2)

$THETA
  (0, 1.0, 20)   ; KA   (1/h)
  (0, 0.04, 5)   ; CL   (L/h/kg, per-kg dose basis)
  (0, 0.5, 5)    ; V    (L/kg, per-kg dose basis)

$OMEGA
  0.09           ; IIV on KA
  0.09           ; IIV on CL
  0.09           ; IIV on V

$SIGMA
  0.05           ; proportional
  0.01           ; additive (mg/L)

$ESTIMATION METHOD=1 INTERACTION MAXEVAL=9999 SIGDIG=3 PRINT=5 POSTHOC
$COVARIANCE PRINT=E

$TABLE ID TIME DV WT SEX KA CL V PRED IPRED CWRES NOAPPEND NOPRINT ONEHEADER
       FILE=sdtab1
