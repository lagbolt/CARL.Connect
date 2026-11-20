#
# FCPL catalog search: payloads, facet helpers, ID resolution, and ID iterators.
#
# Usage: Import search helpers from fcpl_shared.search and pass a requests session.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Graeme Williams  
# carryonwilliams
#

import time
from typing import NamedTuple

from .common import BASEURL, get_delay, post_json


HITS_PER_PAGE = 20
FACET_FILTERS = {
    "Book": {
        "facetDisplay": "Book",
        "facetValue": "Book",
        "facetName": "Format",
    },
    "LastTwoWeeks": {
        "facetDisplay": "Last Two Weeks",
        "facetValue": "LastTwoWeeks",
        "facetName": "DateAddedToSystem",
    },
}


def build_facet_filters(*, book=False, last_two_weeks=False):
    """Build facetFilters list for catalog search API calls."""
    facet_filters = [FACET_FILTERS["Book"]] if book else []
    if last_two_weeks:
        facet_filters.append(FACET_FILTERS["LastTwoWeeks"])
    return facet_filters


class SearchPayload(NamedTuple):
    search_term: str
    start_index: int = 0
    facet_filters: list|None = None
    frbr_search: bool = True

    def payload(self):
        """Constructs the JSON payload for the catalog search API."""
        return {
            "searchTerm": self.search_term,
            "hitsPerPage": HITS_PER_PAGE,
            "facetFilters": self.facet_filters if self.facet_filters else [],
            "branchFilters": [],
            "sortCriteria": "Relevancy",
            "targetAudience": "",
            "addToHistory": True,
            "dbCodes": [],
            "audienceCharacteristicsFilters": [],
            "frbrSearch": self.frbr_search,
            "debug": False,
            "startIndex": self.start_index,
        }

    def partial_copy(
        self,
        search_term=None,
        start_index=None,
        facet_filters=None,
        frbr_search=None,
    ):
        """Creates a new SearchPayload with some fields replaced."""
        return SearchPayload(
            search_term=search_term if search_term is not None else self.search_term,
            start_index=start_index if start_index is not None else self.start_index,
            facet_filters=facet_filters if facet_filters is not None else self.facet_filters,
            frbr_search=frbr_search if frbr_search is not None else self.frbr_search,
        )


def search_request(s, search_term, start_index=0, facet_filters=None, frbr_search=True):
    """Executes a POST request to search the catalog and returns the parsed JSON."""
    payload = SearchPayload(
        search_term=search_term,
        start_index=start_index,
        facet_filters=facet_filters,
        frbr_search=frbr_search,
    ).payload()
    url = f"{BASEURL}/search"
    json_data = post_json(s, url, payload, retries=3)
    time.sleep(get_delay())
    if json_data is None:
        raise RuntimeError("Catalog search returned an empty JSON response.")
    return json_data


def count_hits(s, search_term, facet_filters=None, frbr_search=True):
    """Returns the total number of hits for a given search."""
    payload = SearchPayload(
        search_term=search_term,
        facet_filters=facet_filters,
        frbr_search=frbr_search,
    ).payload()
    url = f"{BASEURL}/search/count"
    json_data = post_json(s, url, payload, retries=3)
    time.sleep(get_delay())
    if json_data is None:
        raise RuntimeError("Catalog search count returned an empty JSON response.")
    return json_data.get("totalHits", 0)


def search_hit_count(s, payload: SearchPayload):
    """Return total hits for a search payload."""
    return count_hits(
        s,
        payload.search_term,
        facet_filters=payload.facet_filters,
        frbr_search=payload.frbr_search,
    )


def choose_resource(resource_list):
    """Selects a specific item from a list, prioritizing 'Book' formats."""
    if not resource_list:
        raise ValueError("Malformed JSON returned by the catalog: resource list is empty.")
    for resource in resource_list:
        if resource["format"] == "Book":
            return resource
    return resource_list[0]


def ids_one_page(s, payload: SearchPayload):
    """Retrieves catalog item IDs from a single page of search results."""
    r = search_request(
        s,
        payload.search_term,
        start_index=payload.start_index,
        facet_filters=payload.facet_filters,
        frbr_search=payload.frbr_search,
    )

    if ("trustedRecords" not in r) or (not r["trustedRecords"]):
        return []

    result_list = []
    for rec in r["trustedRecords"]:
        if rec["preferredBidDbId"]:
            result_list.append(rec["preferredBidDbId"])
        else:
            iid = rec["id"]
            iid_query = f"iid: {iid}"
            iid_payload = payload.partial_copy(search_term=iid_query, frbr_search=False)
            r2 = search_request(
                s,
                iid_payload.search_term,
                start_index=iid_payload.start_index,
                facet_filters=iid_payload.facet_filters,
                frbr_search=iid_payload.frbr_search,
            )
            resource = choose_resource(r2["resources"])
            result_list.append(resource["id"])

    return result_list


def iter_ids(s, payload: SearchPayload, limit=None):
    """Yield catalog item IDs sequentially from the start of the result set."""
    if limit is not None and limit <= 0:
        return
    start_index = 0
    count = 0
    while True:
        page_payload = payload.partial_copy(start_index=start_index)
        id_list = ids_one_page(s, page_payload)
        if not id_list:
            return
        for item_id in id_list:
            yield item_id
            count += 1
            if limit is not None and count >= limit:
                return
        start_index += HITS_PER_PAGE
