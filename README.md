# Talking to CARL•Connect

This repository contains five sets of utilities, each in their own directory, supported by a shared library.  The code in each directory is independent of the other directories (other than the shared library), but they share a common theme:  retrieving and processing data from CARL•Connect in various ways.

The programs target the [FCPL catalog](https://catalog.fcpl.org/) by default. To target another catalog with a
compatible API, change `BASEURL` in `fcpl_shared/common.py`.

## Programs by directory

### `check_tools`

Programs that inspect binary MARC files and report potential cataloging issues.

| Program | Description |
|---|---|
| `check-language.py` | Checks language coding for consistency across MARC fields. |
| `check-names.py` | Finds possible duplicate author names in 100 and 700 fields. |
| `check-records.py` | Runs structural checks against each record in a MARC file. |
| `check-series.py` | Compares Goodreads series information with series fields in MARC records. |
| `check-subjects.py` | Checks 650 subject headings against the supplied subject-term lists. |

Run a program with `--help` for its options. `check-series.py` requires a
Goodreads API key configured in `local_secrets.py`.

### `compare_searches`

Programs that compare FCPL catalog hit counts for search terms and subject matches.

| Program | Description |
|---|---|
| `single-terms.py` | Runs three searches for each interactively entered term. |
| `multiple-terms.py` | Searches up to three interactively entered terms and their combinations. |

### `fcpl_shared`

Installable Python package containing shared catalog and account functionality.

| Module | Description |
|---|---|
| `account.py` | Login, saved-list, loan-history, and availability operations. |
| `cli.py` | Shared console, reporting, interactive-login, and CLI error helpers. |
| `common.py` | Unicode normalization, resilient sessions, HTTP helpers, and resource retrieval. |
| `marc.py` | Retrieves MARC records and provides sequential and random record generators. |
| `search.py` | Builds catalog searches and retrieves hit counts and search results. |

To install the package and its declared prerequisites, run this from the
repository root — the directory which contains `pyproject.toml`:

```
pip install --force-reinstall .
```

`--force-reinstall` reinstalls the local package even when its version number
has not changed.

## Pacing of Network Requests

The shared library waits 5 seconds between catalog requests by default. This
delay is also used as the backoff factor for retries after transient failures.

To change the delay, call `set_delay(seconds)` before creating a session:

```python
from fcpl_shared.common import create_resilient_session, set_delay

set_delay(2)
with create_resilient_session() as session:
    ...
```

Changing the delay during a session affects subsequent request pacing and
`post_json` retries. It does not change the retry backoff factor already
configured in that session's HTTP adapters. Create a new session for the new backoff delay to take effect.

### `account_data`

Programs for viewing and managing information in a library account.

| Program | Description |
|---|---|
| `copy_list.py` | Copies items from one saved list to another. |
| `current-loans.py` | For each current loan, display author, title, hold number, and availability. |
| `delete_loaned.py` | Removes from lists items that appear in loan history. |
| `eresource-test.py` | Looks up a catalog resource and displays physical or e-resource availability. |
| `holds.py` | Displays account holds with availability and hold queue information. |
| `lists.py` | Displays saved lists and can report their items and publication-date counts. |
| `remove_duplicates.py` | Removes duplicate items across saved lists. |
| `search-loans.py` | Searches loan history. |
| `search_to_list.py` | Copies catalog search results to a saved list. |

Programs that access private account data prompt for login credentials.

### `new_records`

| Program | Description |
|---|---|
| `scan-current.py` | Scans recently added titles, tracks their status in SQLite, and writes completed MARC records to an output file. |

### `scrape`

| Program | Description |
|---|---|
| `records.py` | Retrieves consecutive MARC records for a catalog search, samples a range, or counts hits. |

## License and contact

Unless otherwise noted, these tools are licensed under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Graeme Williams  
[carryonwilliams@gmail.com](mailto:carryonwilliams@gmail.com)
