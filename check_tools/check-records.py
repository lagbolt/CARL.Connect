#
#    Scan a MARC file and check for records that match specific tests.
#
#    Usage:  python check-records.py -i <MARC input file> -o <output file> [ -b ]
#
#    -i,  --input       Path to the binary MARC input file. Required.
#    -o,  --output      Path to the output detail report file. Required.
#    -b,  --brief       Limit the output file to records with serious and non-serious errors.
#
#    Edited by Claude.
#    Edited by ChatGPT.
#
#    Version:  0.5.0  11/20/2026
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
#

import argparse
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Tuple, TypeAlias, Union

from fcpl_shared.cli import configure_console, count_phrase, print_terminal_header
from pymarc import Field, Record, MARCReader


configure_console()


class Severity(Enum):
    SERIOUS = "serious"
    NONSERIOUS = "nonserious"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    message: str
    severity: Severity
    fields: Tuple[Field, ...] = ()


# A check function tests a record and returns one of:
#   False or []  - no issue
#   True         - issue found, no specific fields to report
#   [Field, ...] - issue found; the listed fields are the culprits
# Note: an empty list must never be used to mean "issue found with no
# fields" - it is indistinguishable from "no issue" (see missing_245c_fields).
CheckFn: TypeAlias = Callable[[Record], Union[bool, List[Field]]]


@dataclass(frozen=True)
class Check:
    """One test to run against a record: a label, a check function, and the
    severity to report if the check function finds an issue."""
    label: str
    check_fn: CheckFn
    severity: Severity = Severity.SERIOUS


@dataclass
class RecordResult:
    title: str
    record: Record
    issues: List[Issue] = field(default_factory=list)

    @property
    def has_serious(self) -> bool:
        return any(i.severity == Severity.SERIOUS for i in self.issues)

    @property
    def has_nonserious(self) -> bool:
        return any(i.severity == Severity.NONSERIOUS for i in self.issues)

    @property
    def has_warning(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)


# Unicode helper functions

def nfc(s: str) -> str:
    """Returns s in Unicode normalization form NFC, so precomposed and decomposed
    versions of the same text compare equal.  Case is not changed."""
    return unicodedata.normalize("NFC", s)


# Utility functions

def to_string_simple(the_record: Record) -> str:
    """
    Used to identify a record in the output. You can use whatever MARC fields you want here
    """
    if fields_245 := the_record.get_fields('245'):
        # Normalize first so [:60] is less likely to cut an accent off its letter
        return nfc(fields_245[0].get('a',"") + fields_245[0].get('c',""))[:60]
    else:
        return "No 245!!"


def read_from_file(filename):
    """Yields (position, bibnumber, record) for each record in the file, where
    position is the record's 1-based position in the file.  A record that cannot
    be read is yielded as (position, "", None) so the caller can count it."""
    with open(filename, 'rb') as marc_input:
        for position, aRecord in enumerate(MARCReader(marc_input), start=1):
            if aRecord is None:
                yield position, "", None
                continue
            # if you have a MARC field you want to use to identify the record
            # assign it to bibnumber here -- as a string
            if v := aRecord.get('001'):
                bibnumber = v.data
            elif (f := aRecord.get('035')) and (v := f.get('a')):
                bibnumber = v
            else:
                bibnumber = ""
            yield position, bibnumber, aRecord


# *** Predicates that are too complicated to put into a lambda go here ***

def invalid_041_fields(record: Record) -> List[Field]:
    """Returns the 041 field(s) containing an alphabetic subfield whose value
    is not exactly 3 characters long."""
    return [
        f for f in record.get_fields('041')
        if any(len(sf.value) != 3 for sf in f.subfields if sf.code.isalpha())
    ]

def bad_041_indicator1_fields(record: Record) -> List[Field]:
    """Returns the 041 field(s) that contain an $h subfield but whose first
    indicator is not '1' (indicating a translation)."""
    return [f for f in record.get_fields('041') if f.get_subfields('h') and f.indicator1 != '1']

def fields_041_without_546(record: Record) -> Union[bool, List[Field]]:
    """Returns the 041 field(s) present in this record if it has no 546
    field (language note), or False if there are no 041 fields or a 546
    field is present."""
    # Ignore odd case of a single $a subfield (and other edge cases)
    fields_041 = [ fld for fld in record.get_fields('041') if len(fld.subfields)>1]
    if fields_041 and not record.get_fields('546'):
        return fields_041
    return False

