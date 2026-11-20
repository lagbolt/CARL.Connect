#
# Remove duplicate catalog items across the user's lists.
#
# Usage: python remove_duplicates.py [-d/--dryrun]
# Prompts interactively for the library account credentials.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
#

import argparse

from fcpl_shared.common import HTTP_HEADERS, create_resilient_session
from fcpl_shared.account import (
    delete_list_item,
    get_items_from_list,
    get_list_of_lists,
)
from fcpl_shared.cli import interactive_login, run_cli


def main():
    parser = argparse.ArgumentParser(description="Remove duplicate items from lists.")
    parser.add_argument(
        "-d", "--dryrun", action="store_true",
        help="Report duplicate items without deleting them",
    )
    args = parser.parse_args()

    already_seen = set()
    removed_count = 0
    with create_resilient_session() as session:
        session.headers.update(HTTP_HEADERS)
        interactive_login(session)
        lists = get_list_of_lists(session)

        for list_info in lists:
            for list_item in get_items_from_list(session, list_info):
                if list_item.item_id in already_seen:
                    action = "Would delete" if args.dryrun else "Deleting"
                    print(f"Duplicate found: {list_item} in {list_info}; {action.lower()}")
                    if not args.dryrun:
                        delete_list_item(session, list_info, list_item)
                    removed_count += 1
                else:
                    already_seen.add(list_item.item_id)

    outcome = "would be removed" if args.dryrun else "removed"
    print(f"{removed_count} duplicate item(s) {outcome}.")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
