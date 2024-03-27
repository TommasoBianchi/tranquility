import numpy as np

def setup_game(n_players, n_cards=80, n_finish=5, hand_sizes=5, seed=17):
    # define cards (except starts)
    cards = list(np.hstack((np.repeat(n_cards+1,n_finish), np.arange(1, n_cards+1))))
    deck_len = int(np.ceil((len(cards)+1)//n_players))
    # shuffle cards
    np.random.seed(seed)
    np.random.shuffle(cards)
    # given each player a deck
    decks = [cards[i*deck_len:(i+1)*deck_len] for i in range(n_players-1)]
    decks.append(cards[(n_players-1)*deck_len:])
    assert len(decks)==n_players
    assert len(set(np.concatenate(decks)))==n_cards+1, f"Cards are missing from decks dealt to players: {set(cards) - set(np.concatenate(decks))}"
    assert sum([len(deck) for deck in decks])==n_cards+n_finish, f"{n_cards - sum([len(deck) for deck in decks])} cards are missing from decks"
    # generate starting hands
    hands = [[deck.pop() for _ in range(hand_sizes)] for deck in decks]
    # add starts to decks
    for i in range(n_players):
        decks[i].append(0)
        np.random.shuffle(decks[i])
    return decks, hands
    
    
