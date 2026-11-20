#
# Copy items from one catalog list to another.
#
# Usage: python copy_list.py -s <source> -d <destination> [-e] [-c] [-l <limit>]
# Prompts interactively for the library account credentials.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
#

import argparse

from fcpl_shared.common import HTTP_HEADERS, create_resilient_session
from fcpl_shared.account import (
    add_list_item,
    create_and_add,
    delete_list_item,
    get_items_from_list,
    get_list_of_lists,
)
from fcpl_shared.cli import interactive_login, run_cli


def parse_args():
    parser = argparse.ArgumentParser(description="Copy items between catalog lists.")
    parser.add_argument("-s", "--source", required=True, help="Source list name")
    parser.add_argument(
        "-d", "--destination", required=True, help="Destination list name"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=20,
        help="Maximum number of items to copy (default: 20)",
    )
    parser.add_argument(
        "-e", "--empty", action="store_true",
        help="Empty the destination list after confirming",
    )
    parser.add_argument(
        "-c", "--choose", action="store_true",
        help="Choose whether to copy each item",
    )
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be zero or greater")
    return args


def should_copy(list_item):
    print(list_item)
    answer = input("Copy this item? [y/N] ").strip().casefold()
    return answer in {"y", "yes"}


def confirm_empty(list_name):
    answer = input(
        f"Empty destination list '{list_name}'? This removes all its items. Type 'yes' to confirm: "
    ).strip().casefold()
    return answer == "yes"


def main():
    args = parse_args()

    with create_resilient_session() as session:
        session.headers.update(HTTP_HEADERS)
        interactive_login(session)

        lists = get_list_of_lists(session)
        source = next(
            (list_info for list_info in lists if list_info.list_name == args.source),
            None,
        )
        if source is None:
            raise RuntimeError(f"Source list not found: {args.source}.")

        destination = next(
            (
                list_info
                for list_info in lists
                if list_info.list_name == args.destination
            ),
            None,
        )
        if destination is not None and destination.list_id == source.list_id:
            print("Source and destination are the same list; nothing was copied.")
            return

        if args.empty and destination is not None:
            if not confirm_empty(args.destination):
                print("Canceled; the destination list was not changed.")
                return
            for existing_item in get_items_from_list(session, destination):
                delete_list_item(session, destination, existing_item)

        copy_count = min(args.limit, source.list_size)
        items = (
            get_items_from_list(session, source._replace(list_size=copy_count))
            if copy_count
            else []
        )

        copied = 0
        for list_item in items:
            if args.choose and not should_copy(list_item):
                continue
            if destination is None:
                destination = create_and_add(session, args.destination, list_item)
            else:
                add_list_item(session, destination, list_item)
            copied += 1
            print(f"Copied: {list_item.short_title}")

        if destination is None and not items:
            print(
                "No items to copy; a new destination list requires an item "
                "to create it."
            )
            return

    print(f"Copied {copied} item(s) from {args.source} to {args.destination}.")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
