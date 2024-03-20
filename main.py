from game import run_game, GameConfig
from game.player import Player
from tqdm import tqdm
import argparse
from collections import Counter
import numbers
import importlib
import importlib.util
import inspect
from os.path import dirname, join
import numpy as np

parser = argparse.ArgumentParser(
    prog='main.py',
    description='Entrypoint for the Tranquillity game simulator'
)
# Game config
config_group = parser.add_argument_group("config", "Game configurations")
config_group.add_argument("--n-players", type=int, default=4, help="The number of players")
config_group.add_argument("--board-size", type=int, default=36, help="The size of the board (1D)")
config_group.add_argument("--hand-sizes", type=int, default=5, help="The size of each players' hand")
config_group.add_argument("--n-cards", type=int, default=80, help="The total number of numbered cards")
config_group.add_argument("--n-finish", type=int, default=5, help="The total number of finish cards")
config_group.add_argument("--start-discard-size", type=int, default=2, help="The number of cards to discard when the start card is played")
config_group.add_argument("--pass-discard-size", type=int, default=2, help="The number of cards to discard when passing the turn")
# Run config
parser.add_argument("--games", type=int, default=10, help="The number of games to simulate")
parser.add_argument("--players", type=str, nargs="+", help="The player agent classes to use in the simulation")
parser.add_argument("--start-seed", type=int, default=0, help="The starting random seed to use (each game will offset this by 1, incrementally)")
# Metrics config
metrics_group = parser.add_argument_group("metrics", "Metrics display configurations")
metrics_group.add_argument("--print-metrics-every-game", action="store_true", default=False, help="Whether to print metrics for every game")
metrics_group.add_argument("--percentage-digits", type=int, default=2, help="The number of digits to use when rounding percentage metrics")

args = parser.parse_args()

config = GameConfig(
    n_players=args.n_players,
    board_size=args.board_size,
    hand_sizes=args.hand_sizes,
    n_cards=args.n_cards,
    n_finish=args.n_finish,
    start_discard_size=args.start_discard_size,
    pass_discard_size=args.pass_discard_size,
)

assert len(args.players) == 1 or len(args.players) == args.n_players, f"Must configure either 1 or {args.n_players} players"
players_paths = args.players * args.n_players if len(args.players) == 1 else args.players
player_types = []
for i, player_path in enumerate(players_paths):
    try:
        abs_path = join(dirname(__file__), player_path)
        spec = importlib.util.spec_from_file_location(f"player{i}", abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # print(module.__dict__)
        player_classes = [
            cls_obj 
            for _, cls_obj in inspect.getmembers(module) 
            if inspect.isclass(cls_obj) and issubclass(cls_obj, Player) and cls_obj != Player
        ]
        assert len(player_classes) == 1, f"Player module must define only a single player class ({player_path})"
        player_types.append(player_classes[0])
    except ModuleNotFoundError as e:
        print(f"Unable to import code for player in path {player_path}")
        print(f"\tCaused by: {e}")
        exit(1)
player_remapping_dict = {id: f"{name.__name__}{id}" for id, name in enumerate(player_types)}


def compute_metrics(game_config, player_remapping_dict, outcome, history, final_board, percentage_digits=2):
    # Number of filled board spaces
    filled_board_spaces = (~np.isnan(final_board)).sum()
    percentage_filled_board_spaces = filled_board_spaces / game_config.board_size

    # Number and percentage of play/discard actions (total and per player)
    actions_count_by_player = {id: Counter([action[0] for action in h]) for id, h in history.items()}
    percentage_action_types_by_player = {id: {type: round(count[type] / count.total(), percentage_digits) for type in count.keys()} for id, count in actions_count_by_player.items()}
    total_actions_count = Counter([action[0] for h in history.values() for action in h])
    percentage_action_types = {type: round(total_actions_count[type] / total_actions_count.total(), percentage_digits) for type in total_actions_count.keys()}

    # Total and average number of discarded cards per player
    discarded_cards_by_player = {
        id: sum([config.pass_discard_size if action[0] == 'D' else action[-1] for action in h if action[0] in ['P', 'D', 'DS']]) 
        for id, h in history.items()
    }
    total_discarded_cards= sum(discarded_cards_by_player.values())

    # Remaining deck size
    remaining_deck_size = config.n_cards - total_discarded_cards - filled_board_spaces

    return {
        "outcome": outcome,
        "filled_board_spaces": filled_board_spaces,
        "percentage_filled_board_spaces": round(percentage_filled_board_spaces, percentage_digits),
        "actions_count_by_player": {player_remapping_dict[id]: dict(count.items()) for id, count in actions_count_by_player.items()},
        "percentage_action_types_by_player": {player_remapping_dict[id]: v for id, v in percentage_action_types_by_player.items()},
        "total_actions_count": dict(total_actions_count.items()),
        "percentage_action_types": percentage_action_types,
        "discarded_cards_by_player": {player_remapping_dict[id]: v for id, v in discarded_cards_by_player.items()},
        "total_discarded_cards": total_discarded_cards,
        "remaining_deck_size": remaining_deck_size
    }


def print_metrics(game_id, metrics):
    heading = f"# Metrics for game {game_id} #"
    print("#" * len(heading))
    print(heading)
    print("#" * len(heading))
    for key, value in metrics.items():
        print(f"{key:<40} {value}")


n_wins = 0
total_metrics = {}
best_game_results = { "outcome": None, "results": None, "metrics": None }
for game_id in tqdm(range(args.games), disable=args.print_metrics_every_game):
    # Run game
    results = run_game(seed=args.start_seed + game_id, config=config, player_types=player_types)

    # Count wins
    if results["outcome"] == "WIN":
        n_wins += 1

    # Compute metrics
    metrics = compute_metrics(game_config=config, player_remapping_dict=player_remapping_dict, percentage_digits=args.percentage_digits, **results)

    # Update best game
    if best_game_results["outcome"] is None or \
        (best_game_results["outcome"] == "LOSE" and results["outcome"] == "WIN") or \
        (results["outcome"] == "LOSE" and metrics["filled_board_spaces"] > best_game_results["metrics"]["filled_board_spaces"]) or \
        (results["outcome"] == "WIN" and metrics["total_discarded_cards"] < best_game_results["metrics"]["total_discarded_cards"]):
        best_game_results = {
            "game_id": game_id,
            "outcome": results["outcome"],
            "results": results,
            "metrics": metrics
        }

    # Update total metrics
    for key, value in metrics.items():
        if isinstance(value, numbers.Number):
            total_metrics[key] = total_metrics.get(key, 0) + value
    
    # Print metrics if enabled
    if args.print_metrics_every_game:
        print_metrics(game_id=game_id, metrics=metrics)

print(f'Total number of wins: {n_wins} ({n_wins / args.games * 100:.2f}%)')

for key, value in list(total_metrics.items()):
    total_metrics[f"total_{key}"] = value
    total_metrics[f"average_{key}"] = round(value / args.games, 2)
    del total_metrics[key]
print_metrics(game_id="TOTAL", metrics=total_metrics)

# Print best game metrics
print_metrics(game_id=f"BEST (id: {best_game_results['game_id']}, seed: {args.start_seed + best_game_results['game_id']})", metrics=best_game_results["metrics"])
