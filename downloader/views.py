from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip


yt = YouTube('https://www.youtube.com/watch?v=X32dce7_D48')

# getting video stream
video_stream = yt.streams.filter(progressive=False, res="1080p", video_codec='avc1.640028').first()
video_path = video_stream.download(filename='video.mp4')

# getting audio stream
audio_stream = yt.streams.filter(progressive=False, mime_type='audio/webm', abr='160kbps', audio_codec='opus').first()
audio_path = audio_stream.download(filename='audio.webm')

# load audio and video files
video_clip = VideoFileClip(video_path)
audio_clip = AudioFileClip(audio_path)

# combine audio and video
final_clip = video_clip.set_audio(audio_clip)

# Save the final video
final_clip.write_videofile("final_video.mp4", codec='libx264', audio_codec='aac')

# Close the clips
video_clip.close()
audio_clip.close()