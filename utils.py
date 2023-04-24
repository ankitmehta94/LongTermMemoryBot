
import json
import datetime
import os
import requests
from os.path import dirname, join
from dotenv.main import load_dotenv

load_dotenv()
project_root = dirname(dirname(__file__))

root_dir = join(project_root, 'LongTermMemoryBot')


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def create_directory(filepath):
    if not os.path.exists(filepath):
        os.makedirs(filepath)


def json_stringyfy(payload):
    return json.dumps(payload, separators=(',', ':'))


def json_pretty_print(payload):
    return json.dumps(payload, indent=2)


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False,
                  sort_keys=True, indent=2)


def timestamp_to_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time).strftime("%A, %B %d, %Y at %I:%M%p %Z")


def get_json_from_url(url):
    """
    Fetches a JSON file from a URL and returns a dictionary with its contents.

    :param url: The URL of the JSON file.
    :return: A dictionary containing the JSON data.
    """
    try:
        response = requests.get(url)

        # Raise an error if the request failed
        response.raise_for_status()

        # Parse the JSON data into a dictionary
        data = response.json()

        return data

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
