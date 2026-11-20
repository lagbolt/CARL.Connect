## Collect recently cataloged titles

`scan-current.py` searches the [FCPL catalog](https://catalog.fcpl.org/) for
recently added titles and tracks them in an SQLite database. All-uppercase
titles are treated as temporary records for titles that have been ordered but
have not arrived. Mixed-case titles are treated as fully cataloged; their MARC
records are written to the output file. The database prevents already
processed records from being written again and tracks titles that move from
temporary to fully cataloged.

The program targets FCPL by default. To target another catalog with a
compatible API, change `BASEURL` in `../fcpl_shared/common.py`.

### Requirements

- Python 3.10 or newer
- The `fcpl_shared` package and its prerequisites. See
  [its README](../fcpl_shared/README.md) for installation instructions.

### Usage

```bash
python scan-current.py [-o <MARC output file>] [-q <search term>]
```

- `-o`, `--output`: MARC output path. Defaults to `new-records.mrc` beside the
  script.
- `-q`, `--query`: catalog search query. Defaults to
  `callnumber:%/[A-Za-z0-9]/`, a query intended to return all records in the
  catalog. The program also applies book and last-two-weeks facet filters.

Run `python scan-current.py --help` for the options. The program prints
database status summaries before and after the scan, along with counts of the
operations performed.

### Files

- `new-titles.db`: SQLite database beside the script. It is created if missing
  and contains the `new_titles` table, with `Pending`, `New`, and `Done` status
  values.
- `new-records.mrc`: default MARC output file, written beside the script unless
  `-o` specifies another path.

### `runner.bat`

On Windows, `runner.bat` creates a timestamped `run_...` directory, runs
`scan-current.py` to write new records to `new-records.mrc`, then runs the programs in
`../check_tools` on that MARC file and saves their reports in the same run
directory. The Goodreads series check requires a configured API key; see
the `check_tools` README for setup instructions.

## License and contact

CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/

Graeme Williams  
carryonwilliams@gmail.com
