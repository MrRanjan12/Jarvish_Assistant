# Jarvish: Desktop AI Assistant

Jarvish is a powerful, voice-activated desktop assistant developed using Python. Inspired by Iron Man's JARVIS, it is designed to perform a variety of tasks efficiently through natural language commands. Built for Windows, it leverages modern libraries to integrate voice recognition, text-to-speech, and desktop automation features, making it a versatile productivity tool.

## 🧠 Features

- 🎙️ Voice Recognition (using `speech_recognition`)
- 🗣️ Text-to-Speech Response (using `pyttsx3`)
- 🌐 Web Search (Google, YouTube, Wikipedia)
- 📂 File and Application Management (open apps, folders)
- 🕒 Time and Date Reporting
- 💬 ChatGPT-style conversation (local/offline)
- 🎵 Play music and videos
- 📧 Send emails
- 📅 Set reminders and alarms
- 🧪 Experimental AI capabilities for task automation

## 🔧 Technologies Used

- **Python 3.x**
- `pyttsx3` – Text-to-speech conversion
- `speech_recognition` – Voice command recognition
- `wikipedia`, `pywhatkit`, `webbrowser` – Web utilities
- `os`, `subprocess`, `datetime`, `json` – System interaction
- Custom JSON data files – For simple data storage (no SQL used)

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jarvish-desktop-ai-assistant.git
   cd jarvish-desktop-ai-assistant

