from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import get_transcript_from_youtube, generate_chapters, extract_video_id
from .models import VideoChapter

@api_view(['POST'])
def generate_chapters_view(request):
    youtube_url = request.data.get('youtube_url')
    
    if not youtube_url:
        return Response(
            {'error': 'youtube_url is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return Response(
            {'error': 'Invalid YouTube URL'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get transcript
    transcript_list = get_transcript_from_youtube(youtube_url)
    if not transcript_list:
        return Response(
            {'error': 'Could not fetch transcript. Video may not have captions or may be private.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate chapters
    chapters = generate_chapters(transcript_list)
    
    if not chapters:
        return Response(
            {'error': 'Could not generate chapters from transcript'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Format for YouTube description
    youtube_format = '\n'.join([f"{ch['timestamp']} {ch['title']}" for ch in chapters])
    
    # Save to database
    VideoChapter.objects.create(
        youtube_url=youtube_url,
        video_id=video_id,
        title='',  # We can fetch this later with YouTube API if needed
        chapters_json=chapters
    )
    
    return Response({
        'video_id': video_id,
        'chapters': chapters,
        'youtube_format': youtube_format
    })