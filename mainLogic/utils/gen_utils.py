import os
import random
import re
import time
import requests


def setup_directory():
    pass


def generate_safe_folder_name(folder_name: str) -> str:
    """
    Generate a safe folder name by replacing spaces with underscores and removing special characters.

    Parameters:
    folder_name (str): The original folder name.

    Returns:
    str: The safe folder name.
    """
    # Replace spaces with underscores
    safe_name = folder_name.replace(' ', '_')

    # Remove any characters that are not alphanumeric or underscores
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', safe_name)

    return safe_name


def delete_old_files(base_path, t):
    """
    Delete all files in a folder structure /subfolder1/subfolder2/
    that are older than 't' minutes.

    Parameters:
    - base_path (str): The base directory to start the search.
    - t (int): The age threshold in minutes.
    """
    # Convert the time 't' from minutes to seconds
    age_threshold = t * 60

    print(f"Deleting files older than {age_threshold} seconds")

    current_time = time.time()

    print(os.listdir(base_path))

    # Walk through the directory
    for subfolder1 in os.listdir(base_path):
        subfolder1_path = os.path.join(base_path, subfolder1)
        print('\t'+subfolder1_path)
        if os.path.isdir(subfolder1_path):
            for subfolder2 in os.listdir(subfolder1_path):
                print('\t\t'+subfolder2)
                subfolder2_path = os.path.join(subfolder1_path, subfolder2)
                if os.path.isdir(subfolder2_path):
                    for root, dirs, files in os.walk(subfolder2_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            file_age = current_time - os.path.getmtime(file_path)
                            print(f"File: {file_path}, Age: {file_age}")
                            if int(file_age) > int(age_threshold):
                                os.remove(file_path)
                                print(f"Deleted: {file_path}")


def generate_random_word():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    words = response.content.splitlines()

    int1 = random.randint(0, len(words) - 1)
    int2 = random.randint(0, len(words) - 1)

    word1 = words[int1].decode("utf-8")
    word2 = words[int2].decode("utf-8")

    return f"{word1}-{word2}"

from datetime import datetime

def generate_timestamp():
    # Get the current date and time
    now = datetime.now()
    # Format the timestamp as a string
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp
