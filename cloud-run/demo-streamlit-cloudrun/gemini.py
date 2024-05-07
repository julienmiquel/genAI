# @title Import librairies

import base64
import os


from google.cloud import storage

import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

import config as config
# @title Init variables



# # @title Input files

# file_1 = "/datasets/sound/input/Lionel 2mn.m4a"  # @param {type:"string"}
# file_2 = "/datasets/sound/input/Lionel2.m4a"  # @param {type:"string"}

# files = [
#     BUCKET_URI + file_1,
#     BUCKET_URI + file_2
# ]

# audios = [Part.from_uri(file, mime_type="audio/x-m4a") for file in files]
# # replace the extention by txt
# results = [file.replace(".m4a", ".json") for file in files]


# @title Utils functions

# Write function CleanData where data is string parameter and find the first '{' character and the last '}' character and keep only the data inside
def CleanData(data):
    import json
    """Cleans the data by removing everything outside the first '{' and last '}' characters.

  Args:
    data: The data to clean.

  Returns:
    The cleaned data.
  """

    start = data.find('{')
    end = data.rfind('}')
    if start == -1 or end == -1:
        return ""

    data_clean = data[start:end+1]

    return data_clean


def LoadJsonData(data):
    import json
    return json.loads(data)


# @title generate function with gemini

def generate_transcript_from_audio(audio, language):
    vertexai.init(project=config.PROJECT_ID, location=config.REGION)

    generation_config = {
        "max_output_tokens": 8192,
        "top_p": 1.0,
        "temperature": 0.0,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    model = GenerativeModel(config.GEMINI_MULTIMODAL_MODEL_NAME )

    task = f"""

  <Task>
  Transcribe in {language} this recording from the beginning to the end of the recording.
  Identify each persons with their name and their genre if possible.
  </Task>

  <answer_format>
  JSON keys: speaker, speaker_name, time_start, time_stop, text.
  speaker is the speaker id, speaker_name is the name of the speaker.
  time_start and time_stop are the full time in seconds and not truncated.
  text is the text of the speaker.
  </answer_format>
  """

    responses = model.generate_content(
        ["<interview>", audio, "</interview>", task],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    result = []
    for response in responses:
        value = response.text
        print(value, end="")
        result.append(value)
        yield (value, None)

    yield (None, CleanData("".join(result)))


# @title Execute the code to get transcript in cloud storage



# storage_client = storage.Client()
# for audio, result in zip(audios, results):
#   print("\n" + 80*"*" + "\n")
#   print(audio.file_data.file_uri)

#   transcribe = generate_transcript_from_audio(audio)
  
#   print(transcribe)
  
#   # write result in google cloud storage
#   bucket_name, blob_name = result.split("gs://", 1)[1].split("/", 1)
  
#   bucket = storage_client.bucket(bucket_name)
#   blob = bucket.blob(blob_name)

#   # write the file
#   with blob.open("w") as f:
#       f.write(transcribe)
  