from flask import Flask, render_template, request, redirect, url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_user, logout_user,login_required,current_user
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
# -------required for visonai ------------------------
import google.generativeai as genai
import re
import shutil
import os
import requests
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import io
import pyttsx3 as p
import speech_recognition as sr




global engine
global recognizer
global recognized_text



recognizer = sr.Recognizer()

    # Initialize pyttsx3 engine
engine = p.init()

    # Function to speak
def speak(text):
    engine.say(text)
    engine.runAndWait()


def do_listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Adjust for ambient noise and energy threshold
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.energy_threshold = 300  # Adjust this threshold as needed
        print("Listening...")
        audio = recognizer.listen(source)
            
        try:
            text = recognizer.recognize_google(audio)
            print("User:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return "Sorry, I didn't catch that."
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return "Sorry, I didn't catch that."

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'visonai'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/visonai'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)

        
@app.route("/")
def home():
   return render_template('index.html')

# ----------------------------------------------authentication pages -----------------------------------

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            
            return redirect(url_for('home'))
        else:
            flash( 'Invalid email or password',"danger")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists","danger")
            return render_template('signup.html')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# -----------------------------------------------voice  chat message-------------------
# @app.route('/send_message', methods=['POST'])
# def send_message():
#     user_input = request.json['message']
    
#     genai.configure(api_key="AIzaSyCKKEPd0i7DqP-nd3yvBWeEHBpO3OHkppA")
#     # Get conversation history
#     conversation_history = convo.history

#     # Add user input to history
#     conversation_history.append(user_input)

#     # Set up the model
#     generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 0,
#     "max_output_tokens": 8192,
#     }

#     safety_settings = [
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     ]

#     system_instruction = "You are an integral part of VISON AI, serving as a feature called Voice Articulate. Your role is to function as a personalized AI teaching assistant for learners of all backgrounds and ages. Your primary objective is to facilitate easy and effective comprehension of concepts by captivating the user's attention through engaging explanations and responses. Emphasize real-life scenarios to help users relate to the content and remember it better. Craft your responses to provide users with a visual experience through their own imagination, ensuring clarity and understanding. Prioritize efficiency by breaking down lengthy explanations into digestible parts and regularly checking in with the user for feedback and comprehension. When explaining a topic, start with a hook to grab attention, provide a brief background, and then delve into the topic with real-life examples. Pause after each segment to ask the user if they have questions or if they want to continue. Offer summaries of learned content upon request and handle quiz generation by asking for the topic, providing MCQ questions, offering clues if needed, and confirming answers with explanations. Handle unexpected instances with care, ensuring the learner is not overloaded with information and maintaining focus on effective learning. This instruction aims to guide you in delivering your role effectively within the VISON AI framework, ensuring a seamless and enriching learning experience for users . if the user intracts don't give lengthy introductions ask how can you help in some attractive manner and you name is .dont feed the big responses at at a time even if it is lengthy give it in small parts and ask whether you can go to next part dont do this for any kind of responses.your name is  'easify' .never have emojis or facial expressions or expression symbols strictly prohibit them." 

#     model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
#                                 generation_config=generation_config,
#                                 system_instruction=system_instruction,
#                                 safety_settings=safety_settings)

#     convo = model.start_chat(history=conversation_history)
#     print(user_input)
#     convo.send_message(user_input)
#     print(convo.last.text)
#     model_response = convo.last.text
#     speak(model_response)
#     return jsonify({'message': model_response})


# Define a global variable to store conversation history





# Define a global variable to store conversation history
conversation_history = []

concept_history=[]

auto=[]


