from enum import Enum
from random import choices, choice
from time import sleep





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
    totalHealth = 0
    critical = False
    playerItems = []
    myItems = []
    actionChain = []
    isNextBlank = False

    def __new__(cls, *args, **kwargs):
        raise TypeError("PrimaryLayer cannot be instantiated")
    

    @classmethod
    def setState(cls, bullets, myhealth, playerhealth, playerItems=[], myItems=[], total_health=5):
        cls.bullets = bullets
        cls.myhealth = myhealth
        cls.playerhealth = playerhealth
        cls.playerItems = playerItems
        cls.myItems = myItems
        cls.totalHealth = total_health

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
    
    @staticmethod
    def addItem(item_name, inventory):
        for idx, (name, qty) in enumerate(inventory):
            if name == item_name:
                # Item found → increment qty
                inventory[idx] = (name, qty + 1)
                return
        # Item not found → add it with qty 1
        inventory.append((item_name, 1))


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
                return qty
        else:
            return False

    @classmethod
    def RunAlgorithm(cls):
        """
        This method runs the primary layer algorithm to make decisions based on the current state of the game.
        It calculates the number of shells, probabilities, and makes decisions based on health and items.
        """
        state = State.neutral
        if cls.playerhealth <= 3:
            if cls.itemExists("Bazuka", cls.myItems) or (cls.itemExists("Fishing Rod", cls.myItems) and cls.itemExists("Bazuka", cls.playerItems)):
                state =  State.aggressive

        elif cls.myhealth <= (cls.totalHealth//cls.myhealth):
            if cls.itemExists("Injection", cls.myItems) :
                state = State.defensive 
            # elif cls.itemExists("Fishing Rod", cls.myItems) and cls.itemExists("Injection", cls.playerItems):
            elif cls.itemExists("Bazuka", cls.playerItems) and cls.itemExists("Glasses", cls.playerItems):
                state = State.defensive
            elif cls.itemExists("Bazuka", cls.myItems) or (cls.itemExists("Fishing Rod", cls.playerItems) and cls.itemExists("Bazuka", cls.myItems)):
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

    clockCount = 0

    @classmethod
    def selection(cls):
        items = []
        glassesUsed = False
        if PrimaryLayer.itemExists("Glasses", PrimaryLayer.myItems):
            items.append("Glasses")
            glassesUsed = False

        elif PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.myItems) and PrimaryLayer.itemExists("Glasses", PrimaryLayer.playerItems):
            items.extend(["Fishing Rod", "Glasses", "Glasses"])
            PrimaryLayer.playerItems = PrimaryLayer.useItems(["Glasses"], PrimaryLayer.playerItems)
            PrimaryLayer.myItems = PrimaryLayer.useItems(["Fishing Rod"], PrimaryLayer.myItems)
            glassesUsed = False


        if not glassesUsed:
            shellProbability, blankProbability = PrimaryLayer.probabilities()
            choice, items = Neutral.selection(shellProbability, blankProbability)
        else:
            choice = "Opponent" if PrimaryLayer.bullets[0] else "Self"
        
        return choice, items
    

    @classmethod
    def tryToSkipShell(cls, steal=False): # Works Perfectly 
        items = []
        SignalJammers, playerSignalJammers, FishingRods = PrimaryLayer.itemExists("Signal Jammer", PrimaryLayer.myItems), PrimaryLayer.itemExists("Signal Jammer", PrimaryLayer.playerItems), PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.myItems)
        bulletCount = len(PrimaryLayer.bullets)
        for _ in range(SignalJammers):
            if bulletCount <= 0:
                return items
            items.append("Signal Jammer") 
            PrimaryLayer.reCalculateShells()
            PrimaryLayer.bullets.pop(0)
            bulletCount -= 1

        if steal:
            for _ in range(playerSignalJammers):
                if FishingRods <= 0 or bulletCount <= 0:
                    return items
                items.extend(["Fishing Rod", "Signal Jammer", "Signal Jammer"])
                PrimaryLayer.reCalculateShells()
                PrimaryLayer.bullets.pop(0)
                bulletCount -= 1
                FishingRods -= 1

        return items


    
    @classmethod
    def tryToUseClock(cls, steal):
        items = []
        Clocks, playerClocks, FishingRods = PrimaryLayer.itemExists("Clock", PrimaryLayer.myItems), PrimaryLayer.itemExists("Clock", PrimaryLayer.playerItems), PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.myItems)
        bulletCount = len(PrimaryLayer.bullets)
        for _ in range(Clocks):
            if bulletCount <= 0:
                return items
            items.append("Clock") 
            bulletCount -= 1
            
        if steal:
            for _ in range(playerClocks):
                if FishingRods <=0 or bulletCount <=0:
                    return items
                items.extend(["Fishing Rod", "Clock", "Clock"])
                FishingRods -= 1
                bulletCount -= 1

        return items
    

    @classmethod
    def stealStealer(cls): # Works perfectly
        items = []
        FishingRods, playerFishingRod = PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.myItems), PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.playerItems)
        
        for _ in range(FishingRods):
            if not playerFishingRod or not FishingRods:
                return items
            items.extend(["Fishing Rod", "Fishing Rod"])
        return items



    @classmethod
    def main(cls, chain):
        selection = "Opponent"
        chain.extend(Neutral.regainHealth())
        chain.extend(cls.stealStealer())
        chain.extend(cls.tryToSkipShell(steal=True))
        chain.extend(cls.tryToUseClock(steal=True))
        # if PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.playerItems):
        #     if len(PrimaryLayer.bullets) <= len(PrimaryLayer.itemExists("Signal Jammer", PrimaryLayer.playerItems)):
        #         chain.extend(cls.tryToSkipShell(steal=True))
        #     if len(PrimaryLayer.bullets) <= len(PrimaryLayer.itemExists("Clock", PrimaryLayer.playerItems)):
        #         chain.extend(cls.tryToUseClock(steal=True))


        if len(PrimaryLayer.bullets) > 0:
            selection, items = cls.selection()
            chain.extend(items)


        PrimaryLayer.reCalculateShells()
        PrimaryLayer.bullets.pop(0)
        return selection


