#!/usr/bin/env python3
"""
Load the Luvs Creator Price Index, print the last six months, and plot the
advertised price against the real one.

    pip install pandas matplotlib
    python3 examples/load_python.py

Writes chart.png next to this file.
"""
import os
import sys

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display in CI
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

# The real file once it is published, the placeholder before that. `comment='#'`
# is what lets the placeholder's warning header through unread.
REAL = os.path.join(DATA, "price-index.csv")
SAMPLE = os.path.join(DATA, "sample-2026-07.csv")
path = REAL if os.path.exists(REAL) else SAMPLE

if path == SAMPLE:
    print("!! Reading the SAMPLE file. Every value in it is zero on purpose.")
    print("!! It shows the layout and nothing else. Do not cite it.\n")

df = pd.read_csv(path, comment="#", parse_dates=False)
df = df.sort_values("month")

print(f"{len(df)} months, {df['month'].iloc[0]} to {df['month'].iloc[-1]}\n")
print("Last six months:")
print(df.tail(6).to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(df["month"], df["avg_price_advertised"], linestyle="--", marker="o",
        label="Advertised", color="#8b8b8b")
ax.plot(df["month"], df["avg_price_real"], marker="o",
        label="Real, after discounts", color="#ff6464")
ax.set_title("Luvs Creator Price Index")
ax.set_ylabel("USD per month")
ax.set_ylim(bottom=0)
ax.grid(alpha=0.2)
ax.legend()
fig.autofmt_xdate(rotation=45)
fig.tight_layout()

out = os.path.join(HERE, "chart.png")
fig.savefig(out, dpi=140)
print(f"\nSaved {out}")

if path == SAMPLE:
    sys.exit(0)
