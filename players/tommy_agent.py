import numpy as np
from game.player import Player
from game.board import Board

class TommyAgent(Player):
    def __init__(self, id, n_cards, n_players, pass_discard_size, deck, initial_hand):
        super().__init__(id, n_cards, n_players, pass_discard_size, deck, initial_hand)
        self._internal_board = None
        
        # Config
        self.max_admissible_discards = len(initial_hand) // 2

    def observe_board(self, board):
        '''
        updates the knowledge on the board
        '''
        self.board = board
        if self._internal_board is None:
            self._internal_board = Board(size=board.size, n_cards=board.n_cards)
        self._internal_board.board = np.copy(board.board)

    def _compute_useless_cards(self, skip_cards=[], current_play_move=None):
        if current_play_move is not None:
            assert np.isnan(self._internal_board.board[current_play_move[1]])
            self._internal_board.board[current_play_move[1]] = current_play_move[0]
            self._internal_board.__update_board_internals()

        # NOTE: 0 (start) is always useless, n_cards+1 (finish) is useless iff I have more than one
        number_of_finish = len([card for card in self.hand if card == self.n_cards + 1])
        useless_cards = [
            card 
            for card in self.hand 
            if card not in skip_cards + [self.n_cards + 1] and \
                not any([self._internal_board.check_if_position_legal(card, position, hand_size=4) for position in range(self._internal_board.size)])
        ] + [self.n_cards + 1] * (number_of_finish - 1)

        if current_play_move is not None:
            self._internal_board.board[current_play_move[1]] = np.nan
            self._internal_board.__update_board_internals()

        return useless_cards

    def _evaluate_card(self, card):
        best_value = 1000000
        best_position = 0

        for position in range(self.board.size):
            if self.board.check_if_position_legal(card, position, hand_size=4):
                value = self._evaluate_play_action(card, position)

                if value < best_value:
                    best_value = value
                    best_position = position

        return best_value, best_position

    def _evaluate_play_action(self, card, position):
        assert np.isnan(self._internal_board.board[position])
        self._internal_board.board[position] = card
        value = evaluate_board(self._internal_board)
        self._internal_board.board[position] = np.nan

        n_discards = self.board.get_action_cost(card, position)

        closes_gap = position > 0 and position < self.board.size - 1 and not np.isnan(self.board.board[position - 1]) and not np.isnan(self.board.board[position + 1])

        return value + (10 * (n_discards - (0.5 if closes_gap else 0))) ** 2


    def _decide_discards(self, n_to_discard, skip_cards=[], current_play_move=None):
        if n_to_discard == 0:
            return []

        if n_to_discard == len([card for card in self.hand if card not in skip_cards]):
            return [card for card in self.hand if card not in skip_cards]

        useless_cards = self._compute_useless_cards(skip_cards=skip_cards, current_play_move=None)
        if len(useless_cards) >= n_to_discard:
            return useless_cards[:n_to_discard]

        # Evaluate the board after playing each non-useless single card optimally
        evaluated_cards = sorted([(self._evaluate_card(card), card) for card in self.hand if card not in useless_cards + skip_cards + [self.n_cards + 1]], key=lambda el: -el[0][0])
        worst_evaluated_cards = [card for _, card in evaluated_cards][:n_to_discard - len(useless_cards)]

        assert len(useless_cards + worst_evaluated_cards) == n_to_discard
        return useless_cards + worst_evaluated_cards

    def decide_discards_start(self, n_to_discard):
        # return a dictionary.
        # { 'type': 'D','discards': list of discarded cards }

        return { "type": "D", "discards": self._decide_discards(n_to_discard) }
    
    def decide_action(self):
        # returns a dictionary.
        # if you play a card on the board:
        # {'type': 'P', 'card_played': the played card, 'position': the board position to play into, 'discards': list of discarded cards}
        # if you instead discard 2 cards:
        # { 'type': 'D','discards': list of discarded cards }

        possible_moves = []
        for card in self.hand:
            # Add 1/2 moves to play it on the board openly in a reasonable spot
            best_spot = card / self.board.n_cards * self.board.size
            best_spot_floor = int(best_spot)
            best_spot_ceil = int(best_spot + 1)

            if self.board.check_if_position_legal(card, best_spot_floor, hand_size=4) and \
                (best_spot_floor == 0 or np.isnan(self.board.board[best_spot_floor-1])) and \
                (best_spot_floor == self.board.size-1 or np.isnan(self.board.board[best_spot_floor+1])):
                possible_moves.append((card, best_spot_floor))
            if self.board.check_if_position_legal(card, best_spot_ceil, hand_size=4) and \
                (best_spot_ceil == 0 or np.isnan(self.board.board[best_spot_ceil-1])) and \
                (best_spot_ceil == self.board.size-1 or np.isnan(self.board.board[best_spot_ceil+1])):
                possible_moves.append((card, best_spot_ceil))

            if (self.board.board < card).sum() > 0:
                max_lower_card = self.board.board[self.board.board < card].max()
                max_lower_card_position = np.argwhere(self.board.board == max_lower_card).item()
            else:
                max_lower_card = 0
                max_lower_card_position = -1
            if (self.board.board > card).sum() > 0:
                min_higher_card = self.board.board[self.board.board > card].min()
                min_higher_card_position = np.argwhere(self.board.board == min_higher_card).item()
            else:
                min_higher_card = self.board.n_cards + 1
                min_higher_card_position = self.board.size
            
            middle_position = int(max_lower_card_position + (card - max_lower_card) / (min_higher_card - max_lower_card) * (min_higher_card_position - max_lower_card_position))
            if self.board.check_if_position_legal(card, middle_position, hand_size=4) and \
               (middle_position == 0 or np.isnan(self.board.board[middle_position-1])) and \
               (middle_position == self.board.size-1 or np.isnan(self.board.board[middle_position+1])):
                possible_moves.append((card, middle_position))

            # Add a move to play it immediately to the right of the max lower one (if possible)
            if self.board.check_if_position_legal(card, max_lower_card_position+1, hand_size=4):
                possible_moves.append((card, max_lower_card_position+1))

            # Add a move to play it immediately to the left of the min higher one (if possible)
            if self.board.check_if_position_legal(card, min_higher_card_position-1, hand_size=4):
                possible_moves.append((card, min_higher_card_position-1))

        # Compute num of discards for each move
        possible_moves = [(card, position, self.board.get_action_cost(card, position)) for card, position in possible_moves]

        # Remove moves with too many discards
        possible_moves = [move for move in possible_moves if move[2] <= min(len(self.hand) - 1, self.max_admissible_discards)]

        if len(possible_moves) == 0:
            return { "type": "D", "discards": self._decide_discards(2) }

        # Select best move by evaluating resulting board value
        evaluated_moves = [(card, position, n_discards, self._evaluate_play_action(card, position)) for card, position, n_discards in possible_moves]

        best_move = evaluated_moves[0]
        for move in evaluated_moves[1:]:
            if move[3] < best_move[3]:
                best_move = move

        card, position, n_discards, _ = best_move
        return {'type': 'P', 'card_played': card, 'position': position, 'discards': self._decide_discards(n_discards, skip_cards=[card], current_play_move=(card, position)) }

def evaluate_board(board):
    cards_value = 0
    gaps_value = 0

    played_cards = []
    prev_card = None
    prev_card_position = None
    for position, card in enumerate(board.board):
        if not np.isnan(card):
            cards_value += (card - position / board.size * board.n_cards) ** 2

            if prev_card is not None and position - prev_card_position > card - prev_card:
                return 1000000

            played_cards.append(card)
            prev_card = card
            prev_card_position = position

    for i in range(len(played_cards)-1):
        gap_length = played_cards[i+1] - played_cards[i]
        if gap_length == 1:
            continue
        gaps_value = (gap_length - 2 / board.size * board.n_cards) ** 2

    return cards_value + gaps_value