def missing_245c_fields(the_record: Record) -> Union[bool, List[Field]]:
    """Returns the 245 field(s) if a 245 is present but lacks a $c subfield, or
    False if a 245 with $c is present or there is no 245 at all (that case is
    caught by the "no 245" check)."""
    fields_245 = the_record.get_fields('245')
    if not fields_245:
        return False        # Catch this error in the "no 245" check
    if not fields_245[0].get('c'):
        return fields_245
    return False

def no1xx7xx(the_record: Record) -> bool:
    return not the_record.get_fields('100', '110', '111', '130', '700', '710', '711', '720', '730')

def multiple245(the_record: Record) -> Union[bool, List[Field]]:
    """ If this record has more than one 245, returns them all """
    fields_245 = the_record.get_fields('245')
    if len(fields_245) > 1:
        return fields_245
    return False

def check245c1xx7xx(the_record: Record) -> Union[bool, List[Field]]:
    """ Returns the 245 field(s) if this record has a 245$c containing "and
        others" but no 1xx/7xx field, or False otherwise. Yes, this is an
        odd test; it was an experiment. """
    fields_245 = the_record.get_fields('245')
    s = fields_245[0].get('c') if fields_245 else None
    if s and ("and others" in s) and no1xx7xx(the_record):
        return fields_245
    return False

def missing_dollar2_subject_fields(the_record: Record) -> List[Field]:
    """Returns any subject (6xx) fields with indicator2 '7' but no $2 subfield."""
    return [f for f in the_record.subjects if f.indicator2 == '7' and not f.get_subfields('2')]

def missing_indicator7_subject_fields(the_record: Record) -> List[Field]:
    """Returns any subject (6xx) fields with a $2 subfield but indicator2 not '7'."""
    return [f for f in the_record.subjects if f.get_subfields('2') and f.indicator2 != '7']

def duplicate_subject_fields(the_record: Record) -> List[Field]:
    """ Returns every 650 field involved in a duplicate group: fields that
        match another 650 in $a/$b/$c/$d/$v/$x/$y/$z (every occurrence of each
        subfield), ignoring a trailing dot and differences in Unicode
        normalization.  Case is significant. """
    subfields650 = ('a', 'b', 'c', 'd', 'v', 'x', 'y', 'z')

    def key_for(f: Field) -> dict:
        key = {}
        for k in subfields650:
            values = tuple(nfc(v).rstrip('.') for v in f.get_subfields(k) if v)
            if values:
                key[k] = values
        return key

    keyed = [(key_for(f), f) for f in the_record.get_fields('650')]
    return [f for i, (key, f) in enumerate(keyed)
            if any(key == other_key for other_key, _ in keyed[:i] + keyed[i + 1:])]

def checkfactory(label: str, check_fn: CheckFn,
                  severity: Severity = Severity.SERIOUS) -> Check:
    return Check(label, check_fn, severity)

# Construct list of checks. Each check's severity can be set individually;

checkList = (
    checkfactory('no 001', lambda r: not r.get_fields('001')),
    checkfactory('no 1XX', lambda r: not r.get_fields('100', '110', '111', '130'), Severity.NONSERIOUS),
    checkfactory('no 245', lambda r: not r.get_fields('245')),
    checkfactory('no 245c', missing_245c_fields),
    checkfactory('041 with bad code', invalid_041_fields),
    checkfactory('041 but no 546', fields_041_without_546, Severity.WARNING),
    checkfactory('041h w. wrong indicator', bad_041_indicator1_fields, Severity.NONSERIOUS),
    checkfactory('no 1xx or 7xx', no1xx7xx),
    checkfactory('"and others" in 245c but no 1xx/7xx', check245c1xx7xx, Severity.WARNING),
    checkfactory('indicator 7 but no $2 in 6xx', missing_dollar2_subject_fields, Severity.NONSERIOUS),
    checkfactory('$2 in 6xx without indicator 7', missing_indicator7_subject_fields, Severity.NONSERIOUS),
    checkfactory('duplicate subject headings', duplicate_subject_fields, Severity.WARNING),
)

def validate_record(record: Record) -> RecordResult:
    """Runs every check in checkList against a single MARC record."""
    issues: List[Issue] = []

    def add_issue(msg: str, severity: Severity = Severity.SERIOUS,
                  fields: Tuple[Field, ...] = ()) -> None:
        issues.append(Issue(msg, severity, fields))

    for check in checkList:
        result = check.check_fn(record)
        if not result:
            continue
        matched_fields = () if result is True else tuple(result)
        add_issue(check.label, check.severity, matched_fields)

    return RecordResult(title=to_string_simple(record), record=record, issues=issues)

