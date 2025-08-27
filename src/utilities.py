import os
import re
from dataclasses import dataclass
import difflib


def diff_percent(string1, string2):
    """
    Calculate the percentage of difference between two strings.
    """
    seq_matcher = difflib.SequenceMatcher(None, string1, string2)
    diff_ratio = seq_matcher.ratio()
    return diff_ratio * 100


def show_diff(string1, string2, display_percent=False):
    lines1 = string1.splitlines()
    lines2 = string2.splitlines()

    differ = difflib.Differ()
    diff = differ.compare(lines1, lines2)

    for line in diff:
        if line.startswith("- "):
            print(f"\033[31m{line}\033[0m")  # Red for removals
        elif line.startswith("+ "):
            print(f"\033[32m{line}\033[0m")  # Green for additions
        elif line.startswith("? "):
            print(f"\033[33m{line}\033[0m")  # Yellow for hints
        else:
            print(line)

    if display_percent:
        print(f"Similarity: {diff_percent(string1, string2):.2f}%")


def clean_text(text, newline_replacement=True):
    text = text.lower()
    first_line = text.split("\n", 1)[0]
    if "extract" in first_line:
        # remove the first line if it contains "extract"
        try:
            text = text.split("\n", 1)[1]
        except IndexError:
            print(f"Text is likely a blank page: {text}")
            text = ""

    # remove any extra spaces, new lines, or tabs
    if newline_replacement:
        # remove all new lines and replace them with a space
        text = re.sub(r"\n+", " ", text)

    text = re.sub(r"^\s+|\s+$", "", text)

    # strip surrounding quotes from the text
    text = re.sub(r"^['\"”]|['\"”]$", "", text)

    # strip out ```text and ``` from the text
    text = re.sub(r"^```text|```$", "", text)

    # strip our any internal extra spaces
    text = re.sub(r"\s+", " ", text)
    return text


@dataclass
class ConversionArgs:
    input: str
    output: str
    number: int = 0
    all: bool = False
    exclude_background: bool = False
    policy: str = "strict"


def normalize_file_name(file_name):
    """
    Normalize the file name by removing the extension and any trailing numbers.
    """
    # Remove the extension
    base_name = os.path.splitext(file_name)[0]
    # Remove trailing numbers
    normalized_name = re.sub(r"_[0-9]+$", "", base_name)
    # Remove the path
    normalized_name = os.path.basename(normalized_name)
    return normalized_name


def filter_out_unsynced_files(folder, synced_files):
    found_files = []

    print(f"Searching for files in the {folder} folder...")
    for root, _, files in os.walk(folder):
        for file in files:
            found_files.append(os.path.join(root, file))

    if synced_files:
        # Filter the files to only include the synced files regardless of the folder structure or extension (i.e. path/file.txt == other_path/file.png)
        found_synced_files = [normalize_file_name(file) for file in synced_files]
        files = [
            file
            for file in found_files
            if normalize_file_name(file) in found_synced_files
        ]
    else:
        # If no synced files, return all found files
        files = found_files

    return files