@app.route('/send_message', methods=['POST'])
def send_message():
    global conversation_history
    
    # Get user input from the request
    user_input = request.json['message']
    
    # Add user input to the conversation history
    conversation_history.append({"role": "user", "parts": [user_input]})
    
    # Configure the AI assistant
    # genai.configure(api_key="AIzaSyCKKEPd0i7DqP-nd3yvBWeEHBpO3OHkppA")
    genai.configure(api_key="AIzaSyDrgdRG6s55riY4_d2ARznFkOrbnFmMFZI")
    
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

    system_instruction = """
    your name is easify your role as a personal AI teaching assistant is pivotal in facilitating effective learning experiences for users of all backgrounds and ages. Your mission is to convey concepts in a clear, engaging, and accessible manner,catering to auditory and visually impaired learners alike. Begin each response with a captivating "hook" to grab the learner's attention, provide concise "background information", and dive into "clear explanations' supported by "real-life examples".never give lengthy responses at a streatch. Pause after each part to check for understanding and offer summaries upon request. Generate quizzes tailored to the learner's understanding, handle questions effectively, and avoid overwhelming learners with lengthy responses. Adapt to unexpected scenarios while maintaining focus on enhancing the learning experience through stimulating and comprehensible content delivery. Together, let's empower learners and unlock their full potential with VISON AI's Voice Articulate feature! Your name is "easify". Please ensure responses do not contain any emojis, expression symbols, or other extra symbols such as '***' or '##', as these may detract from the user experience when converted to speech.i dont want this emojis in your responses like thsi "Hey there! 👋 It's great to hear from you again. What would you like to learn about today? 😊" i just need text.i  don't want this kind of responses which are lengthy and unwanted symbols like ***,#### in this example response "**Unraveling the Lunar Phases** As the Moon orbits Earth, the amount of sunlight it reflects changes, creating the different phases we observe. Imagine the Moon as a dancer, gracefully moving through a cycle of appearances. Let's explore these phases: * **New Moon:** When the Moon is between Earth and the Sun, its illuminated side faces away from us, making it invisible in the night sky. * **Waxing Crescent:** As the Moon moves eastward in its orbit, a sliver of its illuminated side becomes visible, resembling a crescent. * **First Quarter:** Half of the Moon's illuminated side is visible, appearing as a half-circle. * **Waxing Gibbous:** More than half of the Moon's illuminated side is visible, and it continues to grow. also i  dont want responses to be with  this way of presenting the content to user avoid this "* **" or "##" or any other such symbols  i strictly don't want such symbols or emojis or facial expression or any other kind of emojis in the response so  i need only the  text thats it don't use symbols for representing points or start or end of a response better use the bulletiens or spacing at the  time of your response ."""
    # system_instruction ="you are part of vison ai feature that is voice articulate your work is to make the learner or user to understand the concept what he ask .so if a user ask a concept explanation you need to start with a hook about the topic, background of the topic ,then get into topic with real life examples and applicatiosn so the user can get the concept easily and effectively. if the user ask to give a question or want to test his knowledge the based on the requested topic give a mcq based question then provide clue on request and based on the answer say whether it is correct or not and also say which answer is correct and why.if any other scenario occur handle it in such a way that the user is not overloaded with large responses .the responses should be in digestable parts so that it will be easy for the learner to understand and have interest. so give the parts in meaningful parts which are digestable to the learner afetr each part ask the user whether you can get into another topic or if the learner  has any question.based on the learner response you carry on the conversation.the entire process should be like there is a another human explaining the concept to the learner.don't start header with '##','###' and dont use '***' for end "
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings)

    # Start the chat with the existing conversation history
    convo = model.start_chat(history=conversation_history)
    
    # Send user input to the conversation
    print(user_input)
    convo.send_message(user_input)
    
    # Get the AI assistant's response
    model_response = convo.last.text
    print(model_response)
    text = text.replace('#', '').replace('*', '').replace('###', '')
    print(model_response)
    
    # Append the bot's response to the conversation history
    conversation_history.append({"role": "model", "parts": [model_response]})
    
    # Return the response to the client
    return jsonify({'message': model_response})




# ------------------------------------------------speech recognition------------------------------------------
@app.route('/start-speech-recognition', methods=['GET'])
def start_speech_recognition():
    
    recognized_text=do_listen()
    
    
    # Return the recognized text to the frontend
    return recognized_text

