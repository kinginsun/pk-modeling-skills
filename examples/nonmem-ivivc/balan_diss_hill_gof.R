# Goodness-of-fit plots for balan_diss_hill.mod (Hill dissolution in time)
# Usage from IVIVC/: Rscript balan_diss_hill_gof.R [path/to/sdtab1.dta]
# Default table: ./balan_diss_hill_execute/NM_run1/sdtab1.dta

suppressPackageStartupMessages({
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("Install ggplot2: install.packages(\"ggplot2\")", call. = FALSE)
  }
  if (!requireNamespace("patchwork", quietly = TRUE)) {
    stop("Install patchwork: install.packages(\"patchwork\")", call. = FALSE)
  }
})

args <- commandArgs(trailingOnly = TRUE)
default_tab <- file.path("balan_diss_hill_execute", "NM_run1", "sdtab1.dta")
alt_tab <- file.path("..", "IVIVC", default_tab)
sdtab <- if (length(args) >= 1L) {
  args[1]
} else if (file.exists(default_tab)) {
  default_tab
} else if (file.exists(alt_tab)) {
  alt_tab
} else {
  stop(
    "Cannot find sdtab1.dta. Run from IVIVC after:\n",
    "  execute balan_diss_hill.mod -directory=balan_diss_hill_execute\n",
    "Or pass path: Rscript balan_diss_hill_gof.R /path/to/sdtab1.dta",
    call. = FALSE
  )
}

tab <- utils::read.table(sdtab, skip = 1, header = TRUE, comment.char = "")
form_lab <- c("1" = "A3", "2" = "A7", "3" = "A15")
tab$Group <- factor(
  form_lab[as.character(as.integer(tab$FORM))],
  levels = c("A3", "A7", "A15")
)

p_dv_ipred <- ggplot2::ggplot(tab, ggplot2::aes(IPRED, DV, color = Group)) +
  ggplot2::geom_point(size = 2, alpha = 0.85) +
  ggplot2::geom_abline(slope = 1, intercept = 0, linetype = 2, linewidth = 0.35) +
  ggplot2::coord_fixed(ratio = 1, xlim = range(c(tab$DV, tab$IPRED)), ylim = range(c(tab$DV, tab$IPRED))) +
  ggplot2::labs(
    title = "DV vs IPRED",
    subtitle = "Hill: %diss = Emax * t^gamma / (T50^gamma + t^gamma), per formulation",
    x = "IPRED (% dissolved)",
    y = "DV (% dissolved)"
  ) +
  ggplot2::theme_bw(base_size = 11) +
  ggplot2::theme(legend.position = "top")

p_time <- ggplot2::ggplot(tab, ggplot2::aes(TIME, DV, color = Group)) +
  ggplot2::geom_line(ggplot2::aes(y = IPRED), linewidth = 0.9, alpha = 0.9, linetype = 1) +
  ggplot2::geom_point(size = 2) +
  ggplot2::facet_wrap(~Group, nrow = 1, scales = "free_y") +
  ggplot2::labs(
    title = "Observed points and individual predicted dissolution",
    x = "Time (h)",
    y = "% dissolved"
  ) +
  ggplot2::theme_bw(base_size = 11) +
  ggplot2::theme(legend.position = "none")

p_cwres <- ggplot2::ggplot(tab, ggplot2::aes(TIME, CWRES, color = Group)) +
  ggplot2::geom_hline(yintercept = 0, linetype = 2, linewidth = 0.35) +
  ggplot2::geom_point(size = 2, alpha = 0.85) +
  ggplot2::geom_smooth(method = "loess", se = TRUE, linewidth = 0.6, formula = y ~ x) +
  ggplot2::facet_wrap(~Group, nrow = 1, scales = "fixed") +
  ggplot2::labs(
    title = "CWRES vs time",
    x = "Time (h)",
    y = "CWRES"
  ) +
  ggplot2::theme_bw(base_size = 11) +
  ggplot2::theme(legend.position = "none")

out <- file.path(getwd(), "balan_diss_hill_gof.png")
combined <- (p_dv_ipred) / p_time / p_cwres +
  patchwork::plot_layout(heights = c(1.1, 1, 1))
ggplot2::ggsave(out, combined, width = 9, height = 10, dpi = 150)
message("Wrote ", normalizePath(out, winslash = "/", mustWork = FALSE))
