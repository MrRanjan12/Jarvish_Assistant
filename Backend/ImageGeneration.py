import asyncio
import os
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
from time import sleep
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")
if not API_KEY:
    raise ValueError("HuggingFaceAPIKey not found in .env file")

# API details for Hugging Face Stable Diffusion
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Ensure Data directory exists
DATA_DIR = "Data"
os.makedirs(DATA_DIR, exist_ok=True)

# Async function to send a query to the Hugging Face API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            raise Exception(f"Invalid response content type: {content_type}")
        return response.content
    except Exception as e:
        logger.error(f"Error in API query: {e}")
        raise

# Async function to generate images based on the given prompt
async def generate_images(prompt: str) -> bool:
    try:
        tasks = []
        prompt_clean = prompt.replace(" ", "_")
        for i in range(4):
            payload = {
                "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
            }
            task = asyncio.create_task(query(payload))
            tasks.append(task)

        # Wait for all tasks to complete
        image_bytes_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Save the generated images
        for i, image_bytes in enumerate(image_bytes_list):
            if isinstance(image_bytes, Exception):
                logger.error(f"Failed to generate image {i+1}: {image_bytes}")
                continue
            image_path = os.path.join(DATA_DIR, f"{prompt_clean}{i+1}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Saved image: {image_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating images: {e}")
        return False

# Function to open and display images based on a given prompt
def open_images(prompt: str) -> None:
    prompt_clean = prompt.replace(" ", "_")
    files = [os.path.join(DATA_DIR, f"{prompt_clean}{i}.jpg") for i in range(1, 5)]
    
    for image_path in files:
        try:
            img = Image.open(image_path)
            logger.info(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second
        except IOError as e:
            logger.error(f"Unable to open {image_path}: {e}")

# Function to process image generation
async def generate_and_open_images(prompt: str) -> bool:
    success = await generate_images(prompt)
    if success:
        open_images(prompt)
    return success

# Main function to monitor image generation requests
async def main():
    status_file = os.path.join("Frontend", "Files", "ImageGeneration.data")
    
    while True:
        try:
            if not os.path.exists(status_file):
                logger.warning(f"Status file not found: {status_file}")
                await asyncio.sleep(1)
                continue

            with open(status_file, "r") as f:
                data = f.read().strip()

            if not data:
                logger.warning("Status file is empty")
                await asyncio.sleep(1)
                continue

            try:
                prompt, status = data.split(",")
                status = status.strip() == "True"
            except ValueError:
                logger.error(f"Invalid data format in {status_file}: {data}")
                await asyncio.sleep(1)
                continue

            if status:
                logger.info(f"Generating images for prompt: {prompt}")
                success = await generate_and_open_images(prompt)
                if success:
                    with open(status_file, "w") as f:
                        f.write("False,False")
                    logger.info("Image generation completed")
                else:
                    logger.error("Image generation failed")
            else:
                await asyncio.sleep(1)  # Wait before checking again

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(1)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())