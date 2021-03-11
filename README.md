# Intelligent interfaces

## Purpose of this repo

This repo will be used as main source code for the development of our project with regards to the module Intelligent interfaces, which
takes places within the context of our AI postgraduate program.

## Summary of the project

We propose a project wherein the scope is based on the principles of the game “Cards against humanity” (CaH). This game is an adult party game where players complete fill-in-the-blank statements with dark humour words or sentences that are typically deemed defiant and politically incorrect. The goal in Cards against humanity is to fill-in the statements of the black cards with words or sentences of the white cards. During each round, one of the players, designated as the “Card Tsar”,  plays a black card that the other players fill-in using one of their white cards. The Card Tsar then shuffles the played white cards and chooses the funniest one. The player to whom this white card belongs then earns a point and becomes the Card Tsar for the next round. The player that earned the highest number of points after the last round wins the game. It is played among 3 to 20+ players and the card deck comprises around 600 white cards and 100 black cards.

In our project, we intend to implement an intelligent system that is capable of:
Filling-in the statement of a black card using his white cards 🡪 NLP (Viktor);
Drawing a scene that represents it 🡪 Computer Vision (Sofia);
Supporting an arbitrary number of (virtual) players 🡪 Framework development (Arthur).

The end result will thus be a game where human and machine can play together. The rules of CaH will be slightly modified to incorporate computer vision: instead of having a “Card Tsar”, the black card is randomly chosen and all players (including our AI player) will go through step 1, step 2 is executed after all players submit their phrases and finally, to decide who the winner is, each player votes for the funniest image in their opinion. The player with the most points at the end of the last round wins the game. 
