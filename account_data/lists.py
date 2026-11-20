#
# Display account lists and optionally report their items and publication dates.
#
# Usage: python lists.py [options]
#   -p, --print-lists       Print the list of lists
#   -i, --print-items [LIST_NAME ...]  Print all lists' items or only named lists
#   -t, --print-date-counts Print publication date counts
# Version: 0.5.0  11/20/2026
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
# carryonwilliams@gmail.com
# Edited by: Antigravity
# Edited by ChatGPT.
#

import argparse
from collections import Counter

from fcpl_shared.common import (
    HTTP_HEADERS,
    create_resilient_session,
)
from fcpl_shared.account import (
    get_list_of_lists,
    get_items_from_list,
)
from fcpl_shared.cli import interactive_login, run_cli

def main():
    parser = argparse.ArgumentParser(description="FCPL List Information")
    parser.add_argument('-p', '--print-lists', action='store_true', help="Print the list of lists")
    parser.add_argument(
        '-i', '--print-items', nargs='*', metavar='LIST_NAME', default=None,
        help="Print items for all lists, or only the named lists",
    )
    parser.add_argument('-t', '--print-date-counts', action='store_true', help="Print publication date counts")
    args = parser.parse_args()

    dates = Counter()  # count of publication dates

    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)

        # Step 1: Login
        interactive_login(s)
        print("Login successful\n")

        # Step 2: Get count of lists
        list_of_lists = get_list_of_lists(s)
        print(f"Count of lists: {len(list_of_lists)}\n")
        if args.print_lists:
            print(*list_of_lists, sep="\n")

        if args.print_items is None and not args.print_date_counts:
            return

        lists_to_process = list_of_lists
        if args.print_items:
            lists_by_name = {list_info.list_name: list_info for list_info in list_of_lists}
            missing_names = [
                name for name in args.print_items if name not in lists_by_name
            ]
            if missing_names:
                raise RuntimeError(
                    "List not found: " + ", ".join(missing_names)
                )
            lists_to_process = [lists_by_name[name] for name in args.print_items]

        # Step 4: scan each list in the list of lists
        for list_info in lists_to_process:
            list_of_items = get_items_from_list(s, list_info)  # list of tuples

            if args.print_items is not None:
                print(f"\n{list_info}")
                print(*list_of_items, sep="\n")

            # count dates
            for list_item in list_of_items:
                dates[list_item.pub_date] += 1

    # print date counts
    if args.print_date_counts:
        for date, count in sorted(dates.items()):
            print(f"{date}: {count}")

if __name__ == '__main__':
    raise SystemExit(run_cli(main))
