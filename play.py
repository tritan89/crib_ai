#!/usr/bin/env python3
from Cribbage import Cribbage
from PlayerRandom import PlayerRandom

p1 = PlayerRandom(1,False)
p2 = PlayerRandom(2, False)
player_list = [p1,p2]
game1 = Cribbage(player_list)
game1.playGame()