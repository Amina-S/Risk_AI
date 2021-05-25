import operator
import random

from troop import Troop
from continent import *


class Card:
    # Uniqueness of a card is defined by the territory it represents.
    def __init__(self, troop_type, node):
        self.troop_type = troop_type
        self.node = node

    def __repr__(self):
        if self.troop_type == Troop.WILDCARD:
            return Troop.WILDCARD.name
        return self.node.get_name() + " - " + self.troop_type.name

    def __str__(self):
        if self.troop_type == Troop.WILDCARD:
            return Troop.WILDCARD.name
        return self.node.get_name() + " - " + self.troop_type.name

    def get_troop_type(self):
        return self.troop_type

    def get_node(self):
        return self.node

    def get_info(self):
        return self.troop_type, self.node

    @staticmethod
    def combine(card_lst):
        '''Takes in a 3-card list and returns 1 if all three cards are of
        different types; 0 if all three cards are of the same type; and -1
        otherwise.'''
        assert len(card_lst) == 3
        troops = set()
        for card in card_lst:
            troops.add(card.get_troop_type())
        if len(troops) == 3:
            return 1
        elif len(troops) == 1:
            return 0
        return -1


def add_card(card, card_lst):
    '''
    Uses binary search to add the given Card object to the given Card list.
    If [card] is already in [card_lst], raises ValueError.
    Returns a new list of Card objects.

    Preconditions: [card] is a Card object; [card_lst] is a list of Card objects
        that are sorted by territory name in an increasing order with no
        duplicates. [card_lst] can be empty.
    '''
    if len(card_lst) == 0:
        return [card]

    # Wildcard automatically goes to the end.
    if card.get_troop_type() == Troop.WILDCARD:
        return card_lst + [card]

    i = len(card_lst) // 2
    curr_terr = card_lst[i].get_node()
    given_terr = card.get_node()
    if curr_terr == None or curr_terr.get_name() > given_terr.get_name():
        return add_card(card, card_lst[:i]) + card_lst[i:]
    elif curr_terr.get_name() < given_terr.get_name():
        return card_lst[:i+1] + add_card(card, card_lst[i+1:])
    raise ValueError("Card already in the card list!")


def remove_card(territory, card_lst):
    '''
    Uses binary search to remove the card with given territory from
        the given Card list.
    Returns a new list of Card objects. If the card is not found, raises
        ValueError.

    Preconditions: [territory] is a Node; [card_lst] is a list of Card objects
        that are sorted by territory name in an increasing order with no
        duplicates. [card_lst] can be empty.
    '''

    if len(card_lst) == 0:
        raise ValueError("Card not found in the card list!")
    # If looking for a wildcard, remove ONE wildcar from the end of [card_lst].
    elif territory == None:
        if card_lst[-1].get_troop_type() == Troop.WILDCARD:
            return card_lst[:-1]
        else:
            raise ValueError("Card not found in the card list!")

    i = len(card_lst) // 2
    curr_terr = card_lst[i].get_node()

    if curr_terr == None or curr_terr.get_name() > territory.get_name():
        return remove_card(territory, card_lst[:i]) + card_lst[i:]
    elif curr_terr.get_name() < territory.get_name():
        return card_lst[:i+1] + remove_card(territory, card_lst[i+1:])
    return card_lst[:i] + card_lst[i+1:]


def find_card(territory, card_lst):
    '''
    Uses binary search to find the card with given territory in the given
        Card list.
    Returns a Card object. If the card is not in [card_lst], returns None.

    Preconditions: [territory] is a Node; [card_lst] is a list of Card objects
        that are sorted by territory name in an increasing order with no
        duplicates. [card_lst] can be empty.
    '''

    if len(card_lst) == 0:
        return None
    # If looking for a wildcard, look at the very end of [card_lst].
    elif territory == None:
        if card_lst[-1].get_troop_type() == Troop.WILDCARD:
            return card_lst[-1]
        else:
            return None

    i = len(card_lst) // 2
    curr_terr = card_lst[i].get_node()
    if curr_terr == None or curr_terr.get_name() > territory.get_name():
        return find_card(territory, card_lst[:i])
    elif curr_terr.get_name() < territory.get_name():
        return find_card(territory, card_lst[i+1:])
    return card_lst[i], i


# Initialize all cards.
card_bindings = {
    "Afghanistan": Troop.CAVALRY,
    "Alaska": Troop.INFANTRY,
    "Alberta": Troop.CAVALRY,
    "Argentina": Troop.INFANTRY,
    "Brazil": Troop.ARTILLERY,
    "Central America": Troop.ARTILLERY,
    "China": Troop.INFANTRY,
    "Congo": Troop.INFANTRY,
    "East Africa": Troop.INFANTRY,
    "Eastern Australia": Troop.ARTILLERY,
    "Eastern United States": Troop.ARTILLERY,
    "Egypt": Troop.INFANTRY,
    "Great Britain": Troop.ARTILLERY,
    "Greenland": Troop.CAVALRY,
    "Iceland": Troop.INFANTRY,
    "India": Troop.CAVALRY,
    "Indonesia": Troop.ARTILLERY,
    "Irkutsk": Troop.CAVALRY,
    "Japan": Troop.ARTILLERY,
    "Kamchatka": Troop.INFANTRY,
    "Madagascar": Troop.CAVALRY,
    "Middle East": Troop.INFANTRY,
    "Mongolia": Troop.INFANTRY,
    "New Guinea": Troop.INFANTRY,
    "North Africa": Troop.CAVALRY,
    "Northern Europe": Troop.ARTILLERY,
    "Northwest Territory": Troop.ARTILLERY,
    "Ontario": Troop.CAVALRY,
    "Peru": Troop.INFANTRY,
    "Quebec": Troop.CAVALRY,
    "Russia": Troop.CAVALRY,
    "Scandinavia": Troop.CAVALRY,
    "Siam": Troop.INFANTRY,
    "Siberia": Troop.CAVALRY,
    "South Africa": Troop.ARTILLERY,
    "Southern Europe": Troop.ARTILLERY,
    "Ural": Troop.CAVALRY,
    "Venezuela": Troop.INFANTRY,
    "Western Australia": Troop.ARTILLERY,
    "Western Europe": Troop.ARTILLERY,
    "Western United States": Troop.ARTILLERY,
    "Yakutsk": Troop.CAVALRY
}

# Sort all nodes alphabetically.
all_nodes_alphabetical = sorted(all_nodes, key=operator.attrgetter('name'))
all_cards_sorted = []

# Add territory cards according to bindings.
i = 0
for key in card_bindings:
    node = all_nodes_alphabetical[i]
    assert node.get_name() == key, "Problem with assigning Card values: %s vs %s." % (
        node.get_name(), key)

    all_cards_sorted.append(Card(card_bindings[key], node))
    i += 1

# Add wildcards.
total_wildcards = 2
for _ in range(total_wildcards):
    all_cards_sorted.append(Card(Troop.WILDCARD, None))

all_cards = all_cards_sorted.copy()
random.shuffle(all_cards)
