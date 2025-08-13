from .base import PrimaryLayer, SecondaryLayer, State, Defensive, Aggressive, Neutral


class Bot:
    
    def __init__(self):
        self.actionChain = []
        self.state = State.neutral
        self.turn = False
        SecondaryLayer.setWeights(0.3, 0.5, 0.2)

    def udpate(self, bullets,  myhealth, playerhealth, playerItems=[], myItems=[], total_health=5):
        PrimaryLayer.setState(bullets, myhealth, playerhealth, playerItems, myItems, total_health)

    def udpateShells(self, blanks, live):
        PrimaryLayer.setShells(blanks, live)

    def chooseState(self):
        self.state = PrimaryLayer.RunAlgorithm()
        if self.state == State.neutral:
            self.state = SecondaryLayer.RunAlgorithm()

    def makeMove(self):
        self.chooseState()
        match self.state:
            case State.defensive:
                selection = Defensive.main(self.actionChain)
            case State.aggressive:
                selection = Aggressive.main(self.actionChain)
            case _:
                selection = Neutral.main(self.actionChain)


        # if self.state == State.defensive:
        #     selection = Defensive.main(self.actionChain)
        # elif self.state == State.aggressive:
        #     selection = Aggressive.main(self.actionChain)
        # elif self.state == State.neutral:
        #     selection = Neutral.main(self.actionChain)
        print(self.state)
        # choice = self.state.value.main(self.actionChain)
        return selection
    
  
    @property
    def myItems(self):
        return PrimaryLayer.myItems
    
    @property
    def playerItems(self):
        return PrimaryLayer.playerItems
    


