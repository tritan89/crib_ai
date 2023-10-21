#!/usr/bin/env python3

################################################################################
#
# File : Player_AI.py
# Authors : Kjartan, Tristan
#
# Description : A simple instantiation of a Player. AI makes decisions.
#
# Notes : Player_AI is a simple AI that makes decisions based on the current game
#
# Dependencies:
#    - Player.py (in local project)
#    - Utilities.py (in local project)
#    - Deck.py (in local project)
#    - Arena.py (in local project)          * - for __name__ = '__main__' only
#    - Myrmidon.py (in local project)       * - for __name__ = '__main__' only
#    - numpy (standard python library)      * - for __name__ = '__main__' only
#    - random (standard python library)
#    - matplotlib (standard python library) * - for __name__ = '__main__' only
#
################################################################################

# Cribbage imports
from calendar import c
from Player import Player
from Utilities import *
from Deck import Card,RiggedDeck
from Arena import Arena

# Player imports
from Myrmidon import Myrmidon

# Utility imports
import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt

class Player_AI(Player):

    def __init__(self, number,verboseFlag):
        super().__init__(number)
        self.verbose = verboseFlag
        self.name = "AI"

    def reset(self, gameState=None):
        super().reset()

    def __selectCribCards__(self, handSize):
        return random.randrange(0,handSize,1)
    
    def __selectCard__(self, handSize):
        return random.randrange(0,handSize,1)

    # Function to pass crib card to play hand
    def throwCribCards(self, numCards, gameState):
        print('gameState', gameState);
        handSize = len(self.hand)

        cribCards = []

        # Function to determine which cards to throw into the crib
        selectedCard = self.__selectCribCards__(handSize)
        cribCards.append(self.hand.pop(selectedCard))
        
        if self.verbose:
            print("{} threw {} cards into the crib".format(self.getName(), numCards))

        super().createPlayHand()

        return cribCards

    # Randomly select a card to play while making sure that it won't put the count over 31
    def playCard(self, gameState):
        handSize = len(self.playhand)
        cardIndices = list(range(0, handSize))
        count = gameState['count']
        playedCard = None

        while playedCard is None:
            
            if(self.checkForEmptyHand()):
                return None
        
            index = self.__selectCard__(handSize)
            cardIndex = cardIndices[index]
          
            if(self.checkForNonPlayableCard(cardIndex, count)):
                if(self.checkForNoPlayableCards(cardIndices,index)):
                    return None
                 
            playedCard = self.playhand.pop(cardIndex)
            if(self.verbose):
                print("\tPlayer_AI ({}) played {}".format(self.number, str(playedCard)))

        return playedCard
    
    def checkForNonPlayableCard(self, cardIndex, count):
        if count + self.playhand[cardIndex].value() > 31:
            return True
 
   # checks if the player has any cards left in their hand
    def checkForEmptyHand(self):
        if(len(self.playhand) == 0):
            if(self.verbose):
                print("\tPlayer_AI ({}) has no cards left; go!".format(self.number))
            return True

    # noPlayableCards is called when the player has no playable cards
    def checkForNoPlayableCards(self,cardIndices, index):
        cardIndices.pop(index)
        if len(cardIndices) == 0:
            if(self.verbose):
                print("\tPlayer_AI ({}) has no playable cards; go!".format(self.number))
            return True

    # Explain why certain cards were thrown into the crib
    def explainThrow(self,numCards,gameState):
        print("Random ({}) chose to throw those cards into the crib randomly. No explanation.".format(self.number))
        
    # Explain why a certain card was played during pegging
    def explainPlay(self,numCards,gameState):
        print("Random ({}) chose to play that card during pegging at random. No reason.".format(self.number))

    # Player_AI does not learn
    def learnFromHandScores(self, scores, gameState):
        pass
    
    # Player_AI does not learn
    def learnFromPegging(self, gameState):
        pass
    
if __name__ == '__main__':
    # Initialize variables
    player1 = Player_AI(1, False)
    player2 = Myrmidon(2,5,False)
    numHands = 5000
    repeatFlag = False
    windowSize = 100
        
    # Create and run arena
    arena = Arena([player1, player2],repeatFlag)
    results = arena.playHands(numHands)
    
    # Plot results from arena
    x = np.arange(1,numHands+1-windowSize,1)
    y0 = np.zeros(len(results[0])-windowSize)
    avgResult0 = np.average(results[0])
    mu0 = np.zeros(len(y0))
    y1 = np.zeros(len(results[1])-windowSize)
    avgResult1 = np.average(results[1])
    mu1 = np.zeros(len(y1))
    y2 = np.zeros(len(results[2])-windowSize)
    avgResult2 = np.average(results[2])
    mu2 = np.zeros(len(y2))
    
    for i in range(len(x)):
        y0[i] = np.average(results[0][i:i+windowSize])
        mu0[i] = np.average(avgResult0)
        y1[i] = np.average(results[1][i:i+windowSize])
        mu1[i] = np.average(avgResult1)
        y2[i] = np.average(results[2][i:i+windowSize])
        mu2[i] = np.average(avgResult2)
    
    fig, (ax0,ax1,ax2) = plt.subplots(3, 1, sharex='col')
    fig.set_size_inches(7, 6.5)
    
    moveAvg, = ax0.plot(x,y0,label='Moving Average')
    fullAvg, = ax0.plot(x,mu0,label='Trial Average\n({0:2f} points)'.format(avgResult0))
    ax0.set(ylabel='Pegging Differential', title="Random vs. Myrmidon (5 Simulations)\n(Moving Average Window Size = {0})".format(windowSize))
    ax0.grid()
    ax0.legend(handles=[moveAvg,fullAvg],bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    moveAvg, = ax1.plot(x,y1,label='Moving Average')
    fullAvg, = ax1.plot(x,mu1,label='Trial Average\n({0:2f} points)'.format(avgResult1))
    ax1.set(ylabel='Hand Differential')
    ax1.grid()
    ax1.legend(handles=[moveAvg,fullAvg],bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    moveAvg, = ax2.plot(x,y2,label='Moving Average')
    fullAvg, = ax2.plot(x,mu2,label='Trial Average\n({0:2f} points)'.format(avgResult2))
    ax2.set(xlabel='Hand Number', ylabel='Total Differential')
    ax2.grid()
    ax2.legend(handles=[moveAvg,fullAvg],bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout()

    fig.savefig("randomPlayerLearningCurveNonStationary.png")
    plt.show()