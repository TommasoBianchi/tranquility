import numpy as np
from bottleneck import push
from hashlib import sha512

def forward_fill_na(arr):
    return push(arr)

def backward_fill_na(arr):
    return np.flip(forward_fill_na(np.flip(arr)))

class Board:
    def __init__(self, size=36, n_cards=80):
        self.size = size
        self.n_cards = n_cards
        self.board = np.repeat(np.nan, size)
        self._board_sha = None
        self.min_board, self.max_board = np.repeat(np.nan, size), np.repeat(np.nan, size)
        self.start, self.finish = False, False

    def __board_changed(self):
        current_board_sha = sha512(np.ascontiguousarray(self.board)).hexdigest()
        if self._board_sha != current_board_sha:
            self._board_sha = current_board_sha
            return True
        return False

    def __update_minmax_board(self):
        if self.__board_changed():
            self.max_board = np.nan_to_num(backward_fill_na(self.board), nan=self.n_cards + 1)
            self.min_board = np.nan_to_num(forward_fill_na(self.board), nan=0)

    def check_if_position_legal(self, new_card, position, hand_size):
        if position < 0 or position >= self.size:
            return False
        elif hand_size == 0:
            return False
        elif new_card == 0:
            return not self.start
        elif new_card == self.n_cards+1:
            return (not self.finish) and (sum(np.isnan(self.board))==0)
        elif self.get_action_cost(new_card, position) <= hand_size:
            self.__update_minmax_board()
            return ((self.min_board <= new_card) * (self.max_board >=new_card))[position]
        else:
            return False
    
    def get_action_cost(self, new_card, position):
        # corner cases
        if position == self.size-1:
            if np.isnan(self.board[position-1]):
                return 0
            else:
                return int(new_card - self.board[position-1])
        if position == 0:
            if np.isnan(self.board[position+1]):
                return 0
            else:
                return int(self.board[position+1]-new_card)
        
        if np.isnan(self.board[position-1]) and np.isnan(self.board[position+1]):
            return 0
        elif np.isnan(self.board[position-1]): 
            return int(self.board[position+1]-new_card)
        elif  np.isnan(self.board[position+1]):
            return int(new_card - self.board[position-1])
        else:
            return int(min([new_card - self.board[position-1], self.board[position+1]-new_card]))
    
    def check_completion(self):
        return bool(self.start*self.finish*(sum(np.isnan(self.board))==0))
    
    def receive_card(self, new_card, position, hand_size):
        if new_card == 0:
            assert not self.start
            self.start = True
        elif new_card == self.n_cards+1:
            assert (not self.finish)*(sum(np.isnan(self.board))==0)
            self.finish = True
        else:
            assert self.check_if_position_legal(new_card, position, hand_size)
            self.board[position] = new_card
            self.__update_minmax_board()
        return self.board
    
    
    
    
    

        
