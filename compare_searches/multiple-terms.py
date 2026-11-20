#
# Runs catalog searches for up to three terms and their combinations,
# reporting total and subject-match hit counts.
#
# Usage: python multiple-terms.py
# Search terms are collected interactively from the user.
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

def make_pairwise_list(term_a, term_b):
    """Returns the 13-search pattern for two root terms."""
    return [
        term_a,
        term_b,
        f"{term_a} AND {term_b}",
        f"{term_a} OR {term_b}",
        f"{term_a} AND NOT {term_b}",
        f"{term_b} AND NOT {term_a}",
        f"su:{term_a}",
        f"su:{term_b}",
        f"{term_a} AND NOT su:{term_a}",
        f"{term_b} AND NOT su:{term_b}",
        f"{term_a} AND NOT su:{term_a} AND NOT su:{term_b}",
        f"{term_b} AND NOT su:{term_a} AND NOT su:{term_b}",
        f"({term_a} OR {term_b}) AND NOT su:{term_a} AND NOT su:{term_b}",
    ]

def make_three_term_list(term_a, term_b, term_c):
    """Returns the 18-search direct extension for three root terms,
    followed by the 13-search pairwise list for each of the three pairs
    (57 searches total)."""
    su_exclusions = " ".join(
        f"AND NOT su:{t}" for t in (term_a, term_b, term_c)
    )
    direct = [
        term_a,
        term_b,
        term_c,
        f"{term_a} AND {term_b} AND {term_c}",
        f"{term_a} OR {term_b} OR {term_c}",
        f"{term_a} AND NOT ({term_b} OR {term_c})",
        f"{term_b} AND NOT ({term_a} OR {term_c})",
        f"{term_c} AND NOT ({term_a} OR {term_b})",
        f"su:{term_a}",
        f"su:{term_b}",
        f"su:{term_c}",
        f"{term_a} AND NOT su:{term_a}",
        f"{term_b} AND NOT su:{term_b}",
        f"{term_c} AND NOT su:{term_c}",
        f"{term_a} {su_exclusions}",
        f"{term_b} {su_exclusions}",
        f"{term_c} {su_exclusions}",
        f"({term_a} OR {term_b} OR {term_c}) {su_exclusions}",
    ]
    pairwise = (
        make_pairwise_list(term_a, term_b)
        + make_pairwise_list(term_a, term_c)
        + make_pairwise_list(term_b, term_c)
    )
    return direct + pairwise

def build_search_list(terms):
    """Dispatches to the appropriate list-builder based on how many
    terms were collected, then removes duplicate search strings while
    preserving the order in which they first appear."""
    if len(terms) == 1:
        raw_search_list = make_search_list(terms[0])
    elif len(terms) == 2:
        raw_search_list = make_pairwise_list(terms[0], terms[1])
    else:
        raw_search_list = make_three_term_list(terms[0], terms[1], terms[2])
    return list(dict.fromkeys(raw_search_list))

def collect_terms():
    """Collects up to three terms from the user, one per line, stopping
    on a blank line. A fourth (or later) term triggers a warning and is
    ignored. Returns None if the user quits with 'q' or 'Q'."""
    terms = []
    while True:
        term = input("Term: ")
        if term in ("q", "Q"):
            return None
        if term == "":
            return terms
        if len(terms) >= 3:
            print("Only three terms are supported; ignoring this entry.")
            continue
        terms.append(term)

def main():
    print(
        "Enter up to three search terms, one per line.\n"
        "Enter a blank line when you're done entering terms to run the searches.\n"
        "Enter 'q' or 'Q' at any time to quit."
    )
    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)
        while True:
            terms = collect_terms()
            if terms is None:
                break
            if not terms:
                continue
            search_list = build_search_list(terms)
            print(f"Starting {len(search_list)} searches for: {', '.join(terms)}")
            for term in search_list:
                hits = count_hits(s, term)
                print(f"Search term: {term}, Hits: {hits}")

if __name__ == "__main__":
    raise SystemExit(run_cli(main))
