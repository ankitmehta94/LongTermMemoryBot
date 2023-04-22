import chromadb
from utils import load_json, open_file, json_stringyfy
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chat import gpt3_completion
from sentence_transformers import SentenceTransformer
from uuid import uuid4
from time import time
collection_json = load_json('vector_db_constants.json')

chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                         persist_directory=collection_json["vector_database_directory"]))
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2")


embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
# # currectly using default embedings function all-MiniLM-L6-v2
notes_collection = chroma_client.get_or_create_collection(
    name=collection_json['notes_collection'], embedding_function=sentence_transformer_ef)


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
    vector = embeddings_model.encode(block)

    # Have to convert meta data into string values as chromadb only accepts a str, int, or float
    metadata = {'notes': notes, 'uuids': json_stringyfy(identifiers),
                'times': json_stringyfy(timestamps), 'time': time()}

    notes_collection.add(
        embeddings=[vector],
        metadatas=[metadata],
        ids=str(uuid4()),
    )
    return notes
