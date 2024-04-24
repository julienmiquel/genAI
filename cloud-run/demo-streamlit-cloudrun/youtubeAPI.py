from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_url):
    video_id = video_url.split('v=')[-1]
    try:
        transcripts = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['fr', 'en', 'es'])
        transcripts = transcript.fetch()
    return transcripts
