from dataclasses import dataclass
import numpy as np


@dataclass
class GameConfig:
    n_players: int = 4
    board_size: int = 36
    hand_sizes: int = 5
    n_cards: int = 80
    n_finish: int = 5
    start_discard_size: int = 8
    pass_discard_size: int = 2

    def __post_init__(self):
        assert self.n_players > 0
        assert self.board_size > 0 and self.board_size < self.n_cards
        assert self.n_finish > 0
        assert self.n_cards >= min(
            1, np.ceil(self.n_players * self.hand_sizes) - self.n_finish
        )
        assert self.hand_sizes >= max(
            [self.pass_discard_size, np.ceil(self.start_discard_size / self.n_players)]
        )
        assert self.start_discard_size < self.hand_sizes * self.n_players
