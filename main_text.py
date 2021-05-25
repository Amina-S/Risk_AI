import random
import time

from card import *
from color import Color
from continent import *
from path import path_exists
from player import Player
from roll import blitz


# Initialize players.
initial_troops = 30
red_player = Player(Color.RED, initial_troops, [])
blue_player = Player(Color.BLUE, initial_troops, [])
green_player = Player(Color.GREEN, initial_troops, [])
yellow_player = Player(Color.YELLOW, initial_troops, [])
cyan_player = Player(Color.CYAN, initial_troops, [])
purple_player = Player(Color.PURPLE, initial_troops, [])

# Randomize order.
order = [red_player, blue_player, green_player, yellow_player]
random.shuffle(order)


def territories(color, continents):
    '''Returns a list of territories (Node list) owned by a player with a
    given color in the given continent list (can be empty).'''
    res = []
    for continent in continents:
        for node in continent.get_nodes():
            if node.get_owner() == color:
                res.append(node)
    return res


def find_player(color, player_lst):
    '''Returns the player from [player_lst] with a given color. Raises
    ValueError if not found.'''
    for player in player_lst:
        if player.get_color() == color:
            return player
    raise ValueError('Player with color %s not found!' % str(color))


# WARNING: this function changes both [order] and [nodes].
def claim_territories(order, nodes):
    '''Gives territories for a given [order] in a given territories.'''
    while len(nodes) > 0:
        # Select the next player in the queue.
        curr_player = order.pop(0)
        order.append(curr_player)
        if curr_player.get_troops() == 0:
            continue
        # Get necessary information and pop the first node from [nodes].
        curr_color = curr_player.get_color()
        curr_node = nodes.pop(0)
        assert curr_node.get_troops() == -1, "Non-empty territory during claim!"
        # Set ownership and subtract troops.
        curr_node.set_owner(curr_color)
        curr_node.set_troops(1)
        curr_player.subtract_troops(1)
    return


def initialize_troops(order, nodes):
    # WARNING: this function changes both [order] and [nodes].
    '''Initializes troops using a given order in given node list.'''
    total_remaining_troops = 0
    for player in order:
        total_remaining_troops += player.get_troops()
    while total_remaining_troops > 0:
        # Pop the first node from the queue and put it at the end.
        curr_node = nodes.pop(0)
        nodes.append(curr_node)
        curr_color = curr_node.get_owner()
        # Find player with a given color.
        curr_player = find_player(curr_color, order)
        # Add a random number or, if the player doesn't have enough troops,
        # the remaining troops to the territory
        assigned_troops = min(random.randint(0, 5), curr_player.get_troops())
        curr_node.add_troops(assigned_troops)
        curr_player.subtract_troops(assigned_troops)
        total_remaining_troops -= assigned_troops


def remove_defeated(player_lst):
    '''Removes players with no territories from the given player list.
    Returns a new player list without the defeated players.

    Preconditions: no duplicates in [player_lst].'''
    res = []
    for i in range(len(player_lst)):
        player = player_lst[i]
        if len(territories(player.get_color(), continents)) > 0:
            res.append(player)
        else:
            print("\n%s Player has been defeated!\n" %
                  str(player.get_color()))
    return res


def check_attack(color, continents):
    '''Checks if the player with a given color can perform an attack.
    Returns a boolean.'''
    # First, check if there is at least one node where the player has more
    # than one unit. Next, for each node with more than 1 troop, check if there
    # are any adjacent enemy territories that could be attacked.
    for node in territories(color, continents):
        if node.get_troops() > 1 and len(node.attack_options()) > 0:
            return True
    return False


def check_attack_everyone(order, continents):
    '''Runs check_attack() on every remaining player to make sure at least
    one player can attack.'''
    for player in order:
        if check_attack(player.get_color(), continents):
            return True
    return False


