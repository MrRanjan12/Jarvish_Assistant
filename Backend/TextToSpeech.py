import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Fallback to a default voice

# Validate AssistantVoice
if not isinstance(AssistantVoice, str) or not AssistantVoice:
    raise ValueError("AssistantVoice must be a non-empty string. Check your .env file or use a valid voice name.")

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

# Asynchronous function to convert text to audio file
async def TextToAudioFile(text: str) -> None:
    file_path = r"Data\speech.mp3"
    
    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='-13Hz', rate='-10%', volume='+15%')
    await communicate.save(file_path)

# Function to manage text-to-speech functionality
def TTS(text: str, func=lambda r=None: True) -> bool:
    mixer_initialized = False
    try:
        # Convert text to audio file
        asyncio.run(TextToAudioFile(text))
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        mixer_initialized = True
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()
        
        # Loop until audio is done playing or func returns False
        while pygame.mixer.music.get_busy():
            if not func():
                break
            pygame.time.Clock().tick(10)
        
        return True
    
    except (pygame.error, edge_tts.exceptions.EdgeTTSException, asyncio.TimeoutError) as e:
        print(f"Error in TTS: {e}")
        return False
    
    finally:
        try:
            func(False)
            if mixer_initialized:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Function to manage text-to-speech with responses for long text
def TextToSpeech(text: str, func=lambda r=None: True) -> None:
    data = str(text).split(".")
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        # ... (add other responses as needed)
    ]
    
    # If text is long (>4 sentences and >=250 characters), play first two sentences + response
    if len(data) > 4 and len(text) >= 250:
        short_text = " ".join(data[:2]) + ". " + random.choice(responses)
        TTS(short_text, func)
    else:
        TTS(text, func)

# Main execution loop
if __name__ == "__main__":
    try:
        while True:
            user_input = input("Enter the text: ")
            if user_input.lower() == "exit":
                break
            TextToSpeech(user_input)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error during final cleanup: {e}")