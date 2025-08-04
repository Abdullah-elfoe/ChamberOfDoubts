from random import choice
from sys import exit
import time

def Injection(obj):
    obj.template.myHealthBar.heal()
    items = [(item.holdingItem.name, item.holdingItem.qty) for item in obj.template.myInventory.inventory if item.holdingItem != None]
    data = {
        "opponentHB":obj.template.myHealthBar.current_health,
        "Opponent Inventory":items,
        "used":"Injection", 
        }
    
    obj.network.send_game(data)


def Bazuka(obj):

    obj.increaseDamage()
    items = [(item.holdingItem.name, item.holdingItem.qty) for item in obj.template.myInventory.inventory if item.holdingItem != None]
    data = {
        "Damage":2,
        "Opponent Inventory":items,
        "used":"Bazuka", 
        }
    obj.network.send_game(data)

def Glasses(obj):
    # obj.template.infoBooth.text = f"Bullet {"" if obj.bullets[0] else "not"} Found" 
    # obj.template.infoBooth.permission = True
    obj.template.notebook.addToNotebook(
        "General", 
        "Developers", 
        f"Bullet {"" if obj.bullets[0] else "not"} Found",
        )
    obj.template.notebook.permission = True
    obj.updateInventory()
    data = {
        "used":"Glasses", 
        }
    obj.network.send_game(data)



def fishingRod(obj):
    
    obj.template.opponentInventory.hoverPermission=True
    obj.updateInventory()
    data = {
        "used":"fishingRod", 
        }
    obj.network.send_game(data)




def Clock(obj):
    obj.clockUsed = True
    obj.updateInventory()
    data = {
        "used":"Clock", 
        }
    obj.network.send_game(data)



def Switch(obj):
    if obj.bullets[0]:
        obj.bullets[0] = False
    else:
        obj.bullets[0] = not False
    items = [(item.holdingItem.name, item.holdingItem.qty) for item in obj.template.myInventory.inventory if item.holdingItem != None]
    data = {
        "bullets":obj.bullets,
        "Opponent Inventory":items,   
         "used":"Switch", 
        }
    obj.network.send_game(data)


def SignalJammer(obj):
    obj.bullets.pop(0)
    items = [(item.holdingItem.name, item.holdingItem.qty) for item in obj.template.myInventory.inventory if item.holdingItem != None]
    data = {
        "bullets":obj.bullets,
        "Opponent Inventory":items,   
        "used":"SignalJammer", 
        }
    obj.network.send_game(data)


def Pill(obj):
    hit = choice([True, False])
    if hit:
        obj.template.myHealthBar.hit()
        items = [(item.holdingItem.name, item.holdingItem.qty) for item in obj.template.myInventory.inventory if item.holdingItem != None]
        data = {
            "opponentHB":obj.template.myHealthBar.current_health,
            "Opponent Inventory":items,
            "used":"Pill",
            }
        obj.network.send_game(data)
    else:
        Injection(obj)
    




function_list = {
    "Injection":[Injection,None],
    "Bazuka":[Bazuka, None],
    "Glasses":[Glasses, None],
    "Clock":[Clock, None],
    "Fishing Rod":[fishingRod, None],
    "Switch":[Switch, None],
    "Signal Jammer":[SignalJammer, None],
    "Pill":[Pill, None],

}

def handleMod(obj):
    if obj.mainRef is None:
        return 
    if obj.modClicked == "Computer":
        obj.bots.permission = True
        obj.mainRef.network.stop_listening()
    elif obj.modClicked == "Multiplayer":
        obj.bots.permission = False
        obj.mainRef.network.start_listening()
    obj.mainRef.game.notebook.setTabs(["General"]) if obj.modClicked == "Computer" else obj.mainRef.game.notebook.setTabs(["General", "Chats"])
    obj.mainRef.game.notebook.chattab = ["Chats", obj.mainRef.theMainscreen]
    obj.mainRef.game.notebook.chat_send_button.function = obj.mainRef.game.send

def handleBot(obj):
    obj.data["bot"] = obj.botClicked

menu_list = {
    "handleMod":[handleMod, None],
    "handleBot":[handleBot, None]
}

def Play(obj):
    if obj.home.modClicked == "Computer":
        obj.UImanager.showScreen(obj.gameScreenNo)
    if obj.home.modClicked == "Multiplayer":
        obj.home.connectScreen.visible = True



def Connect(obj):
    obj.mainRef.network.connect(obj.connectScreen.ipAdress, int(obj.connectScreen.port))
    start = time.time()
    while not obj.mainRef.network.is_connected and time.time() - start < 5:
        time.sleep(0.1)

    if obj.mainRef.network.is_connected:
        print("✅ Connected!")
        obj.mainRef.UImanager.showScreen(obj.mainRef.gameScreenNo)
        # obj.mainRef.network.send_chat("hello")


lobby_controls = {
    "Play":[Play, None],
    "Leave":[exit, None],
    "Connect":[Connect, None]
}

