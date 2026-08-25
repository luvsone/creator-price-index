# Luvs Creator Price Index

Monthly subscription pricing data from the subscription creator economy. One
number, computed the same way every month from publicly visible profile data:
the price fans actually pay, after every discount. Releases are frozen when the
month closes, so you can cite them.

[Live stats hub](https://luvs.one/stats) · [Methodology](https://luvs.one/methodology) · [API docs](https://luvs.one/stats#api)

> **No real data is published here yet.** The only file in `data/` is a
> placeholder whose values are all zero, kept to show the column layout. Real
> releases land here once the public API goes live, written by the monthly job in
> `.github/workflows/`. Nothing in this repository is citable until then.

## What's in this repository

| Path | Contents |
|---|---|
| `data/price-index.csv` | The full monthly series. Not published yet. |
| `data/releases/YYYY-MM.csv` | One immutable file per release month, never edited after it is written. Empty for now. |
| `data/sample-2026-07.csv` | Placeholder showing the column layout. All values are zero. |
| `CODEBOOK.md` | Column definitions, method, and known limitations. |
| `CITATION.cff` | Machine readable citation metadata. |
| `examples/load_python.py` | Load with pandas, print the last six months, plot the series. |
| `examples/load_r.R` | Load with base R and summarise. |
| `scripts/export_from_api.py` | Fetches the public API and writes the CSVs. Exits cleanly while the API is unpublished. |

## Data schema

One row per calendar month. Full definitions in [CODEBOOK.md](CODEBOOK.md).

| Column | Type | Meaning |
|---|---|---|
| `month` | `YYYY-MM` | The month the row describes |
| `avg_price_real` | USD | Mean price actually charged, after discounts |
| `avg_price_advertised` | USD | Mean list price, measured on the same profiles |
| `median_price_real` | USD | Median charged price |
| `pct_on_discount` | 0 to 1 | Share of priced profiles running a discount |
| `pct_discount_over_90d` | 0 to 1 | Of those, the share running 90 days or more without a break |
| `median_discount_depth` | 0 to 1 | Median share off the advertised price |
| `price_sample_n` | integer | Priced profiles the row was computed on (sample size) |

An empty cell means the value was not computable for that month. It never means
zero.

## Quick start

```python
import pandas as pd

df = pd.read_csv('data/price-index.csv', comment='#').sort_values('month')
print(df.tail(6))
df.plot(x='month', y=['avg_price_advertised', 'avg_price_real'])
```

`examples/load_python.py` does the same and writes a chart. Both fall back to the
placeholder file while the real one is unpublished.

## What this data is not

Aggregates only. There are no usernames, no identifiers, and no row that
describes one person. Any breakdown by niche or country is published only where
at least 15 profiles back it.

The subscription price here is not creator earnings: it excludes pay-per-view
sales, tips and direct messages, none of which are publicly visible. See
[CODEBOOK.md](CODEBOOK.md#known-limitations) for the rest.

## License & citation

Licensed under [CC BY 4.0](LICENSE). Attribution with a link is required.

Suggested citation:

```
LuvsOne (2026). Luvs Creator Price Index. https://luvs.one/stats
```

See [CITATION.cff](CITATION.cff) for machine readable citation metadata. GitHub
renders it as a "Cite this repository" button.

## About

Maintained by [LuvsOne](https://luvs.one), an independent scoring and price
tracking platform for the creator economy. Contact: data@luvs.one