class Aggressive:

    @classmethod
    def switchShell(cls, Glasses, Switch, FishingRod, playerSwitch, items):
        if not PrimaryLayer.bullets[0]:
            if Switch:
                items.append("Switch")
                choice = "Opponent"
            elif playerSwitch and FishingRod:
                items.extend(["Fishing Rod", "Switch", "Switch"])
                choice = "Opponent"
            choice = "Self"
        else:
            choice = "Opponent"
        return choice
    
    @classmethod
    def endOpponent1(cls):
        items = []
        if cls.itemExists("Bazuka", cls.myItems):
            items.append("Bazuka")
            PrimaryLayer.myItems = PrimaryLayer.useItems(["Bazuka"], PrimaryLayer.myItems)
        elif cls.itemExists("Fishing Rod", cls.myItems) and cls.itemExists("Bazuka", cls.playerItems):
            items.extend(["Fishing Rod", "Bazuka", "Bazuka"])
            PrimaryLayer.playerItems = PrimaryLayer.useItems(["Bazuka"], PrimaryLayer.playerItems)
            PrimaryLayer.myItems = PrimaryLayer.useItems(["Fishing Rod", "Bazuka"], PrimaryLayer.myItems)
        return items
    
    # @staticmethod
    # @classmethod
    # def _getAllItems(cls):
    #     Bazuka, Glasses, FishingRod, Clock, Switch = PrimaryLayer.itemExists("Bazuka", PrimaryLayer.myItems), PrimaryLayer.itemExists("Glasses", PrimaryLayer.myItems), PrimaryLayer.itemExists("Fishing Rod", PrimaryLayer.myItems), PrimaryLayer.itemExists("Clock", PrimaryLayer.myItems), PrimaryLayer.itemExists("Switch", PrimaryLayer.myItems)
    #     playerBazuka, playerGlasses, playerClock, playerSwitch = PrimaryLayer.itemExists("Bazuka", PrimaryLayer.playerItems), PrimaryLayer.itemExists("Glasses", PrimaryLayer.playerItems), PrimaryLayer.itemExists("Clock", PrimaryLayer.playerItems), PrimaryLayer.itemExists("Switch", PrimaryLayer.playerItems)
    #     return {
    #         'Bazuka':int(Bazuka), 
    #         'Glasses':int(Glasses),
    #         'FishingRod':int(FishingRod), 
    #         'Clock':int(Clock), 
    #         'Switch':int(Switch), 
    #         'playerBazuka':int(playerBazuka), 
    #         'playerGlasses':int(playerGlasses), 
    #         'playerClock':int(playerClock), 
    #         'playerSwitch':int(playerSwitch)
    #         }
    @classmethod
    def _getAllItems(cls):
        item_names = ["Bazuka", "Glasses", "Fishing Rod", "Clock", "Switch"]
        result = {}

        for item in item_names:
            my_item = PrimaryLayer.itemExists(item, PrimaryLayer.myItems)
            player_item = PrimaryLayer.itemExists(item, PrimaryLayer.playerItems)

            if my_item:
                key = item.replace(" ", "")  # Remove space if any
                result[key] = my_item

            if player_item:
                key = "player" + item.replace(" ", "")
                result[key] = player_item

        return result

    
    @classmethod
    def endOpponent(cls, qtyOfItem):
        items = []
        choice = "Opponent"
        # if PrimaryLayer.playerhealth >= 2:
        print("HEY BOI")
        if qtyOfItem['Bazuka'] and qtyOfItem['Glasses']:
            items.extend(["Bazuka", "Glasses"])
            choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], qtyOfItem['FishingRod'], qtyOfItem['playerSwitch'], items)
            print("1")

        elif qtyOfItem['Bazuka'] and qtyOfItem['FishingRod'] and qtyOfItem['playerGlasses'] and not qtyOfItem['Glasses']:
            items.extend(["Bazuka", "Fishing Rod","Glasses", "Glasses"])
            fh = qtyOfItem['FishingRod']
            fh -= 1
            choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], fh, qtyOfItem['playerSwitch'], items)
            print("2")

                
        elif qtyOfItem['FishingRod'] and qtyOfItem['Glasses'] and qtyOfItem['playerBazuka'] and not qtyOfItem['Bazuka']:
            items.extend(["Glasses", "Fishing Rod","Bazuka", "Bazuka"])
            fh = qtyOfItem['FishingRod']
            fh -= 1
            choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], fh, qtyOfItem['playerSwitch'], items)
            print("3")

        elif qtyOfItem['FishingRod']>1 and qtyOfItem['playerBazuka'] and qtyOfItem['playerGlasses'] and not qtyOfItem['Bazuka'] and not qtyOfItem['Glasses']:
            items.extend(["Fishing Rod", "Bazuka", "Bazuka", "Fishing Rod", "Glasses", "Glasses"])
            qtyOfItem['FishingRod'] -= 1
            choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], qtyOfItem['FishingRod'], qtyOfItem['playerSwitch'], items)
            print("4")
        elif qtyOfItem['Glasses'] and qtyOfItem['Clock']:
            items.extend(["Clock", "Glasses"])
            if qtyOfItem['Glasses']:
                choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], qtyOfItem['FishingRod'], qtyOfItem['playerSwitch'], items)
            print("5")
        elif qtyOfItem['Clock']:
            items.append("Clock")
            if qtyOfItem['Glasses']:
                choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], qtyOfItem['FishingRod'], qtyOfItem['playerSwitch'], items)
            print("6")
        elif qtyOfItem['FishingRod'] and qtyOfItem['playerClock']:
            items.extend(["Fishing Rod","Clock", "Clock"])
            fh = qtyOfItem['FishingRod']
            fh -= 1
            if qtyOfItem['Glasses']:
                choice = cls.switchShell(qtyOfItem['Glasses'], qtyOfItem['Switch'], fh, qtyOfItem['playerSwitch'], items)
            print("7")


            return choice, items
                

    @classmethod
    def attack(cls):
        items = []
        clocks = Defensive.tryToUseClock(steal=True)
        switches = Defensive.tryToSkipShell(steal=True)
        FishingRods = Defensive.stealStealer()
        items.extend([clocks, switches, FishingRods])
        return items
            
    @classmethod
    def main(cls, chain):
        chain.extend(Neutral.regainHealth())
        if PrimaryLayer.playerhealth <= 2:
            selection, items = cls.endOpponent(cls._getAllItems())
            chain.extend(items)
        else:
            chain.extend(cls.attack())
            shellProbability, blankProbability = PrimaryLayer.probabilities()
            selection = "Self" if shellProbability < blankProbability else "Opponent"

        PrimaryLayer.reCalculateShells()
        PrimaryLayer.bullets.pop(0)
        return selection


