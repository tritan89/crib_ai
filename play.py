#!/usr/bin/env python3
# from re import M
from Cribbage import Cribbage
from MachineAI import MachineAI
from PlayerRandom import PlayerRandom
from Player_AI import Player_AI
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

p1 = MachineAI(1,False)
p2 = PlayerRandom(2, False)
player_list = [p1,p2]



def play_a_game():
    game = Cribbage(player_list)
    game.play()


game_sim = Cribbage(player_list)
p1_score = 0


def sim_hands(numhands):
    scores_ai = np.zeros(numhands)
    scores_random = np.zeros(numhands)
    for i in range(numhands):

        scores_random[i]= game_sim.play_hand_test()[0] 
        scores_ai[i] = game_sim.play_hand_test()[1]
        game_sim.reset_game()
    return scores_random, scores_ai

machine_scores, ai_scores = sim_hands(100)


np.save('machine_scores.npy', machine_scores)
np.save('ai_scores.npy', ai_scores)

machine_scores = np.load('machine_scores.npy')
ai_scores = np.load('ai_scores.npy')
ai_mean = np.mean(ai_scores)
ai_std = np.std(ai_scores)
ai_mode = stats.mode(ai_scores)[0]
ai_median = np.median(ai_scores)


machine_mean = np.mean(machine_scores)
machine_std = np.std(machine_scores)
machine_mode = stats.mode(machine_scores)[0]
machine_median = np.median(machine_scores)



types = ['mean', 'std', 'mode', 'median']
ai_stats = [ai_mean, ai_std, ai_mode, ai_median]
machine_stats = [machine_mean, machine_std, machine_mode, machine_median]

width = 0.25
multiplier = 0
x = np.arange(len(types))
fig, axs = plt.subplots(2, 1, layout='constrained')

for i in range(len(types)):
    offset = width*multiplier
    rects = axs[1].bar(types[i], ai_stats[i])
    axs[1].bar_label(rects, padding=3)
    width+=1 


axs[0].plot(ai_scores,  label = 'AI')
axs[0].plot(machine_scores, label = 'Random')
axs[0].set_ylabel('score')
axs[0].set_xlabel('hand number')



plt.show()



        
        
    
    

   