def blitz_attack(from_node, to_node):
    '''Conducts blitz attack between the two nodes and changes the results.
    Returns a boolean representing whether attack was successful or not.

    Preconditions: from_node.get_troops() > 1 and to_node.get_troops() > 0;
        the nodes have two different owners.'''

    blitz_res = blitz(from_node.get_troops(), to_node.get_troops())

    if blitz_res[0] == 1:
        print("Attack unsuccessful! You now have 1 troop in " + from_node.get_name() + ". The " + str(to_node.get_owner()) +
              " player has " + str(blitz_res[1]) + " troops in " + to_node.get_name())
        from_node.set_troops(1)
        to_node.set_troops(blitz_res[1])
        return False
    elif blitz_res[1] == 0:
        print("\nAttack successful!")
        while True:

            # Only 2 troops survived. 1 automatically goes into a new territory.
            if blitz_res[0] == 2:
                to_node.set_owner(from_node.get_owner())
                from_node.set_troops(1)
                to_node.set_troops(1)
                print("\nYou now have 1 troop in " + from_node.get_name() +
                      " and " + "1 troop in " + to_node.get_name())
                return True

            # Only 3 troops survived. 2 automatically go into a new territory.
            elif blitz_res[0] == 3:
                to_node.set_owner(from_node.get_owner())
                from_node.set_troops(1)
                to_node.set_troops(2)
                print("\nYou now have 1 troop in " + from_node.get_name() +
                      " and " + "2 troops in " + to_node.get_name())
                return True

            # Only 4 troops survived. 3 automatically go into a new territory.
            elif blitz_res[0] == 4:
                to_node.set_owner(from_node.get_owner())
                from_node.set_troops(1)
                to_node.set_troops(3)
                print("\nYou now have 1 troop in " + from_node.get_name() +
                      " and " + "3 troops in " + to_node.get_name())
                return True

            # More than 3 troops survived. At least 3 go into a new territory.
            elif blitz_res[0] > 3:
                while True:
                    print("\nYou have %i troops left in %s." %
                          (blitz_res[0], from_node.get_name()))
                    # Input the number of troops moved and check.
                    moved_troops = request_input(
                        int, "How many troops do you want to move into %s? " % to_node.get_name())
                    if moved_troops < 3:
                        print(
                            "\nNeed to move at least 3 troops into a new territory!")
                    elif moved_troops > blitz_res[0]-1:
                        print(
                            "\nNot enough troops! You have to leave at least 1 troop in %s!" % from_node.get_name())
                    else:
                        # Move troops.
                        from_node.set_troops(blitz_res[0]-moved_troops)
                        to_node.set_troops(moved_troops)
                        to_node.set_owner(from_node.get_owner())

                        from_troops = from_node.get_troops()
                        to_troops = to_node.get_troops()
                        from_name = from_node.get_name()
                        to_name = to_node.get_name()
                        print("You now have %i troops in %s, and %i troops in %s.\n" % (
                            from_troops, from_name, to_troops, to_name))
                        return True
            else:
                raise ValueError(
                    "Wrong results for blitz: (%i, %i)" % blitz_res)
    else:
        raise ValueError("Wrong results for blitz: (%i, %i)" % blitz_res)


