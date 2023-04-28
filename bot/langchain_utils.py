from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema, CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
from utils import convert_string_to_json
import os
from dotenv.main import load_dotenv
load_dotenv()

chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0,
                  openai_api_key=os.environ.get('OPEN_AI_SECRET_KEY'))

response_schemas = [
    ResponseSchema(name="todo", description="the todo created from the text"),
    ResponseSchema(
        name="time", description="how much time the todo should take")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(
            "Create a list of todos from the following transcription returning only json.\n{format_instructions}\n{transcription}")
    ],
    input_variables=["transcription"],
    partial_variables={"format_instructions": format_instructions}
)

disfluency_and_grammaar_fix_system_message = SystemMessage(
    content="Take the following text and return it after removing all disfluency and fixing its grammar. Don't summarize, there should be no loss of detail"),


def get_fixed_message(user_input):
    messages = [
        SystemMessage(
            content="Take the following text and return it after removing all disfluency and fixing its grammar. Don't summarize, there should be no loss of detail"),
        HumanMessage(
            content=user_input)
    ]
    return chat(messages).content


def get_todo_list(user_input):
    messages = [
        SystemMessage(
            content="As a task management expert, I need you to extract todos from input text and provide a time estimate for each task. If no time estimate is provided for a task, please use your best guess to estimate how long it will take. Return a JSON array with objects containing the keys 'todo' and 'time'. The JSON array must follow a strict schema consisting of an array of objects. Each object must have a key 'todo' and a key 'time'. Please ensure that the tone of voice is professional and precise.Please ensure that the only response you provide is the JSON array, and no additional text. Thank you."),
        HumanMessage(
            content=user_input)
    ]
    return convert_string_to_json(chat(messages).content)


def get_langchain_todo_list(user_input):
    _input = prompt.format_prompt(transcription=user_input)
    val = _input.to_messages()
    print('************************INPUT*******************************')
    print(val)
    output = chat(val)
    print('************************OUTPUT*******************************')
    print(output)
    print('************************OUTPUT PARSER*******************************')
    return output_parser.parse(output.content)
