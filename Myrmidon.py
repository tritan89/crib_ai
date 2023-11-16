#!/usr/bin/env python3

################################################################################
#
# File : Myrmidon.py
# Authors : AJ Marasco and Richard Moulton
#
# Description : A Player that makes use of one-step rollouts and heuristics.
#
# Notes : If this file is run, it instantiates an Arena and measures this agent's
#         performance against itself.
#
# Dependencies:
#    - Utilities.py (in local project)
#    - Deck.py (in local project)
#    - Scoring.py (in local project)
#    - Arena.py (in local project)           * - for __name__ = '__main__' only
#    - Player.py (in local project)
#    - numpy (standard python library)
#    - itertools (standard python library)
#    - random (standard python library)
#    - matplotlib (standard python library)  * - for __name__ = '__main__' only
#
################################################################################

# Cribbage imports
from Utilities import cardsString
from Deck import Card
from Scoring import scoreCards, getScore

# Player imports
from Player import Player

# Utility imports
import numpy as np
from itertools import combinations
import random
import matplotlib.pyplot as plt

class Myrmidon(Player):

    def __init__(self, number, numSims,verboseFlag):
        super().__init__(number)
        self.numSims = max(numSims,1)
        self.verbose = verboseFlag
        self.name = "Myrmidon"
        self.cribThrow = []
        self.throwString = ""
        self.playString = ""

    def reset(self, gameState=None):
        super().reset()

    # If the argument card is in the argument set of cards, return true.
    # Otherwise return false.
    def inHand(self, cardToCheck):
        return cardToCheck in self.hand

    # Returns a random starter card that isn't in the player's hand
    def randomStarter(self):
        newCard = Card(random.randint(1, 13), random.randint(1, 4))

        while newCard in self.hand:
            newCard = Card(random.randint(1, 13), random.randint(1, 4))

        return newCard

    # Chooses which cards to throw based on randomly sampling potential starter
    # cards for each combination of cards thrown.
    def throwCribCards(self, numCards, gameState):
        cribCards = []
        cardScores = np.zeros(len(self.hand))
        if gameState['dealer'] == (self.number - 1):
            dealerFlag = True
        else:
            dealerFlag = False 
            
        self.throwString = "Myrmidon ({}) is considering a hand of: {}".format(self.number,cardsString(self.hand))
        if dealerFlag:
            self.throwString = "{}. Own crib.\n".format(self.throwString)
        else:
            self.throwString = "{}. Opponent's crib.\n".format(self.throwString)
            
        # Score the cards that would be left in the player's hand
        for combination in combinations(self.hand, len(self.hand) - numCards):
            for i in range(0, self.numSims):
                starterCard = self.randomStarter()
                score = getScore(list(combination), starterCard, False)
                for j in range(0, len(self.hand)):
                    if self.hand[j] in combination:
                        cardScores[j] += score

        # Score the cards that would be thrown in the crib
        for combination in combinations(self.hand, numCards):
            for i in range(0, self.numSims):
                starterCard = self.randomStarter()
                score = getScore(list(combination), starterCard, False)
                for j in range(0, len(self.hand)):
                    if self.hand[j] in combination:
                        if dealerFlag:
                            # We can worry less about keeping the card if it
                            # will score points for us in the crib
                            cardScores[j] -= score
                            if self.hand[j].rank == 5:
                                cardScores[j] += 2
                        else:
                            # We should keep cards that will score points for 
                            # our opponents in the crib
                            cardScores[j] += score

        for i in range(len(self.hand)):
            self.throwString = "{}\t{}: {}\n".format(self.throwString,str(self.hand[i]),cardScores[i])

        # Pick the lowest scoring cards to throw
        for i in range(0, numCards):
            lowIndex = min(range(len(cardScores)), key=cardScores.__getitem__)
            cribCards.append(self.hand.pop(lowIndex))
            cardScores = np.delete(cardScores, lowIndex)

        self.throwString = "{}I chose to throw: {}\n\n".format(self.throwString, cardsString(cribCards))

        if(self.verbose):
            print("Myrmidon ({}) threw {} cards into the crib".format(self.number, numCards))

        super().createPlayHand()

        self.cribThrow = cribCards

        return cribCards

    def explainThrow(self):
        print(self.throwString)

    # Chooses a card to play during pegging by maximizing the immediate return
    # and the value of the afterstate according to some heuristic rules.
    def playCard(self, gameState):
        cardScores = np.zeros(len(self.playhand))
        playedCard = None
        countCards = gameState['inplay']
        count = gameState['count']

        if len(self.playhand) != 0:
            self.playString = "\tMyrmidon ({}) is considering:\n".format(self.number)
            for i in range(0, len(self.playhand)):
                self.playString = "{}\t{} ".format(self.playString,str(self.playhand[i]))
                # Check that the card can be played
                if count + self.playhand[i].value() < 32:
                    newCountCards = countCards + [self.playhand[i]]
                    cardScores[i] += 10 * scoreCards(newCountCards, False) + self.playhand[i].rank.value
                    self.playString = "{}scores {} for its rank,".format(self.playString,cardScores[i])
                    if (count + self.playhand[i].value() == 5) or (count + self.playhand[i].value() == 10) or (
                            count + self.playhand[i].value() == 21):
                        cardScores[i] = max(1, cardScores[i] - 10)
                        self.playString = "{0}is adjusted to {1} for the count left ({2}), ".format(self.playString,cardScores[i],(count + self.playhand[i].value()))
                    if count + self.playhand[i].value() < 5:
                        cardScores[i] += 15
                        self.playString = "{}is rewarded for leaving a count of less than 5, ".format(self.playString)
                    self.playString = "{} Final score is {}.\n".format(self.playString,cardScores[i])
                else:
                    self.playString = "{}can't be played.\n".format(self.playString)

            if np.amax(cardScores) > 0:
                playedCard = self.playhand.pop(max(range(len(cardScores)), key=cardScores.__getitem__))
                self.playString = "{}\tI choose to play {}\n".format(self.playString,str(playedCard))
                if(self.verbose):
                    print("\tMyrmidon ({}) played {}".format(self.number, str(playedCard)))
            else:
                self.playString = "{}\tI can't play any of my cards and have to say go!\n".format(self.playString)
                if(self.verbose):
                    print("\tMyrmidon ({}) says go!".format(self.number))
        else:
            self.playString = "\tMyrmidon ({}): I have no cards left and have to say go!".format(self.number)
            if(self.verbose):
                print("\tMyrmidon ({}) has no cards left; go!".format(self.number))

        return playedCard

    def explainPlay(self):
       print(self.playString)

    # Myrmidon does not learn
    def learnFromHandScores(self, scores, gameState):
        pass
    
    # Myrmidon does not learn
    def learnFromPegging(self, gameState):
        pass

    def show(self):
        print('{}:'.format(self.getName()))
        print('Hand:' + cardsString(sorted(self.playhand)))
