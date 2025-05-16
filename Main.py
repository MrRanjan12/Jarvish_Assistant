from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Initialize environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', 'r', encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
    File.close()
    
    with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
        file.write(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Merged_query = [i.split('||') for i in Decision if i.startswith("general") or i.startswith("realtime")]

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = subprocess.Popen(["python", r"Backend\ImageGeneration.py"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query[0]))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering ...")
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering ...")
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering ...")
                os._exit(1)  # fixed: os._exit instead of os.exit

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ...")

def SecondThread():
    GraphicalUserInterface()  # This must run in the main thread

if __name__ == "__main__":
    InitialExecution()

    # Start background processing in a thread
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()

    # Run GUI in the main thread
    SecondThread()
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Initialize environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def show_default_chat_if_no_chats():
    """Show default chat if no chats are found."""
    file = open(r'Data\ChatLog.json', 'r', encoding='utf-8')
    if len(file.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def read_chat_log_json():
    """Read chat log from JSON file."""
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def chat_log_integration():
    """Integrate chat log into the database."""
    json_data = read_chat_log_json()
    formatted_chatlog = ""
    
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def show_chats_on_gui():
    """Show chats on the GUI."""
    file = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    data = file.read()
    if len(str(data)) > 0:
        lines = data.split('\n')
        result = '\n'.join(lines)
    file.close()
    
    with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
        file.write(result)

def initial_execution():
    """Perform initial execution."""
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    show_default_chat_if_no_chats()
    chat_log_integration()
    show_chats_on_gui()

def main_execution():
    """Perform main execution."""
    task_execution = False
    image_execution = False
    image_generation_query = ""

    SetAssistantStatus("Listening ...")
    query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {query}")
    SetAssistantStatus("Thinking ...")
    decision = FirstLayerDMM(query)

    print(f"\nDecision : {decision}\n")

    g = any([i for i in decision if i.startswith("general")])
    r = any([i for i in decision if i.startswith("realtime")])
    merged_query = [i.split('||') for i in decision if i.startswith("general") or i.startswith("realtime")]

    for queries in decision:
        if "generate " in queries:
            image_generation_query = str(queries)
            image_execution = True

    for queries in decision:
        if not task_execution and any(queries.startswith(func) for func in Functions):
            run(Automation(list(decision)))
            task_execution = True

    if image_execution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{image_generation_query},True")

        try:
            p1 = subprocess.Popen(["python", r"Backend\ImageGeneration.py"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if g and r or r:
        SetAssistantStatus("Searching ...")
        answer = RealtimeSearchEngine(QueryModifier(merged_query))
        ShowTextToScreen(f"{Assistantname} : {answer}")
        TextToSpeech(answer)
        return True
    else:
        for queries in decision:
            if "general" in queries:
                SetAssistantStatus("Thinking ...")
                query_final = queries.replace("general", "")
                answer = ChatBot(QueryModifier(query_final))
                ShowTextToScreen(f"{Assistantname} : {answer}")
                TextToSpeech(answer)
                SetAssistantStatus("Answering ...")
                return True
            elif "realtime" in queries:
                SetAssistantStatus("Searching ...")
                query_final = queries.replace("realtime", "")
                answer = RealtimeSearchEngine(QueryModifier(query_final))
                ShowTextToScreen(f"{Assistantname} : {answer}")
                TextToSpeech(answer)
                SetAssistantStatus("Answering ...")
                return True
            elif "exit" in queries:
                query_final = "Okay, Bye!"
                answer = ChatBot(QueryModifier(query_final))
                ShowTextToScreen(f"{Assistantname} : {answer}")
                TextToSpeech(answer)
                SetAssistantStatus("Answering ...")
                os._exit(1)  # fixed: os._exit instead of os.exit

def first_thread():
    """Run the first thread."""
    while True:
        current_status = GetMicrophoneStatus()
        if current_status == "True":
            main_execution()
        else:
            ai_status = GetAssistantStatus()
            if "Available ..." in ai_status:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ...")

def second_thread():
    """Run the second thread."""
    GraphicalUserInterface()  # This must run in the main thread

if __name__ == "__main__":
    initial_execution()

    # Start background processing in a thread
    thread1 = threading.Thread(target=first_thread, daemon=True)
    thread1.start()

    # Run GUI in the main thread
    second_thread()