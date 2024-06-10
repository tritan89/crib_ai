Crib AI Design Specification
CSC 421
Tristan Langer 
Kjartan R Einarsson

Problem Description :
I have always loved playing crib with my family and friends growing up and still play lots nowadays. While playing crib on my phone one day I noticed the version of my app has lots of statistics about optimal discarding and possible misplays. This got me thinking about designing an AI to play crib. The goal of this project is to create multiple agents that will use different strategies to solve the problem of playing crib. The goal of the game of crib is to score 121 points before your opponent. Points can be scored via two methods, pegging and counting. This allows us to divide the problem into two separate cases, solving the problem of choosing two cards to discard and then solving the problem of choosing a card to play. 

Select Crib Cards

Parameters:
6 cards
Restrictions:
None
Goal:
Optimal points for 4 card play hand
Output:
4 cards play hand
2 cards discard to crib
Select Card to Play

Parameters:
Cards in hand
Count
Top card
Restrictions:
Empty hand
legal/illegal card
Passing the turn
Goal:
Maximum points
Minimum points for opponent
Output:
1 card to play

For solving the problem of discarding the first iteration will use statistical analysis to find two optimal cards to discard. Later iterations will consider strategies that will choose cards that are good for pegging. The most optimal cards will be selected by considering all possible combinations of four cards from the player's current hand. Then for each combination, calculate the cribbage score of the hand without taking into account the starter card. The starter card is a card revealed during the game that may influence scoring.



The problem of pegging points is more complicated than that of choosing cards to discard. It will require the AI seeing the board state then choosing the optimal card based on the others in their hand, previous hands that have been played and the current score. Then deciding which card to play to earn optimal points in addition to avoiding giving easy points to the opponent. Points can be earned in a variety of ways during the play in cribbage. 

Performance
Environment
Actuators
Sensors
The Agent will be tried against another AI and its performance will be based on the amount of wins
Partially Observable
Sequential
Dynamic
Deterministic 
Discarding cards
Playing cards


Hand, top card, current game state


 

What we will be using to solve the problem
https://github.com/richard-moulton/Cribbage
We are using the structure from this repository to create the environment for our project. This repo contains code that allows us to focus on the logic of the agents without having to build the framework that lets them run. The files we are using from this repo are Cribbage.py, Deck.py, Player.py, PlayerRandom.py, Scoring.py, Myrmidon.py. Cribbage.py contains A class that allows players(agents) to play in the game. The Deck class contains the logic for a deck of cards in python. The player class contains the necessary functions a player needs to interact with the crib game. PlayerRandom is an implemented player class that randomly makes all decisions, this is used for testing purposes. Scoring has all the functions for counting hands. Myrmidon contains a heuristically based agent that plays against an agent using the arena file when it runs.  


Project Goals:
Develop a Cribbage AI player capable of playing the game against human players or other AI opponents.
Train the AI to understand game rules, calculate scores, and make strategic decisions.
Document the AI's development process and provide data point comparisons.

AI Solutions:
Probabilistic reasoning: We will use bayesian networks and to develop the AI's decision-making ability when it comes to card discards and plays.

Machine Learning: Machine learning concepts, including supervised learning and reinforcement learning, will be used to train the AI to improve its gameplay over time.

Rule-Based Systems: We will incorporate rule-based systems to ensure that the AI understands and adheres to the rules of Cribbage, including scoring rules.



Software and Libraries:
Python: The project will be implemented in Python, which is widely used for AI and game development.

Scikit-learn: These libraries will be employed for implementing machine learning components and reinforcement learning.


Roles:
Kjartan:  Machine Learning with Scikit-learn
Tristan: Initial Development setup, Probability based Algorithm

Initial milestones:

Nov 10: Development of AI gameplay logic and rule adherence 
	Nov 10: Get basic AI algorithms running and competing
Nov 24: Implementing probabilistic algorithms and decision-making (Tristan)
	Nov 24: Machine learning and reinforcement learning integration (Kjartan)
Nov 30: Final testing, documentation, and user manual 


Materials from Textbook
 
Ch 13 Probabilistic Reasoning
13.2 The Semantics of Bayesian Networks
Ch 15 Making Simple Decisions
15.1 Combining Beliefs and Desires under Uncertainty
15.2 The Basis of Utility Theory
15.3 Utility Functions
Ch 19 Learning From Example
19.3 Learning Decision Trees
19.4 Model Selection And Optimization
19.9 Developing Machine Learning Systems
Ch 23 Reinforcement Learning
23.1 Learning from Rewards
23.2 Passive Reinforcement Learning
23.3 Active Reinforcement Learning




