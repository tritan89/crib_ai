#!/usr/bin/env python3

################################################################################
#
# File : MachineAI.py
#
# Description : A neural network AI that makes decisions.
#
#
# Dependencies:
#    - Player.py (in local project)
#    - Utilities.py (in local project)
#    - Deck.py (in local project)
#    - numpy (standard python library)      * - for __name__ = '__main__' only
#    - random (standard python library)
#    - matplotlib (standard python library) * - for __name__ = '__main__' only
#
################################################################################

# Cribbage imports
from Utilities import *
from Scoring import *
from itertools import combinations
from Player import Player
import random
import os
import joblib
import sklearn as skl


class MachineAI(Player):
    '''Machine learning AI'''

    def __init__(self, number, hidden_layers=(50, 30, 15), alpha=0.1, epsilon=0.05, gamma=0.3, filename='machine', verbose=False):
        super().__init__(number, verbose)
        self.name = "Machine"

        self.hidden_layers = hidden_layers
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.crib_throw = []

        self.no_action_index = 5
        self.go_action_index = 4
        self.current_action = self.no_action_index

        self.episode_states = []
        self.episode_actions = []
        self.episode_returns = []
        self.prev_score = 0

        self.filename = filename
        self.file_dir = 'learn_bin'
        self.full_file_pegging = os.path.join(
            os.getcwd(), self.file_dir, self.filename + "_peg.brain")
        if os.path.exists(self.full_file_pegging):
            self.peg_brain = joblib.load(self.full_file_pegging)
        else:
            self.peg_brain = skl.neural_network.MLPRegressor(hidden_layer_sizes=(50, 30, 15), activation='relu', solver='adam',  # type: ignore
                                                             alpha=self.alpha, batch_size=4, max_iter=200)

    def backup(self):
        '''Saves the brain to a file'''
        if not os.path.isdir(self.file_dir):
            os.mkdir(self.file_dir)
        joblib.dump(self.peg_brain, self.full_file_pegging)

    def throw_crib_cards(self, num_cards, crib):
        '''selects crib cards based on the highest scoring hand without the starter card'''
        crib_cards = []

        best_hand, crib_cards = self.select_crib_cards()

        self.hand = list(best_hand)

        if self.verbose:
            print(f"{self.get_name()} threw {num_cards} cards into the crib")

        self.crib_throw = crib_cards

        super().create_play_hand()

        return crib_cards

    def select_crib_cards(self):
        '''selects crib cards based on the highest scoring hand without the starter card'''
        possible_hands = combinations(self.hand, 4)
        max_score = -1
        best_hand = []

        for hand in possible_hands:
            score = getScoreNoStarter(list(hand), False)
            if score > max_score:
                max_score = score
                best_hand = hand

        crib_cards = [card for card in self.hand if card not in best_hand]

        return best_hand, crib_cards

    def play_card(self, game_state):
        '''selects a card to play while making sure that it won't put the count over 31'''
        self.check_empty_hand()

        self.current_action = self.pick_play_card(game_state)

        if self.current_action == self.go_action_index:
            # Go
            if self.verbose:
                print(f"\t MachineAI ({self.number}) says go!")
            card_played = None
        else:
            card_played = self.play_hand.pop(self.current_action)
            self.episode_states.append(self.get_current_state(game_state))
            self.prev_score = self.get_relative_score(game_state)
            self.episode_actions.append(self.current_action)

        return card_played

    def pick_play_card(self,  game_state):
        '''selects an optimal card to play'''
        legal = [(game_state['count'] + card.value())
                 <= 31 for card in self.play_hand]
        legal_hand = [card for (card, isLegal) in zip(
            self.play_hand, legal) if isLegal]

        if not legal_hand:
            action_index = self.go_action_index
        else:
            # Choosing a card from the legal cards
            state = self.get_current_state(game_state)
            # Predict using brain
            prob = epsilonsoft(self.sa_values(state), self.epsilon)
            # Set probability of illegal choices to 0
            prob = [p * int(isLegal) for (p, isLegal) in zip(prob, legal)]
            # Re-normalize probabilities
            prob = [p / sum(prob) for p in prob]
            # Choose a card at random based on the probabilities
            action_index = random.choices(range(len(prob)), weights=prob)
            action_index = action_index[0]

        return action_index

    def playable_cards(self, game_state):
        '''Returns a list of playable cards'''
        playable_cards = []
        count = game_state['count']
        for card in self.play_hand:
            if count + card.value() < 32:
                playable_cards.append(card)
        return playable_cards

    def check_empty_hand(self):
        '''checks if the player has any cards left in their hand'''
        if len(self.play_hand) == 0:
            if self.verbose:
                print(f"\tMachineAI ({self.number}) has no cards left; go!")
            return True

    def get_deck_without_hand(self, hand):
        '''Returns a deck without the cards in the hand'''
        deck = Deck(1)
        for card in hand:
            deck.cards.remove(card)
        return deck

    def get_opponent_number(self):
        '''Returns the opponent's number'''
        return 1 if self.number == 2 else 2

    def get_current_state(self, game_state):
        '''Returns the current state of the game'''
        hand_state = [card.rank.value for card in sorted(self.play_hand)]
        while len(hand_state) < 4:
            hand_state.append(0)

        crib_state = [card.rank.value for card in self.crib_throw]
        play_state = [card.rank.value for card in game_state['play_order']]
        while len(play_state) < 8:
            play_state.append(0)

        state = hand_state + play_state + \
            crib_state + [game_state['starter'].value()]
        state = [val / 13 for val in state]
        state.append(game_state['count'] / 31)
        state.append(int(game_state['dealer'] == self.number))
        return state

    def sa_values(self, state):
        '''Returns the action values for the given state'''
        action_values = [0, 0, 0, 0]
        try:
            if isinstance(state[1], list):
                action_values = self.peg_brain.predict(state)
            else:
                while len(state) != 17:
                    state.append(0.0)
                action_values = self.peg_brain.predict([state])
                action_values = action_values[0]
        except skl.exceptions.NotFittedError:  # type: ignore
            # If the brain hasn't seen any training data yet, will return the NotFittedError.
            action_values = [0, 0, 0, 0]

        return action_values

    def update_brain(self, game_state):
        '''Updates the brain with the episode data'''
        if self.episode_actions:
            if len(self.episode_actions) > len(self.episode_returns):
                self.episode_returns.append(
                    self.get_relative_score(game_state) - self.prev_score)
                self.prev_score = self.get_relative_score(game_state)
            X = [state for state in self.episode_states]
            Y = [self.sa_values(state) for state in self.episode_states]
            Gt = [None] * len(self.episode_states)
            G = 0
            for i in reversed(range(len(self.episode_states))):
                try:
                    Gt[i] = (self.gamma * G + self.episode_returns[i]) # type: ignore
                except IndexError:
                    print("what is happening here?")
                G = Gt[i]
                Y[i][self.episode_actions[i]] = Gt[i]  # type: ignore

            self.peg_brain.partial_fit(X, Y)
            self.backup()

    def go(self, game_state):
        self.episode_returns[-1] += self.get_relative_score(
            game_state) - self.prev_score
        self.prev_score = self.get_relative_score(game_state)

    def end_of_game(self, game_state):
        if self.current_action == self.go_action_index:
            self.episode_returns[-1] += self.get_relative_score(
                game_state) - self.prev_score
            self.prev_score = self.get_relative_score(game_state)
        else:
            self.episode_returns.append(
                self.get_relative_score(game_state) - self.prev_score)
            self.prev_score = self.get_relative_score(game_state)

    # Explain why certain cards were thrown into the crib

    def explain_throw(self):
        '''Prints the cards thrown to the console'''
        print(
            f"MachineAI ({self.number}) chose to throw those cards into the crib.")

    # Explain why a certain card was played during pegging
    def explain_play(self):
        print(
            f"MachineAI ({self.number}) chose to play that card during pegging.")

    # PlayerRandom does not learn
    def learn_from_hand_scores(self, scores, game_state):
        pass

    # PlayerRandom does not learn
    def learn_from_pegging(self, game_state):
        if self.current_action == self.go_action_index:
            self.episode_returns[-1] += self.get_relative_score(
                game_state) - self.prev_score
            self.prev_score = self.get_relative_score(game_state)
        elif self.current_action < self.go_action_index:
            reward = self.get_relative_score(game_state) - self.prev_score
            self.prev_score = self.get_relative_score(game_state)
            self.episode_returns.append(reward)

    def reset(self, game_state=None):
        self.update_brain(game_state)
        super().reset()
        self.crib_throw = []
        self.episode_states = []
        self.episode_actions = []
        self.episode_returns = []
        self.current_action = self.no_action_index
