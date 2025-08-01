
import openai


""" Reseting the root diretory manually"""
from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../')))
""" Reseting the root diretory manually"""

from random import choice
from json import dumps
from config.game import PHASES

class Bot:
    def __init__(self, name):
        self.name = name
        self.difficulty_level = 1
        self.inventoryItems = []
        self.ExtraTurn = False
        self.configure()
        

    def configure(self):
        self.currentPhase = 1
        self.health = PHASES[self.currentPhase][2]


    def playTurn(self, functions=[]):
        selection = choice(["Self","Opponent"])
        if selection == "Self" and not self.ExtraTurn:
            self.ExtraTurn = True
            turn_terminated = False

        else:
            turn_terminated = True
            self.ExtraTurn = False

        # turn_terminated = True if selection == "Opponent" else False
        for function in functions:
            function()

        
        data = {"Selection" : selection,"turn terminated": turn_terminated}
        return dumps(data)


