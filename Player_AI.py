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
from Deck import Card,RiggedDeck, Deck
from Arena import Arena
from Scoring import getScoreNoStarter, getScore, scoreCards

# Player imports
from Myrmidon import Myrmidon

# Utility imports
import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt
from itertools import combinations

class Player_AI(Player):

    def __init__(self, number,verboseFlag):
        super().__init__(number)
        self.verbose = verboseFlag
        self.name = "AI"

    def reset(self, gameState=None):
        super().reset()

    # selects crib cards based on the highest scoring hand without the starter card
    def __selectCribCards__(self, handSize):
        possible_hands = combinations(self.hand, 4)
        max_score = -1
        bestHand = []
        for hand in possible_hands: 
            hand = list(hand)
            hand_score = getScoreNoStarter(hand, False)
            if hand_score > max_score:
                max_score = hand_score
                bestHand = hand
        crib_cards = [x for x in self.hand if x not in bestHand]
        return bestHand, crib_cards
    

    
   


    # takes in a list of lists with the inner list containg a list with [hand, hand_score, card, crib_cards]
    #outermost list of list where each list contains a different hand 
    # inner contains a list of the hand with every possible starter card and the score of that hand with that starter card
    def analyzeCribCards(self, scored_hands):
        bestHand = []
        avgResult = []
        hand_list = []
        for hand in scored_hands:
            avg= 0
            for hand_score in hand:
                avg += hand_score[1]
            avg =avg/15
            avgResult.append(avg)
            hand_list.append([hand_score[0],hand_score[3]])
        max_score = max(avgResult)
        index = avgResult.index(max_score)
        bestHand = hand_list[index]
        return bestHand
    
    def get_deck_without_hand(self, hand):
        deck = Deck(1)
        for card in hand:
            deck.cards.remove(card)
        return deck

    def __CribCardsWithstarter__(self):
            possible_hands = combinations(self.hand, 4)
            deck = self.get_deck_without_hand(self.hand)
            bestHand = []
            scores = []
            for hand in possible_hands: 
                hand = list(hand)
                crib_cards = [x for x in self.hand if x not in hand]
                scores_with_card=[]
                for card in deck.cards: # check every card in the deck with the hand given
                    hand_score = getScore(hand, card, False)
                    
                    scores_with_card.append([hand, hand_score, card, crib_cards]) #create a list of lists with the hand, score, starter card, and crib cards
                scores.append(scores_with_card)
            return self.analyzeCribCards(scores)
    


        
    
    
    def __selectCard__(self, handSize):
        return random.randrange(0,handSize,1)

    # Function to pass crib card to play hand
    def throwCribCards(self, numCards, gameState):
        print('gameState', gameState);
        handSize = len(self.hand)

        # Function to determine which cards to throw into the crib
        self.hand, cribCards = self.__CribCardsWithstarter__()
        if self.verbose:
            print("{} threw {} cards into the crib".format(self.getName(), numCards))

        super().createPlayHand()

        return cribCards

    # Randomly select a card to play while making sure that it won't put the count over 31
    def playCard2(self, gameState):
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
    
    # Randomly select a card to play while making sure that it won't put the count over 31
    
    def playCard2(self, gameState):
        selected_card = None
        count = gameState['count']
        for card in self.playhand:
            if count == 0:
                if card.value() < 5:
                    selected_card = card
                    break
            if count < 15:
                if card.value() + count >= 15:
                    selected_card = card
                    break
            if count > 15:
                if card.value() + count < 31:
                    selected_card = card
                    break
        return selected_card
    
    def playCard(self, gameState):
        selected_card = None
        count = gameState['count']
        countCards = gameState['inplay']
        card_scores = np.zeros(len(self.playhand))
        for card, i in self.playhand.enumerate():
            played_cards_new = countCards.append(card)
            if card.value() + count <= 31:
                card_scores[i] += 10 * scoreCards(played_cards_new, False) + self.playhand[i].rank.value
                if (card.value() + count == 10) or (card.value() + count == 5) or (card.value() + count == 21):
                    card_scores[i] = max(1, card_scores[i] - 10)
                if card.value() + count <= 5:
                    card_scores[i] += 15
        if np.amax(card_scores) > 0:
            selected_card = self.playhand.pop(max(range(len(card_scores)), key=card_scores.__getitem__))
        return selected_card
    
    


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
    arena = Arena([player1, player2],repeatFlag,False)
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
    ax0.set(ylabel='Pegging Differential', title="AI vs. Myrmidon (5 Simulations)\n(Moving Average Window Size = {0})".format(windowSize))
    ax0.grid()
    ax0.legend(handles=[moveAvg,fullAvg],bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    moveAvg, = ax1.plot(x,y1,label='Moving Average')
    fullAvg, = ax1.plot(x,mu1,label='Trial Average\n({0:2f} points)'.format(avgResult1))
    ax1.set(ylabel='Hand Differential')
    ax1.grid()
    ax1.legend(handles=[moveAvg,fullAvg],bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    moveAvg, = ax2.plot(x,y2,label='Moving Average')
    fullAvg, = ax2.plot(x,mu2,label='AI Average\n({0:2f} points)'.format(avgResult2))
    ax2.set(xlabel='Hand Number', ylabel='Total Differential')
    ax2.grid()
    ax2.legend(handles=[moveAvg,fullAvg],bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout()

    fig.savefig("AIPlayerLearningCurveNonStationary.png")
    plt.show()