from chat import gpt3_embedding, load_convo, fetch_memories, summarize_memories, get_last_messages, gpt3_completion
from utils import timestamp_to_datetime, save_json, open_file
from time import time
from uuid import uuid4


def generate_response(userInput):
    # get user input, save it, vectorize it, etc
    timestamp = time()
    vector = gpt3_embedding(userInput)
    timestring = timestamp_to_datetime(timestamp)
    message = '%s: %s - %s' % ('USER', timestring, userInput)
    print(message)
    info = {'speaker': 'USER', 'time': timestamp, 'vector': vector,
            'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    filename = 'log_%s_USER.json' % timestamp
    save_json('nexus/%s' % filename, info)
    # load conversation
    conversation = load_convo()
    # compose corpus (fetch memories, etc)
    # pull episodic memories
    memories = fetch_memories(vector, conversation, 10)
    # TODO - fetch declarative memories (facts, wikis, KB, company data, internet, etc)
    notes = summarize_memories(memories)
    # TODO - search existing notes first
    recent = get_last_messages(conversation, 4)
    prompt = open_file('prompt_response.txt').replace(
        '<<NOTES>>', notes).replace('<<CONVERSATION>>', recent)
    # generate response, vectorize, save, etc
    output = gpt3_completion(prompt)
    timestamp = time()
    vector = gpt3_embedding(output)
    timestring = timestamp_to_datetime(timestamp)
    message = '%s: %s - %s' % ('RAVEN', timestring, output)
    info = {'speaker': 'RAVEN', 'time': timestamp, 'vector': vector,
            'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    filename = 'log_%s_RAVEN.json' % time()
    save_json('nexus/%s' % filename, info)
    # print output
    print('\n\nRAVEN: %s' % output)
    return output
