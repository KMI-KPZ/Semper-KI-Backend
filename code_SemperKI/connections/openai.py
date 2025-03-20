"""
Part of Semper-KI software

Silvio Weging, Mahdi Hedayat Mahmoudi 2024

Contains: Calls to "Open"AI API

"""
import logging
import openai
from openai import OpenAI

from django.conf import settings


logger = logging.getLogger("logToFile")
##################################################
class OpenAIManager():
    """
    Manage openAI client

    """
    def __init__(self) -> None:
        openai.api_key = settings.OPENAI_API_KEY
        self.client = OpenAI()
    
openaiManager = OpenAIManager()
    

##################################################
def callChatInterface(gptModel:str, factsheet:str, roleOfSystem:str, responseFormat) -> dict:
    """
    Send messages to the message api and gather response
    
    """
    try:
        completion = openaiManager.client.beta.chat.completions.parse(
            model=gptModel,
            messages=[
                {"role": "system", "content": roleOfSystem},
                {"role": "user", "content": factsheet},
            ],
            response_format=responseFormat,
        )

        message = completion.choices[0].message
        if message.parsed:
            return message.parsed.dict()
        else:
            logging.warning("No parsed data returned from OpenAI: " + message.refusal)
            return None
    except Exception as e:
        logging.error(f"Error in parsing printer factsheet: {e}")
        return e
    
