
from datetime import timedelta
from typing import List, Optional, Sequence, cast

import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

from moviepy.editor import VideoFileClip, TextClip
from google.cloud import videointelligence_v1 as vi

def get_video_text(results: vi.VideoAnnotationResults, min_frames: int = 15):
    annotations = results.text_annotations

    allText = []

    print(" Detected text ".center(80, "-"))
    for annotation in annotations:
        for text_segment in annotation.segments:
            frames = len(text_segment.frames)
            # if frames < min_frames:
            #     continue
            text = annotation.text
            allText.append(text)
            confidence = text_segment.confidence
            start = text_segment.segment.start_time_offset
            seconds = segment_seconds(text_segment.segment)
            print(text)
            print(f"  {confidence:4.0%} | {start} + {seconds:.1f}s | {frames} fr.")
    return allText

def print_video_text(results: vi.VideoAnnotationResults, min_frames: int = 15):
    annotations = sorted_by_first_segment_end(results.text_annotations)

    print(" Detected text ".center(80, "-"))
    for annotation in annotations:
        for text_segment in annotation.segments:
            frames = len(text_segment.frames)
            if frames < min_frames:
                continue
            text = annotation.text
            confidence = text_segment.confidence
            start = text_segment.segment.start_time_offset
            seconds = segment_seconds(text_segment.segment)
            print(text)
            print(f"  {confidence:4.0%} | {start} + {seconds:.1f}s | {frames} fr.")


def sorted_by_first_segment_end(
    annotations: Sequence[vi.TextAnnotation],
) -> Sequence[vi.TextAnnotation]:
    def first_segment_end(annotation: vi.TextAnnotation) -> int:
        return annotation.segments[0].segment.end_time_offset.total_seconds()

    return sorted(annotations, key=first_segment_end)


def segment_seconds(segment: vi.VideoSegment) -> float:
    t1 = segment.start_time_offset.total_seconds()
    t2 = segment.end_time_offset.total_seconds()
    return t2 - t1

def split_video(input_video, output_video, start : int, end: int):

    clip = VideoFileClip(input_video, verbose=True, audio=True).subclip(start,end)
    clip.write_videofile(output_video, verbose=True)

def split_video_shots(input_video, shots):
    print(f"Start split video shots {input_video}")
    print(shots)
    if len(shots) == 0:
        print(f"No video shots found in {input_video}")
        return
    

    print(f" Video shots: {len(shots)} ".center(40, "-"))
    for i, shot in enumerate(shots):
        print("DEBUG - shot")
        print(shot)
        t1 = shot.start_time_offset.total_seconds()
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")
        output_video = f"{input_video } - {i} - {t1} - {t2}.mp4"
        
        split_video(input_video=input_video, output_video=output_video, start=t1, end=t2)
        yield output_video, t1, t2

def split_video_shots_time_min(input_video, shots, min_shot_time):
    print(f"Start split video shots {input_video}")
    print(shots)
    if len(shots) == 0:
        print(f"No video shots found in {input_video}")
        return
    

    print(f" Video shots: {len(shots)} ".center(40, "-"))
    index = 0
    extend_chunk = False
    
    for i, shot in enumerate(shots):
        print("DEBUG - shot")
        print(shot)
        if extend_chunk == False:
            t1 = shot.start_time_offset.total_seconds()
        
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")

        output_video = f"{input_video } - {index} - {t1} - {t2}.mp4"        
        if (t2 -t1) > min_shot_time:
            extend_chunk = False

            print(f"input_video={input_video}, output_video={output_video}, start={t1}, end={t2}")
            index = index+1

            split_video(input_video=input_video, output_video=output_video, start=t1, end=t2)
            yield output_video, t1, t2
        else:
            print(f"SKIP - input_video={input_video}, output_video={output_video}, start={t1}, end={t2}")
            extend_chunk = True



def print_frames(results: vi.VideoAnnotationResults, likelihood: vi.Likelihood):
    frames = results.explicit_annotation.frames
    frames = [f for f in frames if f.pornography_likelihood == likelihood]

    print(f" {likelihood.name} frames: {len(frames)} ".center(40, "-"))
    for frame in frames:
        print(frame.time_offset)
        
def print_video_shots(results: vi.VideoAnnotationResults):
    shots = results.shot_annotations
    print(f" Video shots: {len(shots)} ".center(40, "-"))
    for i, shot in enumerate(shots):
        t1 = shot.start_time_offset.total_seconds()
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")
        

        
def print_video_labels(results: vi.VideoAnnotationResults):
    labels = sorted_by_first_segment_confidence(results.segment_label_annotations)

    print(f" Video labels: {len(labels)} ".center(80, "-"))
    for label in labels:
        categories = category_entities_to_str(label.category_entities)
        for segment in label.segments:
            confidence = segment.confidence
            t1 = segment.segment.start_time_offset.total_seconds()
            t2 = segment.segment.end_time_offset.total_seconds()
            print(
                f"{confidence:4.0%}",
                f"{t1:7.3f}",
                f"{t2:7.3f}",
                f"{label.entity.description}{categories}",
                sep=" | ",
            )


def sorted_by_first_segment_confidence(
    labels: Sequence[vi.LabelAnnotation],
) -> Sequence[vi.LabelAnnotation]:
    def first_segment_confidence(label: vi.LabelAnnotation) -> float:
        return label.segments[0].confidence

    return sorted(labels, key=first_segment_confidence, reverse=True)


def category_entities_to_str(category_entities: Sequence[vi.Entity]) -> str:
    if not category_entities:
        return ""
    entities = ", ".join([e.description for e in category_entities])
    return f" ({entities})"
    

def export_audio(mp4_file):

    # Define the input video file and output audio file
    mp3_file = mp4_file[0:-1] + "3" #"audio.mp3"

    # Load the video clip
    with VideoFileClip(mp4_file, verbose=True, audio=True) as video_clip:

        # Extract the audio from the video clip
        audio_clip = video_clip.audio

        # Write the audio to a separate file
        audio_clip.write_audiofile(mp3_file)

        # Close the video and audio clips
        audio_clip.close()
        

    print("Audio extraction successful!")
    return mp3_file



from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip


def combine_audio_into_video( audio_paths, output_path):
    """Combines multiple audio files into a video file.

    Args:
        video_path: Path to the input video file (MP4).
        audio_paths: List of paths to the audio files to combine.
        output_path: Path to save the output video file (MP4).
    """

    # Load video clip
    
    #video_clip = VideoFileClip(output_path)
    video_clip = TextClip("...", fontsize=70, stroke_width=5)

    
    # Load audio clips
    audio_clips = [AudioFileClip(path) for path in audio_paths]
    total_audio = sum([audio.duration for audio in audio_clips])
    print(f"total_audio = {total_audio}")
    video_clip.set_duration(total_audio)
    
    # Ensure audio clips are the same length as the video. If not, the shorter will loop.
    #final_audio = CompositeAudioClip([audio.set_duration(video_clip.duration) for audio in audio_clips])
    final_audio = CompositeAudioClip(audio_clips)

    # Combine and save the video
    final_clip = video_clip.set_audio(final_audio)
    
    
    final_clip.set_duration(total_audio).write_videofile(output_path, codec="libx264", audio = True, fps=24)

SILENCE_LENGTH = 200  # In Milliseconds
from pydub import AudioSegment
import os
from pathlib import Path


def combine_audio_files(audio_files: List[str], filename: str) -> str:
    full_audio = AudioSegment.silent(duration=SILENCE_LENGTH)

    for file in audio_files:
        sound = AudioSegment.from_mp3(file)
        silence = AudioSegment.silent(duration=SILENCE_LENGTH)
        full_audio += sound + silence
        os.remove(file)

    outfile_name = f"{Path(filename).stem}-complete.mp3"
    full_audio.export(outfile_name, format="mp3")
    return outfile_name