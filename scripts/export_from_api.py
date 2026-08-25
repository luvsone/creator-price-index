#!/usr/bin/env python3
"""
Pull the Luvs Creator Price Index from the public API and write it to
data/price-index.csv, plus one immutable file per release under data/releases/.

Run by .github/workflows/monthly-update.yml on the 2nd of each month, after the
release for the closed month has been frozen.

Exits 0 and writes nothing when the API is not reachable or has published no
releases yet. That is deliberate: a scheduled job that fails loudly every month
until launch is a job people learn to ignore.

    python3 scripts/export_from_api.py [--api-base https://luvs.one]
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import urllib.error
import urllib.request

API_DEFAULT = "https://luvs.one"
ENDPOINT = "/api/v1/price-index"
TIMEOUT = 30

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RELEASES = os.path.join(DATA, "releases")

# The published schema, in order. Kept here rather than derived from the response
# so an added API field cannot silently change the shape of a file people parse.
COLUMNS = [
    "month",
    "avg_price_real",
    "avg_price_advertised",
    "median_price_real",
    "pct_on_discount",
    "pct_discount_over_90d",
    "median_discount_depth",
    "price_sample_n",
]


def fetch(url: str) -> dict | None:
    """The payload, or None when the API is unreachable or not serving yet."""
    req = urllib.request.Request(url, headers={"User-Agent": "creator-price-index-export"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[export] API returned HTTP {e.code}; nothing written.")
    except urllib.error.URLError as e:
        print(f"[export] API unreachable ({e.reason}); nothing written.")
    except (ValueError, TimeoutError) as e:
        print(f"[export] Could not read the API response ({e}); nothing written.")
    return None


def money(v) -> str:
    return "" if v is None else f"{float(v):.2f}"


def fraction(v) -> str:
    """The API reports percentages 0-100; the published files use fractions 0-1."""
    return "" if v is None else f"{float(v) / 100:.4f}"


def integer(v) -> str:
    return "" if v is None else str(int(v))


def row_for(point: dict, summary: dict | None) -> list[str]:
    """One CSV row. A missing value is written as an empty cell, never as a zero."""
    return [
        point.get("month", ""),
        money(point.get("avg_real")),
        money(point.get("avg_advertised")),
        money(point.get("median")),
        fraction(point.get("pct_on_discount")),
        fraction((summary or {}).get("pct_discount_over_90_days")),
        fraction((summary or {}).get("median_discount_depth")),
        # How many paid pages the price figures on this row were computed on.
        # The catalogue headcount is deliberately NOT published: it is a fact
        # about us, not about the market, and it is the number that gets lifted
        # out of context. The sample size is the one a reader needs.
        integer((summary or {}).get("price_n")),
    ]


def csv_text(rows: list[list[str]]) -> str:
    """The exact bytes write_csv would produce, for comparing against a file."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    w.writerows(rows)
    return buf.getvalue()


def write_csv(path: str, rows: list[list[str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(csv_text(rows))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-base", default=os.environ.get("LUVS_API_BASE", API_DEFAULT))
    args = ap.parse_args()

    base = args.api_base.rstrip("/")
    payload = fetch(base + ENDPOINT)
    if not payload:
        print("[export] The public API is not live yet. This is expected before launch.")
        return 0

    series = payload.get("series") or []
    if not series:
        print("[export] The API answered but published no releases; nothing written.")
        return 0

    # Per-month detail the series endpoint does not carry. One request per month,
    # pinned with ?release= so a past month is fetched exactly as it was frozen.
    rows: list[list[str]] = []
    for point in series:
        month = point.get("month")
        if not month:
            continue
        detail = fetch(f"{base}/api/v1/summary?release={month}") or {}
        merged = {**(detail.get("panel") or {}), **(detail.get("headline") or {})}
        disc = fetch(f"{base}/api/v1/discounts?release={month}") or {}
        merged.update({
            k: v for k, v in (disc.get("current") or {}).items()
            if k in ("pct_discount_over_90_days", "median_discount_depth")
        })
        rows.append(row_for(point, merged))

    write_csv(os.path.join(DATA, "price-index.csv"), rows)
    print(f"[export] Wrote data/price-index.csv ({len(rows)} months).")

    # Per-release files. A frozen release is not rewritten on a whim, but it IS
    # rewritten when the source has published a correction: the alternative is a
    # mirror that contradicts luvs.one about the same month, which is worse than
    # a change. Nothing changes quietly either way, because every rewrite lands
    # as its own commit and git log is the audit trail. (This is what happened to
    # 2026-07: exported here on Aug 3, recomputed upstream on Aug 20, and the
    # copy kept the pre-correction figures until this rule changed.)
    written = 0
    corrected = 0
    for row in rows:
        path = os.path.join(RELEASES, f"{row[0]}.csv")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                current = f.read()
            if current == csv_text([row]):
                continue
            write_csv(path, [row])
            corrected += 1
            print(f"[export] Corrected data/releases/{row[0]}.csv to match the source.")
            continue
        write_csv(path, [row])
        written += 1
    print(f"[export] Wrote {written} new release file(s), corrected {corrected}.")

    sample = os.path.join(DATA, "sample-2026-07.csv")
    if os.path.exists(sample):
        os.remove(sample)
        print("[export] Removed the placeholder sample: real data is published now.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
