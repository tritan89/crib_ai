#!/usr/bin/env python3
from re import M
from Cribbage import Cribbage
from MachineAI import MachineAI
from PlayerRandom import PlayerRandom
from Player_AI import Player_AI

# p1 = PlayerRandom(1,False)
p1 = Player_AI(1, False)

p2 = MachineAI(2, False)

player_list = [p1,p2]

game1 = Cribbage(player_list)
game1.play_game()
