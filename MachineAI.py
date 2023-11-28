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


import random
import os
from itertools import combinations
import numpy as np
from sklearn import neural_network as sknn
import sklearn as skl
import joblib
import warnings
import matplotlib.pyplot as plt

from Deck import Card
from Player import Player

# Utility imports
from Utilities import *

class MachineAI(Player):
    '''Machine learning AI'''

    def __init__(self, number, verboseFlag, filename='machine', alpha=0.1, epsilon=0.05, gamma=0.3, hidden_layers=(25, 10)):
        super().__init__(number)
        self.verbose = verboseFlag

        self.name = "Machine"
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.hidden_layers = hidden_layers

        self.throwing_state = []
        self.episode_states = []
        self.episode_actions = []
        self.episode_returns = []
        self.no_action_index = 5
        self.go_action_index = 4
        self.current_action = self.no_action_index
        # Need to track previous score to calculate rewards
        self.prev_score = 0

        self.crib_throw = []
        self.filename = filename
        self.file_dir = 'learn_bin'
        self.full_file_pegging = os.path.join(
            os.getcwd(), self.file_dir, self.filename + "_peg.brain")
        self.full_file_throwing = os.path.join(
            os.getcwd(), self.file_dir, self.filename + "_throw.brain")
        if os.path.exists(self.full_file_pegging):
            self.peg_brain = joblib.load(self.full_file_pegging)
        else:
            self.peg_brain = sknn.MLPRegressor(hidden_layer_sizes=self.hidden_layers, activation='relu', solver='adam',
                                               alpha=self.alpha, batch_size=4, max_iter=200)
        if os.path.exists(self.full_file_throwing):
            self.throwing_brain = joblib.load(self.full_file_throwing)
        else:
            self.throwing_brain = sknn.MLPRegressor(hidden_layer_sizes=(25, 10), activation='relu', solver='adam',
                                                    alpha=self.alpha, batch_size=1, max_iter=200)

    def backup(self):
        '''Saves the brain to a file'''
        if not os.path.isdir(self.file_dir):
            os.mkdir(self.file_dir)
        joblib.dump(self.peg_brain, self.full_file_pegging)
        joblib.dump(self.throwing_brain, self.full_file_throwing)

    def throw_crib_cards(self, num_cards, game_state):
        '''selects crib cards based on the highest scoring hand without the starter card'''
        crib_cards = []
        self.crib_throw = []
        card_indices = list(range(0, len(self.hand)))
        max_value = -np.inf

        if game_state['dealer'] == self.number - 1:
            dealer_flag = 1
        else:
            dealer_flag = 0

        for combination in combinations(card_indices, len(self.hand) - num_cards):
            hand_cards = []
            thrown_cards = []
            for i in range(0, len(card_indices)):
                if i in combination:
                    hand_cards.append(
                        Card(self.hand[i].rank, self.hand[i].suit))
                else:
                    thrown_cards.append(
                        Card(self.hand[i].rank, self.hand[i].suit))

            q = self.throw_value(self.get_throwing_features(
                hand_cards, thrown_cards, dealer_flag))

            if q > max_value:
                max_value = q
                crib_cards = [thrown_cards.pop(), thrown_cards.pop()]

        if self.verbose:
            print(f"{self.get_name()} threw {num_cards} cards into the crib")
        super().create_play_hand()

        return crib_cards

    def play_card(self, game_state):
        '''selects a card to play while making sure that it won't put the count over 31'''

        if len(self.play_hand) == 4:
            self.throwing_state = self.get_current_state(game_state)
        # record current state and score
        self.current_action = self.choose_action(game_state)
        if self.current_action == self.go_action_index:
            # Go
            card_played = None
        else:
            card_played = self.play_hand.pop(self.current_action)
            self.episode_states.append(self.get_current_state(game_state))
            self.prev_score = self.get_relative_score(game_state)
            self.episode_actions.append(self.current_action)

        return card_played

    # Explain why certain cards were thrown into the crib

    def explain_throw(self):
        '''Prints the cards thrown to the console'''
        print(
            f"Random ({self.number}) chose to throw those cards into the crib randomly. No explanation.")

    # Explain why a certain card was played during pegging
    def explain_play(self):
        print(
            f"Random ({self.number}) chose to play that card during pegging at random. No reason.")

    def choose_action(self, game_state):
        '''Chooses an action to take based on the current state of the game'''
        # Make sure hand is sorted
        self.play_hand.sort()
        # Figure out which actions are legal
        legal = [(game_state['count'] + card.value())
                 <= 31 for card in self.play_hand]
        legal_hand = [card for (card, is_legal) in zip(
            self.play_hand, legal) if is_legal]
        # legal hand is a new hand of only the cards that can legally be played
        # If no legal cards, only option is Go.
        if not legal_hand:
            action_index = self.go_action_index
        else:
            # Choosing a card from the legal cards
            state = self.get_current_state(game_state)
            # Predict using brain
            prob = epsilon_soft(self.s_a_values(state), self.epsilon)
            # Set probability of illegal choices to 0
            prob = [p * int(is_legal) for (p, is_legal) in zip(prob, legal)]
            # Re-normalize probabilities
            prob = [p / sum(prob) for p in prob]
            # Choose a card at random based on the probabilities
            action_index = random.choices(range(len(prob)), weights=prob)
            action_index = action_index[0]

        return action_index

    # Predict the value of a state
    def throw_value(self, state):
        '''Predicts the value of a state using the throwing brain'''
        value = 0
        try:
            value = self.throwing_brain.predict([state])
            return value
        except skl.exceptions.NotFittedError:  # type: ignore
            return 0

    # PlayerRandom does not learn
    def learn_from_hand_scores(self, scores, game_state):
        reward = scores[self.number - 1]
        if game_state['dealer'] == (self.number - 1):
            reward += scores[2]
            dealer_flag = 1
        else:
            reward -= scores[2]
            dealer_flag = 0

        state = self.get_throwing_features(
            self.hand, self.crib_throw, dealer_flag)
        q_value = self.throw_value(state)
        np_max = np.max(self.s_a_values(self.throwing_state))
        update = self.alpha * \
            (reward + np_max - q_value)

        self.throwing_brain.partial_fit([state], np.ravel([q_value + update]))

        if self.verbose:
            print(self.name + ": Learning from hand scores!")
            print(f'\tState: ${state}')
            print(f'\tQ-value (pre): {q_value}')
            print(f'\tReward: {reward}')
            print(f'\tUpdate Value : {update}')

        # self.backup()

    def learn_from_pegging(self, game_state):
        if self.current_action == self.go_action_index:
            if self.episode_returns[-1]:
                self.episode_returns[-1] += self.get_relative_score(
                    game_state) - self.prev_score
            self.prev_score = self.get_relative_score(game_state)
        elif self.current_action < self.go_action_index:
            reward = self.get_relative_score(game_state) - self.prev_score
            self.prev_score = self.get_relative_score(game_state)
            self.episode_returns.append(reward)

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

    def update_brain(self, game_state):
        '''Updates the pegging brain with the episode data'''
        if self.episode_actions:
            if len(self.episode_actions) > len(self.episode_returns):
                self.episode_returns.append(
                    self.get_relative_score(game_state) - self.prev_score)
                self.prev_score = self.get_relative_score(game_state)
            x = np.asarray(
                [state for state in self.episode_states], dtype=object)
            y = np.asarray([self.s_a_values(state)
                           for state in self.episode_states], dtype=object)
            g_t = [0] * len(self.episode_states)
            g = 0
            print(f'x: {x}')
            print(f'y: {y}')
            print(f'g_t: {g_t}')
            print(f'g: {g}')
            print(f'episode_states: {self.episode_states}')

            print(f'x length: {len(x)}')
            print(f'y length: {len(y)}')
            print(f'g_t length: {len(g_t)}')

            print(f'x[0] length: {len(x[0])}')
            print(f'y[0] length: {len(y[0])}')

            for i in reversed(range(len(self.episode_states))):
                try:
                    g_t[i] = ((self.gamma * g) + self.episode_returns[i])
                except IndexError:
                    print("what is happening here?")
                g = g_t[i]
                y[i][self.episode_actions[i]] = g_t[i]

            print(f'x: {x}')
            print(f'y: {y}')
            self.peg_brain.partial_fit(np.asarray(
                x, dtype=object),  np.asarray(y, dtype=object))

    def s_a_value(self, state, action_index: int):
        '''Returns the value of a state-action pair'''
        s_a_vals = self.s_a_values(state)
        return s_a_vals[0][action_index]

    def s_a_values(self, state):
        '''Returns the values of a state-action pair'''
        print(f'State: {state}')
        action_values = np.asarray(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=object)
        try:
            if isinstance(state[1], list):
                action_values = self.peg_brain.predict(state)
                print(f'IF INSTANSE Action values: {action_values}')
            else:
                action_values = self.peg_brain.predict([state])
                action_values = action_values[0]
                print(f'ELSE Action values: {action_values}')
        except skl.exceptions.NotFittedError:  # type: ignore
            # If the brain hasn't seen any training data yet, will return the NotFittedError.
            # In this case, we want to return 0.0 for all actions.
            action_values = np.asarray(
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=object)

        print(f'Action values: {action_values}')
        return np.asarray(action_values, dtype=object)

    def get_current_state(self, game_state):
        '''Returns a list of features for the pegging brain'''
        hand_state = [card.rank.value for card in sorted(self.play_hand)]
        while len(hand_state) < 4:
            hand_state.append(0)

        crib_state = [card.rank.value for card in self.crib_throw]
        play_state = [card.rank.value for card in game_state['play_order']]
        while len(play_state) < 8:
            play_state.append(0)

        state = hand_state + play_state + crib_state + \
            [game_state['starter'].value()]
        state = [val / 13 for val in state]
        state.append(game_state['count'] / 31)
        state.append(int(game_state['dealer'] == self.number))
        return state

    def get_throwing_features(self, hand_cards, thrown_cards, dealer_flag):
        '''Returns a list of features for the throwing brain'''
        throwing_features = []

        hand_cards.sort()
        for card in hand_cards:
            throwing_features.append(card.rank.value / 13)
            suit = [0, 0, 0, 0]
            suit[card.suit.value - 1] = 1
            throwing_features.extend(suit)

        thrown_cards.sort()
        for card in thrown_cards:
            throwing_features.append(card.rank.value / 13)
            suit = [0, 0, 0, 0]
            suit[card.suit.value - 1] = 1
            throwing_features.extend(suit)

        throwing_features.append(dealer_flag)

        return throwing_features

    def show(self):
        print('Hand:' + cards_string(sorted(self.play_hand)))
        print('Crib throw:' + cards_string(self.crib_throw))

    def reset(self, game_state=None):
        self.update_brain(game_state)
        super().reset()
        self.crib_throw = []
        self.episode_states = []
        self.episode_actions = []
        self.episode_returns = []
        self.current_action = self.no_action_index
