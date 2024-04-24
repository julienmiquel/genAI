import time
import os

import config as config
import gcs as gcs

#############################
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions
from google.cloud import speech_v2

#############################

def get_sttClient():
    
    client = SpeechClient(    client_options=ClientOptions(api_endpoint=f"{config.REGION}-speech.googleapis.com"))
    return client

def get_recognizer(language_code : str):

    recognizer_id = getReconizerID(language_code)
    client = get_sttClient()
    try:
        
        # Initialize request argument(s) projects/59602385614/locations/us-central1/recognizers/chirp-fr-fr-demo1
        
        request = speech_v2.GetRecognizerRequest(        
            name=f"projects/{config.PROJECT_ID}/locations/{config.REGION}/recognizers/{recognizer_id}",        )
        recognizer = client.get_recognizer(request)
        # Handle the response
        print(recognizer)
        return recognizer
    except Exception as e:
        print(e)
        print("Error getting recognizer. Create new one.")

    recognizer_request = cloud_speech.CreateRecognizerRequest(
        parent=f"projects/{config.PROJECT_ID}/locations/{config.REGION}",
        recognizer_id=recognizer_id,
        recognizer=cloud_speech.Recognizer(
            language_codes=[language_code],
            model="chirp",
        ),
    )
    
    create_operation = client.create_recognizer(request=recognizer_request)
    recognizer = create_operation.result()

    return recognizer

def getReconizerID(language_code : str):
    return f"chirp-{language_code.lower()}-demo1"

def transcribe_gcs(gcs_uri_input: str, gcs_uri_output: str, language_code) -> str:
    """Asynchronously transcribes the audio file specified by the gcs_uri.

    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.

    Returns:
        The generated transcript from the audio file provided.
    """
    from google.cloud.speech_v2 import SpeechClient
    from google.cloud.speech_v2.types import cloud_speech
    from google.api_core.client_options import ClientOptions

    client = SpeechClient(    client_options=ClientOptions(api_endpoint=f"{config.REGION}-speech.googleapis.com"))
    
    recognizer = get_recognizer(language_code    )

    print(f"Created recognizer: {recognizer.name}")

    long_audio_config = cloud_speech.RecognitionConfig(
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True, enable_word_time_offsets=True
        ),
        auto_decoding_config={},
    )

    long_audio_request = cloud_speech.BatchRecognizeRequest(
        recognizer=recognizer.name,
        recognition_output_config={
            "gcs_output_config": {"uri": f"{gcs_uri_output}/transcriptions"}
        },
        files=[{"config": long_audio_config, "uri": gcs_uri_input}],
    )

    print("start stt operation")
    long_audio_operation = client.batch_recognize(request=long_audio_request)
    print("finish stt operation")
    return long_audio_operation

