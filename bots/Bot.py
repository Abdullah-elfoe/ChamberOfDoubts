import requests
import json
from os.path import abspath, dirname, join
from abc import ABC, abstractmethod

class AbstractBot(ABC):
    def __init__(self, health, userhealth ,myinv, oppinv):
        self.chatgpt_key = self.get_api_key()
        self.health = health
        self.userhealth = userhealth
        self.inventoryItems = myinv
        self.opponentInventoryItems = oppinv
        self.turn = False
        self.data = ""

    @staticmethod
    def get_api_key():
        json_path = abspath(join(dirname(__file__), '../keys.json'))
        with open(json_path, 'r') as f:
            config = json.load(f)
        return config["keys"]["Chatgpt"]

    def send(self, msg: str, model: str = "deepseek/deepseek-r1-0528:free") -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.chatgpt_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": msg}
            ]
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"
        except (KeyError, IndexError):
            return "Error: Unexpected response format."

    @abstractmethod
    def updateBot(self):
        pass

    def prepareBot(self):
        """
        Prepares a string containing all rules from the keys.json file under the 'Rules' property.
        Returns:
            str: Formatted rules string.
        """
        json_path = abspath(join(dirname(__file__), '../keys.json'))
        with open(json_path, 'r') as f:
            config = json.load(f)
        rules = config["Rules"]
        rules_str = f"""
            "{rules['Desc']}\n\n"
            "Turn Mechanism:\n{rules['Turns Mechanism']}\n\n"
            "Items and Effects:\n{rules['Items']}\n\n"
            "Summary:\n{rules['Summary']}\n\n"
            "Next Steps:\n{rules['Next steps']}"
            "Answer Format":\n{rules['Answer Format']}"
            """
        
        

class INTERNETBOT(AbstractBot):
    def __init__(self, name, health, userhealth, myinv, oppinv):
        super().__init__(health, userhealth, myinv, oppinv)
        self.name = name

    def updateBot(self, array):
        self.health = array[0]
        self.userhealth = array[1]
        self.inventoryItems = array[2]
        self.opponentInventoryItems = array[3]
        self.data 
    
    def makeaMove(self):
        if not self.turn or not self.data:
            return False
        
        response = self.send(self.data)
        self.turn = False

    def initData(self):
        self.data = f"Updates so far:\n My Health{self.health},\n User Health: {self.userhealth},\n My Inventory: {self.inventoryItems},\n Opponent Inventory: {self.opponentInventoryItems}.\n Now, please make a move."

if __name__ == "__main__":
    print("ChatBot is ready. Type your message and press Enter (Ctrl+C to exit).")
    bot = INTERNETBOT(name="InternetBot", health=100, myinv=[], oppinv=[])
    while True:
        try:
            user_input = input("You: ")
            reply = bot.send(user_input)
            print("Bot:", reply)
        except KeyboardInterrupt:
            print("\nExiting ChatBot.")