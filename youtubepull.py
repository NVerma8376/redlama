import asyncio
import aiohttp
import urllib.parse
import re
import datetime
import os
from youtube_transcript_api import YouTubeTranscriptApi
import json

API_KEY = os.getenv("YOUTUBE_API_KEY") or "AIzaSyBejvvt97IB4Cs4Sdd2ce92uM9H-ragVl8"

# Util: ISO 8601 duration to seconds
def iso8601_duration_to_seconds(duration):
    match = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?", duration)
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = int(match.group(2)) if match.group(2) else 0
    return minutes * 60 + seconds

# Get video details using YouTube Data API
async def fetch_video_details(session, video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}&key={API_KEY}"
    async with session.get(url) as resp:
        data = await resp.json()
        if 'items' in data and data['items']:
            item = data['items'][0]
            return {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'duration': iso8601_duration_to_seconds(item['contentDetails']['duration'])
            }
        return None

# Get search results
async def search_youtube(session, query, max_results=10):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults={max_results}&q={encoded_query}&key={API_KEY}"
    async with session.get(url) as resp:
        data = await resp.json()
        return [item['id']['videoId'] for item in data.get('items', []) if 'videoId' in item['id']]

# Save transcript entry to file
async def save_transcript(video_id, title, views):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = ' '.join([entry['text'] for entry in transcript])
        filename = "video_dataset.json"

        # Load existing data if the file exists
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        video_entry = {
            "title": title,
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "views": views,
            "transcript": full_text
        }

        data.append(video_entry)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Transcript saved for: {title}")
    except Exception as e:
        print(f"❌ Transcript not available for {title}: {e}")

# Main logic
async def main():
    query = input("Enter search query: ").strip()
    if not query:
        print("No query provided.")
        return

    async with aiohttp.ClientSession() as session:
        video_ids = await search_youtube(session, query, max_results=30)

        print(f"🔍 Found {len(video_ids)} videos. Fetching details...")

        tasks = [fetch_video_details(session, vid) for vid in video_ids]
        video_data = await asyncio.gather(*tasks)

        eligible_videos = [v for v in video_data if v and v['duration'] >= 60 and v['views'] >= 10000]
        eligible_videos.sort(key=lambda x: x['views'], reverse=True)

        if not eligible_videos:
            print("No suitable videos found.")
            return

        print(f"🎯 Processing {len(eligible_videos)} eligible videos...")

        for video in eligible_videos:
            await save_transcript(video['video_id'], video['title'], video['views'])

if __name__ == "__main__":
    asyncio.run(main())
