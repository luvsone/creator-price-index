# Luvs Creator Price Index

What a creator subscription actually costs per month, after every discount,
measured the same way each month from publicly visible profile data. Each
release is frozen when the month closes, so a figure you cite today reads the
same in a year.

Aggregates only. The dataset carries no per creator rows and no personal data.

| | |
|---|---|
| Latest release | July 2026 |
| Sample behind it | 496 priced profiles |
| Licence | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| DOI | [10.5281/zenodo.22094426](https://doi.org/10.5281/zenodo.22094426) |
| Upstream source | [luvs.one/stats](https://luvs.one/stats) |

## What the July 2026 release says

The median subscription charged **$6.30** a month,
against a mean advertised price of **$12.76**.
That gap of $4.57 is 36% of the list price, and it is not noise:
56.5% of priced profiles were running a discount when
the month closed, at a median depth of 50.0%.

The interesting part is how permanent those discounts are.
47.1% of the active discounts had been running
without a break for 90 days or more, which makes the advertised price closer to
a reference point than to a price anyone pays.

<LineChart
  data={{
    url: "https://raw.githubusercontent.com/luvsone/creator-price-index/main/data/price-index.csv"
  }}
  title="Median subscription price actually charged, USD per month"
  xAxis="month"
  yAxis="median_price_real"
/>

<LineChart
  data={{
    url: "https://raw.githubusercontent.com/luvsone/creator-price-index/main/data/price-index.csv"
  }}
  title="Mean advertised price, USD per month"
  xAxis="month"
  yAxis="avg_price_advertised"
/>

## The full series

<FlatUiTable
  data={{
    url: "https://raw.githubusercontent.com/luvsone/creator-price-index/main/data/price-index.csv"
  }}
/>

## Get the data

- [Full series as CSV](https://raw.githubusercontent.com/luvsone/creator-price-index/main/data/price-index.csv), rewritten as each month is frozen
- [Frozen releases](https://github.com/luvsone/creator-price-index/tree/main/data/releases), one immutable file per month
- [Release bundle as .zip](https://luvs.one/api/v1/price-index.zip): CSV, JSON metadata and a README with the citation
- [Read only JSON API](https://luvs.one/api/v1/price-index), no key, open CORS. Add `?release=YYYY-MM` to pin a response to a frozen month.

Mirrors: [Zenodo](https://doi.org/10.5281/zenodo.22094426) is the archived copy of record,
with [Kaggle](https://www.kaggle.com/datasets/luvsone/creator-subscription-pricing-luvs-index)
and [Hugging Face](https://huggingface.co/datasets/luvsone/creator_price_index)
carrying the same files.

## How to cite

```
LuvsOne (2026). Luvs Creator Price Index, July 2026 release. https://doi.org/10.5281/zenodo.22094426
```

## Column definitions

| Column | Type | Definition |
|---|---|---|
| `month` | `YYYY-MM` | The calendar month the row describes. |
| `avg_price_real` | USD, 2 decimals | Mean price actually charged for a monthly subscription across the tracked profiles, after every discount in effect. |
| `avg_price_advertised` | USD, 2 decimals | Mean list price across the same profiles, before any discount. Measured on the same set as `avg_price_real`, so the gap between the two is discount rather than an artefact of different denominators. |
| `median_price_real` | USD, 2 decimals | Median of the same charged prices. Less sensitive than the mean to a handful of very expensive profiles. |
| `pct_on_discount` | fraction 0 to 1 | Share of the priced profiles running a discount at the close of the month. |
| `pct_discount_over_90d` | fraction 0 to 1 | Of those on discount, the share whose discount has run without a break for 90 days or more. A gap resets the clock, so a re-activated offer does not qualify. |
| `median_discount_depth` | fraction 0 to 1 | Median depth of an active discount, as a share off the advertised price. |
| `price_sample_n` | integer | Number of priced profiles the price columns on that row were computed on. This is the sample size behind the figures, not a catalogue total. |

An empty cell means the measure was not computable for that month. It never means zero.

## Known limitations

- **Partial market coverage.** This is a curated catalogue, not the whole platform. Nothing here is a census: a figure describes the profiles we publish, and the catalogue grows over time, so `price_sample_n` moving between months reflects coverage as well as the market.
- **Public signals only.** Everything is what a logged-out visitor can see. Private engagement, direct messages and pay-per-view sales are invisible to this dataset, which means the subscription price it reports is not the same thing as what a creator earns per fan.
- **Collection lag.** Profiles are re-checked on a rota rather than continuously, so a monthly figure can trail the market by days. This matters most for discounts, which can start and end inside a single collection interval.
- **Labels are current, not historical.** Niche and country come from the labels a profile carries today, applied to past months as well. They are stable attributes, but a creator who changed direction is described by where she is now.
- **Short series.** Usable price history is recent. The series starts at the first month with enough recorded prices to support an index, not at the first month any profile was observed, so it is shorter than the observation history.

## Where the numbers come from

The index is computed from the published catalogue on
[the LuvsOne stats hub](https://luvs.one/stats), which carries the live figures and the
archive of frozen monthly releases. The sample definition, the per measure
method and the full changelog are documented on
[the dataset documentation page](https://luvs.one/research).
