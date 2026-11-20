#
# Remove list items that appear in the user's loan history.
#
# Usage: python delete_loaned.py [--dry-run]
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
    get_loan_history,
)
from fcpl_shared.cli import interactive_login, run_cli


def parse_args():
    parser = argparse.ArgumentParser(
        description="Remove list items that appear in loan history."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report matching items without deleting them",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    with create_resilient_session() as session:
        session.headers.update(HTTP_HEADERS)
        interactive_login(session)
        loaned_item_ids = {item.item_id for item in get_loan_history(session)}
        lists = get_list_of_lists(session)

        matched_count = 0
        for list_info in lists:
            for list_item in get_items_from_list(session, list_info):
                if list_item.item_id not in loaned_item_ids:
                    continue
                matched_count += 1
                action = "Would delete" if args.dry_run else "Deleting"
                print(f"{action}: {list_item} from {list_info}")
                if not args.dry_run:
                    delete_list_item(session, list_info, list_item)

    outcome = "would be deleted" if args.dry_run else "deleted"
    print(f"{matched_count} loaned item(s) {outcome}.")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
