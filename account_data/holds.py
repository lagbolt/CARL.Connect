#
# Lists account holds with availability and hold queue information.
#
# Usage: python list_holds.py
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

import time

from fcpl_shared.common import (
    HTTP_HEADERS,
    BASEURL,
    create_resilient_session,
    get_json,
)
from fcpl_shared.account import (
    get_eresource_availability,
    ListItem,
    EresourceAvailability,
    AvailabilitySummary,
)
from fcpl_shared.cli import interactive_login, run_cli

def get_current_holds(s):
    holds = []
    start_index = 0
    max_items = 20

    while True:
        url = f"{BASEURL}/requests/{start_index}/{max_items}/Status"
        response_data = get_json(s, url)
        page_holds = response_data["holds"]
        if not page_holds:
            break

        holds.extend(page_holds)
        start_index += max_items

    return holds


def process_holds(s):
    for hold in get_current_holds(s):
        resource = hold["resource"]
        list_item = ListItem.from_resource(resource)
        resource_id = resource["id"]
        host_bib_id = resource["hostBibliographicId"]
        resource_format = resource["format"]

        print(list_item)
        if not resource_format.startswith("e"):
            print(AvailabilitySummary.from_resource(resource))
        print(hold_queue_length(s, resource_id, host_bib_id, resource_format))
        print()


def hold_queue_length(s, resource_id, host_bib_id, resource_format):
    if resource_format.startswith("e"):
        response_data = get_eresource_availability(s, resource_id, host_bib_id)
        return EresourceAvailability.from_response(response_data)

    url = (
        f"{BASEURL}/hostSystem/"
        f"getRealtimeHostRecordInformation/{host_bib_id}"
    )
    response_data = get_json(s, url)
    queue_length = response_data["totalPendingRequests"]
    return f"Hold queue length: {queue_length}"


def main():
    with create_resilient_session() as s:
        s.headers.update(HTTP_HEADERS)
        interactive_login(s)

        process_holds(s)

if __name__ == "__main__":
    raise SystemExit(run_cli(main))
