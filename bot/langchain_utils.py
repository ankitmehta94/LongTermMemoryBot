from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import os

chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0,
                  openai_api_key=os.environ.get('OPEN_AI_SECRET_KEY'))


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
