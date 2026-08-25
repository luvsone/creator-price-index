#!/usr/bin/env python3
"""
build_site.py: renders docs/index.html, the GitHub Pages landing page for the
Luvs Creator Price Index.

The page is GENERATED from the data that ships in this repository, never hand
written, for the same reason CODEBOOK.md is generated: a landing page that
disagrees with its own CSV is worse than no landing page. Run it after
export_from_api.py and commit the result alongside the data, so the published
page and the published data always describe the same release.

Inputs : data/price-index.csv, CODEBOOK.md, CITATION.cff
Outputs: docs/index.html  the GitHub Pages landing page (self contained, no
         external assets, no trackers)
         index.md         the DataHub Cloud page. DataHub syncs this repository
         and renders index.md as the site home, so GitHub keeps showing
         README.md and DataHub shows this one. Its charts point at the CSV by
         URL rather than at numbers pasted into the prose, so they follow every
         monthly refresh on their own.
"""

import csv
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DOI = "10.5281/zenodo.22094426"
SITE = "https://luvs.one"
REPO = "https://github.com/luvsone/creator-price-index"
RAW = "https://raw.githubusercontent.com/luvsone/creator-price-index/main"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def month_label(ym: str) -> str:
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def read_series():
    with open(ROOT / "data" / "price-index.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def usd(v):
    return f"${float(v):.2f}" if v else "n/a"


def pct(v):
    return f"{float(v) * 100:.1f}%" if v else "n/a"


def codebook_rows():
    """The column table, lifted from CODEBOOK.md so the two cannot drift."""
    text = (ROOT / "CODEBOOK.md").read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|$", line)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3)))
    return rows


def limitations():
    """The known limitations, same source, same wording."""
    text = (ROOT / "CODEBOOK.md").read_text(encoding="utf-8")
    block = text.split("## Known limitations", 1)[1].split("## Related", 1)[0]
    out = []
    for para in [p.strip() for p in block.split("\n\n") if p.strip()]:
        m = re.match(r"\*\*(.+?)\*\*\s*(.+)", para.replace("\n", " "), re.S)
        if m:
            out.append((m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()))
    return out


def esc(s):
    return html.escape(str(s), quote=True)


def render():
    rows = read_series()
    latest = rows[-1]
    ym = latest["month"]
    label = month_label(ym)
    cite_plain = (f"LuvsOne ({ym[:4]}). Luvs Creator Price Index, {label} release. "
                  f"https://doi.org/{DOI}")

    headline = [
        ("Median price charged", usd(latest["median_price_real"]),
         "What the middle subscription actually costs per month, after discounts."),
        ("Mean price charged", usd(latest["avg_price_real"]),
         "The average of the same charged prices."),
        ("Mean price advertised", usd(latest["avg_price_advertised"]),
         "The list price on the same profiles, before any discount."),
        ("Profiles on discount", pct(latest["pct_on_discount"]),
         "Share of priced profiles running a discount when the month closed."),
        ("Median discount depth", pct(latest["median_discount_depth"]),
         "How far an active discount cuts the advertised price."),
        ("Discounts running 90 days or more", pct(latest["pct_discount_over_90d"]),
         "Of the profiles on discount, the share held without a break."),
    ]

    series_head = ["Month", "Median charged", "Mean charged", "Mean advertised",
                   "On discount", "Median depth", "Held 90 days or more", "Sample"]
    series_rows = "".join(
        "<tr>"
        f"<td>{esc(month_label(r['month']))}</td>"
        f"<td class=n>{esc(usd(r['median_price_real']))}</td>"
        f"<td class=n>{esc(usd(r['avg_price_real']))}</td>"
        f"<td class=n>{esc(usd(r['avg_price_advertised']))}</td>"
        f"<td class=n>{esc(pct(r['pct_on_discount']))}</td>"
        f"<td class=n>{esc(pct(r['median_discount_depth']))}</td>"
        f"<td class=n>{esc(pct(r['pct_discount_over_90d']))}</td>"
        f"<td class=n>{esc(r['price_sample_n'] or 'n/a')}</td>"
        "</tr>"
        for r in reversed(rows))

    tiles = "".join(
        f'<div class=tile><div class=tile-k>{esc(k)}</div>'
        f'<div class=tile-v>{esc(v)}</div><p class=tile-d>{esc(d)}</p></div>'
        for k, v, d in headline)

    cb = "".join(
        f"<tr><td><code>{esc(c)}</code></td><td class=t>{esc(t)}</td><td>{esc(d)}</td></tr>"
        for c, t, d in codebook_rows())

    lim = "".join(f"<li><strong>{esc(t)}</strong> {esc(b)}</li>" for t, b in limitations())

    release_files = "".join(
        f'<li><a href="{RAW}/data/releases/{esc(r["month"])}.csv">{esc(month_label(r["month"]))}</a></li>'
        for r in reversed(rows))

    bibtex = (
        "@dataset{luvsone_price_index,\n"
        "  title     = {Luvs Creator Price Index},\n"
        "  author    = {{LuvsOne}},\n"
        f"  year      = {{{ym[:4]}}},\n"
        f"  version   = {{{ym}}},\n"
        "  publisher = {Zenodo},\n"
        f"  doi       = {{{DOI}}},\n"
        f"  url       = {{https://doi.org/{DOI}}}\n"
        "}")

    jsonld = f"""{{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Luvs Creator Price Index",
  "alternateName": "LCPI",
  "description": "Monthly aggregate statistics on subscription pricing and discounting in the creator economy, computed from publicly visible profile data. Aggregates only. Releases are frozen when the month closes.",
  "url": "https://luvsone.github.io/creator-price-index/",
  "identifier": "https://doi.org/{DOI}",
  "version": "{ym}",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "creator": {{"@type": "Organization", "name": "LuvsOne", "url": "{SITE}"}},
  "publisher": {{"@type": "Organization", "name": "LuvsOne", "url": "{SITE}"}},
  "spatialCoverage": "Worldwide",
  "temporalCoverage": "{rows[0]['month']}/{ym}",
  "isBasedOn": "{SITE}/stats",
  "distribution": [
    {{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "{RAW}/data/price-index.csv"}},
    {{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": "{SITE}/api/v1/price-index"}}
  ]
}}"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luvs Creator Price Index: monthly subscription pricing data</title>
<meta name="description" content="Open monthly data on what a creator subscription actually costs after discounts. Frozen releases, CC BY 4.0, DOI {DOI}. Latest release: {label}.">
<link rel="canonical" href="https://luvsone.github.io/creator-price-index/">
<meta property="og:title" content="Luvs Creator Price Index">
<meta property="og:description" content="Monthly subscription pricing data from the creator economy. Frozen, citable releases under CC BY 4.0.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://luvsone.github.io/creator-price-index/">
<script type="application/ld+json">{jsonld}</script>
<style>
:root {{
  --bg:#fff; --fg:#16141a; --fg2:#4a4550; --line:#e6e2ea; --soft:#faf9fb;
  --accent:#7c3aed; --code:#f4f2f7;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#131117; --fg:#f2eff5; --fg2:#a8a1b4; --line:#2b2733; --soft:#1a1720;
           --accent:#b087ff; --code:#1e1a26; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-text-size-adjust:100%; }}
.wrap {{ width:100%; padding:0 clamp(18px,3vw,44px) 80px; }}
header {{ padding:56px 0 28px; border-bottom:1px solid var(--line); margin-bottom:36px; }}
h1 {{ font-size:clamp(28px,5vw,40px); line-height:1.15; margin:0 0 12px; letter-spacing:-0.02em; }}
.lede {{ font-size:18px; color:var(--fg2); margin:0 0 20px; }}
.meta {{ display:flex; flex-wrap:wrap; gap:8px; }}
.pill {{ font-size:13px; padding:5px 11px; border:1px solid var(--line); border-radius:999px;
  color:var(--fg2); text-decoration:none; background:var(--soft); }}
.pill:hover {{ border-color:var(--accent); color:var(--fg); }}
h2 {{ font-size:22px; margin:44px 0 6px; letter-spacing:-0.01em; }}
h2 + p {{ margin-top:0; color:var(--fg2); }}
a {{ color:var(--accent); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; margin:20px 0 0; }}
.tile {{ border:1px solid var(--line); border-radius:12px; padding:16px; background:var(--soft); }}
.tile-k {{ font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:var(--fg2); }}
.tile-v {{ font-size:30px; font-weight:600; margin:6px 0 4px; font-variant-numeric:tabular-nums; }}
.tile-d {{ font-size:13px; color:var(--fg2); margin:0; }}
.scroll {{ overflow-x:auto; margin:18px 0; border:1px solid var(--line); border-radius:12px; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th,td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); white-space:nowrap; }}
th {{ background:var(--soft); font-weight:600; font-size:13px; }}
tr:last-child td {{ border-bottom:0; }}
td.n {{ font-variant-numeric:tabular-nums; }}
td.t, td:last-child {{ white-space:normal; }}
code {{ background:var(--code); padding:2px 6px; border-radius:5px; font-size:13px;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
pre {{ background:var(--code); padding:14px 16px; border-radius:12px; overflow-x:auto;
  font-size:13px; line-height:1.5; border:1px solid var(--line); }}
pre code {{ background:none; padding:0; }}
ul {{ padding-left:20px; }}
li {{ margin:8px 0; }}
.cols {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:24px; }}
footer {{ margin-top:56px; padding-top:24px; border-top:1px solid var(--line);
  color:var(--fg2); font-size:14px; }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Luvs Creator Price Index</h1>
  <p class="lede">What a creator subscription actually costs per month, after every discount, measured the same way each month from publicly visible profile data. Each release is frozen when the month closes, so a figure you cite today reads the same in a year.</p>
  <div class="meta">
    <a class="pill" href="https://doi.org/{DOI}">DOI {DOI}</a>
    <a class="pill" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>
    <a class="pill" href="{REPO}">Source repository</a>
    <span class="pill">Latest release: {label}</span>
  </div>
</header>

<h2>The {label} release</h2>
<p>Computed on {esc(latest['price_sample_n'])} priced profiles. Empty cells mean a measure was not computable, never zero.</p>
<div class="grid">{tiles}</div>

<h2>Full series</h2>
<p>Every month published so far, newest first. The same table ships as <a href="{RAW}/data/price-index.csv">price-index.csv</a>.</p>
<div class="scroll"><table>
<thead><tr>{''.join(f'<th>{esc(h)}</th>' for h in series_head)}</tr></thead>
<tbody>{series_rows}</tbody>
</table></div>

<h2>Get the data</h2>
<div class="cols">
<div>
<h3 style="font-size:15px;margin:0 0 6px">Files</h3>
<ul>
<li><a href="{RAW}/data/price-index.csv">Full series (CSV)</a>, rewritten as each month is frozen.</li>
<li><a href="{REPO}/tree/main/data/releases">Frozen releases</a>, one immutable file per month.</li>
<li><a href="{SITE}/api/v1/price-index.zip">Release bundle (.zip)</a>: CSV, JSON metadata and a README with the citation.</li>
</ul>
</div>
<div>
<h3 style="font-size:15px;margin:0 0 6px">API</h3>
<ul>
<li><a href="{SITE}/api/v1/price-index">Full series as JSON</a>, read only, no key, open CORS.</li>
<li><a href="{SITE}/api/v1/price-index.csv">Same series as CSV</a>.</li>
<li>Add <code>?release=YYYY-MM</code> to pin a response to a frozen month.</li>
</ul>
</div>
</div>

<h3 style="font-size:15px;margin:24px 0 6px">Frozen release files</h3>
<ul style="columns:2;column-gap:32px">{release_files}</ul>

<h3 style="font-size:15px;margin:24px 0 6px">Mirrors</h3>
<ul>
<li><a href="https://doi.org/{DOI}">Zenodo</a>, the archived and versioned copy of record.</li>
<li><a href="https://www.kaggle.com/datasets/luvsone/creator-subscription-pricing-luvs-index">Kaggle</a>, with a starter notebook.</li>
<li><a href="https://huggingface.co/datasets/luvsone/creator_price_index">Hugging Face</a>, with dataset viewer and Croissant metadata.</li>
</ul>

<h2>How to cite</h2>
<p>The DOI resolves to the newest version. To cite one frozen month, use its own release file.</p>
<pre><code>{esc(cite_plain)}</code></pre>
<pre><code>{esc(bibtex)}</code></pre>

<h2>Column definitions</h2>
<p>The same definitions ship as <a href="{REPO}/blob/main/CODEBOOK.md">CODEBOOK.md</a> with the data.</p>
<div class="scroll"><table>
<thead><tr><th>Column</th><th>Type</th><th>Definition</th></tr></thead>
<tbody>{cb}</tbody>
</table></div>

<h2>Known limitations</h2>
<p>Read these before quoting a figure.</p>
<ul>{lim}</ul>

<h2>Where the numbers come from</h2>
<p>The index is computed from the published catalogue on <a href="{SITE}/stats">the LuvsOne stats hub</a>, which carries the live figures and the archive of frozen monthly releases. The sample definition, the per measure method and the full changelog are documented on <a href="{SITE}/research">the dataset documentation page</a>. Both pages are the upstream source: this repository mirrors them so the data stays downloadable and archived independently of the site.</p>

<footer>
<p>Luvs Creator Price Index, published by <a href="{SITE}">LuvsOne</a>. Free to reuse under CC BY 4.0 with attribution. Aggregates only: the dataset carries no per creator rows and no personal data.</p>
<p>This page is generated from the data in this repository by <code>scripts/build_site.py</code> and refreshed with every monthly release.</p>
</footer>

</div>
</body>
</html>
"""


def render_datahub(rows):
    """The DataHub Cloud page. Prose figures come from the release; the charts
    and the table read the CSV directly, so they never fall behind it."""
    latest = rows[-1]
    ym = latest["month"]
    label = month_label(ym)
    csv_url = f"{RAW}/data/price-index.csv"
    gap = float(latest["avg_price_advertised"]) - float(latest["avg_price_real"])
    gap_pct = gap / float(latest["avg_price_advertised"]) * 100
    lim = "\n".join(f"- **{t}** {b}" for t, b in limitations())
    cb = "\n".join(f"| `{c}` | {t} | {d} |" for c, t, d in codebook_rows())

    return f"""# Luvs Creator Price Index

What a creator subscription actually costs per month, after every discount,
measured the same way each month from publicly visible profile data. Each
release is frozen when the month closes, so a figure you cite today reads the
same in a year.

Aggregates only. The dataset carries no per creator rows and no personal data.

| | |
|---|---|
| Latest release | {label} |
| Sample behind it | {latest['price_sample_n']} priced profiles |
| Licence | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| DOI | [{DOI}](https://doi.org/{DOI}) |
| Upstream source | [luvs.one/stats]({SITE}/stats) |

## What the {label} release says

The median subscription charged **{usd(latest['median_price_real'])}** a month,
against a mean advertised price of **{usd(latest['avg_price_advertised'])}**.
That gap of {usd(gap)} is {gap_pct:.0f}% of the list price, and it is not noise:
{pct(latest['pct_on_discount'])} of priced profiles were running a discount when
the month closed, at a median depth of {pct(latest['median_discount_depth'])}.

The interesting part is how permanent those discounts are.
{pct(latest['pct_discount_over_90d'])} of the active discounts had been running
without a break for 90 days or more, which makes the advertised price closer to
a reference point than to a price anyone pays.

<LineChart
  data={{{{
    url: "{csv_url}"
  }}}}
  title="Median subscription price actually charged, USD per month"
  xAxis="month"
  yAxis="median_price_real"
/>

<LineChart
  data={{{{
    url: "{csv_url}"
  }}}}
  title="Mean advertised price, USD per month"
  xAxis="month"
  yAxis="avg_price_advertised"
/>

## The full series

<FlatUiTable
  data={{{{
    url: "{csv_url}"
  }}}}
/>

## Get the data

- [Full series as CSV]({csv_url}), rewritten as each month is frozen
- [Frozen releases]({REPO}/tree/main/data/releases), one immutable file per month
- [Release bundle as .zip]({SITE}/api/v1/price-index.zip): CSV, JSON metadata and a README with the citation
- [Read only JSON API]({SITE}/api/v1/price-index), no key, open CORS. Add `?release=YYYY-MM` to pin a response to a frozen month.

Mirrors: [Zenodo](https://doi.org/{DOI}) is the archived copy of record,
with [Kaggle](https://www.kaggle.com/datasets/luvsone/creator-subscription-pricing-luvs-index)
and [Hugging Face](https://huggingface.co/datasets/luvsone/creator_price_index)
carrying the same files.

## How to cite

```
LuvsOne ({ym[:4]}). Luvs Creator Price Index, {label} release. https://doi.org/{DOI}
```

## Column definitions

| Column | Type | Definition |
|---|---|---|
{cb}

An empty cell means the measure was not computable for that month. It never means zero.

## Known limitations

{lim}

## Where the numbers come from

The index is computed from the published catalogue on
[the LuvsOne stats hub]({SITE}/stats), which carries the live figures and the
archive of frozen monthly releases. The sample definition, the per measure
method and the full changelog are documented on
[the dataset documentation page]({SITE}/research).
"""


def main():
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(render(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "index.md").write_text(render_datahub(read_series()), encoding="utf-8")
    print(f"wrote {DOCS / 'index.html'} and {ROOT / 'index.md'}")


if __name__ == "__main__":
    main()
