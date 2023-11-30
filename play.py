#!/usr/bin/env python3
from Cribbage import Cribbage
from PlayerRandom import PlayerRandom
from Player_AI import Player_AI
from MachineAI import MachineAI
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
p1 = PlayerRandom(1,False)
p2 = Player_AI(2, False)
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

# random_scores, ai_scores = sim_hands(1000)


# np.save('random_scores.npy', random_scores)
# np.save('ai_scores.npy', ai_scores)

random_scores = np.load('random_scores.npy')
ai_scores = np.load('ai_scores.npy')
ai_mean = np.mean(ai_scores)
ai_std = np.std(ai_scores)
ai_mode = stats.mode(ai_scores, keepdims=True)[0]
ai_median = np.median(ai_scores)


random_mean = np.mean(random_scores)
random_std = np.std(random_scores)
random_mode = stats.mode(random_scores, keepdims=True)[0]
random_median = np.median(random_scores)



types = ['mean', 'std', 'mode', 'median']
ai_stats = [ai_mean, ai_std, ai_mode, ai_median]
random_stats = [random_mean, random_std, random_mode, random_median]

width1 = 0.25
multiplier = 0
x = np.arange(len(types))
fig, axs = plt.subplots(2, 1, layout='constrained')


   
axs[1].bar(x, ai_stats, width= width1, color = 'blue')
axs[1].bar(x+0.25, random_stats,  width= width1, color = 'orange')
axs[1].set_xticks(x + width1 )
axs[1].set_xticklabels(types)
axs[1].legend(['AI', 'Random'])


axs[0].plot(ai_scores,  label = 'AI')
axs[0].plot(random_scores, label = 'Random')
axs[0].set_ylabel('score')
axs[0].set_xlabel('hand number')
axs[0].legend(['AI', 'Random'])


plt.show()



        
        
    
    

   