PROGRAM = "check-records"
VERSION = "0.6.0"


def summary_lines(total: int, skipped: int, errors: int, error_records: int) -> List[str]:
    return [
        f"{total} records processed, {skipped} skipped",
        f"{count_phrase(errors, 'error', 'errors')} found in {count_phrase(error_records, 'record', 'records')}",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan MARC records for possible cataloging problems.")
    parser.add_argument("--input", "-i", required=True, dest="inputfile",
                        help="Path to the binary MARC input file")
    parser.add_argument("--output", "-o", required=True, dest="outputfile",
                        help="Path to the output detail report file")
    parser.add_argument("--brief", "-b", action="store_true", dest="brief",
                        help="Limit output file to records with serious and non-serious errors")
    args = parser.parse_args()

    serious_counter: Counter = Counter()
    nonserious_counter: Counter = Counter()
    warning_counter: Counter = Counter()
    total_records = 0
    skipped_records = 0
    errors_found = 0
    records_with_errors = 0
    records_with_serious_errors = 0
    records_with_nonserious_errors = 0
    records_with_only_warnings = 0

    source = args.inputfile
    print_terminal_header(PROGRAM, VERSION, source, args.outputfile)

    with open(args.outputfile, 'w', encoding='utf-8') as out_f:
        out_f.write(f"# {PROGRAM} {VERSION}\n")
        out_f.write(f"# Input:  {source}\n")
        out_f.write(f"# Output: {args.outputfile}\n")
        out_f.write("# Record Scan Report\n")
        out_f.write("# " + "=" * 72 + "\n\n")

        for position, bibnum, theRecord in read_from_file(source):
            if theRecord is None:
                skipped_records += 1
                continue
            total_records += 1
            result = validate_record(theRecord)

            if not result.issues:
                continue

            errors_found += len(result.issues)
            records_with_errors += 1

            if result.has_serious:
                records_with_serious_errors += 1
            elif result.has_nonserious:
                records_with_nonserious_errors += 1
            elif result.has_warning:
                records_with_only_warnings += 1

            for issue in result.issues:
                if issue.severity == Severity.SERIOUS:
                    serious_counter[issue.message] += 1
                elif issue.severity == Severity.NONSERIOUS:
                    nonserious_counter[issue.message] += 1
                elif issue.severity == Severity.WARNING:
                    warning_counter[issue.message] += 1

            if result.has_serious or result.has_nonserious or not args.brief:
                out_f.write(f"Record {position} ({bibnum}): {result.title}\n")
                for issue in result.issues:
                    out_f.write(f"    [{issue.severity.value}] {issue.message}\n")
                    for f in issue.fields:
                        out_f.write(f"        {f}\n")
                out_f.write("\n")

        out_f.write("\n# " + "=" * 72 + "\n")
        for line in summary_lines(total_records, skipped_records, errors_found, records_with_errors):
            out_f.write(f"# {line}\n")

    # Print summary to terminal
    terminal_summary = summary_lines(
        total_records, skipped_records, errors_found, records_with_errors
    )
    print(terminal_summary[0])
    print(terminal_summary[1], file=sys.stderr)
    print(
        f"  {count_phrase(records_with_serious_errors, 'record with', 'records with')} serious errors",
        file=sys.stderr,
    )
    print(f"  {count_phrase(records_with_nonserious_errors, 'record whose', 'records whose')} "
          f"worst issue is non-serious", file=sys.stderr)
    print(
        f"  {count_phrase(records_with_only_warnings, 'record with', 'records with')} only warnings",
        file=sys.stderr,
    )
    print("-" * 40, file=sys.stderr)
    if not serious_counter and not nonserious_counter and not warning_counter:
        print("Excellent! No problems found.")
    else:
        print("Serious Errors:", file=sys.stderr)
        if serious_counter:
            for error, count in serious_counter.items():
                print(f"[{count:4d}] {error}", file=sys.stderr)
        else:
            print("  None", file=sys.stderr)
        print("\nNon-Serious Errors:", file=sys.stderr)
        if nonserious_counter:
            for error, count in nonserious_counter.items():
                print(f"[{count:4d}] {error}", file=sys.stderr)
        else:
            print("  None", file=sys.stderr)
        print("\nWarnings:", file=sys.stderr)
        if warning_counter:
            for error, count in warning_counter.items():
                print(f"[{count:4d}] {error}", file=sys.stderr)
        else:
            print("  None", file=sys.stderr)
    print("=" * 40, file=sys.stderr)
    print(f"Detailed report written to: {args.outputfile}\n")


if __name__ == "__main__":
    main()
