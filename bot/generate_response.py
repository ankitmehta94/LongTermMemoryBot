from chat import get_last_messages, gpt3_completion
from utils import open_file
from chroma_utils import summarize_memories, add_chat_message_to_db, encode_embeddings_model, fetch_memories, get_last_messages


USER = 'USER'
BOT_NAME = 'MONETA'


def generate_response(userInput):
    # get user input, save it, vectorize it, etc
    vector = encode_embeddings_model(userInput)
    add_chat_message_to_db(USER, userInput, vector)
    # compose corpus (fetch memories, etc)
    # pull episodic memories

    memories = fetch_memories(vector, 10)
    # TODO - fetch declarative memories (facts, wikis, KB, company data, internet, etc)
    notes = summarize_memories(memories)
    # TODO - search existing notes first
    recent = get_last_messages(4)
    prompt = open_file('prompt_response.txt').replace('<<BOT_NAME>>', BOT_NAME).replace(
        '<<NOTES>>', notes).replace('<<CONVERSATION>>', recent)
    # generate response, vectorize, save, etc
    output = gpt3_completion(prompt)
    output_vector = encode_embeddings_model(output)
    add_chat_message_to_db(BOT_NAME, output, output_vector)
    # print output
    print('\n\n{BOT_NAME}: {output}'.format(BOT_NAME=BOT_NAME, output=output))
    return output
