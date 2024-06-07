import pyttsx3 as p
import speech_recognition as sr
from gpt4all import GPT4All
from fuzzywuzzy import process
import requests


# Initialize GPT4All model
model = GPT4All("C:/Users/reddy/gpt4all/gguf models/mistral-7b-instruct-v0.1.Q4_0.gguf", allow_download=False)

# Initialize speech recognizer
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
            return ""
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return ""

# -----------------------------------------------
def handle_conversation():
    user_input = do_listen()
    if user_input:
        response = model.generate(f"user: {user_input}", temp=0.7, max_tokens=50)
        print("AI:", response)
        return response
         
# -----------------------------------------------

def interrupt():
    print("Seek answers to your burning questions. Share your curiosity with me.")
    speak("Seek answers to your burning questions. Share your curiosity with me.")
    query_question=do_listen()
    answer_for_query = generate_query_explanation(query_question)
    print("Assistant:", answer_for_query)
    speak(answer_for_query)

#  method to generate hook about particular  topic    
def hook_make(explanation_topic):
    prompt=f"""user: Generate a single line hook that captures the attention with  a surprising fact, or a relevant anecdote related to the concept of "{explanation_topic}".
            assistant:hook."""
    hook_of_topic = model.generate(prompt, temp=0.6)
    print(hook_of_topic)
    speak(hook_of_topic)
    print("do you have any question? ")
    speak("do you have any question? ")
    anything=do_listen()
    if "no"  in anything.lower() or "continue" in anything.lower():
        background_make(explanation_topic)
    else:
        interrupt()

# method to generate background of a topic 
def background_make(explanation_topic):
    prompt=f"""generate   background about the topic  "{explanation_topic}"  
               Background format: Provide a brief overview of the concept, placing it in context with previously learned knowledge or real-world experiences it should be only one paragraph . """
    background_of_topic = model.generate(prompt, temp=0.6)
    print(background_of_topic)
    speak(background_of_topic)
    print("do you have any question? ")
    speak("do you have any question? ")
    anything=do_listen()
    if "no"  in anything.lower() or "continue" in anything.lower():
        topic_generator(explanation_topic)
    else:
        interrupt()

# method to generate the  content  of the user input 
def topic_generator(explanation_topic):
    prompt=f"""generate information about the topic  "{explanation_topic}" by following the format given. information format:Definition: Provide a clear and concise definition of the concept, using simple language and avoiding jargon or overly technical terms.Key Points: Break down the concept into smaller, more manageable chunks, highlighting the essential aspects and relationships between them.Examples: Illustrate the concept with concrete examples from everyday life, relevant fields of study, or historical events.generate all this above topic with seperate paragarph """
    topic_generated = model.generate(prompt, temp=0.6,max_tokens=1000)
    print(topic_generated)
    speak(topic_generated)
    print("do you have any question? ")
    speak("do you have any question? ")
    anything=do_listen()
    if "no"  in anything.lower() or "continue" in anything.lower() :
        summery_generator(topic_generated)
    else:
        interrupt()

# method to generate summery for the context  given 
def summery_generator(topic_generated):
    prompt= f"""read  the following text:"{topic_generated}"  and now i  want you to generate a small summery that will cover all the concepts in the text i gave you """
    summery_generated = model.generate(prompt, temp=0.6)
    print(summery_generated)
    speak(summery_generated)

# this method is to generate the summery of the content you generated in overall 
def generate_summery(summery_topic):
    prompt=f"""generate a summery of the context {summery_topic} 
            Summary: Summarize the key points and take aways from the explanation, reinforcing the essential aspects of the concept."""
    
    summery = model.generate(prompt, temp=0)
    return summery 

def generate_query_explanation(user_input):
    prompt = f"""you are a ai assistant your work is to answer the questions asked by the user 
                user question:{user_input}"""
    explanation = model.generate(prompt, temp=0.6,max_tokens=500)
    return explanation

# method to frame a question for quiz
def generate_quiz_question(user_input):
    
    # Using the GPT-4All model to generate a quiz question based on the current topic
    prompt = f"""Generate a multiple-choice question about {user_input}:
    Question:Question?
    a) Option 1
    b) Option 2
    c) Option 3
    d) Option 4
"""
    quiz_question = model.generate(prompt, temp=0.6)
    return quiz_question

