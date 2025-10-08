import yt_dlp
import re

def get_transcript_from_youtube(url):
    """Get transcript using yt-dlp"""
    video_id = extract_video_id(url)
    print(f"DEBUG: Extracted video_id: {video_id}")
    if not video_id:
        return None
    
    try:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get subtitles
            if 'subtitles' in info and 'en' in info['subtitles']:
                # Manual subtitles preferred
                sub_url = info['subtitles']['en'][0]['url']
            elif 'automatic_captions' in info and 'en' in info['automatic_captions']:
                # Fall back to auto-generated
                sub_url = info['automatic_captions']['en'][0]['url']
            else:
                print("DEBUG: No subtitles found")
                return None
            
            # Fetch and parse subtitle file
            import urllib.request
            import json
            
            response = urllib.request.urlopen(sub_url)
            subtitle_data = json.loads(response.read())
            
            # Convert to our format
            transcript_list = []
            for event in subtitle_data.get('events', []):
                if 'segs' in event:
                    text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                    transcript_list.append({
                        'start': event.get('tStartMs', 0) / 1000,
                        'duration': event.get('dDurationMs', 0) / 1000,
                        'text': text.strip()
                    })
            
            print(f"DEBUG: Got {len(transcript_list)} transcript entries")
            return transcript_list
            
    except Exception as e:
        print(f"DEBUG ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def extract_video_id(url):
    patterns = [
        r"v=([A-Za-z0-9_-]+)",
        r"youtu\.be/([A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# Keep your generate_chapters, generate_title_from_text, and format_timestamp functions as-is

def generate_chapters(transcript_list):
    """
    Generate chapters from transcript with actual timestamps.
    Uses time gaps and keyword detection - completely free.
    """
    if not transcript_list or len(transcript_list) == 0:
        return []
    
    # Transition keywords that often indicate new topics
    transition_keywords = [
        'now', 'next', 'first', 'second', 'third', 'finally',
        'moving on', 'let\'s talk about', 'today we', 'in this',
        'step', 'part', 'chapter', 'section'
    ]
    
    chapters = []
    current_segment = {
        'start': transcript_list[0]['start'],
        'text_parts': []
    }
    
    for i, entry in enumerate(transcript_list):
        text_lower = entry['text'].lower()
        current_segment['text_parts'].append(entry['text'])
        
        # Calculate duration of current segment
        duration = entry['start'] - current_segment['start']
        
        # Check for transition keywords
        has_transition = any(keyword in text_lower for keyword in transition_keywords)
        
        # Check for time gap (pause > 2 seconds)
        time_gap = False
        if i < len(transcript_list) - 1:
            next_start = transcript_list[i + 1]['start']
            current_end = entry['start'] + entry.get('duration', 0)
            time_gap = (next_start - current_end) > 2
        
        # Create chapter if:
        # - We hit a transition keyword AND segment is at least 45 seconds
        # - OR there's a time gap AND segment is at least 60 seconds
        should_create_chapter = (
            (has_transition and duration >= 45) or
            (time_gap and duration >= 60)
        )
        
        if should_create_chapter or i == len(transcript_list) - 1:
            title = generate_title_from_text(current_segment['text_parts'])
            chapters.append({
                'start': int(current_segment['start']),
                'timestamp': format_timestamp(current_segment['start']),
                'title': title
            })
            
            # Start new segment
            if i < len(transcript_list) - 1:
                current_segment = {
                    'start': transcript_list[i + 1]['start'],
                    'text_parts': []
                }
    
    return chapters
def generate_title_from_text(text_parts):
    """Generate a chapter title from text segments."""
    if not text_parts:
        return "Chapter"
    
    # Combine more text
    combined = ' '.join(text_parts[:15])
    
    # Remove music/sound indicators and filler words
    filler_patterns = [
        r'\[Music\]', r'\[Applause\]', r'\[Laughter\]',
        r'\bum\b', r'\buh\b', r'\byou know\b', r'\bokay\b', r'\balright\b'
    ]
    for pattern in filler_patterns:
        combined = re.sub(pattern, '', combined, flags=re.IGNORECASE)
    
    combined = ' '.join(combined.split())
    
    # Try to get a complete sentence
    sentences = re.split(r'[.!?]', combined)
    if sentences and len(sentences[0].strip()) > 15:
        title = sentences[0].strip()
    else:
        # Take words until we hit 50-60 chars
        words = combined.split()
        title = ""
        for word in words:
            if len(title + " " + word) > 60:
                break
            title += (" " + word) if title else word
    
    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]
    else:
        return "Introduction"
    
    return title

def format_timestamp(seconds):
    """Convert seconds to YouTube timestamp format (MM:SS or H:MM:SS)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"