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
import random
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# Cribbage imports
from Player import Player
from Deck import Deck
from Scoring import getScoreNoStarter, getScore


class Player_AI(Player):
    '''A simple instantiation of a Player. AI makes decisions.'''

    def __init__(self, number, verboseFlag):
        super().__init__(number)
        self.verbose = verboseFlag
        self.name = "AI"

    # selects crib cards based on the highest scoring hand without the starter card
    def __selectCribCards__(self):
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

    # takes in a list of lists with the inner list containing a list with [hand, hand_score, card, crib_cards]
    # outermost list of list where each list contains a different hand
    # inner contains a list of the hand with every possible starter card and the score of that hand with that starter card
    def analyzeCribCards(self, scored_hands):
        bestHand = []
        avgResult = []
        hand_list = []
        for hand in scored_hands:
            avg = 0
            for hand_score in hand:
                avg += hand_score[1]
            avg = avg/15
            avgResult.append(avg)
            hand_list.append([hand_score[0], hand_score[3]])
        max_score = max(avgResult)
        index = avgResult.index(max_score)
        bestHand = hand_list[index]
        return bestHand

    def get_deck_without_hand(self, hand):
        '''Returns a deck without the cards in the hand'''
        deck = Deck(1)
        for card in hand:
            deck.cards.remove(card)
        return deck

    def __CribCardsWithstarter__(self):
        possible_hands = combinations(self.hand, 4)
        deck = self.get_deck_without_hand(self.hand)
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
        return random.randrange(0, handSize, 1)

    # Function to pass crib card to play hand
    def throw_crib_cards(self, num_cards, game_state):
        print('game_state', game_state)

        # Function to determine which cards to throw into the crib
        self.hand, cribCards = self.__CribCardsWithstarter__()
        if self.verbose:
            print("{} threw {} cards into the crib".format(
                self.get_name(), num_cards))

        super().create_play_hand()

        return cribCards

    # Randomly select a card to play while making sure that it won't put the count over 31
    def playCard(self, gameState):
        handSize = len(self.play_hand)
        cardIndices = list(range(0, handSize))
        count = game_state['count']
        playedCard = None

        while playedCard is None:

            if (self.checkForEmptyHand()):
                return None

            index = self.__selectCard__(handSize)
            cardIndex = cardIndices[index]

            if (self.checkForNonPlayableCard(cardIndex, count)):
                if (self.checkForNoPlayableCards(cardIndices, index)):
                    return None

            playedCard = self.play_hand.pop(cardIndex)
            if (self.verbose):
                print("\tPlayer_AI ({}) played {}".format(
                    self.number, str(playedCard)))

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
        if count + self.play_hand[cardIndex].value() > 31:
            return True

   # checks if the player has any cards left in their hand
    def checkForEmptyHand(self):
        if (len(self.play_hand) == 0):
            if (self.verbose):
                print("\tPlayer_AI ({}) has no cards left; go!".format(self.number))
            return True

    # noPlayableCards is called when the player has no playable cards
    def checkForNoPlayableCards(self, cardIndices, index):
        cardIndices.pop(index)
        if len(cardIndices) == 0:
            if (self.verbose):
                print("\tPlayer_AI ({}) has no playable cards; go!".format(self.number))
            return True

    def explain_throw(self):
        '''Prints the cards thrown to the console'''
        print(
            f"Random ({self.number}) chose to throw those cards into the crib randomly. No explanation.")

    def explain_play(self):
        '''Prints the card played to the console'''''
        print(
            f"Random ({self.number}) chose to play that card during pegging at random. No reason.")

    # Player_AI does not learn
    def learn_from_hand_scores(self, scores, game_state):
        pass

    # Player_AI does not learn
    def learn_from_pegging(self, game_state):
        pass
