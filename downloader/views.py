from django.shortcuts import render
from django.http import FileResponse, HttpResponseBadRequest
from .forms import YouTubeForm
from pytubefix import YouTube
import os
import subprocess
from django.conf import settings
import tempfile
import threading

def download_video(request):
    if request.method == 'POST':
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                yt = YouTube(url)
               
                # Get highest resolution video-only stream
                video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', mime_type='video/mp4').order_by('resolution').desc().first()
                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

                # Create temporary files for video and audio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_file:
                    video_path = video_file.name
                    video_stream.download(output_path=os.path.dirname(video_path), filename=os.path.basename(video_path))

                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as audio_file:
                    audio_path = audio_file.name
                    audio_stream.download(output_path=os.path.dirname(audio_path), filename=os.path.basename(audio_path))

                # Set output path (overwrite existing file)
                output_path = os.path.join(settings.MEDIA_ROOT, 'final_output.mp4')

                # Ensure MEDIA_ROOT exists
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

                # Combine using ffmpeg (overwrite existing file)
                command = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -y "{output_path}"'
                subprocess.run(command, shell=True, check=True)

                # Clean up temporary files
                def cleanup_files():
                    os.remove(video_path)
                    os.remove(audio_path)

                # Start cleanup in a new thread
                threading.Thread(target=cleanup_files).start()

                # Serve the combined file for download
                response = FileResponse(open(output_path, 'rb'), as_attachment=True, filename='final_output.mp4')

                return response

            except Exception as e:
                return HttpResponseBadRequest(f"Error: {str(e)}")
    else:
        form = YouTubeForm()
    return render(request, 'downloader/download.html', {'form': form})