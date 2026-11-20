#
# Displays current loans, hold queue lengths, and availability.
#
# Usage: python current-loans.py
# Prompts interactively for the library account credentials.
# Version: 0.5.0  11/20/2026
#
#
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Graeme Williams  
# carryonwilliams
#

from fcpl_shared.common import (
    HTTP_HEADERS,
    BASEURL,
    create_resilient_session,
    get_json,
    )
from fcpl_shared.account import (
    AvailabilitySummary,
    EresourceAvailability,
    ListItem,
    get_eresource_availability,
)
from fcpl_shared.cli import interactive_login, run_cli

def get_current_loans(s):
    loans = []
    start_index = 0
    max_items = 20

    while True:
        url = f"{BASEURL}/loans/{start_index}/{max_items}/Status"
        response_data = get_json(s, url)
        page_loans = response_data["loans"]
        if not page_loans:
            break

        loans.extend(page_loans)
        start_index += max_items

    return loans

def main():
    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)
        interactive_login(s)
        current_loans = get_current_loans(s)
        print(f"Current loans: {len(current_loans)}")
        for loan in current_loans:
            resource = loan["resource"]
            list_item = ListItem.from_resource(resource)
            print(list_item)
            if "holdQueueLength" in loan:
                queue_length = loan["holdQueueLength"]
                print(f"Hold queue length: {queue_length}")
                availability_summary = AvailabilitySummary.from_resource(resource)
                print(availability_summary)
            else:  # e-resource
                response_data = get_eresource_availability(
                    s, resource["id"], resource["hostBibliographicId"]
                )
                eresource_availability = EresourceAvailability.from_response(response_data)
                print(eresource_availability)

if __name__ == "__main__":
    raise SystemExit(run_cli(main))
