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
import random
from Player import Player


class MachineAI(Player):
    '''Machine learning AI'''

    def __init__(self, number, verboseFlag):
        super().__init__(number)
        self.verbose = verboseFlag
        self.name = "Machine"

    def throw_crib_cards(self, num_cards, crib):
        '''selects crib cards based on the highest scoring hand without the starter card'''
        crib_cards = []

        for _ in range(0, num_cards):
            crib_cards.append(self.hand.pop(random.randrange(len(self.hand))))

        if self.verbose:
            print(f"{self.get_name()} threw {num_cards} cards into the crib")
        super().create_play_hand()

        return crib_cards

    def play_card(self, game_state):
        '''selects a card to play while making sure that it won't put the count over 31'''

        card_indices = list(range(0, len(self.play_hand)))
        played_card = None
        count = game_state['count']
        if len(self.play_hand) != 0:
            while played_card is None:
                index = random.randint(0, len(card_indices) - 1)
                cardIndex = card_indices[index]
                if count + self.play_hand[cardIndex].value() < 32:
                    played_card = self.play_hand.pop(cardIndex)
                    if self.verbose:
                        print(
                            f"\tPlayerRandom ({self.number}) played {str(played_card)}")
                else:
                    card_indices.pop(index)
                    if len(card_indices) == 0:
                        if self.verbose:
                            print(f"\tPlayerRandom ({self.number}) says go!")
                        break
        else:
            if self.verbose:
                print(f"\tPlayerRandom ({self.number}) has no cards left; go!")

        return played_card

    # Explain why certain cards were thrown into the crib
    def explain_throw(self):
        '''Prints the cards thrown to the console'''

        print(
            f"Random ({self.number}) chose to throw those cards into the crib randomly. No explanation.")

    # Explain why a certain card was played during pegging
    def explain_play(self):
        print(
            f"Random ({self.number}) chose to play that card during pegging at random. No reason.")

    # PlayerRandom does not learn
    def learn_from_hand_scores(self, scores, game_state):
        pass

    # PlayerRandom does not learn
    def learn_from_pegging(self, game_state):
        pass
