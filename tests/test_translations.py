import unittest
import re
import os
from collections import defaultdict

# --- Assumption ---
# Assuming your translations.py is in the parent directory relative to the tests directory
# (e.g., project_root/translations.py) and defines a dictionary named 'translations'.
# Adjust the import path if your project structure is different.
try:
    # Assumes tests/ is a subdir of the project root
    from ..translations import translations
except ImportError:
     # Fallback if running the test directly from the project root might work sometimes,
    # or if translations.py is in the same directory (less common for tests)
    try:
        from translations import translations
    except ImportError:
        print("Error: Could not import 'translations' dictionary.")
        print("Ensure 'translations.py' exists in the correct path relative to the test")
        print("and contains a dictionary named 'translations'.")
        translations = None # Set to None to cause tests to fail clearly
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")
    translations = None


class TestTranslations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test data once for the class."""
        if translations is None:
            # Skip all tests in this class if translations aren't loaded
            raise unittest.SkipTest("Translations could not be loaded.")

        cls.translations_data = translations
        cls.required_languages = ['en', 'no']
        # Store where each key was found: {key: {filename1, filename2}, ...}
        cls.key_locations = defaultdict(set)
        cls.html_files_processed = []
        cls.html_files_with_errors = {} # Store errors per file {filename: error_message}

        # --- Assumption ---
        # Assuming templates/ directory is in the parent directory relative to the tests directory
        # (e.g., project_root/templates/)
        base_dir = os.path.dirname(__file__)
        # Go up one level from tests/ to the project root, then into templates/
        project_root = os.path.dirname(base_dir)
        templates_dir = os.path.join(project_root, 'templates')


        if not os.path.isdir(templates_dir):
             # Try alternative structure: tests/ and templates/ are direct children of root
             alt_templates_dir = os.path.join(os.path.dirname(project_root), 'templates')
             if os.path.isdir(alt_templates_dir):
                 templates_dir = alt_templates_dir
             else:
                 raise unittest.SkipTest(f"Templates directory not found at expected locations: {templates_dir} or {alt_templates_dir}")


        found_html_files = False
        # Use os.walk to recursively find html files in templates and subdirectories
        for root, _, files in os.walk(templates_dir):
             for filename in files:
                 if filename.lower().endswith('.html'):
                     found_html_files = True
                     # Get path relative to the templates directory for cleaner reporting
                     relative_path = os.path.relpath(os.path.join(root, filename), templates_dir)
                     full_path = os.path.join(root, filename)
                     cls.html_files_processed.append(relative_path)
                     try:
                         with open(full_path, 'r', encoding='utf-8') as f:
                             html_content = f.read()
                         # Regex to find patterns like {{ t['key_name'] }} or {{t['key_name']}} etc.
                         keys_in_file = set(re.findall(r"\{\{\s*t\['(.*?)'\]\s*\}\}", html_content))
                         for key in keys_in_file:
                             cls.key_locations[key].add(relative_path) # Store relative path
                         # print(f"Found keys in {relative_path}: {keys_in_file}") # Optional: for debugging
                     except FileNotFoundError:
                         # Should not happen if os.walk worked, but good practice
                          cls.html_files_with_errors[relative_path] = "File not found during read attempt."
                     except Exception as e:
                          cls.html_files_with_errors[relative_path] = f"Error reading or parsing file: {e}"


        if not found_html_files:
             # If no HTML files found, we might want to skip the HTML-related tests
             # or handle it depending on project requirements. Here we'll skip.
             raise unittest.SkipTest(f"No .html files found in directory (and subdirectories): {templates_dir}")


        # Derive the set of all unique keys found
        cls.html_keys = set(cls.key_locations.keys())


        if not cls.html_keys and not cls.html_files_with_errors:
             # If files were processed but no keys found at all
             print(f"Warning: No translation keys (e.g., {{ t['key'] }}) found in any HTML files processed in {templates_dir}")
             # Depending on reqs, you might want to fail or just warn.
             # We'll proceed, tests below might catch issues if keys *should* exist.


    def test_html_file_read_errors(self):
        """Check if any HTML files failed to be read or parsed during setup."""
        self.assertFalse(self.html_files_with_errors,
                         f"Errors occurred while processing HTML files: {self.html_files_with_errors}")

    def test_all_keys_exist_in_translations(self):
        """Verify that every key used in HTML files exists in the translations structure."""
        if not self.translations_data:
             self.fail("Translations data is empty or not loaded.")
        if not self.html_keys:
            self.skipTest("No HTML translation keys were found to test.")

        # Store detailed info about missing keys and their locations
        missing_keys_details = {} # {key: {file1, file2}, ...}
        for key in self.html_keys:
            # Check if the key exists in *at least one* language's dictionary
            key_found = any(key in lang_dict for lang_dict in self.translations_data.values())
            if not key_found:
                # Get the files where this missing key is used
                files_using_key = self.key_locations.get(key, {"Error: location not tracked"})
                missing_keys_details[key] = files_using_key

        if missing_keys_details:
            error_message = ["Keys used in HTML files but not found in ANY translation language:"]
            for key, files in missing_keys_details.items():
                file_list = ", ".join(sorted(list(files))) # Sort for consistent output
                error_message.append(f"  - Key: '{key}' (Used in: {file_list})")
            self.fail("\n".join(error_message)) # Use fail with multi-line message

    def test_all_languages_covered_for_html_keys(self):
        """Verify that every key used in HTML files has a translation for all required languages."""
        if not self.translations_data:
             self.fail("Translations data is empty or not loaded.")
        if not self.html_keys:
            self.skipTest("No HTML translation keys were found to test.")

        # Store detailed info about missing translations: {lang: {key: {file1, ...}}, ...}
        missing_translations_details = defaultdict(dict)
        warnings = []

        for lang in self.required_languages:
            if lang not in self.translations_data:
                # This failure indicates a fundamental issue with the translations dict
                self.fail(f"Required language '{lang}' not found in the main translations dictionary.")
                continue # Should not be reached if assertFail works

            lang_dict = self.translations_data.get(lang, {}) # Use .get for safety, though checked above

            for key in self.html_keys:
                if key not in lang_dict:
                    # Key exists overall, but missing for this specific language
                    files_using_key = self.key_locations.get(key, {"Error: location not tracked"})
                    missing_translations_details[lang][key] = files_using_key
                # Optional: Check if the translation string is empty or just whitespace
                elif not lang_dict.get(key, "").strip():
                     files_using_key = self.key_locations.get(key, {"Error: location not tracked"})
                     file_list = ", ".join(sorted(list(files_using_key)))
                     warnings.append(f"Warning: Key '{key}' has an empty/whitespace translation for language '{lang}' (Used in: {file_list}).")

        # Print warnings first, if any
        if warnings:
            print("\n--- Translation Warnings ---")
            for warning in warnings:
                print(warning)
            print("--------------------------\n")

        # Now, fail if there are missing translations
        if missing_translations_details:
            error_message = ["Missing translations for keys used in HTML files:"]
            for lang, missing_keys in missing_translations_details.items():
                error_message.append(f"  Language: '{lang}'")
                for key, files in missing_keys.items():
                     file_list = ", ".join(sorted(list(files)))
                     error_message.append(f"    - Key: '{key}' (Used in: {file_list})")
            self.fail("\n".join(error_message))


if __name__ == '__main__':
    unittest.main()