# method to find the correct answer to the aksed question
def correct(quiz_question):
    # question=question_extractor(quiz_question)
    prompt = f"""pick the correct answer for the given question {quiz_question}
                answer:correct option and the reason why it is correct 
"""
    verified_output=model.generate(prompt,temp=0.5)
    print(verified_output)
    speak(verified_output)
    return verified_output

# method to check the correctness of the answer given by the user
def evaluate_answer(user_answer):
    answer=correct(quiz_question)
    if user_answer.lower()  in  answer.lower():
        feedback = "That's correct! Great job!"
    else:
        feedback = "That's incorrect. " 
    return feedback

# method to  handle the unexpected input 
def handle_unexpected_input():
    return "I'm ready to assist you. Feel free to ask me anything!"

def main():
    global user_input
    global quiz_question
    welcome_message = "Hello! Welcome to your AI learning assistant. My name is AI Buddy. What should I call you?"
    print(welcome_message)
    speak(welcome_message)

    user_name = do_listen()
    if user_name:
        print(f"Nice to have you here {user_name} ")
        speak(f"Nice to have you here {user_name} ")
    
    conversation_ongoing = True
    while conversation_ongoing:
        print("How can I assist you?")
        speak("How can I assist you?")

        user_input = do_listen()

        if not user_input:
            continue

        if "exit" in user_input.lower() or "quit" in user_input.lower():
            break

        # Match user input to available options
        options = {
             
            "quizzes": ["quiz", "test", "exam", "challenge", "knowledge", "assessment"],
            "explanations": ["explain", "explore", "understand", "learn", "details", "clarify", "elaborate"],
            "summaries": ["summarize", "summary", "overview", "recap", "concise", "brief", "synopsis"],
            "queries": ["question", "answer", "information", "know", "query", "doubt", "inquiry"]
        }

        # Find the option with the highest similarity score
        matched_option, score = process.extractOne(user_input.lower(), options.keys())
        print(score)
        print(matched_option)
        # Determine the option with the highest similarity score
        if score >= 50:  # Adjusted threshold for better accuracy
            print("Selected option:", matched_option)
            # Route to the appropriate handler function
            
            if matched_option == "quizzes":
                print("Put your knowledge to the test! What topic would you like to quiz yourself on?")
                speak("Put your knowledge to the test! What topic would you like to quiz yourself on?")
                topic = do_listen()
                quiz_question = generate_quiz_question(topic)
                print("Assistant:", quiz_question)
                speak(quiz_question)
                print("Please select the best answer from the following choices.")
                speak("Please select the best answer from the following choices.")
                user_answer = do_listen()
        # Evaluate user's answer and give feedback------------------------------
        
                feedback = evaluate_answer(user_answer)
                print("Assistant:", feedback)
                speak(feedback)
                # Handle quizzes
            elif matched_option == "explanations":
                print("Delve deeper into a fascinating topic. What would you like to explore?")
                speak("Delve deeper into a fascinating topic. What would you like to explore?")
                explanation_topic = do_listen()
                hook_make(explanation_topic)
                # Handle explanations
            elif matched_option == "summaries":
                print("Capture the essence of a topic in a nutshell. What would you like me to summarize?")
                speak("Capture the essence of a topic in a nutshell. What would you like me to summarize?")
                summery_topic = do_listen()
                summery = generate_summery(summery_topic)
                print(summery)
                # Handle summaries
            elif matched_option == "queries":
                print("Seek answers to your burning questions. Share your curiosity with me.")
                speak("Seek answers to your burning questions. Share your curiosity with me.")
                query_question = do_listen()
                answer_for_query = generate_query_explanation(query_question)
                print("Assistant:", answer_for_query)
                speak(answer_for_query)
                # Handle queries
            
        else:
            # Unexpected input
            error = handle_unexpected_input()
            print("Assistant:", handle_unexpected_input())
            speak(error)

if __name__ == "__main__":
    main()
