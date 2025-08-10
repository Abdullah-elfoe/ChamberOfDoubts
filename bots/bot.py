from .base import PrimaryLayer, SecondaryLayer, State, Defensive, Aggressive, Neutral


class Bot:
    

    def __init__(self):
        self.actionChain = []
        self.state = State.neutral
        self.turn = False
        SecondaryLayer.setWeights(0.3, 0.5, 0.2)

    def udpate(self, bullets,  myhealth, playerhealth, playerItems=[], myItems=[]):
        PrimaryLayer.setState(bullets, myhealth, playerhealth, playerItems, myItems)

    def udpateShells(self, blanks, live):
        PrimaryLayer.setShells(blanks, live)

    def chooseState(self):
        self.state = PrimaryLayer.RunAlgorithm()
        if self.state == State.neutral:
            self.state = SecondaryLayer.RunAlgorithm()

    def makeMove(self):
        self.chooseState()
        # if self.state == State.defensive:
        #     Defensive.play()
        # elif self.state == State.aggressive:
        #     Aggressive.play()
        # elif self.state == State.neutral:
        #     Neutral.play()
        choice = Neutral.play(self.actionChain)
        return choice
    
  
    @property
    def myItems(self):
        return PrimaryLayer.myItems
    
    @property
    def playerItems(self):
        return PrimaryLayer.playerItems
    


