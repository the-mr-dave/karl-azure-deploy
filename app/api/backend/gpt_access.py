import os

import openai
import json

key = os.environ.get('GPT_API_KEY')
base = os.environ.get('GPT_API_BASE')
name = os.environ.get('GPT_DEPLOYMENT_NAME')

openai.api_key = key
openai.api_base = base
openai.api_type = 'azure'
openai.api_version = '2023-05-15'  # this might change in the future
deployment_name = name


def send_message(message):
    """
    This method handels the connection with the API of GPT and uses fixed values. Only modifiable value is the message to be sent.
    :param message: Message to be sent.
    :return: The response from the API.
    """
    answer = openai.ChatCompletion.create(

        engine="GPT4StudentAssessment",

        messages=message,

        temperature=0.25,

        max_tokens=1000,

        top_p=0.95,

        frequency_penalty=0,

        presence_penalty=0,

        stop=None
    )
    return answer['choices'][0]['message']['content']


def send_message_and_temp(message, temp):
    """
    This method handels the connection between the GPT API and uses fixed values. Only modifiable values are the
    temperature and the message to be sent.
    :param message: Message to be sent.
    :param temp: value of the temperature. It regulates the answer creativity.
    :return:
    """
    response = openai.Completion.create(
        engine="GPT4StudentAssessment",

        messages=message,

        temperature=temp,

        max_tokens=800,

        top_p=0.95,

        frequency_penalty=0,

        presence_penalty=0,

        stop=None
    )
    return response['choices'][0]['message']['content']


def convert_response_into_json(response):
    """
    This method converts the response received from the API into a json format.
    :param response: response received from the API.
    :return: a json formatted Object
    """
    json_object = None
    try:
        if response.startswith("```"):
            response = response.lstrip("```json")
            response = response.rstrip("```")
        json_object = json.loads(response)
    except Exception as e:
        print("The response is not valid JSON", e)
    finally:
        return json_object
