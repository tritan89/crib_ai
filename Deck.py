#!/usr/bin/env python3

################################################################################
#
# File : Deck.py
# Authors : AJ Marasco and Richard Moulton
#
# Description : Classes representing Suits, Ranks, Cards and Decks.
#
# Notes : Every card has a suit and rank. A card's value is what it contributes
#         to the count according to the rules of cribbage.
#
# Dependencies:
#    - enum (standard python library)
#    - random (standard python library)
#
################################################################################

from enum import Enum
import random


class Suit(Enum):
    '''Enum representing the four suits of a standard deck of cards'''
    Spades = 1
    Hearts = 2
    Diamonds = 3
    Clubs = 4


class Rank(Enum):
    '''Enum representing the 13 ranks of a standard deck of cards'''
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13


class Card:
    '''Class representing a single card in a standard deck of cards'''

    def __init__(self, rank, suit):
        if isinstance(suit, int):
            self.suit = Suit(suit)
        else:
            self.suit = suit

        if isinstance(rank, int):
            self.rank = Rank(rank)
        else:
            self.rank = rank

    def __lt__(self, other):
        return self.rank.value < other.rank.value

    def __gt__(self, other):
        return self.rank.value > other.rank.value

    def __eq__(self, other):
        return self.rank.value == other.rank.value

    def uid(self):
        '''Returns a unique identifier for the card'''
        return 13 * (self.suit.value - 1) + self.rank.value

    def get_rank(self):
        '''Returns the rank of the card'''
        return self.rank

    def get_suit(self):
        '''Returns the suit of the card'''
        return self.suit

    def value(self):
        '''Returns the value of the card'''
        if self.rank.value > 10:
            return 10
        else:
            return self.rank.value

    def __str__(self):
        symbols = ["", "\u2660", "\u2661", "\u2662", "\u2663"]
        vals = ["0", "A", "2", "3", "4", "5", "6",
                "7", "8", "9", "10", "J", "Q", "K"]
        return f"{symbols[self.suit.value]} {vals[self.rank.value]}"

    def show(self):
        '''Prints the card to the console'''
        print(str(self))

    def explain(self):
        '''Prints the card to the console with additional information'''
        print(f"{self.rank.name} of {self.suit.name} has a value of {self.value()} and a uid of {self.uid()}")

    def is_identical(self, card):
        '''Returns True if the card is identical to the given card'''
        return card.uid() == self.uid()


class Deck:
    '''Class representing a deck of cards'''

    def __init__(self, num_decks):
        self.cards = []
        for _ in range(1, num_decks + 1):
            self.build()

    def build(self):
        '''Builds a deck of cards'''
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(rank, suit))

    def shuffle(self):
        '''Shuffles the deck of cards'''
        for _ in range(random.randint(3, 10)):
            random.shuffle(self.cards)

    def cut(self):
        '''Cuts the deck of cards'''
        t = random.randint(1, len(self.cards))
        self.cards = self.cards[t:] + self.cards[:t]

    def deal(self, players, num_cards):
        '''Deals cards to the players'''
        for _ in range(1, num_cards + 1):
            for player in players:
                player.draw(self)

    def show(self):
        '''Prints the deck of cards to the console'''
        for card in self.cards:
            card.show()
