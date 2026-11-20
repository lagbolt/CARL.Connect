#
# Looks up a catalog resource and prints physical or e-resource availability.
#
# Usage: python eresource-test.py
# Enter resource IDs interactively; submit a blank line to quit.
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
    create_resilient_session,
    get_resource,
)
from fcpl_shared.account import (
    ListItem,
    AvailabilitySummary,
    EresourceAvailability,
    get_eresource_availability,
)
from fcpl_shared.cli import run_cli

def main_logic(s, id):
    resource = get_resource(s, id)

    if not (host_bibliographic_id := resource.get("hostBibliographicId")):
        print("No hostBibliographicId found")
        return

    item = ListItem.from_resource(resource)
    print(item)
    
    if resource.get('holdingsInformations'):
        availability_summary = AvailabilitySummary.from_resource(resource)
        print(availability_summary)
    else:
        response = get_eresource_availability(s, id, host_bibliographic_id)
        eresource_availability = EresourceAvailability.from_response(response)
        print(eresource_availability)


def main():
    with create_resilient_session() as s:
        while id := input("Enter resource id: "):
            main_logic(s, id)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))

