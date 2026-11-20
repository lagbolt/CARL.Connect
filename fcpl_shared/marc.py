#
# FCPL catalog MARC fetch and record generators.
#
# Usage: Import MARC fetch and record-generator functions from fcpl_shared.marc.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Graeme Williams  
# carryonwilliams@gmail.com
#

import random
import time

import pymarc
from .common import BASEURL, get_delay, get_json
from .search import HITS_PER_PAGE, SearchPayload, ids_one_page, iter_ids


def get_one_marc(s, id):
    """Fetch MARC for a catalog ID and return a PyMARC Record."""
    url = f"{BASEURL}/marcrecord/{id}"
    try:
        json_data = get_json(s, url)
    except RuntimeError as exc:
        raise RuntimeError(f"Could not fetch MARC for ID {id}: {exc}") from exc
    time.sleep(get_delay())

    record = pymarc.Record()  # type: ignore
    record.leader = (json_data["leader"]+(24*" "))[0:24]  # MUST be 24 characters long
    for field in json_data["fields"]:
        tag = field["tag"]

        ind1 = field.get("indicator1", " ")
        ind2 = field.get("indicator2", " ")
        indicators = [ind1, ind2]

        if field.get("subfields"):
            subfields = []
            for subfield in field["subfields"]:
                code = subfield["name"]
                value = subfield["data"]
                subfields.append(pymarc.Subfield(code=code, value=value))  # type: ignore
            record.add_field(
                pymarc.Field(tag=tag, indicators=indicators, subfields=subfields)  # type: ignore
            )
        else:
            data = field.get("data", "")
            record.add_field(pymarc.Field(tag=tag, data=data))  # type: ignore

    return record


def bulk_marc_gen(s, payload: SearchPayload, limit):
    """Yield sequential MARC records from the start of the result set."""
    if limit <= 0:
        return
    count = 0
    for item_id in iter_ids(s, payload):
        yield get_one_marc(s, item_id)
        count += 1
        if count >= limit:
            return


def random_marc_gen(s, payload: SearchPayload, limit, start_range, end_range):
    """Yield MARC records from random unique indexes within a range."""
    if start_range < 0 or end_range < start_range:
        raise ValueError("The index range must be non-negative and start_range <= end_range.")
    if limit < 0:
        raise ValueError("limit must be non-negative.")
    range_size = end_range - start_range + 1
    if limit > range_size:
        raise ValueError(f"Cannot sample {limit} unique indexes from a range of {range_size}.")
    if limit == 0:
        return
    target_indexes = sorted(random.sample(range(start_range, end_range + 1), limit))
    current_id_list = None
    current_page_start = -1

    for index in target_indexes:
        target_page_start = (index // HITS_PER_PAGE) * HITS_PER_PAGE

        if target_page_start != current_page_start:
            page_payload = payload.partial_copy(start_index=target_page_start)
            current_id_list = ids_one_page(s, page_payload)
            current_page_start = target_page_start

            if not current_id_list:
                break

        local_index = index - target_page_start

        if local_index < len(current_id_list):  # type: ignore
            record_id = current_id_list[local_index]  # type: ignore
            yield get_one_marc(s, record_id)
