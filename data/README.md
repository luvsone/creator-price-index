# data/

## Status: no real data published yet

The only file here is `sample-2026-07.csv`. It exists to show the column layout
and nothing else. **Every value in it is zero on purpose, so it cannot be mistaken
for a measurement and cannot be cited.**

Real data lands here once the public API is live:

| File | Contents |
|---|---|
| `price-index.csv` | The full monthly series, rewritten by the monthly job as new releases are frozen |
| `releases/YYYY-MM.csv` | One immutable file per release month, never edited after it is written |

`price-index.csv` is the convenient file. `releases/` is the citable one: a release
is computed once when the month closes and never revised, so a row in
`releases/2026-07.csv` will read the same in five years.

Column definitions, methodology and known limitations are in
[../CODEBOOK.md](../CODEBOOK.md).

## Reading the files

The sample carries `#` comment lines at the top. Real files will not, but passing
the comment character costs nothing either way:

```python
pd.read_csv('data/price-index.csv', comment='#')
```

```r
read.csv('data/price-index.csv', comment.char = '#')
```
