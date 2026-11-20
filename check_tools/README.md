## MARC check tools

A set of command-line scripts that read a binary MARC file (`.mrc`) and report possible cataloging problems.

### Requirements

- Python 3.10 or newer
- The packages in `requirements.txt` (`pymarc` 5.0.0 or newer, `requests`,
  `rich` and `xmltodict`):

  ```
  pip install -r requirements.txt
  ```
Installing the fcpl_shared library also installs these dependencies.

### The scripts

| Script | What it checks |
|---|---|
| `check-records.py` | Runs a set of structural checks on each record and writes a detailed report. Problems are classified as serious, non-serious or warnings. |
| `check-language.py` | Checks language coding for consistency across the 008, 041, 240 $l, 546 and 700 fields, such as an 008 language code that disagrees with the 041. |
| `check-names.py` | Looks for possible duplicate author names in the 100 and 700 fields (for example, "Smith, Bob" and "Smith, Bob, 1972-"). Accents and case are ignored when names are compared. |
| `check-subjects.py` | Checks the 650 subject headings against lists of Library of Congress subject terms and children's subject terms, and prints records with headings that aren't in either list. |
| `check-series.py` | Looks up each record's author and title on Goodreads and compares the Goodreads series name with the series information in the 490 and 8XX fields. |

### Usage

Run any script with `--help` to see its options, for example:

```
python check-records.py --help
```

Each script also begins with a comment block that describes its options and
output in more detail.

### Supporting files

- `subject-terms.txt` and `childrens-terms.txt`: the term lists used by
  `check-subjects.py`. Keep them in the same folder as the script.
- `check-series.py` needs a Goodreads API key. Put it in a file named
  `local_secrets.py` (see `secrets_stub.py` for the format) and keep that file
  private. Without a key, the Goodreads comparison won't work.

### License

CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/

Graeme Williams  
carryonwilliams@gmail.com
