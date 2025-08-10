from enum import Enum
from random import choices, choice
from time import sleep


class State(Enum):
    """
    Enum representing the state of a bot.
    """
    defensive = 1
    aggressive = 2
    neutral = 3


class Layers(Enum):
    """
    Enum representing the layers for decision making.
    """
    primary = 1
    secondary = 2


class PrimaryLayer:
    """"
    This class represents the primary layer of decision making for a bot.
    1. This includes shell tracking and use probalities of the next shell, being live or empty. 
    2. Also tracking health of both players. 
    3. After that tracking items that could instantly end you (like combo of clock and bazuka). Items that can instantly heal him making you attack null (like injection or pill).
    """
    bullets = 0
    blanks = 0
    live = 0
    myhealth = 0
    playerhealth = 0
    critical = False
    playerItems = []
    myItems = []
    actionChain = []
    isNextBlank = False

    def __new__(cls, *args, **kwargs):
        raise TypeError("PrimaryLayer cannot be instantiated")
    

    @classmethod
    def setState(cls, bullets, myhealth, playerhealth, playerItems=[], myItems=[]):
        cls.bullets = bullets
        cls.myhealth = myhealth
        cls.playerhealth = playerhealth
        cls.playerItems = playerItems
        cls.myItems = myItems

    @classmethod
    def setShells(cls, blanks, live):
        cls.blanks = blanks
        cls.live = live

    @classmethod
    def reCalculateShells(cls):
        if len(cls.bullets) <= 0:
            return
        if cls.bullets[0]:
            cls.live -= 1
        else:
            cls.blanks -= 1

    @staticmethod
    def useItems(iterables, inventory):
        inventory_dict = dict(inventory)

        for item in iterables:
            if item in inventory_dict and inventory_dict[item] > 0:
                inventory_dict[item] -= 1

        return list(inventory_dict.items())


    @classmethod
    def probabilities(cls):
        """ This method returns the probabilities (of shell, of blank)"""
        if len(cls.bullets) > 0 :
            # print(len(cls.bullets), len(cls.bullets) > 0 , cls.bullets[0])
            shellPropbability = (cls.live/len(cls.bullets)) 
        else:
            shellPropbability = 0
        return (shellPropbability, 1-shellPropbability)
        ...
    
    @staticmethod
    def itemExists(item_name, inventory):
        for item, qty in inventory:
            # print(qty if qty==0 else '\033[F')
            if item_name == item and (qty > 0):
                return True

    @classmethod
    def RunAlgorithm(cls):
        """
        This method runs the primary layer algorithm to make decisions based on the current state of the game.
        It calculates the number of shells, probabilities, and makes decisions based on health and items.
        """
        state = State.neutral
        if cls.playerhealth <= 2:
            if cls.itemExists("Bazuka", cls.myItems):
                state =  State.aggressive

        elif cls.myhealth <= 2:
            if cls.itemExists("Injection", cls.myItems) :
                state = State.defensive 
            elif cls.itemExists("Fishing Rod", cls.myItems) and cls.itemExists("Injection", cls.playerItems):
                state = State.defensive
            else:
                state = State.aggressive

        return state



class SecondaryLayer:
    """
    This class represents the secondary layer of decision making for a bot.
    This layer helps to choose state of the bot, if choosing other state makes no sinificant difference,then the one chosen by Primary Layer. It is done by the use of weights.
    """
    defensiveWeight = 0.5
    aggressiveWeight = 0.5
    neutralWeight = 0.5
    actionChain = []


    def __new__(cls, *args, **kwargs):
        raise TypeError("PrimaryLayer cannot be instantiated")
    
    @classmethod
    def setWeights(cls, defensive: float, aggressive: float, neutral: float):
        cls.defensiveWeight = defensive
        cls.aggressiveWeight = aggressive
        cls.neutralWeight = neutral

    @classmethod
    def RunAlgorithm(cls):
        state = choices([State.defensive, State.aggressive, State.neutral], [cls.defensiveWeight, cls.aggressiveWeight, cls.neutralWeight], k=1)
        return state



class Defensive:
    @classmethod
    def play(self):
        ...


class Aggressive:
    @classmethod
    def play(self):
        ...


class Neutral:

    counter = 0
    @classmethod
    def selection(cls, shellProbablity, blankProbability, randomness=True): # It works !!
        items = []
        useswtich = False
        selection = None
        if PrimaryLayer.itemExists("Switch", PrimaryLayer.myItems):
            useswtich  = choice([True, False]) if randomness else True
            if useswtich:
                # print(PrimaryLayer.myItems, "Initial")
                for index, data in enumerate(PrimaryLayer.myItems):
                    item, qty = data
                    # print(item)
                    if item == "Switch":
                        qty -= 1
                        PrimaryLayer.myItems[index] = (item, qty)
                        break


                items.append("Switch")
                # PrimaryLayer.myItems = PrimaryLayer.useItems(["Switch"], PrimaryLayer.myItems)
                # sleep(2)
        
        if useswtich:
            selection = "Self" if shellProbablity >= blankProbability else "Opponent"
        else:
            selection = "Self" if shellProbablity <= blankProbability else "Opponent"
        print(selection)

        return selection, items
    
    @classmethod
    def checkForSecondTurn(cls, randomness=True):
        cls.counter += 1
        items = []
            # sleep(2)
        if (PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.myItems) and PrimaryLayer.itemExists("Clock", PrimaryLayer.playerItems)) :
            selection = choice([True, False]) if randomness else True
            if selection:
        # choice([True, False]):
                items.extend(["Fishing Rod", "Clock"])
                PrimaryLayer.myItems = PrimaryLayer.useItems(["Fishing Rod"], PrimaryLayer.myItems)
                PrimaryLayer.playerItems = PrimaryLayer.useItems(["Clock"], PrimaryLayer.playerItems)

            # sleep(2)
        if PrimaryLayer.itemExists("Clock", PrimaryLayer.myItems): 
            selection = choice([True, False]) if randomness else True
            if selection:
                items.append("Clock")
                PrimaryLayer.myItems = PrimaryLayer.useItems(["Clock"], PrimaryLayer.myItems)
                
        # print(PrimaryLayer.playerItems)
        print(f'counter : {cls.counter}')
        return items
    

    @classmethod
    def lessenShells(cls, randomness=True):
        items = []
        selecion = choice([True, False]) if randomness else True
        if selecion:
            if PrimaryLayer.itemExists("Signal Jammer", PrimaryLayer.myItems):
                items.append("Signal Jammer")
                PrimaryLayer.reCalculateShells()
                PrimaryLayer.myItems = PrimaryLayer.useItems(["Signal Jammer"], PrimaryLayer.myItems)
                # PrimaryLayer.reCalculateShells()

    

    @classmethod
    def play(cls, chain):
        print(PrimaryLayer. bullets, "pre")
        shellProbablity, blankProbability = PrimaryLayer.probabilities()
        selection, items = cls.selection(shellProbablity, blankProbability)
        chain.extend(items)
        items = cls.checkForSecondTurn()
        if len(items) > 0:
            chain.extend(items)
        print(PrimaryLayer. bullets, "post")

        return selection
        



            # Play defensively
            # Defensive.play()
