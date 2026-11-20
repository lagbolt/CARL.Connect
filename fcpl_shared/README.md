### Shared Library for Retrieving and Interpreting FCPL Catalog Data

These five Python modules include routines for reading data from the [FCPL catalog](https://catalog.fcpl.org/) and interpreting the results.

The shared routines target FCPL by default. To target another catalog with a
compatible API, change `BASEURL` in `common.py`.

From the repository root (the directory containing `pyproject.toml`), install or
reinstall the shared library and its prerequisites with:

```bash
pip install --force-reinstall .
```

`--force-reinstall` reinstalls the local package even when its version number
has not changed.

#### Modules

##### `account.py`

Account, list, loan, and availability data and operations.

|Name|Description|
|-|-|
|`ListItem`|Holds a catalog item's ID, short title, author, publication date, and format.|
|`ListInfo`|Holds a saved list's name, ID, and item count.|
|`AvailabilitySummary`|Summarizes local-branch and other-branch print-copy availability.|
|`EresourceAvailability`|Holds e-resource copy and hold counts.|
|`_local_branch_name`|Branch name used to separate local-branch holdings from other holdings.|
|`pub_date`|Extracts the publication date from a catalog resource.|
|`post_account_json`|Sends an account-related JSON POST through the shared request helper.|
|`_require_success`|Raises an error if the catalog response does not confirm an operation.|
|`delete_list_item`|Removes an item from a saved list.|
|`add_list_item`|Adds an item to a saved list.|
|`create_and_add`|Creates a private list containing one item.|
|`delete_list`|Deletes a saved list.|
|`login`|Authenticates a session with a barcode or username and password.|
|`get_list_count`|Returns the number of saved lists.|
|`get_eresource_availability`|Retrieves availability for an electronic resource.|
|`get_list_of_lists`|Retrieves details of saved lists and their item counts.|
|`get_items_from_list`|Retrieves the items in a saved list.|
|`get_loan_history`|Retrieves logged-in user's loan history.|

##### `cli.py`

Shared console and command-line helpers.

|Name|Description|
|-|-|
|`configure_console`|Configures Python and Windows console output for UTF-8 text.|
|`print_terminal_header`|Prints a standard program, version, input, and output header.|
|`count_phrase`|Formats a count with the correct singular or plural noun.|
|`interactive_login`|Prompts for credentials and logs in the supplied session.|
|`run_cli`|Runs a command-line entry point and reports runtime errors to stderr.|

##### `common.py`

Shared Unicode, HTTP, session, and catalog-resource helpers.

|Name|Description|
|-|-|
|`BASEURL`|Base URL used to build requests to the catalog service.|
|`_delay`|Default request delay in seconds; use `get_delay` and `set_delay` to access it.|
|`HTTP_HEADERS`|Standard HTTP headers for requests to the FCPL catalog.|
|`unicode_normalize`|Case-folds and canonically decomposes text for comparisons.|
|`unicode_collapse`|Case-folds text and removes combining accent marks.|
|`create_resilient_session`|Creates a context-manager-compatible requests session with retry handling.|
|`get_delay`|Returns the current delay in seconds between catalog requests.|
|`get_json`|Performs a GET request and parses its JSON response with concise errors.|
|`get_xml`|Performs a GET request and parses its XML response with concise errors.|
|`post_json`|Sends a JSON POST, optionally retrying transient failures.|
|`set_delay`|Sets the delay in seconds; call it before creating a session to configure retry backoff.|
|`get_resource`|Retrieves a catalog resource by resource id.|

##### `marc.py`

Fetches and generates MARC records from catalog search results.

|Name|Description|
|-|-|
|`get_one_marc`|Retrieves and converts JSON from the catalog into a PyMARC record.|
|`bulk_marc_gen`|Yields consecutive MARC records from the beginning of a search result set.|
|`random_marc_gen`|Yields records at randomly sampled indexes within a search range.|

##### `search.py`

Builds catalog searches and retrieves search results and IDs.

|Name|Description|
|-|-|
|`HITS_PER_PAGE`|Number of catalog results requested per search page.|
|`FACET_FILTERS`|Catalog facet definitions used to filter searches.|
|`SearchPayload`|Stores search parameters and builds or copies the JSON payload for a catalog search.|
|`build_facet_filters`|Builds facet filters to limit search results to books and/or recently added items.|
|`search_request`|Sends a catalog search request and returns its JSON response.|
|`count_hits`|Returns the total number of hits for a search.|
|`search_hit_count`|Returns the total hits for an existing `SearchPayload`.|
|`choose_resource`|Selects a resource from a multiple format or multiple edition search result, preferring book format.|
|`ids_one_page`|Retrieves item resource ids from one search results page.|
|`iter_ids`|Yields item resource ids sequentially, optionally up to a limit.|

`__init__.py` marks this directory as the `fcpl_shared` Python package.

Example programs in the other directories show how to use these helpers. If you need help, please contact me.

#### License

CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/

Graeme Williams  
carryonwilliams@gmail.com

