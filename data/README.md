# data/

| File | Contents |
|---|---|
| `price-index.csv` | The full monthly series, rewritten by the monthly job as new releases are frozen |
| `releases/YYYY-MM.csv` | One file per release month |

`price-index.csv` is the convenient file. `releases/` is the citable one: a release
is computed once when the month closes, so a row in `releases/2026-07.csv` reads
the same whenever someone follows a citation to it.

A release file is rewritten in exactly one case: the source published a correction
to that month, which luvs.one records in its own changelog. Mirroring a correction
is not the same as revising history quietly, and it beats the alternative, which is
a copy here that contradicts the source about the same month. Every such rewrite is
a separate commit, so `git log` shows what changed and when.

Column definitions, methodology and known limitations are in
[../CODEBOOK.md](../CODEBOOK.md).

## Reading the files

The files carry no comment lines, but passing the comment character costs nothing
and makes a reader robust to one being added:

```python
pd.read_csv('data/price-index.csv', comment='#')
```

```r
read.csv('data/price-index.csv', comment.char = '#')
```
