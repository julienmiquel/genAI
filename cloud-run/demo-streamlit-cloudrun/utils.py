import datetime

def create_timestamped_name(prefix):
  """Creates a timestamped name.

  Args:
    prefix: The prefix of the name.

  Returns:
    A timestamped name.
  """

  timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
  return f"{prefix}_{timestamp}"


import re

def extract_speak_content(text):
    """Extracts all text within <speak> and </speak> tags from non-valid HTML text.

    Args:
        text: The non-valid HTML text to search.

    Returns:
        A list of strings, each representing the text content within a <speak> tag.
    """
    text = text.replace("< speak", "<speak").replace("< ","<")

    pattern = r'<speak>(.*?)</speak>'  # Regex to match content between tags
    matches = re.findall(pattern, text, re.DOTALL)  # Find all matches, including newlines
    return matches