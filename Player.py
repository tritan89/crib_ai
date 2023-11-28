#!/usr/bin/env python3

################################################################################
#
# File : Player.py
# Authors : AJ Marasco and Richard Moulton
#
# Description : An abstract class defining what methods a player class must have
#               in order to play well with Cribbage.py.
#
# Notes : Abstract methods are: throw_crib_cards, play_card, learnFromHandScores,
#         and learnFromPegging
#
#         The verboseFlag is used to control whether or not the print commands
#         are used throughout the file.
#
# Dependencies:
#    - Deck.py (in local project)
#    - abc (standard python library)
#
################################################################################

from abc import ABC, abstractmethod
from Deck import Card


class Player(ABC):
    '''Abstract class defining what methods a player class must have in order to'''

    def __init__(self, number, verbose=False):
        self.hand = []
        self.play_hand = []
        self.number = number
        self.pips = 0
        self.name = "Generic Player"
        self.verbose = verbose

    def new_game(self):
        '''Resets the player's hand and pips for a new game'''
        self.reset()
        self.pips = 0

    def reset(self):
        '''Resets the player's hand for a new hand'''
        self.hand = []
        self.play_hand = []

    def remove_card(self, card):
        '''Removes the argument card from the player's hand'''
        for card in self.play_hand:
            if card.isIdentical(card):
                self.play_hand.remove(card)
                return

        print(
            f"Tried to remove the { str(card)} from {self.get_name()}'s play_hand, but it wasn't there!")

    @abstractmethod
    def throw_crib_cards(self, num_cards, game_state):
        '''Returns a list of cards to throw to the game_state'''

    @abstractmethod
    def play_card(self, game_state):
        '''Returns a card to play'''

    @abstractmethod
    def explain_throw(self):
        '''Prints the cards thrown to the console'''

    @abstractmethod
    def explain_play(self):
        '''Prints the card played to the console'''

    @abstractmethod
    def learn_from_hand_scores(self, scores, game_state):
        '''Updates the player's knowledge based on the scores from the hand'''

    @abstractmethod
    def learn_from_pegging(self, game_state):
        '''Updates the player's knowledge based on the pegging'''

    def end_of_game(self, game_state):
        '''end_of_game is called at the end of the game to allow the player to reset'''

    def thirty_one(self, game_state):
        '''thirty_one is called when the player scores 31 points'''

    def go(self, game_state):
        '''go is called when the player says "go"'''

    def create_play_hand(self):
        '''Creates a copy of the player's hand to be used for pegging'''
        for card in self.hand:
            self.play_hand.append(Card(card.rank, card.suit))

    def get_relative_score(self, game_state):
        '''Returns the score of the player relative to the other player'''
        score = 0
        print('game_state', game_state)
        print(game_state['scores'])
        try:
            if self.number == 1:
                score = game_state['scores'][0] - game_state['scores'][1]
            else:
                score = game_state['scores'][1] - game_state['scores'][0]
        except IndexError as e:
            print(f'Error occurred: {e}')

        return score

    def get_name(self):
        '''Returns the name of the player'''
        return str(self.name + f"({self.number})")

    def __str__(self):
        ''' Returns a string representation of the player's hand'''
        hand = f"{self.get_name()}: "
        for card in self.hand:
            hand = hand + str(card) + ", "

        hand = hand[:-2]
        return hand

    def show(self):
        '''Prints the player's hand to the console'''
        print(f"{self.get_name()} has scored {self.pips} pips.")
        if self.hand:
            print("Current hand is:")
            for card in self.hand:
                print(f"\t{str(card)}")
        else:
            print("Current hand is empty.")

    def is_in_hand(self, check_card):
        '''Returns true if the card is in the player's hand'''
        return check_card in self.hand

    def is_in_play_hand(self, check_card):
        '''Returns true if the card is in the player's play hand'''
        return check_card in self.play_hand

    def draw(self, deck):
        '''Draws a card from the deck and adds it to the player's hand'''
        self.hand.append(deck.cards.pop())
