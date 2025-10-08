from django.db import models


class VideoChapter(models.Model):
    youtube_url = models.URLField()
    video_id = models.CharField(max_length=20)
    title = models.CharField(max_length=500, blank=True)
    chapters_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.video_id} - {self.title or 'Untitled'}"