# ----------------------------------------------------features page -------------------------------------------
@app.route("/features", methods=['POST','GET'])
@login_required
def features():
    
    return render_template('features.html')


# -------------------------------------------voice articulate design page -------------------------------------

@app.route("/voicearticulate", methods=['POST','GET'])
@login_required
def voicearticulate():
    return render_template('voicearticulate.html')

# ---------------------------------------- voice articulate ---------------------------------------------------

@app.route("/voicechat", methods=['POST','GET'])
@login_required
def voicechat():
    return render_template('voicechat.html')
    
# ---------------------------------------------concept to life design page-----------------------------

@app.route("/concepttolife",methods=['POST', 'GET'])
@login_required
def concepttolife():
    return render_template('concepttolife.html')



# ---------------------------method to delete the previously generated properties --------------------
def cleanup_previous_files(exclude_final_video=False):
    # Define the directory paths for audio, images, and videos
    audio_dir = "audio"
    images_dir = "images"
    videos_dir = "videos"

    # check if the folders really exist if not skip this process 
    for directory in [audio_dir, images_dir, videos_dir]:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Skipping cleanup.")
            return

    # Remove all files in the audio directory
    for filename in os.listdir(audio_dir):
        file_path = os.path.join(audio_dir, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path}, {e}")

    # Remove all files in the images directory
    for filename in os.listdir(images_dir):
        file_path = os.path.join(images_dir, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path}, {e}")

    # Remove all files in the videos directory, excluding the final video if specified
    for filename in os.listdir(videos_dir):
        file_path = os.path.join(videos_dir, filename)
        try:
            if exclude_final_video and filename == "finalvideo.mp4":
                continue
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path}, {e}")

    print("Previous files have been cleaned up successfully.")

    # Rename the final video if it exists
    final_video_path = "static/finalvideo.mp4"
    if os.path.exists(final_video_path):
        try:
            # Move the final video to a new location or rename it with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_final_video_path = f"static/previous_videos/finalvideo_{timestamp}.mp4"
            shutil.move(final_video_path, new_final_video_path)
            print(f"Final video renamed to: {new_final_video_path}")
        except Exception as e:
            print(f"Error renaming final video: {e}")

# -------------------------------------------------watch the generated video --------------------------------------


@app.route("/conceptchat",methods=['POST', 'GET'])
@login_required
def conceptchat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        genai.configure(api_key="AIzaSyDrgdRG6s55riY4_d2ARznFkOrbnFmMFZI")

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

        system_instruction = """Your role as the professional video script generator within VISION AI's Concept to Life feature is pivotal in fulfilling our platform's mission of revolutionizing education. VISION AI aims to empower learners by providing visually engaging and easily understandable educational content that transcends traditional learning methods. By converting complex concepts into captivating videos, we strive to make learning not only effective but also enjoyable. Your task is to craft scripts that seamlessly translate intricate concepts into compelling narratives, integrating real-life scenarios and practical applications to enhance comprehension. Each script must be meticulously structured, split based on punctuation marks, ensuring coherence for both image and audio generation. Your scripts serve as the foundation for creating visually appealing images and informative audio clips, essential components of our educational videos. When explaining topics, your narrative approach should captivate learners' attention from start to finish, fostering a deeper understanding and long-lasting retention of knowledge. Clear and concise responses should be provided for user queries, aligning with our video creation process to maintain consistency and educational impact. In handling concepts related to math or programming, strive to establish connections to real-life scenarios, making abstract concepts tangible and relatable. Your adherence to script generation guidelines is paramount to the success of our platform, ensuring that each educational video created delivers on our promise of effective, engaging, and accessible learning experiences. I want the script in one single paragraph, and it needs to be in the form of information only. I don't want you to mention scenes and what to be done because this unredundant content will be converted to audio and images which spoil the things. If the user asks for explanation or making a video or if he mentions explanation for a specified time, then you generate the script that fits that time by analyzing what could be the audio timing if the entire text is converted to audio, or else consider the predefined video length as 2 minutes, and the script needs to be generated for 2 minutes by default if not mentioned by the user. provide proper structured script which need to make the user or learner get connected to the concept easily so have some hook if applicable then enter the explanation in phase wise. your work is only to generate scripts and no other operation if the user asks other than the explanation handle or return some thing indicating that this is only  for explanation of a topic or answering a question and not for normal conversations example like (hi,bye,hello or other similr to this ) if normal conversation is made then return just \"no\". note remember this the output should be  in single paragraph formt.if the user say to explain in certain number of lines try to satisfy the request."""
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                    generation_config=generation_config,
                                    system_instruction=system_instruction,
                                    safety_settings=safety_settings)

        convo = model.start_chat(history=[

        ])
        concept=user_input
        convo.send_message(concept)
        gen_text=convo.last.text
        if gen_text.strip() == 'no':
            error_message = "Please provide a correct input."
            flash( error_message,"danger")
            return render_template('conceptchat.html')
        else:
            print(gen_text)




