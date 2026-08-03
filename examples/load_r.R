#!/usr/bin/env Rscript
# Load the Luvs Creator Price Index and summarise it.
#
#     Rscript examples/load_r.R

# sys.frame()$ofile only exists when the file is source()d, so Rscript needs the
# --file= argument instead. Fall back to the repository layout either way.
script_path <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  hit <- grep("^--file=", args, value = TRUE)
  if (length(hit)) return(normalizePath(sub("^--file=", "", hit[1])))
  of <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (!is.null(of)) return(normalizePath(of))
  file.path(getwd(), "examples", "load_r.R")
}
here <- dirname(script_path())
data_dir <- file.path(dirname(here), "data")

real <- file.path(data_dir, "price-index.csv")
sample <- file.path(data_dir, "sample-2026-07.csv")
path <- if (file.exists(real)) real else sample

if (identical(path, sample)) {
  message("!! Reading the SAMPLE file. Every value in it is zero on purpose.")
  message("!! It shows the layout and nothing else. Do not cite it.\n")
}

# comment.char skips the placeholder's warning header; harmless on the real file.
df <- read.csv(path, comment.char = "#", stringsAsFactors = FALSE)
df <- df[order(df$month), ]

cat(sprintf("%d months, %s to %s\n\n", nrow(df), df$month[1], df$month[nrow(df)]))

cat("Last six months:\n")
print(utils::tail(df, 6), row.names = FALSE)

cat("\nSummary:\n")
print(summary(df[, c("avg_price_real", "avg_price_advertised",
                     "median_price_real", "pct_on_discount")]))
