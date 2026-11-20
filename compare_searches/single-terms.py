#
# Runs three catalog searches for one term and reports each hit count.
#
# Usage: python single-terms.py
# Enter search terms at the prompt; submit a blank line to quit.
#
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Graeme Williams  
# carryonwilliams
#

from fcpl_shared.common import HTTP_HEADERS, create_resilient_session
from fcpl_shared.cli import run_cli
from fcpl_shared.search import count_hits

def make_search_list(search_term):
    """Returns a list of search terms to use for the search."""
    return [
        search_term,
        f"su:{search_term}",
        f"{search_term} AND NOT su:{search_term}"
    ]

def main():
    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)
        while term := input("Term: "):
            search_list = make_search_list(term)
            for term in search_list:
                hits = count_hits(s,term)
                print(f"Search term: {term}, Hits: {hits}")

if __name__ == "__main__":
    raise SystemExit(run_cli(main))
