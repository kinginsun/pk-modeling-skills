#!/usr/bin/env Rscript
# gof_plots.R — GOF figures from the $TABLE output (sdtab1), per easy-nonmem
# reference.md. Outputs: gof_indfits.png, gof_diag.png

suppressPackageStartupMessages(library(ggplot2))

# NOTE: NONMEM writes a "TABLE NO.  1" banner line before the header —
# skip=1 is required when reading $TABLE output written with ONEHEADER.
# Dose rows carry DV="." which read.table turns into NA; drop them.
d <- read.table("sdtab1", header = TRUE, skip = 1)
d <- d[!is.na(d$DV), , drop = FALSE]   # observations only

theme_set(theme_bw(base_size = 11))

# ---- figure 1: individual fits + observations --------------------------------
p1 <- ggplot(d, aes(TIME, IPRED)) +
  geom_line(aes(group = ID), color = "steelblue", linewidth = 0.6) +
  geom_point(aes(y = DV), size = 1.6, alpha = 0.85) +
  facet_wrap(~ID, scales = "free_x") +
  labs(title = "Theophylline: individual fits (IPRED) and observations (DV)",
       x = "Time (h)", y = "Concentration (mg/L)")
ggsave("gof_indfits.png", p1, width = 9, height = 7, dpi = 150)

# ---- figure 2: diagnostic panels ---------------------------------------------
df <- data.frame(
  IPRED = d$IPRED, PRED = d$PRED, DV = d$DV, CWRES = d$CWRES, TIME = d$TIME
)

p_obs <- ggplot(df, aes(IPRED, DV)) +
  geom_point(alpha = 0.6) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, color = "firebrick") +
  geom_smooth(method = "loess", se = FALSE, color = "steelblue") +
  coord_equal() +
  labs(title = "DV vs IPRED", x = "IPRED", y = "DV")

p_pred <- ggplot(df, aes(PRED, DV)) +
  geom_point(alpha = 0.6) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, color = "firebrick") +
  geom_smooth(method = "loess", se = FALSE, color = "steelblue") +
  coord_equal() +
  labs(title = "DV vs PRED", x = "PRED", y = "DV")

p_cwres <- ggplot(df, aes(TIME, CWRES)) +
  geom_point(alpha = 0.6) +
  geom_hline(yintercept = 0, linetype = 2, color = "firebrick") +
  geom_smooth(method = "loess", se = FALSE, color = "steelblue") +
  labs(title = "CWRES vs time", x = "Time (h)", y = "CWRES")

library(gridExtra)
p_all <- arrangeGrob(p_obs, p_pred, p_cwres, ncol = 2)
ggsave("gof_diag.png", p_all, width = 9, height = 7, dpi = 150)

cat("wrote gof_indfits.png and gof_diag.png\n")
