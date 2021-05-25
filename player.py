# from continent import *
from itertools import combinations

from color import Color
from card import Card, add_card, find_card, remove_card, total_wildcards
from troop import Troop


class Player():
    def __init__(self, color, troops, territories = [], cards=[]):
        ''' [color] is a Color object. [troops] is int. [cards] is a list of
        Card objects. No duplicates, i.e. each player has their own unique
        color.
        Note: [troops] refers to new troops that the player gets in the
            beginning of each turn, as well as the initial troops they have
            during territory claim in the very beginning of the game.'''
        self.color = color
        self.troops = troops
        self.territories = territories
        self.cards = cards

    def get_color(self):
        return self.color

    def get_troops(self):
        return self.troops

    def get_territories(self):
        return self.territories

    def add_territory(self, id):
        self.territories.append(id)

    def get_cards(self):
        return self.cards

    def set_troops(self, troops):
        self.troops = troops

    def add_troops(self, troops):
        self.troops += troops

    def subtract_troops(self, troops):
        self.troops -= troops

    # Note: [card] must be a Card object.
    def give_card(self, card):
        self.cards = add_card(card, self.cards)

    def take_card(self, territory):
        '''Returns the card with given [territory] while removing it from
        the player's hand. [territory] must be a Node.'''
        card = find_card(territory, self.cards)
        self.cards = remove_card(territory, self.cards)
        return card

    # def string_cards(self):
    #     if len(self.cards) == 0:
    #         return "[]"
    #     res = "["
    #     for i in range(len(self.cards)-1):
    #         # For some reason, __str__() method in Card class doesn't work
    #         # as intended. Instead, it keeps printing __str__() for Node.
    #         card = self.cards[i]
    #         res += str(self.cards[i])
    #         res += ", "
    #     res += str(self.cards[-1])
    #     res += "]"
    #     return res

    def count_wildcards(self):
        '''Helper function for combine_cards().
        Returns the number wildcards owned by player and a copy of player's hand
        without the wildcards (Card list). Doesn't change player's hand.'''
        count = 0
        no_wildcards = []
        for card in self.cards:
            if card.get_troop_type() == Troop.WILDCARD:
                assert card.get_node() == None, "A wildcard with non-empty territory!"
                count += 1
            else:
                no_wildcards.append(card)
        assert count <= total_wildcards, "%s Player has too many wildcards!" % self.color.name
        return count, no_wildcards

    @staticmethod
    def count_wildcards_list(card_lst):
        '''Counts wildcards in [card_lst].'''
        count = 0
        for card in card_lst:
            if card.get_troop_type() == Troop.WILDCARD:
                count += 1
        return count

    @staticmethod
    def two_same(card_lst):
        '''
        Helper function for possible_combos().
        Given [card_lst], returns a list of all possible combinations of two
        cards where the two cards are of the same kind. Could return an
        empty list.

        Precondition: [card_lst] has no wildcards.
        '''
        if len(card_lst) < 2:
            return []
        elif len(card_lst) == 2 and card_lst[0].get_troop_type() == card_lst[1].get_troop_type():
            return card_lst

    def possible_combos(self):
        '''
        Helper function for decide().
        Finds all possible card combinations available for the player.
        Returns a possibly empty list of all possibilities of cards (Card list list).

        Preconditions: there are only two wildcards in the desk,
            i.e. [num_wildcards] == 2. Author might possibly make the function
            compatible with more wildcards in deck in the future.
        '''
        res = []
        if self.cards == []:
            return []
        wildcards_owned, other_cards = self.count_wildcards()
        # Initialize a wild card to possibly add to the output.
        wildcard = Card(Troop.WILDCARD, None)
        # Player has 2 wildcards. Any other card will make a combo.
        if wildcards_owned == 2 and len(self.cards) > 2:
            for card in other_cards:
                res.append([wildcard, wildcard, card])
        # Player at least one wildcard. Any 2 cards of either the same or
        # different types will make a combination.
        if wildcards_owned >= 1:
            two_comb = combinations(other_cards, 2)
            for el in list(two_comb):
                res.append([wildcard] + list(el))
        # Check all 3-card combos without wildcards.
        three_comb = combinations(other_cards, 3)
        for comb in list(three_comb):
            if Card.combine(comb) > -1:
                res.append(comb)
        return res

    def count_bonus(self, card_lst, deploy=False):
        '''Given a valid card combination, calculates the total bonus given
        to the player (+2 troops per territory on a card that is owned by the
        player). If [deploy] is False, it will just count territorial bonus
        without actually deploying troops.

        Preconditions: [card_lst] is a valid 3-card combination that can bring
        bonus troops. No more than 2 wildcards allowed.'''
        assert len(card_lst) == 3
        card_bonus = 0
        total_bonus = 0
        wildcards = Player.count_wildcards_list(card_lst)
        troops = set()

        # Count territory bonus and troop types.
        for card in card_lst:
            if card.get_troop_type() != Troop.WILDCARD:
                troops.add(card.get_troop_type())
                # Check for territorial bonus.
                node = card.get_node()
                if node.get_owner() == self.color:
                    total_bonus += 2
                    if deploy:
                        print("2 bonus troops deployed in %s." %
                              node.get_name())
                        node.add_troops(2)

        if len(troops) == 3 or (len(troops) == 2 and wildcards == 1) or (wildcards == 2):
            card_bonus = 10
        else:
            card_bonus = troops.pop().value

        # # Count card bonus depending on wildcards in [card_lst].
        # if wildcards == 1:
        #     if len(troops) == 2:
        #         card_bonus = 10
        #     else:
        #         card_bonus = troops.pop().value
        # elif wildcards == 2:
        #     card_bonus = 10
        # # No wildcards.
        # else:
        #     if len(troops) == 3:
        #         card_bonus = 10
        #     elif len(troops) == 1:
        #         card_bonus = troops.pop().value
        total_bonus += card_bonus

        return card_bonus, total_bonus

    def decide(self):
        '''Based on player's hand, picks the best possible hand.'''
        best_hand = []
        best_hand_wildcards = 0
        max_bonus = 0

        card_combos = self.possible_combos()
        for combo in card_combos:
            # print("\nBest hand: %s." % str(best_hand))
            # print("Best wildcards: %i. Best card bonus: %i. Best total bonus: %i." %
            #       (best_hand_wildcards, self.count_bonus(combo, False)[0], self.count_bonus(combo, False)[1]))
            # print("\nCurrent combo: %s." % str(combo))
            wildcards = Player.count_wildcards_list(combo)
            card_bonus, total_bonus = self.count_bonus(combo, False)
            # print("Wildcards: %i. Card bonus: %i. Total bonus: %i." %
            #       (wildcards, card_bonus, total_bonus))
            # Pick the highest bonus with least wildcards used.
            if total_bonus > max_bonus or (total_bonus == max_bonus and wildcards < best_hand_wildcards):
                best_hand = combo
                best_hand_wildcards = wildcards
                max_bonus = total_bonus

        return list(best_hand)

    def use_cards(self, card_lst):
        card_bonus, total_bonus = self.count_bonus(card_lst, True)
        print("You have %i total troops in bonus." % total_bonus)
        for card in card_lst:
            _ = self.take_card(card.get_node())
        return card_bonus


