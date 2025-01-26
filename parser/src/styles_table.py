import csv
import json
import os
import re


class StylesTable:
    def __init__(self, csv_file="styles.csv", separate_files=True):
        """
        Initialize the class with a CSV file for known and optionally unknown keys.

        Args:
            csv_file (str): The name of the CSV file for known keys (and optionally unknown keys).
            separate_files (bool): If True, use separate files for known and unknown keys.
                                  If False, use a single file for both.
        """
        self.csv_file = csv_file
        self.separate_files = separate_files
        self.unknown_csv_file = "unknown_styles.csv" if separate_files else csv_file
        self.known_keys = {}
        self.unknown_keys = {}
        self.all_key_names = set()
        self.load_known_keys()

    def _parse_row(self, row):
        """
        Parse a CSV row into a key dictionary and metadata.

        Args:
            row (dict): A CSV row dictionary

        Returns:
            tuple: (key_dict, kind, occurrences, first_text)
        """
        # Normalize all values to strings
        key_dict = {
            k: str(row.get(k, ""))  # Convert all values to strings
            for k in self.all_key_names
            if k not in ["kind", "occurrences", "first_text", "first_strings"]
        }
        key_str = json.dumps(key_dict, sort_keys=True)

        # Handle missing or null values for metadata fields
        kind = str(row.get("kind", "")).strip()  # Default to empty string if missing
        occurrences = int(row.get("occurrences", 0))  # Default to 0 if missing
        first_text = str(
            row.get("first_text", "")
        ).strip()  # Default to empty string if missing

        return (
            key_str,
            kind,
            occurrences,
            first_text,
        )

    def load_known_keys(self):
        """Load data from the known keys CSV file and merge known keys from the unknown CSV file."""
        # Load known keys from the primary CSV file
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames is None:
                    raise ValueError(
                        f"CSV file {self.csv_file} is empty or improperly formatted."
                    )

                self.all_key_names.update(
                    key
                    for key in reader.fieldnames
                    if key not in ["kind", "occurrences", "first_text", "first_strings"]
                )

                for row in reader:
                    try:
                        # Normalize row: replace None values with empty strings
                        normalized_row = {
                            k: ("" if v is None else v) for k, v in row.items()
                        }
                        key_str, kind, occurrences, first_text = self._parse_row(
                            normalized_row
                        )
                        if kind:  # Only load known keys
                            self.known_keys[key_str] = {
                                "kind": kind,
                                "occurrences": 0,  # Reset occurrences
                                "first_text": "",  # Reset first_text
                                "first_strings": [],
                            }
                    except Exception as e:
                        print(f"Error parsing row: {row}. Error: {e}")

        # Load and merge known keys from the unknown CSV file
        if self.separate_files and os.path.exists(self.unknown_csv_file):
            with open(
                self.unknown_csv_file, mode="r", newline="", encoding="utf-8"
            ) as file:
                reader = csv.DictReader(file)
                if reader.fieldnames is None:
                    raise ValueError(
                        f"CSV file {self.unknown_csv_file} is empty or improperly formatted."
                    )

                self.all_key_names.update(
                    key
                    for key in reader.fieldnames
                    if key not in ["kind", "occurrences", "first_text", "first_strings"]
                )

                for row in reader:
                    try:
                        # Normalize row: replace None values with empty strings
                        normalized_row = {
                            k: ("" if v is None else v) for k, v in row.items()
                        }
                        key_str, kind, occurrences, first_text = self._parse_row(
                            normalized_row
                        )
                        if kind:  # If the row has a kind, treat it as a known key
                            self.known_keys[key_str] = {
                                "kind": kind,
                                "occurrences": 0,  # Reset occurrences
                                "first_text": "",  # Reset first_text
                                "first_strings": [],
                            }
                    except Exception as e:
                        print(f"Error parsing row: {row}. Error: {e}")

    def save_csv_files(self):
        """Save data to the CSV files."""
        # Update all key names from existing keys
        all_key_dicts = list(self.known_keys.keys()) + list(self.unknown_keys.keys())
        for key_str in all_key_dicts:
            key_dict = json.loads(key_str)
            self.all_key_names.update(key_dict.keys())

        fieldnames = (
            ["kind", "first_text", "first_strings","occurrences"]
            + sorted(list(self.all_key_names))
        )

        # Save known keys
        with open(self.csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for key_str, data in self.known_keys.items():
                row_data = json.loads(key_str)
                # Ensure all values are strings
                row_data = {k: str(v) for k, v in row_data.items()}
                row_data.update(
                    {
                        "kind": data["kind"],
                        "occurrences": data["occurrences"],
                        "first_text": data["first_text"],
                        "first_strings": data["first_strings"],
                    }
                )
                writer.writerow(row_data)

        # Save unknown keys (if using separate files)
        if self.separate_files:
            with open(
                self.unknown_csv_file, mode="w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for key_str, data in self.unknown_keys.items():
                    row_data = json.loads(key_str)
                    # Ensure all values are strings
                    row_data = {k: str(v) for k, v in row_data.items()}
                    row_data.update(
                        {
                            "kind": "",
                            "occurrences": data["occurrences"],
                            "first_text": data["first_text"],
                            "first_strings": data["first_strings"],
                        }
                    )
                    if data["first_strings"]:
                        writer.writerow(row_data)
        else:
            # Append unknown keys to the same file
            with open(self.csv_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                for key_str, data in self.unknown_keys.items():
                    row_data = json.loads(key_str)
                    # Ensure all values are strings
                    row_data = {k: str(v) for k, v in row_data.items()}
                    row_data.update(
                        {
                            "kind": "",
                            "occurrences": data["occurrences"],
                            "first_text": data["first_text"],
                            "first_strings": data["first_strings"],
                        }
                    )
                    writer.writerow(row_data)

    def _contains_hebrew_or_english(self, text):
        """
        Check if the text contains at least one Hebrew or English character
        and has a total length of at least 3 characters.

        Args:
            text (str): The text to check.

        Returns:
            bool: True if the text contains at least one Hebrew or English character
                  and has a length of at least 3, False otherwise.
        """
        # Check if the text length is at least 3
        if len(text) < 3:
            return False

        # Regex to match at least one Hebrew or English character
        hebrew_english_pattern = re.compile(r"[\u0590-\u05FFa-zA-Z]")
        return bool(hebrew_english_pattern.search(text))

    def lookup(self, key_dict, first_text=""):
        """
        Look up a key in the known keys.
        If not found, record it in the unknown keys table.
        """
        # Normalize key_dict: convert all values to strings
        normalized_key_dict = {
            k: str(v) if v is not None else "" for k, v in key_dict.items()
        }

        # Convert the normalized dictionary to a JSON string
        key_str = json.dumps(normalized_key_dict, sort_keys=True)
        self.all_key_names.update(key_dict.keys())

        if key_str in self.known_keys:
            return self.known_keys[key_str]["kind"]

        # Strip whitespace from first_text
        first_text = first_text.strip()

        # Save first_text only if it contains at least 3 Hebrew or English characters
        if not self._contains_hebrew_or_english(first_text):
            first_text = ""

        if key_str not in self.unknown_keys:
            self.unknown_keys[key_str] = {
                "first_text": first_text,
                "first_strings": [],  # Initialize list of first strings
                "occurrences": 0,
            }

        # Add first_text to the list if it's not already there and the list has fewer than 20 items
        if first_text and first_text not in self.unknown_keys[key_str]["first_strings"]:
            if len(self.unknown_keys[key_str]["first_strings"]) < 20:
                self.unknown_keys[key_str]["first_strings"].append(first_text)

        self.unknown_keys[key_str]["occurrences"] += 1
        return None

    def save(self):
        """Save the current state to the CSV files."""
        self.save_csv_files()
        if self.separate_files:
            print(f"Known keys saved to {self.csv_file}")
            print(f"Unknown keys saved to {self.unknown_csv_file}")
        else:
            print(f"All keys saved to {self.csv_file}")

    def load(self):
        """Reload the known keys CSV file to reflect any offline edits."""
        self.known_keys = {}
        self.unknown_keys = {}
        self.all_key_names = set()
        self.load_known_keys()
        print(f"Known keys reloaded from {self.csv_file}")
