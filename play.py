#!/usr/bin/env python3
from Cribbage import Cribbage
from PlayerRandom import PlayerRandom
from Player_AI import Player_AI

p1 = PlayerRandom(1,False)
p2 = Player_AI(2, False)
player_list = [p1,p2]

game1 = Cribbage(player_list)
game1.playGame()