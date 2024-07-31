import numpy as np
from game.player import Player


class GreedyPlayer(Player):
    def __init__(self, id, n_cards, n_players, pass_discard_size, deck, initial_hand):
        super().__init__(id, n_cards, n_players, pass_discard_size, deck, initial_hand)

    def __decide_action_type(self):
        if self.check_possible_play():
            return "P"
        else:
            return "D"

    def __decide_discards(self):
        possible_discards = self.get_all_possible_discards()
        idx = np.random.choice(np.arange(len(possible_discards)))
        return possible_discards[idx]

    def __decide_play(self):
        possible_plays = self.get_all_possible_plays()
        idx = np.random.choice(np.arange(len(possible_plays)))
        return possible_plays[idx]

    def decide_discards_start(self, n_to_discard):
        possible_discards = self.get_all_possible_discards(n_to_discard)
        idx = np.random.choice(np.arange(len(possible_discards)))
        return possible_discards[idx]

    def decide_action(self):
        a_type = self.__decide_action_type()
        if a_type == "P":
            return self.__decide_play()
        else:
            return self.__decide_discards()
