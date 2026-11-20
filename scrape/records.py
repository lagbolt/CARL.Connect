#
#    Extract MARC records from the FCPL catalog based on a text-format search query.
#    Allows for extracting the first N records, a random sample of N records within
#    a specified range, or counting the total number of hits. Can optionally filter
#    results to only include books or titles from the last two weeks.
#
#    Usage:  python records.py
#                -q <query>
#                (-r [<n>] | -f [<n>] | -c)
#                [ -o <output file> ]
#                [ -s <start> ]
#                [ -e <end> ]
#                [ -b ]
#                [ -l ]
#
#    The output file is written as a binary MARC file. The output file defaults 
#    to output-records.mrc.
#
#    The -s and -e options are required if and only if the -r option is used.
#    The options define the range from which the random records will be selected.
#
#    The -b option filters the search results to only include books.
#
#    The -l option filters the search results to only include titles from the
#    last two weeks.
#
#    The -c option counts the total number of hits for the query and exits.
#    The -o option is ignored if -c is used - no records are written,
#
#    If you find yourself wishing for different functionality, please email me.
#
#    Version:  0.5.0  11/20/2026
#
#
# Edited by ChatGPT.
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import argparse

import pymarc
from fcpl_shared.common import HTTP_HEADERS, create_resilient_session
from fcpl_shared.cli import run_cli
from fcpl_shared.marc import bulk_marc_gen, random_marc_gen
from fcpl_shared.search import SearchPayload, build_facet_filters, search_hit_count


def main():
    """Main program handling command-line arguments, some consistency checking, and calling
       the top-level functions."""

    parser = argparse.ArgumentParser(description="Extract MARC records from the FCPL catalog.")

    parser.add_argument("-o", "--output", default="output-records.mrc", help="Output MARC file (default: output-records.mrc)")
    parser.add_argument("-q", "--query", required=True, help="Search query (simple text or JSON string)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", "--random", type=int, nargs="?", const=5, help="Number of random records to extract (default: 5)")
    group.add_argument("-f", "--first", type=int, nargs="?", const=5, help="Number of sequential records to extract starting from zero (default: 5)")
    group.add_argument("-c", "--count", action="store_true", help="Count the total number of records matching the query")

    parser.add_argument("-s", "--start", type=int, help="Start of the random range")
    parser.add_argument("-e", "--end", type=int, help="End of the random range")

    parser.add_argument("-b", "--book", action="store_true", help="Filter results to only include books")
    parser.add_argument("-l", "--lasttwoweeks", action="store_true", help="Only include titles from the last two weeks")

    args = parser.parse_args()

    if args.random is not None and args.random < 0:
        parser.error("--random count must be non-negative.")
    if args.first is not None and args.first < 0:
        parser.error("--first count must be non-negative.")

    if args.random is not None:
        if args.start is None or args.end is None:
            parser.error("--start (-s) and --end (-e) are required when using --random (-r).")

    search = SearchPayload(
        args.query,
        facet_filters=build_facet_filters(book=args.book, last_two_weeks=args.lasttwoweeks),
    )

    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)

        count_result = search_hit_count(s, search)

        if count_result == 0:
            print(f"No records found matching the query '{args.query}'. Exiting.")
            return
        print(f"Found {count_result} records matching the query '{args.query}'.")

        if not args.count:
            if args.random is not None:
                if args.start < 0 or args.end < 0 or args.start > args.end:
                    parser.error("Invalid range: start and end must be non-negative and start must be less than or equal to end.")
                if args.start >= count_result:
                    print(f"Start index {args.start} is out of bounds. Total records: {count_result}.  Exiting.")
                    return
                if args.end >= count_result:
                    print(f"End index {args.end} is out of bounds. Adjusting to {count_result - 1}.")
                    args.end = count_result - 1

                total_possible = (args.end - args.start) + 1
                if args.random > total_possible:
                    print(f"Requested {args.random} random records, but only {total_possible} available in the range.")
                    print(f"Adjusting request to {total_possible} random records.")
                    args.random = total_possible

                print(f"Extracting {args.random} random records from range {args.start}-{args.end}...")
                record_generator = random_marc_gen(s, search, args.random, args.start, args.end)

            else:
                if args.first > count_result:
                    print(f"Requested {args.first} records, but only {count_result} available.")
                    print(f"Adjusting request to {count_result} records.")
                    args.first = count_result

                print(f"Extracting the first {args.first} sequential records...")
                record_generator = bulk_marc_gen(s, search, args.first)

            print(f"Writing records to {args.output}...")
            with open(args.output, "wb") as out_file:
                writer = pymarc.MARCWriter(out_file)
                for index, record in enumerate(record_generator):
                    if record:
                        writer.write(record)
                        if (index + 1) % 60 == 0:
                            print(".", end="", flush=True)
                writer.close()

            print("Done!")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
