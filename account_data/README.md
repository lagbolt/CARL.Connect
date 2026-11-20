# Account tools

These command-line programs display and manage information from your account
in the [FCPL catalog](https://catalog.fcpl.org/). Programs that access private
account data prompt for login credentials.

These programs target FCPL by default. To target another catalog with a
compatible API, change `BASEURL` in `../fcpl_shared/common.py`.

See each program's usage notes at the top of its source file. Programs with
command-line option parsers also accept `--help`.

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

## License and contact

CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/

Graeme Williams  
carryonwilliams@gmail.com
