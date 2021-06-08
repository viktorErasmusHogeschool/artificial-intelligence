# Cards Against Humanity ![test](./cah/cah_logo.jpg)

## Purpose of this repo

This repo will be used as main source code for the development of our project with regards to the module Intelligent 
interfaces, that takes places within the context of our AI postgraduate program at Erasmushogeschool Brussel (EhB).

## Summary of the project

This project is based on the principles of the game “Cards against humanity” (CAH). The game is an
adult party game where players complete fill-in-the-blank statements with dark humour words or sentences
that are typically deemed defiant and politically incorrect. The goal in CAH is to fill-in the statements
of the black cards with words or sentences of the white cards. During each round, one of the players,
designated as the “Card Tsar”,  plays a black card that the other players fill-in using one of their
white cards. The Card Tsar then shuffles the played white cards and chooses the funniest one. The player
to whom this white card belongs then earns a point and becomes the Card Tsar for the next round. The
player that earned the highest number of points after the last round wins the game. It is played among
3 to 20+ players and the card deck comprises around 600 white cards and 100 black cards.

This package implements an intelligent system that is capable of:
* Filling-in the statement of a black card using his own white cards (using the BERT API);
* Choosing the funniest card among the collection of cards played by humans (again using BERT);
* Drawing a scene that represents the winner's white card at each round (using GANs).

This intelligent player also supports an arbitrary number of players and white cards on the board. Humans
and AI can thus challenge one another for who detains the finest sense of humour! Are you willing to take
on the challenge?

## Installation

As a first step, make sure to clone this repository at the location of your choice:

```python
git clone https://github.com/viktorErasmusHogeschool/intelligent-interfaces.git
```

This repository comes in with a dedicated environment that can be created using conda. Therefore, go to the
project directory where the *cah.yml* file is located and hit the following command:

```python
conda env create --file cah.yml
```

Alternatively, you can use any other Python that you like. For this, use pip to make sure you install all 
the packages contained in the *requirements.txt* file:

```python
pip install -r requirements.txt
```

Once your environment is setup, you will need to setup the code using the following command:

```python
pip install -e .
```

In case it does not work out, try the same command using *sudo*:

```python
sudo -H pip install -e . --user
```

## Code directories

The CAH module within this repository is made of the following submodules:

1) **cah**
   
   This module contains the heart of our code. It ensures the correct behaviour of a game as well as
   a connection to our remote **Linode server**. It is made of the following sub-elements:
   - Game: Creates the game and communicates to other users via the remote Linode server;
   - Network: Ensures the communication between the game instance and the server (send & receive data);
   - Player: Creates an instance with a dedicated card deck that can be selected in each round;
   - Canvas: Renders the graphics of the game (including the part on image generation);
   - Sprite: Pygame's sprite instance to accommodate for buttons & cards
  
2) **data**

    This directory gathers two main types of formats:
    - The pandas dataframes used to fetch a potential candidate sentence for image generation;
    - The torch models that create Generative Adversarial Networks (GANs) to render an artificial image of the
     selected white card.
    
    It has to be noted that the dataframes are placed here just to query the path associated to each white card. The
    distribution of the white cards themselves happens on the server side.
   
3) **gans**

    The GAN module allows the loading of pre-trained GANs that render the image of a specific white card. After the end
    of each round, this module is called to render the image associated to the new winner's white card. For instance, if
    the white card "black hole" was used by the winning player, the GAN model will draw a black hole on each player's
    board. Cool, isn't it? Note however that not each white card has an associated GAN as their training is 
    computationally expensive. Future models will be added in the upcoming upgrades!

4) **python-server**

    The code of this directory is just a reproduction of the code on the server-side. While not being used directly on
    the player's side, it allow to illustrate how the two parties communicate. In particular, the server works as follows:
    - A global game instance is created on the server side;
    - An artificial player is automatically added to the game;
    - Players can connect to this server using sockets;
    - Each player has a unique ID known by the game instance;
    - The game listens to each player's choices and returns its actual state, namely:
        * The status of each player (played or not played);
        * The scoring table of the game;
        * The player's white cards;
        * The game's black card;
        * The choices of other players.
    - If every player has played its card, the voting process is launched and the Tsar may choose the next Tsar.
    
    Note that the vote of the AI player is automatic and happens through the *bert_api.py* script, also
    running on the server. This script runs 
    [Tensorflow's BERT model](https://www.tensorflow.org/text/tutorials/classify_text_with_bert) on an Amazon Web Service
    server and was trained on a [Kaggle dataset](https://www.kaggle.com/abhinavmoudgil95/short-jokes) made of more than 
    200 000 short jokes.
    
5) **speech**
    
    Once a new Tsar has been chosen, the winning sentence is pronounced using the [gTTS](https://pypi.org/project/gTTS/) 
    (Google Text-to-Speech) library. The latter is also used to announce the beginning of a new round. Stay focused to
    hear what the best player selected as white card!
    
## Running the code

Getting the code running is pretty straightforward; all you need is a server and ... players to play with. The only
command to be executed on the server side is the following (cf. python-server directory):

```python
python3 server.py
```

This will create a socket instance that will listen to each player's action. In order to connect to this server from
the client side (i.e., your side), just hit the following command:

```python
python run.py
```

This will create a new game instance that will automatically send your actions to the server as well as fetch the 
server's state at the same time. Now you're all set! Enjoy your game and choose your cards wisely!