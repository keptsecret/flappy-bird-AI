# Flappy Bird AI

A flappy bird game played by an AI.  
The aim is to train an AI to perfectly play flappy bird with the NEAT algorithm.

This project is written entirely in Python, using the pygame module for the game and my own implementation of NEAT to produce and evolve networks.  
More info about the NEAT implementation I used described [here](http://nn.cs.utexas.edu/downloads/papers/stanley.cec02.pdf)

## Some general details

There is an input buffer of every 0.15 seconds to prevent spamming flap.  
Run with 100 players for smooth real-time playback.  
Supports more than 500 simultaneous players without crashing (possibly could go up to 1000).  
The current AI version begins to play properly usually by generation #3 and begins to play optimally by generation #7-8.

Play manually with the command line argument `--manual`.
