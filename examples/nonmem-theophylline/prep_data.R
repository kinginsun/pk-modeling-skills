#!/usr/bin/env Rscript
# prep_data.R — convert the Monolix-format theophylline CSV into NONMEM format.
# Input : ../monolix-theophylline/theophylline_data.csv (ID,AMT,TIME,CONC,WEIGHT,SEX)
# Output: theo_nm.csv (ID TIME AMT DV WT SEX EVID CMT MDV)
#
# NONMEM conventions used:
#   - ADVAN2 (1-cpt, first-order absorption): CMT=1 depot (dose), CMT=2 central (obs)
#   - dose rows: EVID=1, MDV=1, DV=. ; obs rows: EVID=0, MDV=0, AMT=.

d <- read.csv("../monolix-theophylline/theophylline_data.csv",
              stringsAsFactors = FALSE, na.strings = c("NA", "."))

out <- data.frame(
  ID   = d$ID,
  TIME = d$TIME,
  AMT  = ifelse(is.na(d$AMT), ".", d$AMT),
  DV   = ifelse(is.na(d$CONC), ".", d$CONC),
  WT   = d$WEIGHT,
  SEX  = ifelse(d$SEX == "M", 1, 0),   # 1 = male, 0 = female
  EVID = ifelse(is.na(d$AMT), 0, 1),
  CMT  = ifelse(is.na(d$AMT), 2, 1),   # obs in central, dose in depot
  MDV  = ifelse(is.na(d$CONC), 1, 0),
  stringsAsFactors = FALSE
)
write.table(out, "theo_nm.csv", sep = ",", row.names = FALSE, quote = FALSE)
cat("wrote theo_nm.csv:", nrow(out), "rows,",
    sum(out$EVID == 1), "doses,", sum(out$EVID == 0), "observations,",
    length(unique(out$ID)), "subjects\n")
