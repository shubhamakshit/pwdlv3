import json

csv_file = input('Enter CSV file:')

json = ''

x = json.loads(json)

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

def generate_safe_filename(filename):
  """
  Converts a filename to a safe format containing only alphabets, periods (.), and colons (:).

  Args:
      filename: The original filename to be converted.

  Returns:
      A safe filename string with only allowed characters.
  """
  # Replace all characters except alphabets, periods, and colons with underscores
  safe_filename = re.sub(r"[^\w\.\:]", "_", filename)
  return safe_filename

lines = []

for videos in x['data']:

    line = f"{generate_safe_filename(videos['title'])},{extract_uuid(videos['content'][0]['videoUrl'])[0]}"
    lines.append(line)

with open(csv_file, 'w') as f:
    f.write('\n'.join(lines))