# p1 = Player(Color.RED, 0, [
#     Card(Troop.WILDCARD, None),
#     Card(Troop.WILDCARD, None),
#     Card(Troop.INFANTRY, E1)
# ])

# p2 = Player(Color.RED, 0, [
#     Card(Troop.WILDCARD, None),
#     Card(Troop.WILDCARD, None)
# ])

# p3 = Player(Color.RED, 0, [
#     Card(Troop.INFANTRY, E2),
#     Card(Troop.INFANTRY, E3),
#     Card(Troop.INFANTRY, E4),
# ])

# p4 = Player(Color.RED, 0, [
#     Card(Troop.INFANTRY, E5),
#     Card(Troop.INFANTRY, E6),
#     Card(Troop.CAVALRY, E7),
# ])

# p5 = Player(Color.RED, 0, [
#     Card(Troop.INFANTRY, AF1),
#     Card(Troop.CAVALRY, AF2),
#     Card(Troop.ARTILLERY, AF3),
# ])

# p6 = Player(Color.RED, 0, [
#     Card(Troop.WILDCARD, None),
#     Card(Troop.ARTILLERY, AF4),
#     Card(Troop.INFANTRY, AF5),
# ])

# p7 = Player(Color.RED, 0, [
#     Card(Troop.WILDCARD, None),
#     Card(Troop.ARTILLERY, AS1),
#     Card(Troop.INFANTRY, AS2),
#     Card(Troop.INFANTRY, AS3),
#     Card(Troop.CAVALRY, AS4),
# ])

# p8 = Player(Color.RED, 0, [
#     Card(Troop.WILDCARD, None),
#     Card(Troop.WILDCARD, None),
#     Card(Troop.ARTILLERY, AS5),
#     Card(Troop.INFANTRY, AS6),
#     Card(Troop.CAVALRY, AS7),
#     Card(Troop.INFANTRY, AS8),
#     Card(Troop.ARTILLERY, AS9),
# ])


# p9 = Player(Color.RED, 0, [
#     Card(Troop.INFANTRY, AS10),
#     Card(Troop.CAVALRY, AS11),
#     Card(Troop.ARTILLERY, AS12),
#     Card(Troop.INFANTRY, AU1),
#     Card(Troop.CAVALRY, AU2),
#     Card(Troop.ARTILLERY, AU3),
# ])


# p10 = Player(Color.RED, 0, [
#     Card(Troop.WILDCARD, None),
#     Card(Troop.ARTILLERY, NA1),
#     Card(Troop.INFANTRY, NA2),
#     Card(Troop.INFANTRY, NA3),
#     Card(Troop.ARTILLERY, NA4),
# ])

# p11 = Player(Color.RED, 0, [
#     Card(Troop.INFANTRY, NA5),
#     Card(Troop.INFANTRY, NA6),
#     Card(Troop.CAVALRY, NA7),
#     Card(Troop.CAVALRY, NA8),
# ])
