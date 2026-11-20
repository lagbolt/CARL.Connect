#
# Shared console, reporting, interactive-login, and error helpers for FCPL CLIs.
#
# Usage: Import the required helpers from fcpl_shared.cli.
# Version: 0.5.0  11/20/2026
# Edited by ChatGPT.
# License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
# Author: Graeme Williams
#

import subprocess
import sys

from .account import login


def configure_console():
    """Configure Windows console code-page and stdout encoding for text output."""
    if sys.platform == "win32":
        subprocess.run("chcp 65001 >nul", shell=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def print_terminal_header(program: str, version: str, inputfile: str, outputfile: str) -> None:
    """Print the standard program, version, input, and output header."""
    print("=" * 45)
    print(f"  {program} {version}")
    print(f"  Input:  {inputfile}")
    print(f"  Output: {outputfile}")
    print("=" * 45)


def count_phrase(n: int, singular: str, plural: str) -> str:
    """Return a count with the matching singular or plural noun."""
    return f"{n} {singular if n == 1 else plural}"


def interactive_login(session):
    """Prompt for account credentials and log in, raising if the user is missing."""
    username_or_barcode = input("Enter your username or barcode: ")
    if not username_or_barcode:
        raise RuntimeError("Username or barcode is required.")

    password_prompt = (
        "Enter your last name: "
        if username_or_barcode.isdigit()
        else "Enter your password: "
    )
    password = input(password_prompt)
    login(session, username_or_barcode, password)


def run_cli(main_function):
    """Run a command-line entry point and report operational errors to stderr."""
    try:
        main_function()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
