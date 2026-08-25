# Luvs Creator Price Index

Monthly subscription pricing data from the subscription creator economy. One
number, computed the same way every month from publicly visible profile data:
the price fans actually pay, after every discount. Releases are frozen when the
month closes, so you can cite them.

[Dataset home page](https://luvsone.github.io/creator-price-index/) · [Live stats hub](https://luvs.one/stats) · [Dataset documentation](https://luvs.one/research) · [API](https://luvs.one/research#api)

A new month is added by the job in `.github/workflows/`, which reads the public
API on the 2nd of each month, once the previous month has been frozen.

## What's in this repository

| Path | Contents |
|---|---|
| `data/price-index.csv` | The full monthly series, rewritten as each new month is frozen. |
| `data/releases/YYYY-MM.csv` | One file per release month. Rewritten only to follow a published correction at the source, and every such rewrite is its own commit. |
| `CODEBOOK.md` | Column definitions, method, and known limitations. |
| `CITATION.cff` | Machine readable citation metadata. |
| `examples/load_python.py` | Load with pandas, print the last six months, plot the series. |
| `examples/load_r.R` | Load with base R and summarise. |
| `scripts/export_from_api.py` | Fetches the public API and writes the CSVs. Exits cleanly while the API is unpublished. |
| `scripts/build_site.py` | Regenerates `docs/index.html`, the GitHub Pages landing page, from the CSV and the codebook. |
| `docs/index.html` | The published landing page. Generated, never hand edited. |

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

`examples/load_python.py` does the same and writes a chart.

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
tracking platform for the creator economy.

Questions about the data, or a breakdown that is not published here? Ask through
the [contact form](https://luvs.one/contact?topic=press). We reply within two
business days and prepare custom aggregate cuts for journalists and researchers,
free, with the methodology attached.
