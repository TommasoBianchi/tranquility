from game import run_game, GameConfig
from game.player import Player
from tqdm import tqdm
import argparse
import importlib
import importlib.util
import inspect
from os.path import dirname, join

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


n_wins = 0
for seed in tqdm(range(args.games)):
    results = run_game(args.start_seed + seed, config, player_types)
    if results["outcome"] == "WIN":
        n_wins += 1

print(f'Total number of wins: {n_wins} ({n_wins / args.games * 100:.2f}%)')
