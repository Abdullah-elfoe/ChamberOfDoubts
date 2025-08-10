import openai
from openai import OpenAI

""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../')))
""" Reseting the root diretory manually"""

# --- Everything below is commented out except the above ---

# from random import choice
# from json import dumps
# from config.game import PHASES
# import json

# json_path = abspath(join(dirname(__file__), '../keys.json'))

# with open(json_path, 'r') as f:
#     config = json.load(f)

# # Access the ChatGPT key
# chatgpt_key = config["keys"]["Chatgpt"]
# openai.api_key = chatgpt_key

# # Build system message content from JSON rules
# rules = config["Rules"]
# system_content = (
#     f"{rules['Desc']}\n\n"
#     f"Turn Mechanism:\n{rules['Turns Mechanism']}\n\n"
#     f"Items and Effects:\n{rules['Items']}\n\n"
#     f"Summary:\n{rules['Summary']}\n\n"
#     f"Next Steps:\n{rules['Next steps']}"
# )
# system_content = "you are a savage AI who do not answer the question, but beats around the bush"
# # Initialize messages with system prompt from JSON and no personality yet
# messages = [
#     {"role": "system", "content": system_content}
# ]

# # Function to send player action and get AI response
# client = OpenAI(api_key=chatgpt_key)

# def send_action(player_action: str):
#     messages.append({"role": "user", "content": player_action})

#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=messages
#     )

#     reply = response.choices[0].message.content
#     messages.append({"role": "assistant", "content": reply})
#     return reply

# class Bot:
#     def __init__(self, name):
#         self.name = name
#         self.difficulty_level = 1
#         self.inventoryItems = []
#         self.ExtraTurn = False
#         self.configure()
        

#     def configure(self):
#         self.currentPhase = 1
#         self.health = PHASES[self.currentPhase][2]


#     def playTurn(self, functions=[]):
#         selection = choice(["Self","Opponent"])
#         if selection == "Self" and not self.ExtraTurn:
#             self.ExtraTurn = True
#             turn_terminated = False

#         else:
#             turn_terminated = True
#             self.ExtraTurn = False

#         # turn_terminated = True if selection == "Opponent" else False
#         for function in functions:
#             function()

        
#         data = {"Selection" : selection,"turn terminated": turn_terminated}
#         return dumps(data)



# while True:
#     user = input("Enter something to send chatgpt: ")
#     print(send_action(user))

# --- ChatGPT communication functionality below ---

import json

json_path = abspath(join(dirname(__file__), '../keys.json'))

with open(json_path, 'r') as f:
    config = json.load(f)

chatgpt_key = config["keys"]["Chatgpt"]
# openai.api_key = chatgpt_key

# client = OpenAI(api_key=chatgpt_key)

# def chatgpt_communicate(prompt: str):
#     messages = [
#         {"role": "system", "content": "You are ChatGPT, a helpful assistant."},
#         {"role": "user", "content": prompt}
#     ]
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",  # Change to gpt-4 if you have access
#         messages=messages
#     )
#     return response.choices[0].message.content

# if __name__ == "__main__":
#     while True:
#         user_input = input("Enter your message for ChatGPT: ")
#         response = chatgpt_communicate(user_input)
#         print("ChatGPT:", response)


import openrouter
from openai import OpenAI

# If the model requires the provider's API key, pass it as 'api_key'. If not, you can omit it and use the OpenRouter API key.


import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {chatgpt_key}"
  },
  data=json.dumps({
    "model": "deepseek/deepseek-r1-0528:free", 
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life? Asnwer me in a single word"
      }
    ]
  })
)

print(response.json()["choices"][0]["message"]["content"])