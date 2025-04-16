from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
from deep_translator import GoogleTranslator
import os
import time

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

# HTML code for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                setTimeout(() => recognition.start(), 1000);  // Delay restart
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Use existing Data directory
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")
    f.write(HtmlCode)

# File paths using existing directories
current_dir = os.getcwd()
Link = f"file:///{current_dir}/Data/Voice.html".replace("\\", "/")  # Normalize path
TempDirPath = os.path.join(current_dir, "Frontend", "Files")  # Use existing Frontend/Files

# Set Chrome options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def SetAssistantStatus(Status):
    """Write assistant status to file."""
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
            file.write(Status)
    except IOError as e:
        print(f"Error writing status: {e}")

def QueryModifier(Query):
    """Modify query for proper punctuation and formatting."""
    if not Query:
        return ""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip(".!?") + "?"
    else:
        new_query = new_query.rstrip(".!?") + "."
    return new_query.capitalize()

def UniversalTranslator(Text):
    """Translate text to English."""
    try:
        return GoogleTranslator(source="auto", target="en").translate(Text).capitalize()
    except Exception as e:
        return f"Translation error: {e}"

def SpeechRecognition():
    """Perform speech recognition."""
    try:
        driver.get(Link)
        driver.find_element(By.ID, "start").click()

        while True:
            try:
                Text = driver.find_element(By.ID, "output").text
                if Text:
                    driver.find_element(By.ID, "end").click()
                    if InputLanguage.lower().startswith("en"):
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating ...")
                        return QueryModifier(UniversalTranslator(Text))
                time.sleep(0.1)  # Prevent excessive CPU usage
            except (webdriver.common.exceptions.NoSuchElementException, 
                    webdriver.common.exceptions.WebDriverException) as e:
                print(f"Browser error: {e}")
                time.sleep(1)
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return None

# Main execution
if __name__ == "__main__":
        while True:
            Text = SpeechRecognition()
            print(Text)