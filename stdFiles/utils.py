import openai
from googletrans import Translator
# from typing import Callable, Optional, Tuple, Union, List


def connectPepper():
    """
    Requres the NAOQi API for Pepper robots.
    :return:
    """
    

def promptGPT(prompt: str,
              model: str = "text-davinci-003",
              max_tokens: int = 500,
              temperature: float = 0.90,
              top_p: float = 0.75,
              frequency_penalty: float = 0,
              presence_penalty: float = 0):
    """
    Function used to call a response, given a prompt, from one of the many openai models.
        - gpt3: text-davinci-003
        - chatGPT: gpt-3.5-turbo

    :param prompt : str:
    :param model : str:
    :param max_tokens: int:
    :param temperature: float:
    :param top_p: float:
    :param frequency_penalty: float:
    :param presence_penalty: float:
    :return: openai model response as str
    """
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
    )
    return response.choices[0].text


def translateText(text: str,
                  dest: str = 'en',
                  src: str = 'auto'):
    """
    Function made to simplify the translation of some text. This way we do not need to import googletrans explicitly
    in our main script.

    Translator works with: googletrans==3.1.0a0

    :param text: str: the text to be translated
    :param dest: str: destination language
    :param src: str:language to be translated from
    :return: the text in the original language and the translated text
    """
    translator = Translator()
    trans_obj = translator.translate(text, dest=dest, src=src)
    return trans_obj.origin, trans_obj.text