Project Progress Report
In our current iteration of the project we have successfully implemented optimal card discarding, optimal pegging of cards and have begun implementing these as bayesian networks. First we will analyse the solution to finding the best two cards to discard. 



This method generates possible cribbage hands by finding combinations of 4 cards from a given hand. It then iterates over each possible hand, removes those cards from the deck, and calculates scores for each hand with every card in the remaining deck as a starter card. The results, including the hand, score, starter card, and crib cards, are collected and passed to the analyzeCribCards method.


The GetScore function analyses the current set of 4 cards and checks for all possible ways of scoring points. 

Fifteen: For adding a card that makes the total 15.			2 Points
Pair: For adding a card of the same rank as the card just played.	2 Points 
Triplet: For adding the third card of the same rank.			6 Points
Four: For adding the fourth card of the same rank. 			12 Points 
Run (Sequence): For adding a card that form:
sequence of three 	3 Points
sequence of four. 	4 Points
sequence of five. 	5 Points



This method takes a list of lists (scored_hands) as input, where each inner list represents a different hand. Each hand contains a list with information about the hand, hand score, a card, and crib cards.It calculates the average score for each hand and selects the hand with the highest average score. In total for each hand played the program calculates 690 possible combinations.






Now onto the pegging optimization. 

For each card, it calculates a score based on its value and the current count in the game. The score takes into account conditions related to the total count after playing the card and specific values that the count might reach (e.g., 10, 5, or 21). Additionally, certain adjustments are made to the score based on specific conditions.
If the player's hand is not empty, and if the maximum score calculated for any card is greater than 0, the method selects the card with the maximum score using the NumPy function amax and the pop method removes it from the player's hand. The selected card is then returned.
Here you can see I've done some basic analytics on the current iteration of our project analysing the performance of our AI vs a random player over 1000 hands of playing. This statistical analysis is only looking at the total number of points in each hand. Further analysis will delve deeper into the exact pegging functions and see their results.



Machine Learning / Neural Networks
A basic structure of a machine learning AI has been developed, with the use of scikit-learn.

Play_card checks for empty hand and passes the turn if no legal action is possible. Then selects a Card to play supplying a current_action value.  Given a card is played we append to a list of every game action taken by the AI.


Pick_play_card check cards for legal cards to play. Then analyses the board state and makes a prediction based upon all past learnt data, giving a probability array for the current legal_hand. Selecting at random with the given probabilities. 



Sa_values calculates the given state action value for each card in play hand.

If there are any actions recorded in self.episode_actions, it starts processing.
If there are more actions than returns, it calculates the difference between the current score and the previous score, and adds it to the returns list. Then it updates the previous score.
It creates a list X of all states encountered in the episode, and a list Y of the action-value pairs for each state.
It initializes a list Gt with the same length as the number of states, and a variable G to 0. These are used to calculate the discounted return for each state-action pair.
It then goes through each state in reverse order. For each state, it calculates the discounted return Gt[i] as the current return plus the discounted return from the next state. If there's an IndexError, it prints a message.
It then updates the action-value pair for the action taken in state i to the calculated discounted return.
After going through all states, it updates the model (self.peg_brain) with the states and the updated action-value pairs.
Finally, it calls self.backup(), which might be a function to save the current state of the model.




If the current action is the "go" action (as indicated by self.current_action == self.go_action_index), it increases the last return in self.episode_returns by the difference between the current score and the previous score. Then it updates the previous score to the current score.
If the current action is not the "go" action but some other action (as indicated by self.current_action < self.go_action_index), it calculates the reward as the difference between the current score and the previous score. Then it updates the previous score to the current score and appends the calculated reward to self.episode_returns.
In both cases, the function is updating the returns based on the difference in scores before and after the current action. This difference is treated as the reward for the action. The "go" action is treated differently from other actions, possibly because it represents a different kind of action in the game.

Learning 
Over the course of this project I have taught myself both the numpy and matplotlib python libraries. It was super fun exploring all the different functions and statistical methods available on the data I have created. Using numpy has taught me more about memory allocation and optimization and how to write code that works with the library.
Exploring neural networks and machine learning has been a great learning experience and helped me give a frame to my understanding on how these programs operate. Utilising a new tool Scikit-learn was difficult but interesting and useful.
Challenges  
Currently I am working on implementing the functions using a bayesian network. The most difficult part is creating a function that turns the hand score into a probability. There are several methods I am researching right now. 
Training the peg_brain and saving the data to learn from is the final step of implementation of the ai. 

