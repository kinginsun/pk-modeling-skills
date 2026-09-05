#!/usr/bin/env Rscript
# smoke_plot.R — verify R + ggplot2 work; plots the bundled popPK example data.
# Usage: Rscript smoke_plot.R <data.csv> <out.png>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  cat("usage: Rscript smoke_plot.R <data.csv> <out.png>\n")
  quit(status = 2)
}

suppressPackageStartupMessages(library(ggplot2))
d <- read.csv(args[1], stringsAsFactors = FALSE)
obs <- d[d$MDV == 0, , drop = FALSE]
if (nrow(obs) == 0) { cat("no observations in data\n"); quit(status = 1) }

p <- ggplot(obs, aes(TIME, DV)) +
  geom_point() +
  labs(title = "pk-modeling-skills smoke test", x = "Time", y = "DV")
ggsave(args[2], p, width = 4, height = 3, dpi = 100)
cat("wrote", args[2], "\n")
