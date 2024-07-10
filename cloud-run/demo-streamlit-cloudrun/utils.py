import requests
import json
import datetime
import config
import gcs
import streamlit as st

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



def CleanJsonOutput(str_json):
    str_json = str_json.replace("json", "").replace("JSON", "").replace("```", "")
    str_json = str_json.replace("\'", "\"")

    return str_json        



def get_date_time_string(timestamp = None):
    """Returns a string representing the current date and time.

    Args:
        timestamp: A timestamp object.

    Returns:
        A string representing the current date and time.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()

    return timestamp.strftime("%Y-%m-%d %H:%M:%S")  





def download_file(url, filename):
    """Downloads a file from a given URL and saves it to a specified filename."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded {filename} successfully.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    

def save_sound_gcs(name, media_data):
    print(f"BUCKET_NAME: {config.BUCKET}")
    gcs_uri_input = gcs.write_bytes_to_gcs(config.BUCKET, "datasets/input/" + name,  media_data, "binary/octet-stream")
    print(f"gcs_uri_input: {gcs_uri_input}")
    gcs_uri_output = f"gs://{config.BUCKET}/datasets/transcript/{name}/"
    print(f"gcs_uri_output: {gcs_uri_output}")
        
    if gcs_uri_input.endswith(".m4a") :
        mime_type="audio/x-m4a"
    elif gcs_uri_input.endswith(".mp3") :
        mime_type="audio/mpeg"
    elif gcs_uri_input.endswith(".wav") :
        mime_type="audio/x-wav" 
    elif gcs_uri_input.endswith(".ogg") :
        mime_type="audio/ogg"
    elif gcs_uri_input.endswith(".flac") :
        mime_type="audio/flac"
    else:
        mime_type="audio/*"
    
    return gcs_uri_input,gcs_uri_output,mime_type
