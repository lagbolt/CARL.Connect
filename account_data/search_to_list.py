#
# Copy catalog search results to a private list.
#
# Usage: python search_to_list.py -q <query> -d <destination> [-b] [-e] [-c] [-l <limit>]
# Prompts interactively for the library account credentials.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
#

import argparse
from itertools import chain

from fcpl_shared.common import (
    HTTP_HEADERS,
    create_resilient_session,
    get_resource,
)
from fcpl_shared.account import (
    ListItem,
    add_list_item,
    create_and_add,
    delete_list_item,
    get_items_from_list,
    get_list_of_lists,
)
from fcpl_shared.cli import interactive_login, run_cli
from fcpl_shared.search import SearchPayload, build_facet_filters, iter_ids


def parse_args():
    parser = argparse.ArgumentParser(
        description="Copy catalog search results to a destination list."
    )
    parser.add_argument("-q", "--query", required=True, help="Catalog search query")
    parser.add_argument(
        "-b", "--books", action="store_true", help="Limit the search to books"
    )
    parser.add_argument(
        "-d", "--destination", required=True, help="Destination list name"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=20,
        help="Maximum number of titles to copy (default: 20)",
    )
    parser.add_argument(
        "-e", "--empty", action="store_true",
        help="Empty the destination list after confirming",
    )
    parser.add_argument(
        "-c", "--choose", action="store_true",
        help="Choose whether to copy each search result",
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

        payload = SearchPayload(
            search_term=args.query,
            facet_filters=build_facet_filters(book=args.books),
        )
        result_ids = iter_ids(session, payload, limit=args.limit)
        first_id = next(result_ids, None)
        if first_id is None:
            if args.limit == 0:
                print("The limit is zero; no list was created or changed.")
            else:
                print("The search returned no results; no list was created or changed.")
            return

        destination = next(
            (
                list_info
                for list_info in get_list_of_lists(session)
                if list_info.list_name == args.destination
            ),
            None,
        )
        if args.empty and destination is not None:
            if not confirm_empty(args.destination):
                print("Canceled; the destination list was not changed.")
                return

        first_item = ListItem.from_resource(get_resource(session, first_id))
        if args.empty and destination is not None:
            for existing_item in get_items_from_list(session, destination):
                delete_list_item(session, destination, existing_item)

        copied_count = 0
        list_items = chain(
            (first_item,),
            (
                ListItem.from_resource(get_resource(session, item_id))
                for item_id in result_ids
            ),
        )
        for list_item in list_items:
            if args.choose and not should_copy(list_item):
                continue
            if destination is None:
                destination = create_and_add(session, args.destination, list_item)
            else:
                add_list_item(session, destination, list_item)
            copied_count += 1
            print(f"Copied: {list_item.short_title}")

    print(f"Copied {copied_count} title(s) to {args.destination}.")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
