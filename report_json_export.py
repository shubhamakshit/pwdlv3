import json
import os
import requests
from datetime import datetime

def export_to_json_v3(test_id, test_name, test_mapping_id, questions_json, args):
    """Exports test data to a JSON v3.0 file."""
    
    output_dir = args.output_dir or '.'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    payload = {
        "version": "3.0",
        "source": "pwdlv3",
        "test_name": test_name,
        "test_id": test_id,
        "test_mapping_id": test_mapping_id,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat()
        },
        "config": {
            "statuses_to_include": ["wrong", "unattempted"],
            "layout": {
                "images_per_page": args.images_per_page if hasattr(args, 'images_per_page') else 4,
                "orientation": "portrait"
            }
        },
        "questions": questions_json,
        "view": not args.auto_generate if hasattr(args, 'auto_generate') else True
    }

    file_name = f"{test_mapping_id or test_id}.json"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"Successfully exported test to {file_path}")
    return file_path

def send_to_report_generator(json_file_path, api_url):
    """Sends the JSON file to the Report-Generator API."""
    
    if not os.path.exists(json_file_path):
        print(f"Error: JSON file not found at {json_file_path}")
        return

    with open(json_file_path, 'r') as f:
        payload = json.load(f)

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Successfully sent JSON to Report-Generator API.")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending JSON to API: {e}")

def process_test_v3():
    # This is a placeholder function. 
    # The main logic will be in report.pwdl.py which calls the functions above.
    pass