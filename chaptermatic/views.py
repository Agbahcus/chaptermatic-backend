from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_chapters, format_timestamp
from .models import VideoChapter

@api_view(['POST'])
def generate_chapters_view(request):
    transcript_data = request.data.get('transcript')
    youtube_url = request.data.get('youtube_url')
    video_id = request.data.get('video_id')
    
    if not transcript_data:
        return Response(
            {'error': 'transcript is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate transcript format
    if not isinstance(transcript_data, list) or len(transcript_data) == 0:
        return Response(
            {'error': 'Invalid transcript format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate chapters
    try:
        chapters = generate_chapters(transcript_data)
        
        if not chapters:
            return Response(
                {'error': 'Could not generate chapters from transcript'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Format for YouTube description
        youtube_format = '\n'.join([f"{ch['timestamp']} {ch['title']}" for ch in chapters])
        
        # Save to database (optional)
        if youtube_url and video_id:
            VideoChapter.objects.create(
                youtube_url=youtube_url,
                video_id=video_id,
                title='',
                chapters_json=chapters
            )
        
        return Response({
            'video_id': video_id or 'unknown',
            'chapters': chapters,
            'youtube_format': youtube_format
        })
    except Exception as e:
        return Response(
            {'error': f'Error generating chapters: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )