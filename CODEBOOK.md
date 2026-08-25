# Codebook

Column definitions, how the numbers are produced, and what they do not cover.

## Columns

Every file in `data/` uses this schema, one row per calendar month.

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

An empty cell means the value was not computable for that month. It never means
zero. A month with no usable price coverage is published with empty price columns
rather than dropped or filled in.

## Method

**Sources.** Everything is derived from publicly visible profile pages. Nothing
comes from behind a paywall, and no account is used to collect it.

**Price basis.** Point in time: the last price observed in the month, not a mean
of the month's observations. Averaging prices produces figures nobody was ever
charged and distorts both the median and the mode.

**Aggregation.** Monthly. A month is closed on the 1st of the following month, and
the release for it is computed once at that point.

**Immutability.** A release is never recomputed. Corrections, if one is ever
needed, are published as a new file and noted, never as a silent edit to an old
one.

**Suppression.** Any breakdown by dimension (niche, country) is published only
where at least 15 profiles back it. Below that, a "niche average" is a list of
individual prices wearing an aggregate's clothes, so it is withheld rather than
published thin. Country membership appears at a lower floor because the site
already publishes a public page per country, but the price for a country still
requires 15.

**No per-profile rows.** This dataset contains aggregates only. There are no
usernames, no identifiers, and no row that describes one person.

## Known limitations

**Partial market coverage.** This is a curated catalogue, not the whole platform.
Nothing here is a census: a figure describes the profiles we publish, and the
catalogue grows over time, so `price_sample_n` moving between months reflects
coverage as well as the market.

**Public signals only.** Everything is what a logged-out visitor can see. Private
engagement, direct messages and pay-per-view sales are invisible to this dataset,
which means the subscription price it reports is not the same thing as what a
creator earns per fan.

**Collection lag.** Profiles are re-checked on a rota rather than continuously, so
a monthly figure can trail the market by days. This matters most for discounts,
which can start and end inside a single collection interval.

**Labels are current, not historical.** Niche and country come from the labels a
profile carries today, applied to past months as well. They are stable attributes,
but a creator who changed direction is described by where she is now.

**Short series.** Usable price history is recent. The series starts at the first
month with enough recorded prices to support an index, not at the first month any
profile was observed, so it is shorter than the observation history.

## Related

- Live figures and the frozen release archive: <https://luvs.one/stats>
- Dataset documentation, sample definition and limitations: <https://luvs.one/research>
- Read only API serving the same figures: <https://luvs.one/research#api>
