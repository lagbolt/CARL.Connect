## Collect MARC records from the FCPL catalog

`records.py` retrieves MARC records from the [FCPL catalog](https://catalog.fcpl.org/)
for a search query. It can retrieve the first N results, select a random sample
within a specified range, or count the total number of hits. Searches can also
be limited to books, titles added in the last two weeks, or both.

The program targets FCPL by default. To target another catalog with a
compatible API, change `BASEURL` in `../fcpl_shared/common.py`.

### Requirements and installation

The program uses `pymarc` and the shared `fcpl_shared` library. From the
repository root (the directory containing `pyproject.toml`), install the shared
package and its prerequisites with:

```bash
pip install --force-reinstall .
```

### Usage

Run the program from this directory. Its query and retrieval-mode options are
required; run the following to see all options and defaults:

```bash
python records.py --help
```

### License and contact

CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/

Graeme Williams  
carryonwilliams@gmail.com
