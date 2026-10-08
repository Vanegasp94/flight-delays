"""Round-1 sample of Codigo Justificativa: first 1,500,001 bytes of selected monthly files.

In the session this was done with HTTP range requests (``curl -r 0-1500000``)
against the ANAC server; here the same byte range is read from the local files.
Superseded by item3.py, which counts full files. Reconstructed from an inline
command run in the session (it was not saved as a file at the time).
"""

import collections

from _common import vra_path

for y, m in [(2010, 7), (2015, 7), (2019, 7), (2021, 7), (2023, 7), (2025, 7), (2026, 6)]:
    with open(vra_path(y, m), "rb") as fh:
        raw = fh.read(1500001)
    d = raw.decode("utf-8", "replace").splitlines()[2:-1]
    c = collections.Counter(line.split(";")[-1].strip('"') for line in d)
    print(f"-- {y}-{m:02d}:", len(d), "rows sampled;", c.most_common(8))