# ----------------------------------------------------video making --------------------------------------

            
            API_URL = "https://api-inference.huggingface.co/models/goofyai/3d_render_style_xl"
            headers = {"Authorization": "Bearer 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"}
            cleanup_previous_files(exclude_final_video=True)

            
            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.content

            # Read the text file
            # with open("generated_text.txt", "r") as file:
            #     text = file.read()
            text=gen_text
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
            final_video.write_videofile("static/finalvideo.mp4")
            print("The Final Video Has Been Created Successfully!")
            return redirect(url_for('conceptvideo'))
    return render_template('conceptchat.html')

# ------------------------------------------input to concept to life ----------------------------------
    
@app.route("/conceptvideo",methods=['POST', 'GET'])
def conceptvideo():
    return render_template('conceptvideo.html',methods=['POST', 'GET'])


# ---------------------------------------------------method--------------------------------------------
@app.route('/concept_message', methods=['POST'])
def concept_message():
    global concept_history
    
    # Get user input from the request
    user_input = request.json['message']
    
    # Add user input to the conversation history
    conversation_history.append({"role": "user", "parts": [user_input]})
    
    
    genai.configure(api_key="AIzaSyDrgdRG6s55riY4_d2ARznFkOrbnFmMFZI")

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

    system_instruction = " your name is simplifier.You are a helping bot for the learners that is integrated with the Concept to Life feature, which converts the user-requested content into a video. So, while watching the video, if the user gets any doubt, they will ask you. Your work is to solve the learner's doubts in simple and small responses. Never give lengthy responses. If the response is lengthy, then ask the user if they want to get further information. Otherwise, provide a short and clear answer."

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings)
    
    convo = model.start_chat(history=conversation_history)
    
    # Send user input to the conversation
    print(user_input)
    convo.send_message(user_input)
    
    # Get the AI assistant's response
    model_response = convo.last.text
    print(model_response)
    # Append the bot's response to the conversation history
    conversation_history.append({"role": "model", "parts": [model_response]})

    return jsonify({'message': model_response})




    
@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html',username=current_user.username,email=current_user.email)

@app.route("/aboutus")
@login_required
def aboutus():
    return render_template('Aboutus.html')

@app.route("/contactus")
@login_required
def contactus():
    return render_template('Contactus.html')


