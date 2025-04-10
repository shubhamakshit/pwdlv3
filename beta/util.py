import json
import re

def extract_uuid(text):
  """
  Extracts UUIDs from a string using a regular expression.

  Args:
      text: The string to search for UUIDs.

  Returns:
      A list of extracted UUIDs, or an empty list if none are found.
  """
  pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
  matches = re.findall(pattern, text)
  return matches

def generate_safe_file_name(name):
    """
    Generates a safe file name by replacing spaces with underscores and removing special characters.

    Args:
        name: The original name to be converted.

    Returns:
        A string that is a safe file name.
    """
    # Replace spaces with underscores and remove special characters
    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
    return safe_name