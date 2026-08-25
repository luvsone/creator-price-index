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

path <- file.path(data_dir, "price-index.csv")

if (!file.exists(path)) {
  stop(sprintf("Not found: %s. Run scripts/export_from_api.py first.", path))
}

# comment.char costs nothing here and keeps the reader robust to a header line.
df <- read.csv(path, comment.char = "#", stringsAsFactors = FALSE)
df <- df[order(df$month), ]

cat(sprintf("%d months, %s to %s\n\n", nrow(df), df$month[1], df$month[nrow(df)]))

cat("Last six months:\n")
print(utils::tail(df, 6), row.names = FALSE)

cat("\nSummary:\n")
print(summary(df[, c("avg_price_real", "avg_price_advertised",
                     "median_price_real", "pct_on_discount")]))
