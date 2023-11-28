
# Cribbage imports
from Cribbage import Cribbage
from Deck import Deck, Card

# Player imports
from Player_AI import Player_AI
from MachineAI import MachineAI

def run_trials( num_trials):
    '''Runs a number of trials of cribbage'''

    p1 = MachineAI(1, False)
    p2 = Player_AI(2, False)

    player_list = [p1,p2]

    game = Cribbage(player_list)
    
    cumulative_score = 0

    for trial in range(0, num_trials):
      
        game.play_game()

        scores = [0,0]

        print(f"Trial {trial+1} of {num_trials}")
        game.play_game()

        print('game.players', game.players)
        for i in range(0, 1):
            scores[i] = scores[i] + game.players[i].pips
        print("Score for this hand was "+game.score_string())


        game.reset_game()
        print("The point differential for "+game.players[0].get_name()+" was {0}.\n".format(scores[0]-scores[1]))
        cumulative_score = cumulative_score + scores[0] - scores[1]
    print("The overall point differential for "+ game.players[0].get_name()+" was {0}, or {1} points-per-hand.\n".format(cumulative_score,cumulative_score/(num_trials*2)))


if __name__ == '__main__':
    num_trials = int(input("How many hands do you want to play?: "))

    run_trials(num_trials)
