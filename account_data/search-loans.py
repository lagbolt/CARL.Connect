#
# Search the user's loan history for entered words.
#
# Usage: python search-loans.py
# Prompts for search words and treats them as if joined with AND.
# Version: 0.5.0  11/20/2026
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
# carryonwilliams@gmail.com
# Edited by: Antigravity
# Edited by ChatGPT.
#

from fcpl_shared.common import HTTP_HEADERS, create_resilient_session
from fcpl_shared.account import ListItem, get_loan_history
from fcpl_shared.cli import interactive_login, run_cli

def find_matches(matches, search_items):
    # We're relying on __str__ in ListItem
    search_strings = [ str(item) for item in search_items ]
    matches_casefolded = [word.casefold() for word in matches]
    return [
        s for s in search_strings
        if all(word in s.casefold() for word in matches_casefolded)
        ]


def main():

    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)
        interactive_login(s)
        print("Login successful\nWait for loan history to be loaded ... ", end="", flush=True)
        loan_history = get_loan_history(s)

    while (match := input("Search for: ")):
        search_terms = match.split()
        if not search_terms:
            print("Warning: Enter at least one search term.")
            continue
        matches = find_matches(search_terms, loan_history)
        if matches:
            for m in matches:
                print(m)
        else:
            print("No results")


if __name__ == '__main__':
    raise SystemExit(run_cli(main))