def calculate_troops_gained(curr_color, continents, print_details=False):
    '''Calculates the number of troops gained by the player with a given color
    in the beginning of their turn.
    Returns the number of gained troops (int), the number of territories owned
    by the player (int), and the list of continents owned by the player
    (Continent list).'''
    continents_owned = []
    territories_owned = len(territories(curr_color, continents))
    territory_bonus = max(territories_owned//3, 3)
    troops_gained = 0
    troops_gained += territory_bonus
    for continent in continents:
        if continent.get_owner() == curr_color:
            continents_owned.append(continent)
            bonus = continent.get_bonus()
            troops_gained += bonus
            if print_details:
                print("%i troops for %s," % (bonus, continent.get_name()))
    if print_details:
        print("%i troops for %i territories." %
              (territory_bonus, territories_owned))
    return troops_gained, territories_owned, continents_owned


def print_continent_list(continent_lst):
    '''Helper function for deploy_phase(). Returns a string.'''
    size = len(continent_lst)

    if size == 0:
        return ""
    elif size == 1:
        return continent_lst[0].get_name()
    elif size == 2:
        return "%s and %s" % (continent_lst[0].get_name(), continent_lst[1].get_name())
    return continent_lst[0].get_name() + ", " + print_continent_list(continent_lst[1:])


def request_input(input_type, msg):
    '''
    Helper function for deploy_phase(), attack_phase(), and fortify_phase().
    Requests input of a given [input_type] (either 'int', 'float', or 'str')
        with a given message (str) until user enters input of a type needed.
    Returns user's input.
    '''
    while True:
        try:
            res = input_type(input(msg))
            return res
        except ValueError:
            print("Invalid input!")


def set_continent_owners(continents):
    '''Checks if any of the continents is owned by a single color and
    sets owners if there are ones.'''
    for continent in continents:
        single_owner = True
        node_lst = continent.get_nodes()
        possible_owner = node_lst[0].get_owner()
        for node in node_lst[1:]:
            if node.get_owner() != possible_owner:
                single_owner = False
                continent.demonopolize()
                break
        if single_owner:
            continent.monopolize(possible_owner)


def deploy_phase(curr_player):
    print("\nDEPLOY.\n")

    print("You have the following cards: %s.\n" % str(curr_player.get_cards()))

    bonus_troops = 0

    # Check if player has more than 4 cards.
    if len(curr_player.get_cards()) > 4:
        print("\nYou have too many cards! You have to use them to get bonus troops!")
        best_hand = curr_player.decide()
        # Used cards are added to the deck in random locations.
        for card in best_hand:
            all_cards.insert(random.randint(0, len(all_cards)), card)
        bonus_troops += curr_player.use_cards(best_hand)

    elif len(curr_player.possible_combos()) > 0:
        best_hand = curr_player.decide()
        _, possible_bonus = curr_player.count_bonus(best_hand, False)
        while True:
            msg_card = "\nYou have an opportunity to use cards and to obtain %i bonus troops! Enter 1 to use it now or -1 to skip: " % possible_bonus
            card_use = request_input(int, msg_card)
            if card_use == 1:
                print("\nYou used your bonus cards.")
                # Used cards are added to the deck in random locations.
                for card in best_hand:
                    all_cards.insert(random.randint(0, len(all_cards)), card)
                bonus_troops += curr_player.use_cards(best_hand)
                break
            elif card_use == -1:
                print("\nYou skipped.")
                break
            else:
                print("\nWrong input! Please enter either 1 or -1.")

    curr_color = curr_player.get_color()
    assert curr_player.get_troops() == 0, "Undeployed troops for %s Player!" % curr_color

    troops_gained, _, _ = calculate_troops_gained(curr_color, continents, True)
    troops_gained += bonus_troops
    curr_player.set_troops(troops_gained)
    print("Total %i troops to deploy." % troops_gained)
    print("\nChoose where to put your troops.")

    msg_1 = "Your currently owned territories: \n" + \
        str(territories(curr_color, continents)) + \
        "\nEnter the id of a node where to put troops: "
    msg_2 = "Enter the number of troops to add: "

    # Keep placing troops until player has no more undeployed troops.
    while curr_player.get_troops() > 0:
        print("\nYou have %i more troops to deploy." %
              curr_player.get_troops())
        # Ask for a node id.
        nodeid = request_input(int, msg_1)
        node = find_node(nodeid, all_nodes_sorted)
        # Node not found.
        if node == None:
            print("\nNode with such id not found!")
            continue
        # Check ownership of the node.
        elif node.get_owner() != curr_color:
            print("\nYou don't own this territory!")
            continue
        # Ask for a number of troops to add.
        troops_added = request_input(int, msg_2)
        if troops_added < 0:
            print("\nNumber of deployed troops can't be negative!")
        elif troops_added > curr_player.get_troops():
            print("\nYou don't have that many troops to deploy!")
        else:
            node.add_troops(troops_added)
            curr_player.subtract_troops(troops_added)
            print("\nDone! You now have %i troops in %s." %
                  (node.get_troops(), node.get_name()))

    print("\nDone deploying troops.\n")


def attack_phase(curr_player):
    print("\nATTACK.\n")

    curr_color = curr_player.get_color()

    get_card = False
    while True:
        # Check if current player can attack.
        if not check_attack(curr_color, continents):
            print("Sorry! You currently don't have any opportunities to attack!")
            return
        # [msg] HAS to be defined here in order to keep updated with new territories
        # in case of multiple attacks in one turn.
        msg = "\nYour currently owned territories: \n" \
            + str(territories(curr_color, continents)) \
            + "\nEnter the id of a node from which to attack or -1 to finish ATTACK phase: "
        from_id = request_input(int, msg)

        # Check if done.
        if from_id == -1:
            break

        from_node = find_node(from_id, territories(curr_color, continents))
        if from_node == None:
            print(
                "You don't own a territory with such id! Please enter id of a territory you own!")
            continue
        elif from_node.get_troops() < 2:
            print(
                "You need to have at least 2 troops in a territory to be able to attack!")
            continue
        else:
            options = from_node.attack_options()
            # Check if can attack from the node.
            if len(options) == 0:
                print("You can't attack any nodes from the given node!")
                continue
            else:
                print("You have %i troops in %s." %
                      (from_node.get_troops(), from_node.get_name()))
                print("Possible nodes to attack: ", options)
                to_id = request_input(
                    int, "Enter the id of a node to attack: ")
                to_node = find_node(to_id, from_node.get_neighbors())
                if to_node == None:
                    print(
                        "Invalid node id! Node should be adjacent to the current node!")
                elif to_node.get_owner() == curr_color:
                    print(
                        "Territory already owned by you! Pick another territory.")
                else:
                    # Once set to True, [get_card] stays True.
                    # However, blitz_attack() should be called in any case in order to make changes.
                    get_card = blitz_attack(from_node, to_node) or get_card

    if get_card:
        card = all_cards.pop(0)
        curr_player.give_card(card)
        print("\nYou get a card!")
        print("Your card: \033[44m%s\033[0m" % str(card))
    print("\nDone attacking.\n")

    # done = False
    # while not done:
    #     to_id = int(
    #         input("Enter the id of a node which to attack: "))
    #     to_node = find_node(to_id, from_node.get_neighbors())
    #     if to_node == None:
    #         print(
    #             "Invalid node id! Node should be adjacent to the current node!")
    #     elif to_node.get_owner() == curr_color:
    #         print(
    #             "Territory already owned by you! Pick another territory.")
    #     else:
    #         blitz_attack(from_node, to_node)
    #         done = True


def fortify_phase(curr_player):
    print("\nFORTIFY.\n")

    curr_color = curr_player.get_color()
    str_terr = "Your currently owned territories: \n" + \
        str(territories(curr_color, continents))
    msg_from = str_terr + \
        "\nEnter the id of a node from which to take troops or -1 to skip FORTIFY phase: "
    msg_to = "\nEnter the id of a node to transfer troops to or -1 to get back to pick a different node: "

    while True:
        from_id = request_input(int, msg_from)
        # Check if skip.
        if from_id == -1:
            break
        # Find the node from which to take troops.
        from_node = find_node(from_id, territories(curr_color, continents))
        if from_node == None:
            print(
                "\nYou don't own a territory with such id! Please enter id of a territory you own!\n")
            continue
        elif from_node.get_troops() < 2:
            print(
                "\nYou need to have at least 2 troops in a territory to take troops from it!\n")
            continue
        else:
            # Find the node to which to take troops.
            to_id = request_input(int, msg_to)
            # Check if get back.
            if to_id == -1:
                continue
            to_node = find_node(to_id, territories(curr_color, continents))
            if to_node == None:
                print(
                    "\nYou don't own a territory with such id! Please enter id of a territory you own!\n")
                continue
            # Check if the two territories are connected.
            elif not path_exists(from_node, to_node):
                print(
                    "\nThe two territories aren't connected! You need to own all territories in a path between them to transfer troops!\n")
            else:
                # Ask how many troops to get.
                from_name = from_node.get_name()
                from_troops = from_node.get_troops()
                to_name = to_node.get_name()
                to_troops = to_node.get_troops()
                msg_num = "\nYou have %i troops in %s and %i troops in %s." % (from_troops, from_name, to_troops, to_name) + \
                    "\nEnter the number of troops to transfer from %s to %s: " % (
                        from_name, to_name)

                num_troops = request_input(int, msg_num)
                if num_troops < 0:
                    print("\nThe number of troops can't be negative!\n")
                elif num_troops >= from_troops:
                    print(
                        "\nNot enough troops in %s! At least 1 troop should remain!\n" % from_name)
                else:
                    from_node.subtract_troops(num_troops)
                    to_node.add_troops(num_troops)
                    print("\nDone. You now have %i troops in %s and %i troops in %s.\n" %
                          (from_node.get_troops(), from_name, to_node.get_troops(), to_name))
                    break

    print("\nDone fortifying.\n")

    print("\nYour cards: %s.\n" % str(curr_player.get_cards()))




claim_territories(order, all_nodes.copy())
initialize_troops(order, all_nodes.copy())
# Ensure there are no unowned nodes.
for continent in continents:
    for node in continent.get_nodes():
        if node.get_owner() == Color.NONE:
            raise ValueError('Unowned node!' + str(node))