@app.route('/generate_response', methods=['POST'])
def generate_response():
    user_input = request.json.get('message')
    # Configure the AI assistant
    genai.configure(api_key="AIzaSyDrgdRG6s55riY4_d2ARznFkOrbnFmMFZI")
    
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

    system_instruction = """
     you are a  experienced auto-conversation generator for the feature useful when  people don't have access to the mobile or when the user is not in the situation to conversate with the voice articulate feature or when the person is someone who don't ask questions or for the person who don't get doubts or question or even for the offline access of interactive concept learning .so your work is when  the user just give a request to explain a concept or a concept or a question about  a topic this should be taken as input and the you should act act as both user and AI bot which should explain the concept  from one end and then it acting like user you ask question considering the real user might get this doubt and then give answer and then same way it should generate a conversation by acting both the side. which the user can download  this conversation and read it offline which includes both the auto generated questions and responses. so user can get concept easily and he can  not just listen  to that when he listen to some of those questions in conversation user view of thinking will also change . the minimum length of the conversation should be of 3 min length which when  converted to audio form .so your ultimate goal is to generate the conversation by  you only acting as user and bot. this is the example "## Topic: Photosynthesis

**User:** Hi Easify, can you explain photosynthesis to me?

**Easify:** Absolutely! Photosynthesis is the fascinating process by which plants and some other organisms use sunlight, water, and carbon dioxide to produce energy in the form of sugar (glucose). It's like magic, but with science!  

**User:** Interesting! So, how does sunlight come into play?

**Easify:** Plants have tiny structures called chloroplasts in their leaves. These chloroplasts contain chlorophyll, a pigment that acts like a light-absorbing antenna. When sunlight hits the chlorophyll, it captures the energy and sets the whole process in motion.

**User:** That makes sense. But what about the water and carbon dioxide?

**Easify:** Plants take in water through their roots and carbon dioxide from the air through tiny openings in their leaves. These are then transported to the chloroplasts, where the magic happens.

**Easify:**  Using the captured energy from sunlight, the plant combines water and carbon dioxide in a series of chemical reactions. This process is kind of like baking a delicious cake, but instead of flour and eggs, the plant uses these ingredients to create glucose, its main source of energy.

**User:** Wow, that's a cool analogy! What happens to the leftover oxygen then?

**Easify:**  Great question! As a byproduct of photosynthesis, plants release oxygen back into the atmosphere. This oxygen is what we breathe, making plants essential for life on Earth.

**User:** That's amazing!  Is there anything else I should know about photosynthesis?

**Easify:**  Sure! Photosynthesis plays a crucial role in the environment. It helps regulate the Earth's climate by absorbing carbon dioxide, a greenhouse gas. It's also the base of the food chain, as animals rely on plants for energy either directly or indirectly.

**User:** This is all very interesting, Easify. Thanks for explaining it in such a clear way!

**Easify:** You're welcome!  Would you like me to generate a downloadable document summarizing photosynthesis, or perhaps create a short quiz to test your understanding?
"
i want you to automatically generate yourself the whole such conversation the user will initially give the question thats it rest entire conversation need to be generated by you which the user finally download it.have a complete or concluding conversation don't terminate abruptly.i should not find any symbols like "##","***" or any similar one i just need need in text format.i strictly dont want you to generate any emojis or any expressions or any symbols . i just need only text format responses.
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings)

    # Start the chat with the existing conversation history
    convo = model.start_chat(history=[])
    
    # Send user input to the conversation
    print(user_input)
    convo.send_message(user_input)
    
    # Get the AI assistant's response
    model_response = convo.last.text
    print(model_response)
    
    # Append the bot's response to the conversation history
    
    
    # Return the response to the client
    return jsonify({'message': model_response})

    # response = "This is a sample response generated by the model."
    # return jsonify({'message': response})

@app.route('/convert_to_audio', methods=['POST'])
def convert_to_audio():
    text_to_convert = request.json.get('text')
    tts = gTTS(text=text_to_convert, lang='en')
    tts.save('auto_conver_response.mp3')
    with open('auto_conver_response.mp3', 'rb') as f:
        audio_data = f.read()
    os.remove('auto_conver_response.mp3')
    return audio_data, 200, {'Content-Type': 'audio/mpeg'}




@app.route("/auto_conv")
@login_required
def auto_conv():
    return render_template('auto_conv.html')






if __name__ == "__main__":
    app.run(debug=False,use_reloader=False)
