# Import required libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GrokAPIKey = env_vars.get("GroqAPIkey")

# Define CSS classes for parsing specific elements in HTML content
classes = ["zCbuf", "hGKeLc", "LTKOO s7ric", "z0lcw", "gsrt vk bk FzWvSb YwPhnf", 
           "pclqee", "tw-data-text tw-text-small tw-ta", "iZgrdc", "o5uR6d LtkOO", 
           "vlyz6d", "webanswers--webanswers_table__webanswers-table", "dDNo ikb4bb gsrt", 
           "sxLAOe", "LWkfKe", "vQF4g", "qW3wPe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with the API key
client = Groq(api_key=GrokAPIKey)

# Predefined professional responses for user interactions
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# List to store chatbot messages
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'AI Assistant')}. You're a content writer. You have to write content like letters, emails, etc."}]

def GoogleSearch(Topic):
    """Perform a Google search for the given topic."""
    try:
        search(Topic)
        return True
    except Exception as e:
        print(f"Error in GoogleSearch: {e}")
        return False

def Content(Topic):
    """Generate content using AI and save it to a file."""
    def OpenNotepad(File):
        """Open the specified file in Notepad."""
        try:
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, File])
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False

    def ContentWriterAI(prompt):
        """Generate content using AI based on the provided prompt."""
        try:
            messages.append({"role": "user", "content": f"{prompt}"})
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            Answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
                    Answer = Answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": Answer})
            return Answer
        except Exception as e:
            print(f"Error in ContentWriterAI: {e}")
            return ""

    try:
        Topic = Topic.replace("Content", "").strip()
        if not os.path.exists("Data"):
            os.makedirs("Data")
            
        ContentByAI = ContentWriterAI(Topic)
        if not ContentByAI:
            return False

        filename = rf"Data\{Topic.lower().replace(' ', '')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(ContentByAI)

        return OpenNotepad(filename)
    except Exception as e:
        print(f"Error in Content: {e}")
        return False

def YouTubeSearch(Topic):
    """Search for a topic on YouTube."""
    try:
        Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
        webbrowser.open(Url4Search)
        return True
    except Exception as e:
        print(f"Error in YouTubeSearch: {e}")
        return False

def PlayYoutube(query):
    """Play a video on YouTube based on the query."""
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"Error in PlayYoutube: {e}")
        return False

def OpenApp(app, sess=requests.session()):
    """Open the specified application or webpage."""
    # List of common web services
    web_services = {
        'facebook': 'https://facebook.com',
        'instagram': 'https://instagram.com',
        'twitter': 'https://twitter.com',
        'linkedin': 'https://linkedin.com',
        'youtube': 'https://youtube.com'
    }
    
    # Check if it's a known web service
    if app.lower() in web_services:
        try:
            webbrowser.open(web_services[app.lower()])
            return True
        except Exception as e:
            print(f"Error opening web service {app}: {e}")
            return False
    
    # Try to open as a desktop application
    try:
        appopen(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"Error opening app {app}: {e}")
        return False

def CloseApp(app):
    """Close the specified application."""
    try:
        if "chrome" in app.lower():
            return True  # Skip Chrome
        close(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"Error closing app {app}: {e}")
        return False

def System(command):
    """Execute system-level commands."""
    try:
        command = command.lower()
        if command == "mute":
            keyboard.press_and_release("volume mute")
        elif command == "unmute":
            keyboard.press_and_release("volume mute")
        elif command == "volume up":
            keyboard.press_and_release("volume up")
        elif command == "volume down":
            keyboard.press_and_release("volume down")
        else:
            print(f"Unknown system command: {command}")
            return False
        return True
    except Exception as e:
        print(f"Error in System: {e}")
        return False

async def TranslateAndExecute(commands: list[str]):
    """Translate and execute user commands asynchronously."""
    funcs = []
    
    for command in commands:
        command = command.strip().lower()
        
        if command.startswith("open "):
            app = command[5:].strip()
            if app:  # Only proceed if there's actually an app name
                funcs.append(asyncio.to_thread(OpenApp, app))
                
        elif command.startswith("close "):
            app = command[6:].strip()
            if app:
                funcs.append(asyncio.to_thread(CloseApp, app))
                
        elif command.startswith("play "):
            query = command[5:].strip()
            if query:
                funcs.append(asyncio.to_thread(PlayYoutube, query))
                
        elif command.startswith("content "):
            topic = command[8:].strip()
            if topic:
                funcs.append(asyncio.to_thread(Content, topic))
                
        elif command.startswith("google search "):
            query = command[14:].strip()
            if query:
                funcs.append(asyncio.to_thread(GoogleSearch, query))
                
        elif command.startswith("youtube search "):
            query = command[15:].strip()
            if query:
                funcs.append(asyncio.to_thread(YouTubeSearch, query))
                
        elif command.startswith("system "):
            cmd = command[7:].strip()
            if cmd:
                funcs.append(asyncio.to_thread(System, cmd))
                
        else:
            print(f"Unrecognized command: {command}")
    
    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"Command execution error: {result}")
            yield result
    else:
        yield False

async def Automation(commands: list[str]):
    """Automate the execution of user commands."""
    success = True
    async for result in TranslateAndExecute(commands):
        if not result:
            success = False
    return success

if __name__ == "__main__":
    # Example usage
    commands = [
        "open facebook",
        "content write a letter to my friend",
        "play hello by adele",
        "system volume up"
    ]
    
    result = asyncio.run(Automation(commands))
    print(f"Automation completed {'successfully' if result else 'with errors'}")