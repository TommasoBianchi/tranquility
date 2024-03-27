import numpy as np
from abc import ABC, abstractmethod
from itertools import combinations

class Player(ABC):
    def __init__(self, id, n_cards, n_players, pass_discard_size, deck, initial_hand):
        self.id = id
        self.n_cards = n_cards
        self.n_players = n_players
        self.pass_discard_size = pass_discard_size
        self.deck = deck # it's illegal to observe the deck to take decisions! only the length is observable
        self.hand = initial_hand
        self.hand_size = len(initial_hand)
        self.discards_history = []
        self.action_history = []
        self.board = None
        self.players_history = [None for i in range(n_players)]
        self.players_discards = [0 for i in range(n_players)]
        self.players_hand_sizes = [len(initial_hand) for i in range(n_players)]
        self.players_deck_sizes = [None for i in range(n_players)]
    
    def check_possible_discard(self):
        '''
        returns true if it's possible to use the standard discard to pass the turn
        '''
        return len(self.hand) >= self.pass_discard_size
    
    def check_possible_play(self):
        '''
        returns true if there's at least one card that can be played on the board in the hand
        '''
        for card in self.hand:
            for position in np.arange(1, self.board.size):
                if self.board.check_if_position_legal(card, position, len(self.hand)-1):
                    return True
        return False
    
    def get_all_possible_discards(self, n_discards=2):
        '''
        returns a list of dictionaries containing all the possible combinations of discards for a number of n_discards cards to discard
        '''
        return [{'type': 'D','discards':list(iter)} for iter in combinations(self.hand, n_discards)]
    
    def get_all_possible_plays(self):
        '''
        returns a list of dictionaries containing all the possible plays on the board, for every card in hand, for every feasible position 
        on the board, for every possible set of discards to pay the cost
        '''
        possible_plays = []
        for i in self.hand:
            for p in range(self.board.size):
                if self.board.check_if_position_legal(i, p, len(self.hand)-1):
                    cost = self.board.get_action_cost(i,p)
                    for iter in combinations([c for c in self.hand if c != i], cost):
                        possible_plays.append({'type': 'P', 'card_played': i, 'position':p, 'discards':list(iter)})
        return possible_plays

    def is_start_mandatory(self):
        '''
        checks if there's a start in the hand and no start have been played yet
        '''
        return (0 in self.hand) and not self.board.start

    def check_if_alive(self, start_turn_discard=0):
        '''
        checks if the player has at least one possible action or if, instead, the game is lost
        '''
        return (len(self.hand)>=start_turn_discard) and (self.check_possible_discard() or self.check_possible_play()) 
        
    def update_hand(self):
        '''
        draws card from the deck untile the deck is finished of the hand is full
        '''
        while len(self.hand)<self.hand_size and len(self.deck)>0:
            self.hand.append(self.deck.pop())

    def discard_cards(self, cards):
        '''
        removes cards from hand and append them to the history of discarded cards
        '''
        for card in cards:
            self.hand.remove(card)
            self.discards_history.append(card)

    def play_card(self, card):
        '''
        removes the card from the hand before placing it on the board
        '''
        self.hand.remove(card)
    
    @abstractmethod
    def decide_action(self):
        # returns a dictionary.
        # if you play a card on the board:
        # {'P', card played (int), position (int), discarded cards (list of int)}
        # if you instead discard 2 cards:
        # {'D', discarded cards (list of int)}
        pass

    @abstractmethod
    def decide_discards_start(self, n_to_discard):
        # return a dictionary.
        # {'D', discarded cards (list of int)}
        pass

    def observe_board(self, board):
        '''
        updates the knowledge on the board
        '''
        self.board = board

    def observe_players(self, players):
        '''
        updates the knowledge on other player statuses (history of plays on the board, number of discards, size of hand, size of deck)
        '''
        for player in players:
            self.players_history[player.id] = player.action_history
            self.players_discards[player.id] = len(player.discards_history)
            self.players_hand_sizes[player.id] = len(player.hand)
            self.players_deck_sizes[player.id] = len(player.deck)

    def play(self, start_turn_discards=0, print_history=False):
        '''
        main function, return an action in the form of a dictionary
        '''
        if not self.check_if_alive(start_turn_discards):
            if print_history:
                print("ACTION: lose")
            return ('F', -1)
        if self.is_start_mandatory():
            a = ('S')
            self.play_card(0)
            if print_history:
                print("ACTION: play start card")
        elif self.n_cards + 1 in self.hand and sum(np.isnan(self.board.board))==0:
            a = ('W')
            self.play_card(self.n_cards + 1)
            if print_history:
                print("ACTION: play finish card (win)")
        elif start_turn_discards > 0:
            action = self.decide_discards_start(n_to_discard=start_turn_discards)
            self.discard_cards(action['discards'])
            a = ('DS', len(action['discards']))
            if print_history:
                print(f"ACTION: discard for start card ({action['discards']})")
        else:
            action = self.decide_action()
            if action['type'] == 'P':
                if print_history:
                    print(f"ACTION: play card {action['card_played']} in position {action['position']} discarding {action['discards']}")
                assert self.board.check_if_position_legal(action['card_played'], action['position'], len(self.hand) - 1), f"Illegal action {action}"
                action_cost = self.board.get_action_cost(action['card_played'], action['position'])
                assert action_cost == len(action['discards']), f"Wrong cost for action {action} (should be {action_cost})"
                self.play_card(action['card_played'])
                a = (action['type'], action['card_played'], action['position'], len(action['discards']))
            elif action['type'] == 'D':
                a = (action['type'])
                if print_history:
                    print(f"ACTION: discard to pass ({action['discards']})")
                assert len(action['discards']) == self.pass_discard_size
            self.discard_cards(action['discards'])
        self.update_hand()
            
        self.action_history.append(a)
        return a
            