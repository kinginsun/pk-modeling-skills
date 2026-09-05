$PROBLEM  Balan et al. in vitro dissolution — Hill in time (formulation-specific T50, gamma; shared EMAX)
$ABBR DERIV2=NO
$INPUT   ID TIME DV MDV EVID FORM
$DATA    balan_dissolution_nm.csv

$PRED
; Hill: Fdiss = EMAX * TIME^gamma / (T50^gamma + TIME^gamma)
IF (FORM.EQ.1) THEN
  T50 = THETA(1)
  GAM = THETA(2)
ELSE IF (FORM.EQ.2) THEN
  T50 = THETA(3)
  GAM = THETA(4)
ELSE
  T50 = THETA(5)
  GAM = THETA(6)
ENDIF
EMAX = THETA(7)
IF (TIME.LE.0) THEN
  FDISS = 0
ELSE
  TG = TIME**GAM
  TG50 = T50**GAM
  FDISS = EMAX * TG / (TG50 + TG)
ENDIF
IPRED = FDISS
; ETA(1) with OMEGA fixed ~0: forces population mode for $PRED (NM-TRAN else infers single-subject)
Y = IPRED * EXP(ETA(1)) * (1 + EPS(1)) + EPS(2)

$THETA
(0.01, 0.45, 5)    ; T50 (h) formulation A3
(0.1, 2.5, 12)     ; Hill exponent A3
(0.1, 2.5, 20)     ; T50 (h) A7
(0.1, 2, 12)       ; Hill exponent A7
(0.5, 6, 30)       ; T50 (h) A15
(0.1, 1.5, 12)     ; Hill exponent A15
(85, 99.5, 102)    ; EMAX (% dissolved asymptote)

$OMEGA
1.E-30 FIX         ; no IIV; needed with POPETAS=1

$SIGMA
0.0004 ; proportional error on %
0.04   ; additive error (%)

$ESTIMATION METHOD=1 INTERACTION MAXEVAL=9999 SIGDIG=3 PRINT=5
$COVARIANCE PRINT=E UNCONDITIONAL

$TABLE ID TIME MDV EVID DV PRED IPRED RES WRES CWRES FORM NOAPPEND
       FILE=sdtab1.dta FORMAT=s1PE23.15
