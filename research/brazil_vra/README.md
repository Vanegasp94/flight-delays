# Brazil ANAC VRA research

Scripts behind [`docs/research/brazil-vra.md`](../../docs/research/brazil-vra.md).
That document has the findings, the source URLs, what was not verified, and a
reproduction section listing the run order and expected output.

- `scripts/_common.py` - data directory configuration and loaders.
- `scripts/download.py` - fetches the source files from the original URLs.
- `scripts/*.py` - one script per check; each prints its results and writes
  nothing.

Data directory: `BRAZIL_VRA_DATA_DIR` (default `data/research/brazil_vra`,
git-ignored).

```bash
uv run python research/brazil_vra/scripts/download.py
uv run python research/brazil_vra/scripts/tz1.py
```
