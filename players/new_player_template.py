import numpy as np
from game.player import Player

class HeuristicPlayer(Player):
    def __init__(self, id, n_cards, n_players, pass_discard_size, deck, initial_hand):
        super().__init__(id, n_cards, n_players, pass_discard_size, deck, initial_hand)

    def decide_discards_start(self, n_to_discard):
        pass
    
    def decide_action(self):
        pass