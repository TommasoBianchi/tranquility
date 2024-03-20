import numpy as np
from game.board import Board
from game.game_setup import setup_game
from .config import GameConfig

def run_game(seed: int, config: GameConfig, player_types):    

    # Setup game    
    decks, initial_hands = setup_game(
        n_players=config.n_players,
        n_cards=config.n_cards,
        n_finish=config.n_finish,
        hand_sizes=config.hand_sizes,
        seed=seed
    )

    # Init players
    players = [
        player_types[i](
            id=i,
            n_cards=config.n_cards,
            n_players=config.n_players,
            pass_discard_size=config.pass_discard_size,
            deck=decks[i],
            initial_hand=initial_hands[i]
        ) for i in range(config.n_players)
    ]

    # Init board
    board = Board(size=config.board_size, n_cards=config.n_cards)

    start_discards = [config.start_discard_size // config.n_players] * config.n_players
    for i in range(config.start_discard_size - sum(start_discards)):
        start_discards[i] += 1

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

    return {
        "outcome": "WIN" if np.isnan(board.board).sum() == 0 else "LOSE",
        "history": {player.id: player.action_history for player in players},
        "final_board": board.board
    }

