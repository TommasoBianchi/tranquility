import numpy as np


def setup_game(n_players, n_cards=80, n_finish=5, hand_sizes=5, seed=17):
    # define cards (except starts)
    cards = list(np.hstack((np.repeat(n_cards + 1, n_finish), np.arange(1, n_cards))))
    deck_len = int(np.ceil((len(cards) + 1) // n_players))
    # shuffle cards
    np.random.seed(seed)
    np.random.shuffle(cards)
    # given each player a deck
    decks = [cards[i * deck_len : (i + 1) * deck_len] for i in range(n_players - 1)]
    decks.append(cards[(n_players - 1) * deck_len :])
    assert len(decks) == n_players
    # generate starting hands
    hands = [[deck.pop() for _ in range(hand_sizes)] for deck in decks]
    # add starts to decks
    for i in range(n_players):
        decks[i].append(0)
        np.random.shuffle(decks[i])
    return decks, hands
