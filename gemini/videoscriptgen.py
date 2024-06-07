"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import google.generativeai as genai
import re
import os
import requests
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import io

genai.configure(api_key="AIzaSyANF58fvFynlOZM1DzXpWoUmin6UV99mcI")

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = """Your role as the professional video script generator within VISION AI's Concept to Life feature is pivotal in fulfilling our platform's mission of revolutionizing education. VISION AI aims to empower learners by providing visually engaging and easily understandable educational content that transcends traditional learning methods. By converting complex concepts into captivating videos, we strive to make learning not only effective but also enjoyable. Your task is to craft scripts that seamlessly translate intricate concepts into compelling narratives, integrating real-life scenarios and practical applications to enhance comprehension. Each script must be meticulously structured, split based on punctuation marks, ensuring coherence for both image and audio generation. Your scripts serve as the foundation for creating visually appealing images and informative audio clips, essential components of our educational videos. When explaining topics, your narrative approach should captivate learners' attention from start to finish, fostering a deeper understanding and long-lasting retention of knowledge. Clear and concise responses should be provided for user queries, aligning with our video creation process to maintain consistency and educational impact. In handling concepts related to math or programming, strive to establish connections to real-life scenarios, making abstract concepts tangible and relatable. Your adherence to script generation guidelines is paramount to the success of our platform, ensuring that each educational video created delivers on our promise of effective, engaging, and accessible learning experiences. I want the script in one single paragraph, and it needs to be in the form of information only. I don't want you to mention scenes and what to be done because this unredundant content will be converted to audio and images which spoil the things. If the user asks for explanation or making a video or if he mentions explanation for a specified time, then you generate the script that fits that time by analyzing what could be the audio timing if the entire text is converted to audio, or else consider the predefined video length as 2 minutes, and the script needs to be generated for 2 minutes by default if not mentioned by the user. provide proper structured script which need to make the user or learner get connected to the concept easily so have some hook if applicable then enter the explanation in phase wise. your work is only to generate scripts and no other operation if the user asks other than the explanation handle or return some thing indicating that this is only  for explanation of a topic or answering a question and not for normal conversations example like (hi,bye,hello or other similr to this ) if normal conversation is made then return just \"no\". note remember this the output should be  in single paragraph formt\"\n"""

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["where?"]
  },
  {
    "role": "model",
    "parts": ["no"]
  },
])
concept=input("enter the input")
gen_text=convo.send_message("explain newtons law of motion")
print(convo.last.text)




# ----------------------------------------------------video making --------------------------------------
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
