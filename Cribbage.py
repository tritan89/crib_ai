#!/usr/bin/env python3

################################################################################
#
# File : Cribbage.py
# Authors : AJ Marasco and Richard Moulton
#
# Description : Main file for playing a game of cribbage. Plays through hands
#               one at a time, scoring for nobs, pegging and hands as it goes.
#               Winner is declared as soon as one player reaches 121 points.
#
# Notes : Although this class is mostly written flexibly to allow for three or
#         four player cribbage, it has not been tested for these games. As well,
#         the game does not have a conception of players being on the same team.
#
#         The verboseFlag is used to control whether or not the print commands
#         are used throughout the file.
#
# Dependencies:
#    - Deck.py (in local project)
#    - Scoring.py (in local project)
#    - Utilities.py (in local project)
#    - random (standard python library)
#
################################################################################

# Cribbage imports
import random
from Deck import Rank, Deck
from Scoring import getScore, scoreCards

# Utility imports
from Utilities import cardsString, areCardsEqual


class Cribbage:
    '''Class representing a game of cribbage'''

    def __init__(self, player_array, critic=None, verbose_flag=True, rigged=False):
        # Build a single standard deck
        self.rigged = rigged
        self.create_deck()
        # Initialize and empty crib
        self.crib = []
        # Initialize a holder for the cut card
        self.starter = []
        # Initialize the list of played cards
        self.play_order = []
        # Initialize the list of cards currently counting
        self.in_play = []
        # Randomly select which player starts with the crib
        # also the dealer
        self.dealer = random.randint(0, len(player_array) - 1)
        # initialize the players
        self.players = player_array
        self.critic = critic

        # determine how much printing should occur
        self.verbose = verbose_flag

    def reset_game(self):
        '''Reset the game's state, but keep the same players. For use during extended'''
        self.create_deck()
        self.deck.shuffle()
        self.crib = []
        self.starter = []
        self.play_order = []
        self.dealer = random.choice(range(len(self.players)))
        for player in self.players:
            player.new_game()

    def game_state(self):
        '''Returns a dictionary representing the state of the game'''
        state = dict()
        scores = [player.pips for player in self.players]
        state['scores'] = scores
        num_cards = [len(player.play_hand) for player in self.players]
        state['num_cards'] = num_cards
        state['in_play'] = self.in_play
        state['play_order'] = self.play_order
        state['dealer'] = self.dealer
        state['starter'] = self.starter
        state['count'] = sum([card.value() for card in self.in_play])

        return state

    def check_win(self):
        '''Returns the number of the player who has won, or 0 if no one has won yet'''
        for player in self.players:
            if player.pips > 120:
                return player.number
        return 0

    def play_hand(self):
        '''Plays a single hand of cribbage'''
        self.deal()
        self.create_crib()
        self.cut()
        if self.verbose:
            self.show()
        self.play()

        self.score_hands()
        if self.verbose:
            print("Score is " + self.score_string())
            print("*******************************")
        self.restore_deck()
        for player in self.players:
            player.reset()

    def play_game(self):
        '''Plays a complete game of cribbage'''
        while not self.check_win():
            self.play_hand()

        print(
            f"{self.players[self.check_win() - 1].get_name()} wins! The final score was {self.score_string()} ")

        return self.players[0].pips - self.players[1].pips

    def deal(self):
        '''Deals the initial hands to each player'''
        # Shuffle the deck
        self.deck.shuffle()
        # deal 6 cards to each player, starting to the left of the dealer
        deal_order = [x % len(self.players) for x in range(
            self.dealer + 1, self.dealer + len(self.players) + 1)]
        for _ in range(6):
            for player in deal_order:
                self.players[player].draw(self.deck)

    def create_crib(self):
        '''Creates the crib'''

        # Each player throws cards into the crib. For 2-player cribbage, each
        # player throws 2 cards into the crib.
        for player in self.players:
            thrown = player.throw_crib_cards(2, self.game_state())

            if not (self.critic is None) and player.number == 1:
                critic_throws = self.critic.throw_crib_cards(
                    2, self.game_state())
                if not areCardsEqual(critic_throws, thrown):
                    self.players[0].explain_throw()
                    self.critic.explain_throw()
            if self.verbose:
                print(f"{player.get_name()} threw 2 cards into the crib.")
            for card in thrown:
                self.crib.append(card)

    def cut(self, card=None):
        '''Cuts the deck to determine the starter card'''
        if card is None:
            # Cut the deck
            self.deck.cut()
            # Top card is the starter
            self.starter = self.deck.cards.pop()
        else:
            self.starter = card
        # If starter is a jack, dealer gets 2 pips
        if self.starter.rank is Rank.Jack:
            self.players[self.dealer].pips += 2
            if self.verbose:
                print(
                    f"{ self.players[self.dealer].get_name()} scores 2 for nobs!")

    # Score hands in the proper order
    def score_hands(self):
        '''Scores the hands and crib'''
        for i in range(self.dealer + 1, self.dealer + 1 + len(self.players)):
            if self.check_win():
                break
            player = self.players[i % len(self.players)]
            score = getScore(player.hand, self.starter, self.verbose)
            player.pips += score
            if self.verbose:
                print(
                    f"Scoring {player.get_name()}'s hand: {cardsString(player.hand)} + {str(self.starter)}")
                print(f"\t{player.get_name()}'s hand scored {score}")

        if not self.check_win():
            crib_score = getScore(self.crib, self.starter, self.verbose)
            self.players[self.dealer].pips += crib_score
            if self.verbose:
                print(
                    f"In {self.players[self.dealer].get_name()}'s crib: {cardsString(self.crib)} + {str(self.starter)}")
                print(
                    f"{self.players[self.dealer].get_name()} scored {crib_score} in the crib!\n\n")

        for player in self.players:
            player.learn_from_hand_scores([getScore(self.players[0].hand, self.starter, False), getScore(
                self.players[1].hand, self.starter, False), getScore(self.crib, self.starter, False)], self.game_state())

    def play(self):
        '''Plays the pegging phase of the game'''
        if self.verbose:
            print(f"{self.players[self.dealer].get_name()} dealt this hand.")

        if not self.critic is None:
            self.critic.play_hand = []
            for i in range(0, 4):
                self.critic.play_hand.append(self.players[0].play_hand[i])
            # self.players[0].show()
            # self.critic.show()

        self.play_order = []

        # Starting player is not the dealer
        to_play = (self.dealer + 1) % len(self.players)
        self.play_order = []
        # as long as any player has cards in hand, and the game isn't over
        while (any(len(player.play_hand) > 0 for player in self.players)) and not self.check_win():
            self.in_play = []  # those cards that affect the current count
            count = 0  # the current count
            go_counter = 0  # a counter for the number of consecutive "go"s

            while (count < 31) and (go_counter < 2) and (not self.check_win()):
                if self.verbose:
                    print(
                        f"It is { self.players[to_play].get_name()}'s turn. Score is + {self.score_string()} ")
                # Call on agent to choose a card
                if to_play == 0 and not self.critic is None:
                    critic_card = self.critic.play_card(self.game_state())
                    if not critic_card is None:
                        self.critic.play_hand.append(critic_card)
                else:
                    critic_card = None
                played_card = self.players[to_play].play_card(
                    self.game_state())
                if played_card is None:
                    if go_counter == 0:
                        go_counter = 1
                    else:
                        go_counter = 2
                        self.players[to_play].pips += 1
                        if self.verbose:
                            print(
                                f"{self.players[to_play].get_name()} scores 1 for the go.\n")
                else:
                    if not critic_card is None and not self.critic is None:
                        if not critic_card.is_identical(played_card):
                            self.players[0].explain_play()
                            self.critic.explain_play()
                        else:
                            print(
                                f"{self.critic.get_name()} agrees with {self.players[0].get_name()}'s play.")
                        self.critic.remove_card(played_card)
                    count += played_card.value()
                    self.in_play.append(played_card)
                    self.play_order.append(played_card)
                    if self.verbose:
                        print(f"\t{count}: {cardsString(self.in_play)}")
                    self.players[to_play].pips += scoreCards(
                        self.in_play, self.verbose)
                    go_counter = 0

                to_play = (to_play + 1) % len(self.players)
                # Allow agent to learn from the previous round of plays
                self.players[to_play].learn_from_pegging(self.game_state())

            if go_counter == 2:
                # A go has happened
                for player in self.players:
                    player.go(self.game_state())

            if count == 31:
                # A 31 has happened
                for player in self.players:
                    player.thirty_one(self.game_state())

            if self.check_win():
                # Someone won
                for player in self.players:
                    player.end_of_game(self.game_state())
                if self.verbose:
                    print('Game Over!')

    def restore_deck(self):
        '''Restores the deck to its original state and passes the deal to the next player'''
        self.dealer = (self.dealer + 1) % len(self.players)
        self.create_deck()
        self.crib = []
        self.starter = []
        self.play_order = []

    def create_deck(self):
        '''Creates a deck of cards'''
        self.deck = Deck(1)

    def score_string(self):
        '''Returns a string representing the current score'''
        return str(self.players[0].pips) + " - " + str(self.players[1].pips)

    def show(self):
        '''Prints the current state of the game to the console'''
        for player in self.players:
            print(player)

        print("Cut: " + str(self.starter))
        print("Crib: " + cardsString(self.crib))
