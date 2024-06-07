import re
import os
import requests
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import io

API_URL = "https://api-inference.huggingface.co/models/goofyai/3d_render_style_xl"
headers = {"Authorization": "Bearer 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"}

# Method to query the Hugging Face model
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# Read the text file
with open("generated_text.txt", "r") as file:
    text = file.read()

# Split the text by , and .
paragraphs = re.split(r"[,.]", text)

# Create Necessary Folders
os.makedirs("audio", exist_ok=True)
os.makedirs("images", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# Define the desired video resolution
video_width = 1920
video_height = 1080

# Define text parameters
fontsize = int(video_width / 40)  # Adjust font size according to video width
font = 'Truculenta'  # Change font style to your desired font
bg_color = 'black'  # Background color for text
txt_color = 'white'  # Text color
text_gap = int(video_height / 40)

# Loop through each paragraph and generate an image for each
i = 1
for para in paragraphs[:-1]:
    # Query the Hugging Face model to generate an image
    image_bytes = query({
        "inputs": para.strip(),
    })
    image = Image.open(io.BytesIO(image_bytes))

    # Resize the image to match the video resolution
    image = image.resize((video_width, video_height))

    image.save(f"images/image{i}.jpg")
    print("The Generated Image Saved in Images Folder!")

    # Create gTTS instance and save to a file
    tts = gTTS(text=para, lang='en', slow=False)
    tts.save(f"audio/voiceover{i}.mp3")
    print("The Paragraph Converted into VoiceOver & Saved in Audio Folder!")

    # Load the audio file using moviepy
    print("Extract voiceover and get duration...")
    audio_clip = AudioFileClip(f"audio/voiceover{i}.mp3")
    audio_duration = audio_clip.duration

    # Load the image file using moviepy
    print("Extract Image Clip and Set Duration...")
    image_clip = ImageClip(f"images/image{i}.jpg").set_duration(audio_duration)

    # Create a text clip with background and adjust font size and style
    text_clip = TextClip(para, fontsize=fontsize, font=font, color=txt_color, bg_color=bg_color, align='center')
    # text_clip = TextClip(para, fontsize=fontsize, font=font, color=txt_color, bg_color=bg_color, align='center')
    text_clip = text_clip.set_position(('center', video_height - fontsize - text_gap)).set_duration(audio_duration)

    # text_clip = text_clip.set_position(('center', 'bottom')).set_duration(audio_duration)

    # Use moviepy to create a final video by concatenating
    # the audio, image, and text clips
    print("Concatenate Audio, Image, Text to Create Final Clip...")
    clip = image_clip.set_audio(audio_clip)
    video = CompositeVideoClip([clip, text_clip])

    # Save the final video to a file
    video = video.write_videofile(f"videos/video{i}.mp4", fps=24)
    print(f"The Video{i} Has Been Created Successfully!")
    i += 1


def extract_number(filename):
    return int(re.search(r'\d+', filename).group())

# Get a list of video files
video_files = os.listdir("videos")
print(video_files)
# Sort the video files based on the numeric part of the filename
sorted_video_files = sorted(video_files, key=extract_number)
print(sorted_video_files)
# Create VideoFileClip objects for each video file
clips = [VideoFileClip(f"videos/{filename}") for filename in sorted_video_files]

# Concatenate all the clips
final_video = concatenate_videoclips(clips, method="compose")

# Write the final video to a file
final_video.write_videofile("finalvideo.mp4")
print("The Final Video Has Been Created Successfully!")

# clips = []
# l_files = os.listdir("videos")
# for file in l_files:
#     clip = VideoFileClip(f"videos/{file}")
#     clips.append(clip)

# print("Concatenate All The Clips to Create a Final Video...")
# final_video = concatenate_videoclips(clips, method="compose")
# final_video = final_video.write_videofile("final_video.mp4")
# print("The Final Video Has Been Created Successfully!")
