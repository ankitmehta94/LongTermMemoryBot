import chromadb
from utils import load_json, open_file, json_stringyfy, timestamp_to_datetime
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chat import gpt3_completion
from sentence_transformers import SentenceTransformer
from uuid import uuid4
from time import time
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
collection_json = load_json('vector_db_constants.json')

chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                         persist_directory=collection_json["vector_database_directory"]))
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2")


embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
# # currectly using default embedings function all-MiniLM-L6-v2
notes_collection = chroma_client.get_or_create_collection(
    name=collection_json['notes_collection'], embedding_function=sentence_transformer_ef)

logs_collection = chroma_client.get_or_create_collection(
    name=collection_json['logs_collection'], embedding_function=sentence_transformer_ef)


def summarize_memories(memories):
    # sort them chronologically
    memories = sorted(memories, key=lambda d: d['time'], reverse=False)
    block = ''
    identifiers = list()
    timestamps = list()
    for mem in memories:
        block += mem['message'] + '\n\n'
        identifiers.append(mem['uuid'])
        timestamps.append(mem['time'])
    block = block.strip()
    prompt = open_file('prompt_notes.txt').replace('<<INPUT>>', block)
    # TODO - do this in the background over time to handle huge amounts of memories
    notes = gpt3_completion(prompt)
    # SAVE NOTES
    vector = encode_embeddings_model(block)

    # Have to convert meta data into string values as chromadb only accepts a str, int, or float
    metadata = {'notes': notes, 'uuids': json_stringyfy(identifiers),
                'times': json_stringyfy(timestamps), 'time': time()}

    notes_collection.add(
        embeddings=[vector],
        metadatas=[metadata],
        ids=str(uuid4()),
    )
    return notes


def encode_embeddings_model(message):
    if not message or not isinstance(message, str):
        raise ValueError("Message must be a non-empty string.")
    return embeddings_model.encode(message)


def add_chat_message_to_db(speaker, message, vector=None):
    if not speaker or not isinstance(speaker, str):
        raise ValueError("Speaker must be a non-empty string.")
    if not message or not isinstance(message, str):
        raise ValueError("Message must be a non-empty string.")

    timestamp = time()

    timestring = timestamp_to_datetime(timestamp)
    message = '%s: %s - %s' % (speaker, timestring, message)
    print(message)
    metadata = {'speaker': speaker, 'time': timestamp,
                'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    logs_collection.add(
        embeddings=[vector],
        metadatas=[metadata],
        ids=str(uuid4()),
    )


def fetch_memories(vector, count):
    actual_count = min(logs_collection.count(), count)
    response = logs_collection.query(
        query_embeddings=[vector],
        n_results=actual_count,
        include=["metadatas", "distances"]
    )
    merged_res = add_distance_to_array(
        response['distances'][0], response['metadatas'][0])
    return sorted(merged_res, key=lambda d: d['distance'], reverse=True)


def add_distance_to_array(array1, array2):
    if not isinstance(array1, list) or not isinstance(array2, list):
        raise TypeError("Both arguments must be lists")
    if not all(isinstance(x, (int, float)) for x in array1):
        raise ValueError("The first array must contain only numbers")
    if not all(isinstance(x, dict) for x in array2):
        raise ValueError("The second array must contain only dictionaries")
    if not all("message" in x and "speaker" in x for x in array2):
        raise ValueError(
            "Each dictionary in the second array must contain 'message' and 'speaker' keys")

    for i, d in enumerate(array2):
        d["distance"] = array1[i]

    return array2


def get_last_messages(count):
    actual_count = min(logs_collection.count(), count)
    response = logs_collection.get(
        include=["metadatas"],
        limit=actual_count
    )
    output = ''
    for i in response["metadatas"]:
        output += '%s\n\n' % i['message']
    output = output.strip()
    return output
