from django.urls import path
from . import views

urlpatterns = [
    path('generate-chapters/', views.generate_chapters_view, name='generate-chapters'),
]