class Neutral:

    counter = 0
    @classmethod
    def selection(cls, shellProbablity, blankProbability, randomness=True):
        items = []
        useswtich = False
        selection = None
        if PrimaryLayer.itemExists("Switch", PrimaryLayer.myItems):
            useswtich  = choice([True, False]) if randomness else True
            if useswtich:
                # print(PrimaryLayer.myItems, "Initial")
                print("Ujing switch")
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
                items.extend(["Fishing Rod", "Clock", "Clock"])
                print("Ujing rod to steal clock")

                PrimaryLayer.myItems = PrimaryLayer.useItems(["Fishing Rod"], PrimaryLayer.myItems)
                PrimaryLayer.playerItems = PrimaryLayer.useItems(["Clock"], PrimaryLayer.playerItems)

            # sleep(2)
        elif PrimaryLayer.itemExists("Clock", PrimaryLayer.myItems): 
            selection = choice([True, False]) if randomness else True
            selection = False 
            if selection:
                print("Ujing clock")
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
                PrimaryLayer.bullets.pop(0)
        return items
                
                # PrimaryLayer.reCalculateShells()

    @classmethod
    def regainHealth(cls):
        items = []
        item = "Injection" if PrimaryLayer.itemExists("Injection", PrimaryLayer.myItems) else "Pills" if PrimaryLayer.itemExists("Pill", PrimaryLayer.myItems) else None

        # if PrimaryLayer.itemExists("Injection", PrimaryLayer.myItems):
        if item:
            items.append(item)
            PrimaryLayer.myItems = PrimaryLayer.useItems([item], PrimaryLayer.myItems)
        # elif PrimaryLayer.itemExists("Pill", PrimaryLayer.myItems):
        #     items.append("Pill")
        return items if PrimaryLayer.myhealth < PrimaryLayer.totalHealth else []

    @classmethod
    def main(cls, chain):
        print(PrimaryLayer.bullets, len(PrimaryLayer.bullets), "pre Base.py")
        chain.extend(cls.lessenShells())
        chain.extend(cls.regainHealth())
        shellProbablity, blankProbability = PrimaryLayer.probabilities()
        selection, items = cls.selection(shellProbablity, blankProbability)
        chain.extend(items)
        chain.extend(cls.checkForSecondTurn())
        print(PrimaryLayer.bullets, len(PrimaryLayer.bullets), "post Base.py")
        
        PrimaryLayer.reCalculateShells()
        PrimaryLayer.bullets.pop(0)
        return selection
        



            # Play defensively
            # Defensive.play()


class State(Enum):
    """
    Enum representing the state of a bot.
    """
    defensive = 1
    aggressive = 2
    neutral = 3
