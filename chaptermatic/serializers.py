from rest_framework import serializers
from .models import VideoChapter

class VideoChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChapter
        fields = ['id', 'youtube_url', 'video_id', 'title', 'chapters_json', 'created_at']
        read_only_fields = ['id', 'video_id', 'title', 'chapters_json', 'created_at']

class ChapterGenerationSerializer(serializers.Serializer):
    youtube_url = serializers.URLField(required=True)
    
    def validate_youtube_url(self, value):
        # Basic YouTube URL validation
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError("Must be a valid YouTube URL")
        return value