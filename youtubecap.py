from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'mB0EBW-vDSQ'
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# Convert full transcript to plain text
full_text = "\n".join([entry['text'] for entry in transcript])

with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
