from googlesearch import search
from groq import Groq  # Import the Groq library to use its API
from json import load, dump  # Importing functions to read and write JSON files
import datetime  # For getting current date and time
from dotenv import dotenv_values  # For loading .env variables

# Load environment variables from the .env file
env_variables = dotenv_values(".env")

# Retrieve values from .env
Username = env_variables.get("Username")
Assistantname = env_variables.get("Assistantname")
GroqAPIkey = env_variables.get("GroqAPIkey")  # Removed extra space

# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIkey)

# Define the system instructions for the chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist
try:
    with open(r"Data\Chatlog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\Chatlog.json", "w") as f:
        dump([], f)
    messages = []

# Function to perform a Google search and format the results
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=3))
    Answer = f"The search results for '{query}' are:\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    return Answer.strip()

# Function to clean up the answer by removing empty lines
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Predefined chatbot conversation system message
PredefinedChatbot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time
def Information():
    current_date_time = datetime.datetime.now()
    return (
        f"Use this real-time Information if needed:\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Hour: {current_date_time.strftime('%H')}\n"
        f"Minute: {current_date_time.strftime('%M')}\n"
        f"Second: {current_date_time.strftime('%S')}\n"
    )

# Main function to process user input, get search results, and call Groq API
def RealtimeSearchEngine(prompt):
    global PredefinedChatbot, messages

    # Load chat history again
    with open(r"Data\Chatlog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    # Perform Google Search
    search_result = GoogleSearch(prompt)
    PredefinedChatbot.append({"role": "system", "content": search_result})

    # Generate response using Groq API (streaming)
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=PredefinedChatbot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    # Collect the streamed response
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean up the response
    Answer = Answer.strip().replace("\n", " ")

    # Update chat log
    messages.append({"role": "assistant", "content": Answer})
    with open(r"Data\Chatlog.json", "w") as f:
        dump(messages, f, indent=4)

    # Remove the temporary system message
    PredefinedChatbot.pop()

    return AnswerModifier(Answer)

# Entry point
if __name__ == "__main__":
    while True:
        prompt = input("Ask something: ")
        if prompt.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        print(RealtimeSearchEngine(prompt))
