import numpy as np
from game.board import Board
from game.game_setup import setup_game
from players.greedy_player import GreedyPlayer

n_players = 4

player_types = [GreedyPlayer for _ in range(n_players)]

assert len(player_types) == n_players

board_size = 36
hand_sizes = 5 
n_cards = 80 
n_finish = 5
start_discard_size = 2
pass_discard_size = 2

assert n_players > 0
assert board_size > 0 and board_size < n_cards
assert n_finish > 0
assert n_cards >= min(1, np.ceil(n_players*hand_sizes) - n_finish)
assert hand_sizes >= max([pass_discard_size, start_discard_size, np.ceil(start_discard_size/n_players)])

n_wins = 0
for seed in np.arange(10):
    print(f'Game {seed}')
    decks, initial_hands = setup_game(n_players=n_players, n_cards=n_cards, n_finish=n_finish, hand_sizes=hand_sizes, seed=seed)
    players = [player_types[i](i, n_cards, n_players, pass_discard_size, decks[i], initial_hands[i]) for i in range(n_players)]

    board = Board(size=board_size, n_cards=n_cards)

    start_discards = [int(np.ceil(start_discard_size//len(players))) for p in players[:-1]]
    start_discards.append(start_discard_size-sum(start_discards))

    start, start_player_id = False, -1
    win, lose = False, False
    while not lose and not win:
        for player in players:
            player.observe_board(board)
            player.observe_players(players)
            if start:
                player.play(start_turn_discards=start_discards[player.id])
                if player.id == start_player_id:
                    start = False
            else:
                a = player.play()
                if a[0] == 'S':
                    start = True
                    start_player_id = player.id
                    board.receive_card(0, 0, len(player.hand))
                elif a[0] == 'P':
                    board.receive_card(a[1], a[2], len(player.hand)+1+a[3])
                    win = board.check_completion()
                elif a[0] == 'F':
                    lose = True
            if win or lose:
                break
        if win or lose:
            break

    outcome = 'L'
    if np.isnan(board.board).sum() == 0:
        outcome = 'W'
        n_wins +=1

    for player in players:
        print(f'Player {player.id}: ', player.action_history)

    print('Final Board: ', board.board)
    print(f'Outcome: {outcome}')

print(f'Total number of wins: {n_wins}')
