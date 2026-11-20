#
# Catalog account, list, loan, and availability operations.
#
# Usage: Import these functions and pass an authenticated requests session.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
#

import time
from typing import NamedTuple

from .common import BASEURL, get_delay, get_json, post_json


def pub_date(raw_item):
    """Return the publication date from a catalog resource, or a default."""
    embedded_dict = raw_item.get("publicationDate", {})
    return embedded_dict.get("publicationDate", "0000")


class ListItem(NamedTuple):
    item_id: str
    short_title: str = "Dummy Title"
    short_author: str = "Dummy Author"
    pub_date: str = "0000"
    format: str = ""

    @classmethod
    def from_resource(cls, resource):
        return cls(
            item_id=resource["id"],
            short_title=resource.get("shortTitle", "Missing Title"),
            short_author=resource.get("shortAuthor", "Missing Author"),
            pub_date=pub_date(resource),
            format=resource.get("format", ""),
        )

    def __str__(self):
        return (
            f"({self.item_id}) {self.short_title} by {self.short_author} "
            f"({self.pub_date}) ({self.format})"
        )


class ListInfo(NamedTuple):
    list_name: str
    list_id: str
    list_size: int

    def __str__(self):
        return f"{self.list_name} ({self.list_id}) {self.list_size} items"


_local_branch_name = "C. Burr Artz"  # fixed for now


class AvailabilitySummary(NamedTuple):
    local_avail: int = 0
    local_total: int = 0
    other_avail: int = 0
    other_total: int = 0

    @classmethod
    def from_resource(cls, resource):
        if (holdings := resource.get("holdingsInformations")):
            local_avail = local_total = other_avail = other_total = 0
            for holding in holdings:
                if holding["branchName"] == _local_branch_name:
                    if holding["onshelf"]:
                        local_avail += 1
                    local_total += 1
                else:
                    if holding["onshelf"]:
                        other_avail += 1
                    other_total += 1
            return cls(local_avail, local_total, other_avail, other_total)
        return None

    def __str__(self):
        return (
            f"{_local_branch_name}: {self.local_avail}/{self.local_total}, "
            f"Other: {self.other_avail}/{self.other_total}"
        )


class EresourceAvailability(NamedTuple):
    copies_owned: int = 0
    copies_available: int = 0
    number_of_holds: int = 0

    @classmethod
    def from_response(cls, response):
        availability = response[0]["availabilitySources"][0]
        return cls(
            copies_owned=availability["copiesOwned"],
            copies_available=availability["copiesAvailable"],
            number_of_holds=availability["numberOfHolds"],
        )

    def __str__(self):
        return (
            f"Owned: {self.copies_owned}, Available: {self.copies_available}, "
            f"Holds: {self.number_of_holds}"
        )


def post_account_json(s, url, payload, retries=0):
    """Send an account POST through the shared JSON request helper."""
    return post_json(s, url, payload, retries=retries)


def _require_success(response_data, operation):
    if not isinstance(response_data, dict) or response_data.get("success") is not True:
        raise RuntimeError(f"Catalog did not confirm that it could {operation}.")


def delete_list_item(s, list_info, list_item):
    # print(f"Deleting item {list_item} from list {list_info}")
    url = f"{BASEURL}/list/static/{list_info.list_id}/remove"
    payload = [list_item.item_id]  # book id, not list id
    response_data = post_account_json(s, url, payload)
    time.sleep(get_delay())
    _require_success(response_data, "delete the list item")


def add_list_item(s, list_info, list_item):
    # print(f"Adding item {list_item} to list {list_info}")
    url = f"{BASEURL}/list/static/{list_info.list_id}/add"
    payload = [list_item.item_id]  # book id, not list id
    response_data = post_account_json(s, url, payload)
    time.sleep(get_delay())
    _require_success(response_data, "add the list item")


def create_and_add(s, list_name, list_item):
    url = f"{BASEURL}/list/static"
    payload = {
        "scope": "Private",
        "name": list_name,
        "resourceIds": [list_item.item_id],
    }
    response_data = post_account_json(s, url, payload)
    time.sleep(get_delay())
    _require_success(response_data, "create the list")
    list_id = response_data.get("id")
    if not list_id:
        raise RuntimeError("Catalog created the list but did not return its ID.")
    return ListInfo(list_name, list_id, 1)


def delete_list(s, list_info):
    url = f"{BASEURL}/lists/delete"
    payload = {"listIds": [list_info.list_id]}
    response_data = post_account_json(s, url, payload)
    time.sleep(get_delay())
    # slightly different response format
    if (
        not isinstance(response_data, list)
        or not response_data
        or not isinstance(response_data[0], dict)
        or response_data[0].get("success") is not True
    ):
        raise RuntimeError("Catalog did not confirm that it could delete the list.")


# This API supports either barcode/last name or username/password.
def login(s, name_or_code, password):
    login_url = f"{BASEURL}/login"
    payload = {
        "username": name_or_code,
        "lastName": password,
        "rememberMe": False,
        "": "Cancel",
        "password": password,
    }
    response_data = post_account_json(s, login_url, payload)
    time.sleep(get_delay())
    _require_success(response_data, "log in")


def get_list_count(s):
    url = f"{BASEURL}/list/count/static"
    response_data = get_json(s, url)
    time.sleep(get_delay())
    return response_data["count"]


def get_eresource_availability(s, id, host_bib_id):
    """Return e-resource availability using the catalog's availability endpoint."""
    url = f"{BASEURL}/eResource/availability"
    payload = [{
        "hostBibliographicId": host_bib_id,
        "resourceId": id,
        "useLoggedInUserCredentials": False,
    }]
    return post_account_json(s, url, payload, retries=3)


def get_list_of_lists(s, count=None):
    if count is None:
        count = get_list_count(s)
    url = f"{BASEURL}/lists/static/0/{count}/Name"
    response_data = get_json(s, url)
    time.sleep(get_delay())
    return [
        ListInfo(item["name"], item["id"], item["resourceCount"])
        for item in response_data
    ]


def get_items_from_list(s, list_info):
    url = (
        f"{BASEURL}/list/static/{list_info.list_id}/"
        f"0/{list_info.list_size}/Title"
    )
    response_data = get_json(s, url)
    time.sleep(get_delay())
    resources = response_data["resources"]
    return [ListItem.from_resource(resource) for resource in resources]


def get_loan_history(s):
    loan_list = []
    loans_per_page = 20
    start_index = 0
    there_is_more = True
    while there_is_more:
        url = (
            f"{BASEURL}/loans/history/page/"
            f"{start_index}/{loans_per_page}/OutDate"
        )
        time.sleep(get_delay())
        response_data = get_json(s, url)
        count = response_data["count"]
        start_index += loans_per_page
        if start_index >= count:
            there_is_more = False
        loans = response_data["loans"]

        for entry in loans:
            loan = entry["resource"]
            if not loan:  # orphaned entry
                continue
            loan_list.append(ListItem.from_resource(loan))
    return loan_list
