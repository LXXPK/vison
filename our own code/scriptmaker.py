from gpt4all import GPT4All

model = GPT4All("C:/Users/reddy/gpt4all/gguf models/mistral-7b-instruct-v0.1.Q4_0.gguf", allow_download=False)


global user_input,main_generated
 
# method to find  the operation of selected by the user 
def user_select(user_input):
    
    if "transform your ideas into engaging videos"  in  user_input.lower() or "1" in user_input.lower():
        return "topic"
    elif "question-to-video:turn your queries into explainer videos"  in user_input.lower() or "2" in user_input.lower():
        return "question"
    elif "bring text to life:convert concepts into videos" in user_input.lower() or "3" in user_input:
        return "summery"
    else:
        return "others"

#  method to generate content  about particular  topic  ------------------------------------------

# method to generate introduction 
def generate_intro(user_input):
    prompt=f"""consider this topic  "{user_input}" and generate the following Hook,Relevance and Significance,Contextualization. format_for_generating:Hook: Utilizes an engaging statement, question, anecdote, or intriguing fact to immediately grab the viewer's attention.
            Relevance and Significance: Establishes why the concept being discussed is important or why the viewer should care about understanding it.
            Contextualization: Offers a brief overview or background information about the concept without delving into specifics. """
    intro_generated = model.generate(prompt, temp=0.6,max_tokens=1000)
    print(intro_generated)
    main_point_gen(user_input)

# method to main points for the topic given 
def main_point_gen(user_input):
    global main_generated
    prompt=f"""consider this topic  "{user_input}" and generate the following Structural Division,Sequential Explanation,Clarity and Simplification.format_for_generating:1.Structural Division: Organizes the concept into distinct sections or topics, each addressing a specific aspect.
            2.Sequential Explanation: Provides a coherent explanation of each section, ensuring a logical flow from one point to another.
            3.Clarity and Simplification: Uses straightforward language, analogies, or visual aids to simplify complex ideas and enhance comprehension."""
    main_generated = model.generate(prompt, temp=0.6,max_tokens=1000)
    print(main_generated)
    application_gen(user_input)

# method to generate applications and examples 
def application_gen(user_input):
    prompt=f"""consider this topic  "{user_input}" and generate the following 1.Real-Life Scenarios 2.Variety and Context.generating_format:1.Real-Life Scenarios: Presents relatable examples showcasing the concept's application.
    2.Variety and Context: Diverse examples covering different contexts where the concept applies."""
    application_generated = model.generate(prompt, temp=0.6,max_tokens=1000)
    print(application_generated)
    generate_summery(main_generated)

#method to generate summery  
def generate_summery(summery_topic):
    prompt=f"""generate a summery of the context {summery_topic} 
            Summary: Summarize the key points and take aways from the explanation, reinforcing the essential aspects of the concept."""
    summery = model.generate(prompt, temp=0.6,max_tokens=1000)
    print(summery) 


# method to generate explanation  for the question given by the user -------------------------------------------------
def explain_user_question(user_input):
    question_hook(user_input)

def question_hook(user_input):
    prompt=f"""assistant:you are a ai assistant and your work is to generate  hook representing the question  that  Hooks the audience's attention and introduces the question.
            Purpose:Creates curiosity and establishes the central theme.
            question:"{user_input}" """
    q_hook = model.generate(prompt, temp=0.6)
    print(q_hook) 
    question_intro(user_input)

def question_intro(user_input):
    prompt = f"""Make this question more curious and attractive for the user.
            question:"{user_input}"  """
    global question_intro
    question_intro = model.generate(prompt, temp=0.6)
    print(question_intro)

    question_overview(user_input)


def question_overview(user_input):
    prompt = f"""assistant:I want you to generate an overview or background information about the subject to be highlighted in the solution for this question.
    Purpose: Introduces the topic and provides foundational knowledge.
    question:"{user_input}"  """
    global overview_generated
    overview_generated = model.generate(prompt, temp=0.6)
    print(overview_generated)
    main_topic(user_input)


def main_topic(user_input):
    prompt = f"""assistant:I want you to generate a systematic breakdown of the solution topic for this question, simplifying complex components.
    Purpose: Clarifies intricate details in an understandable manner.
    question:"{user_input}" """
    global main_generated
    main_generated = model.generate(prompt, temp=0.6)
    print(main_generated)
    conclu_part(user_input)


def conclu_part(user_input):
    prompt = f"""assistant:I want you to generate a conclusion that concludes this explanation, emphasizing the significance or implications of understanding the topic.
            Purpose: Encourages reflection and leaves the audience with key takeaways.
            explanation:"{user_input}" """
    conclude = model.generate(prompt, temp=0.6)
    print(conclude)



# method to give explanation to text given by the user ---------------------------------------------------------------
def user_text(text):
    prompt=f"""user:i am a learner so i have  need explanation about the text i have given you.
    Assistant:you are a ai assiatant and your work is to generate explanation of the piece of text given by the user in step by step format which include introduction,core of the topic,aapplicationsor real life examples,conclusion.
            piece_text:"{text}" """
    application_generated = model.generate(prompt, temp=0.6,max_tokens=1500)
    print(application_generated)


# method to  handle the unexpected input-------------------------------------------------------------------------------
def handle_unexpected_input():
    return "I'm sorry, I didn't understand that.please make your option clear try again "

print(""" i am glad to help you . ok say me what can i do for you 
        1.Transform Your Ideas into Engaging Videos.
        2.Question-to-Video: Turn Your Queries into Explainer Videos.
        3.Bring Text to Life: Convert Concepts into Videos.
         """ )

user_input = input("User: ")
# check if input is "exit" -----------------------------------------------
selected = user_select(user_input)
# Switch based on intent to drive the conversation-------------------------
if selected == "topic":
    topic=input("enter the topic ")
    generate_intro(topic)
elif selected == "question":
    question=input("enter the question ")
    explain_user_question(question)
elif selected == "summery":
    text=input("enter the text ")
    user_text(text)
elif selected == "others":
    print("Assistant:", handle_unexpected_input())
    
