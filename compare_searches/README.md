## FCPL search-term hit counters

Two small command-line scripts that report how many records in the FCPL catalog match a search term,
combined in different ways so you can see how many of those matches come from the term appearing as
a subject (`su:`) and how many come from elsewhere in the record.

The scripts target FCPL by default. To target another catalog with a
compatible API, change `BASEURL` in `fcpl_shared/common.py`.

| Script | What it does |
|---|---|
| `single-terms.py` | Takes one term at a time and runs 3 searches for it. |
| `multiple-terms.py` | Takes up to three terms and runs searches for each term and for the ways the terms combine (AND, OR, AND NOT). |

### Requirements

- Python 3.10 or newer
- The `fcpl-shared` library, which supplies the catalog search code and installs
`requests` as a dependency:

### single-terms.py

```
python single-terms.py
```

Type a term at the `Term:` prompt. The script runs three searches and prints the
hit count for each:

1. the term by itself
2. `su:` the term, meaning a subject search
3. the term `AND NOT su:` the term, meaning matches that are not subject matches

Enter a blank line to quit.

Example (hit counts are made up for illustration; yours will differ):

```
Term: dogs
Search term: dogs, Hits: 1200
Search term: su:dogs, Hits: 410
Search term: dogs AND NOT su:dogs, Hits: 790
Term: 
```

### multiple-terms.py

```
python multiple-terms.py
```

Enter up to three terms, one per line, then a blank line to run the searches.
Enter `q` or `Q` at any time to quit. A fourth term is ignored with a warning.
After the searches finish, you can enter another set of terms.

The number of searches depends on how many terms you enter:

| Terms | Searches |
|---|---|
| 1 | 3 (the same three as `single-terms.py`) |
| 2 | 13 |
| 3 | 39 (duplicate searches are removed) |

With two terms, the searches cover each term alone, `AND`, `OR`, each term
`AND NOT` the other, subject searches, and the matches that remain after
subject matches are excluded.

Example with two terms (hit counts are made up for illustration; yours will
differ, and the middle of the list is shortened here):

```
Enter up to three search terms, one per line.
Enter a blank line when you're done entering terms to run the searches.
Enter 'q' or 'Q' at any time to quit.
Term: dogs
Term: cats
Term: 
Starting 13 searches for: dogs, cats
Search term: dogs, Hits: 1200
Search term: cats, Hits: 900
Search term: dogs AND cats, Hits: 150
Search term: dogs OR cats, Hits: 1950
Search term: dogs AND NOT cats, Hits: 1050
Search term: cats AND NOT dogs, Hits: 750
Search term: su:dogs, Hits: 410
Search term: su:cats, Hits: 300
...
Search term: (dogs OR cats) AND NOT su:dogs AND NOT su:cats, Hits: 1340
Term: q
```

Each search is a separate request to the catalog, with a delay between each request, so a three-term run takes a
little longer than a one-term run.

## License

CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/

Graeme Williams  
carryonwilliams@gmail.com
