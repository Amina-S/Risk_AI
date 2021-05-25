import random
import time

from card import *
from color import Color
from continent import *
from path import path_exists
from player import Player
from roll import blitz

import numpy as np
from state import State
from statespace import Statespace




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

        if (curr_node.get_id() not in curr_player.get_territories()):
            curr_player.add_territory(curr_node.get_id())
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
                    moved_troops = blitz_res[0]-1
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

    #             if moved_troops < 3:
    #                 print("\nNeed to move at least 3 troops into a new territory!")
    #             elif moved_troops > blitz_res[0]
    #             You now have 1 troop in " + from_node.get_name() + " and " + str(blitz_res[0]-1) +
    #                 " troops in " + to_node.get_name())
    #             print("You get a card!")
    #             from_node.set_troops(1)
    #             curr_color=from_node.get_owner()
    #             to_node.set_owner(curr_color)
    #             to_node.set_troops(blitz_res[0]-1)
    # else:
    #     raise ValueError("Wrong results for blitz: (%i, %i)" % blitz_res)


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


# def attack_phase(curr_player):
#     print("\nATTACK.\n")

#     curr_color = curr_player.get_color()

#     get_card = False
#     cont = True
#     while cont:
#         # Check if current player can attack.
#         if not check_attack(curr_color, continents):
#             print("Sorry! You currently don't have any opportunities to attack!")
#             return
#         # [msg] HAS to be defined here in order to keep updated with new territories
#         # in case of multiple attacks in one turn.
#         msg = "\nYour currently owned territories: \n" \
#             + str(territories(curr_color, continents)) \
#             + "\nEnter the id of a node from which to attack or -1 to finish ATTACK phase: "
#         from_id = request_input(int, msg)

#         # Check if done.
#         if from_id == -1:
#             break

#         from_node = find_node(from_id, territories(curr_color, continents))
#         if from_node == None:
#             print(
#                 "You don't own a territory with such id! Please enter id of a territory you own!")
#             cont = False
#             continue
#         elif from_node.get_troops() < 2:
#             print(
#                 "You need to have at least 2 troops in a territory to be able to attack!")
#             continue
#         else:
#             options = from_node.attack_options()
#             # Check if can attack from the node.
#             if len(options) == 0:
#                 print("You can't attack any nodes from the given node!")
#                 continue
#             else:
#                 print("You have %i troops in %s." %
#                       (from_node.get_troops(), from_node.get_name()))
#                 print("Possible nodes to attack: ", options)
#                 to_id = request_input(
#                     int, "Enter the id of a node to attack: ")
#                 to_node = find_node(to_id, from_node.get_neighbors())
#                 if to_node == None:
#                     print(
#                         "Invalid node id! Node should be adjacent to the current node!")
#                 elif to_node.get_owner() == curr_color:
#                     print(
#                         "Territory already owned by you! Pick another territory.")
#                 else:
#                     # Once set to True, [get_card] stays True.
#                     # However, blitz_attack() should be called in any case in order to make changes.
#                     get_card = blitz_attack(from_node, to_node) or get_card

#     if get_card:
#         card = all_cards.pop(0)
#         curr_player.give_card(card)
#         print("\nYou get a card!")
#         print("Your card: \033[44m%s\033[0m" % str(card))
#     print("\nDone attacking.\n")



# def fortify_phase(curr_player):
#     print("\nFORTIFY.\n")

#     curr_color = curr_player.get_color()
#     str_terr = "Your currently owned territories: \n" + \
#         str(territories(curr_color, continents))
#     msg_from = str_terr + \
#         "\nEnter the id of a node from which to take troops or -1 to skip FORTIFY phase: "
#     msg_to = "\nEnter the id of a node to transfer troops to or -1 to get back to pick a different node: "

#     while True:
#         from_id = request_input(int, msg_from)
#         # Check if skip.
#         if from_id == -1:
#             break
#         # Find the node from which to take troops.
#         from_node = find_node(from_id, territories(curr_color, continents))
#         if from_node == None:
#             print(
#                 "\nYou don't own a territory with such id! Please enter id of a territory you own!\n")
#             continue
#         elif from_node.get_troops() < 2:
#             print(
#                 "\nYou need to have at least 2 troops in a territory to take troops from it!\n")
#             continue
#         else:
#             # Find the node to which to take troops.
#             to_id = request_input(int, msg_to)
#             # Check if get back.
#             if to_id == -1:
#                 continue
#             to_node = find_node(to_id, territories(curr_color, continents))
#             if to_node == None:
#                 print(
#                     "\nYou don't own a territory with such id! Please enter id of a territory you own!\n")
#                 continue
#             # Check if the two territories are connected.
#             elif not path_exists(from_node, to_node):
#                 print(
#                     "\nThe two territories aren't connected! You need to own all territories in a path between them to transfer troops!\n")
#             else:
#                 # Ask how many troops to get.
#                 from_name = from_node.get_name()
#                 from_troops = from_node.get_troops()
#                 to_name = to_node.get_name()
#                 to_troops = to_node.get_troops()
#                 msg_num = "\nYou have %i troops in %s and %i troops in %s." % (from_troops, from_name, to_troops, to_name) + \
#                     "\nEnter the number of troops to transfer from %s to %s: " % (
#                         from_name, to_name)

#                 num_troops = request_input(int, msg_num)
#                 if num_troops < 0:
#                     print("\nThe number of troops can't be negative!\n")
#                 elif num_troops >= from_troops:
#                     print(
#                         "\nNot enough troops in %s! At least 1 troop should remain!\n" % from_name)
#                 else:
#                     from_node.subtract_troops(num_troops)
#                     to_node.add_troops(num_troops)
#                     print("\nDone. You now have %i troops in %s and %i troops in %s.\n" %
#                           (from_node.get_troops(), from_name, to_node.get_troops(), to_name))
#                     break

#     print("\nDone fortifying.\n")

#     print("\nYour cards: %s.\n" % str(curr_player.get_cards()))

################################# AI ######################################
def debug_state(state):
    tt = []
    ott = []
    for terr,_ in state.get_trp_terr():
        node = find_node(terr, all_nodes_sorted)
        tt.append((str(node.get_owner()),str(node)))
    for terr,_ in state.get_opp_trp_terr():
        node = find_node(terr, all_nodes_sorted)
        ott.append((str(node.get_owner()),str(node)))
    return tt, ott

def init_state_space(curr_player, opp): 
    global statespace
    territory_ids = curr_player.get_territories()
    # print(territory_ids)
    tt = []
    ott = []
    for terr in all_nodes:
        # print(terr)
        # print(terr.get_owner(), curr_player.get_color(), terr.get_owner() == curr_player.get_color())
        if (terr.get_owner() == curr_player.get_color()):
            add = (terr.get_id(), terr.get_troops())
            # print('add', add)
            tt.append(add)

        else:
            ott.append((terr.get_id(), terr.get_troops()))
    print('tt:' , tt, '\nott', ott)
    for nod_id,_ in tt:
        nod = find_node(nod_id, all_nodes_sorted)
        assert nod.get_owner() == curr_player.get_color()
    for nod_id,_ in ott:
        nod = find_node(nod_id, all_nodes_sorted)
        assert nod.get_owner() == opp.get_color()
    start = State(current_player=curr_player, opponent=opp, likelihood=1, trp_terr=tt, opp_trp_terr=ott)
    statespace.set_pointer(start)
    build_state_paths(curr_player, opp, -(2 * 10**62), (2 * 10**62), start, 0)

import random
def state_attack_options(state, terr_id):
        '''Returns a list of nodes that could be attacked from the given node.'''
        res = []
        node = find_node(terr_id, all_nodes_sorted) # TODOne: all_nodes_sorted
        # if random.randint(0,100) == 100:
        #     print("\nLOOK!")
        #     print(state.get_current_player().get_color())
        #     for e in state.get_trp_terr():
        #         nod = find_node(e[0],all_nodes_sorted)
        #         print(nod, nod.get_owner())
        #     print("SALUT")
        #     for e in state.get_opp_trp_terr():
        #         nod = find_node(e[0],all_nodes_sorted)
        #         print(nod, nod.get_owner())
        for t in node.get_neighbors():
            # get_opp_trp_terr() returns smth like [(t_id1, #troops), (t_id2, #troops), ...]
            for e in state.get_opp_trp_terr():
                if (e[0]==t.get_id()):
                    # print(t)
                    res.append(t)
        return res


def build_state_paths(curr_player, opponent, a, b, state, d):
    global count
     #if current player has now won (all territories conquered)
    if (d >= MAX_DEPTH or len(state.get_trp_terr()) == 42):
        if (curr_player.get_color() != Color.RED):
            h = 0
        else:
            tot_troops = 0
            for (terr, trp) in state.get_trp_terr():
                tot_troops += trp
            h = state.get_likelihood() * tot_troops
        state.set_h(h) 
        return h

    if (curr_player.get_color() == Color.RED):
        temp = -(2 * 10**62)
        for (t_id, num_troops) in state.get_trp_terr():
            #if player can attack from this territory with high likelihood of success
            if (num_troops >= 2):
                # print(state, t_id)
                n_neighbors = state_attack_options(state, t_id)
                #for each attackable neighbor
                for neighbor in n_neighbors:
                    # print("Assertion")
                    # assert neighbor.get_owner() == Color.BLUE, str(neighbor) + str(neighbor.get_owner())
                    #possible number of defending troops
                    neighbor_id = neighbor.get_id()
                    # print(neighbor_id)
                    neighbor_troops = state.get_troops(neighbor_id)
                    # defending = min(2, neighbor_troops)
                    if (num_troops-1 > neighbor_troops):
                        l = prob_capture(num_troops, neighbor_troops)
                        # l = prob_capture(num_troops, defending) #TODO: change defending to neighbor_troops
                        if (l>PROB_THRESHOLD):
                            #make children:
                            #the current opponent becomes the next player, who just lost the territory
                            new_tt = [e for e in state.get_opp_trp_terr() if e not in [(neighbor_id, neighbor_troops)]]
                            # print(state.get_opp_trp_terr())
                            #current player becomes the opponent, plus the conquered territory, and adjust the troops in the terr attacked from
                            new_ott = [e for e in state.get_trp_terr() if e not in [(t_id, num_troops)]]+[(neighbor_id, num_troops-1), (t_id, 1)]
                            new_child = State(current_player=opponent, opponent=state.get_current_player(), move=(t_id,neighbor_id), likelihood=l*state.get_likelihood(), trp_terr=new_tt, opp_trp_terr=new_ott)
                            count = count + 1
                            if count%100 == 0:
                                print (count)
                            state.add_child(new_child)
                            res = build_state_paths(opponent, curr_player, a, b, new_child, d+1)
                            m = max(res, temp)
                            #a-b prune
                            a = max(a, res)
                            if b <= a:
                                break
    else:
        temp = 2 * 10**62
        for (t_id, num_troops) in state.get_trp_terr():
            #if player can attack from this territory with high likelihood of success
            if (num_troops >= 2):
                n_neighbors = state_attack_options(state, t_id)
                #for each attackable neighbor
                for neighbor in n_neighbors:
                    #possible number of defending troops
                    neighbor_id = neighbor.get_id()
                    neighbor_troops = state.get_troops(neighbor_id)
                    defending = min(2, neighbor_troops)
                    if (num_troops-1 > defending):
                        l = prob_capture(num_troops, defending)
                        if (l>PROB_THRESHOLD):
                            #make children:
                            #the current opponent becomes the next player, who just lost the territory
                            new_tt = [e for e in state.get_opp_trp_terr() if e not in [(neighbor_id, neighbor_troops)]]
                            #current player becomes the opponent, plus the conquered territory, and adjust the troops in the terr attacked from
                            new_ott = [e for e in state.get_trp_terr() if e not in [(t_id, num_troops)]]+[(neighbor_id, num_troops-1), (t_id, 1)]
                            new_child = State(current_player=state.opponent, opponent=state.get_current_player(), move=(t_id,neighbor_id), likelihood=l*state.get_likelihood(), trp_terr=new_tt, opp_trp_terr=new_ott)
                            count = count + 1
                            if count%100 == 0:
                                print (count)
                            state.add_child(new_child)
                            res = build_state_paths(opponent, curr_player, a, b, new_child, d+1)
                            m = min(res, temp)
                            #a-b prune
                            b = min(b, res)
                            if b <= a:
                                break
    state.set_h(m)
    return m
                    

probs = np.zeros((2,3,3))
probs[0,0] = [0.4167, 0., 0.5833]
probs[0,1] = [0.5787, 0., 0.4213]
probs[0,2] = [0.6597, 0., 0.3403]
probs[1,0] = [0.2546, 0., 0.7454]
probs[1,1] = [0.2276, 0.3241, 0.4483]
probs[1,2] = [0.3717, 0.3357, 0.2926]

#finished
def prob_capture(attack, defend, n=1000):
    assert attack > 1 and defend > 0
    wins = 0
    for i in range(n):
        curr_attack = attack
        curr_defend = defend
        while curr_defend > 0 and curr_attack > 1:
            attacking_dice = min(curr_attack-1, 3)
            defending_dice = min(curr_defend, 2)
            roll = np.random.uniform()
            lo = probs[defending_dice-1, attacking_dice-1, 0]
            hi = lo + probs[defending_dice-1, attacking_dice-1, 1]
            if roll < lo:
                curr_defend -= min(attacking_dice, defending_dice) 
            elif lo <= roll <= hi:
                curr_attack -= 1
                curr_defend -= 1
            else:
                curr_attack -= min(attacking_dice, defending_dice) 
        if curr_attack > 1:
            wins += 1
    return wins/n

#tentatively finished
def ai_deploy_phase(curr_player): 
    global statespace
    rand_deploy_phase(curr_player)

def ai_attack_phase(curr_player, order): 
    global statespace
    print("\nATTACK.\n")

    curr_color = curr_player.get_color()

    get_card = False
    cont = True
    # while cont:
    # Check if current player can attack.
    if not check_attack(curr_color, continents):
        print("Sorry! You currently don't have any opportunities to attack!")
        return
    # [msg] HAS to be defined here in order to keep updated with new territories
    # in case of multiple attacks in one turn.
    msg = "\nYour currently owned territories: \n" \
        + str(territories(curr_color, continents)) \
        + "\nEnter the id of a node from which to attack or -1 to finish ATTACK phase: "
    

    #ENTER CODE
    state = statespace.get_pointer()
    print('first pointer:', statespace.get_pointer())
    max_h = 0
    for c in state.get_children():
        if c.get_h() >= max_h:
            max_h = c.get_h()
            chosen_state = c
    # print("\nREAD")
    # print("tt: %s, \n ott: %s" % debug_state(chosen_state))
    from_id, to_id = chosen_state.get_move()
    from_node = find_node(from_id, all_nodes_sorted)
    to_node = find_node(to_id, all_nodes_sorted)
    print(state.get_current_player().get_color())
    print("HULLO")
    print(from_node.get_owner(), from_node)
    print(to_node.get_owner(), to_node)
    # print('ai-- children:', state.get_children(), 'move:', c.get_move())
    
    statespace.set_pointer(chosen_state)
    print('new pointer:', statespace.get_pointer())



    print(from_id, territories(curr_color, continents))
    from_node = find_node(from_id, territories(curr_color, continents))
    if from_node == None:
        print(
            "You don't own a territory with such id! Please enter id of a territory you own!")
        cont = False
        # continue
    elif from_node.get_troops() < 2:
        print(
            "You need to have at least 2 troops in a territory to be able to attack!")
        # continue
    else:
        options = from_node.attack_options()
        # Check if can attack from the node.
        if len(options) == 0:
            print("You can't attack any nodes from the given node!")
            # continue
        else:
            print("You have %i troops in %s." %
                    (from_node.get_troops(), from_node.get_name()))
            print("Possible nodes to attack: ", options)
            # to_id = request_input(
            #     int, "Enter the id of a node to attack: ")
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
                if not blitz_attack(from_node, to_node) :
                    init_state_space(curr_player, order[0])





############################## RANDOM ######################################
#tentatively finished, needs to update the start state
def rand_deploy_phase(curr_player): 
    global statespace
    print("\nDEPLOY.\nThe random player has the following cards: %s.\n" % str(curr_player.get_cards()))

    bonus_troops = 0
    curr_color = curr_player.get_color()
    assert curr_player.get_troops() == 0, "Undeployed troops for Random Player!" 
    troops_gained, _, _ = calculate_troops_gained(curr_color, continents, True)
    troops_gained += bonus_troops
    curr_player.set_troops(troops_gained)
    print("Total %i troops to deploy." % troops_gained)


    # Keep placing troops until player has no more undeployed troops.
    while curr_player.get_troops() > 0:
        print("\nYou have %i more troops to deploy." %
              curr_player.get_troops())
        nodeid = random.choice(curr_player.get_territories())
        node = find_node(nodeid, all_nodes_sorted)
        # Node not found.
        if node == None:
            print("\nNode with such id not found!")
            continue
        # Check ownership of the node.
        elif node.get_owner() != curr_color:
            print("\nYou don't own this territory!")
            continue
        troops_added = 1
        node.add_troops(troops_added)
        curr_player.subtract_troops(troops_added)
        print("\nDone! You now have %i troops in %s." %
                (node.get_troops(), node.get_name()))

    print("\nDone deploying troops.\n")

def rand_attack_phase(curr_player, order): 
    global statespace
    print("\nATTACK.\n")

    curr_color = curr_player.get_color()

    get_card = False
    # while True:
    # Check if current player can attack.
    if not check_attack(curr_color, continents):
        print("Sorry! You currently don't have any opportunities to attack!")
        return
    # [msg] HAS to be defined here in order to keep updated with new territories
    # in case of multiple attacks in one turn.
    msg = "\nYour currently owned territories: \n" \
        + str(territories(curr_color, continents)) \
        + "\nEnter the id of a node from which to attack or -1 to finish ATTACK phase: "
    

    #ENTER CODE
    state = statespace.get_pointer()
    print('first pointer:', statespace.get_pointer())
    #pick random child (prob of winning the territory is still above threshold)
    c = state.get_children()[0]
    from_id, to_id = c.get_move()
    print('random-- children:', state.get_children(), 'move:', c.get_move())
    statespace.set_pointer(c)
    from_node = find_node(from_id,all_nodes_sorted)
    to_node = find_node(to_id,all_nodes_sorted)
    print(from_id, territories(curr_color, continents))
    print(state.get_current_player().get_color())
    print("HULLO2")
    print(from_node.get_owner(), from_node)
    print(to_node.get_owner(), to_node)
    print('new pointer:', statespace.get_pointer())

    from_node = find_node(from_id, territories(curr_color, continents))
    if from_node == None:
        print(
            "You don't own a territory with such id! Please enter id of a territory you own!")
        # continue
    elif from_node.get_troops() < 2:
        print(
            "You need to have at least 2 troops in a territory to be able to attack!")
        # continue
    else:
        options = from_node.attack_options()
        # Check if can attack from the node.
        if len(options) == 0:
            print("You can't attack any nodes from the given node!")
            # continue
        else:
            print("You have %i troops in %s." %
                    (from_node.get_troops(), from_node.get_name()))
            print("Possible nodes to attack: ", options)
            # to_id = request_input(
            #     int, "Enter the id of a node to attack: ")
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
                if not blitz_attack(from_node, to_node) :
                    init_state_space(curr_player, order[0])






############################################################################
# Because of colored printing, printing nodes owned by Color.NONE will result
# in TypeError (since Color.None.Value is int).
# print(Europe.nodes)


def play_random():
    # Initialize players.
    
    red = Player(Color.RED, INITIAL_TROOPS, [], [])
    blue = Player(Color.BLUE, INITIAL_TROOPS, [], [])

    # Randomize order.
    order = [red, blue]
    random.shuffle(order)

    claim_territories(order, all_nodes.copy())
    initialize_troops(order, all_nodes.copy())
    # Ensure there are no unowned nodes.
    for continent in continents:
        for node in continent.get_nodes():
            if node.get_owner() == Color.NONE:
                raise ValueError('Unowned node!' + str(node))
    # territory_ids = curr_player.get_territories()
    game_over = False
    first_turn = True
    # while not game_over:
    for i in range (2):
        # Remove defeated players.
        order = remove_defeated(order)
        # Check if there's a victor.
        if len(order) == 1:
            col = str(order[0].get_color())
            print("\n\n%s Player won! Congratulations!\n\n" %
               col )
            game_over = True
            return (col == 'red')
        # Make a turn.
        else:
            # Check if at least one player can attack.
            if not check_attack_everyone(order, continents):
                print("\n\nNo one can attack on this turn!\n\n")
                # game_over = True
            curr_player = order.pop(0)
            order.append(curr_player)
            print("\nCurrent player: %s.\n" % str(curr_player.get_color()))
            # set_continent_owners(continents)
            if (first_turn):
                     all_nodes.sort(key = lambda x: x.get_id())
                     init_state_space(curr_player, order[0])
                     first_turn = False
            if (curr_player.get_color() == Color.RED):
                # ai_deploy_phase(curr_player)
                ai_attack_phase(curr_player, order)
            else: 
                # rand_deploy_phase(curr_player)
                rand_attack_phase(curr_player, order)





count = 0
PROB_THRESHOLD  = 0.9 
ITERATIONS = 1
INITIAL_TROOPS = 70
MAX_DEPTH = 3
ai_wins = 0
ai_losses = 0
statespace = Statespace()
for i in range(ITERATIONS):
    if (play_random()):
        ai_wins += 1
    else:
        ai_losses += 1
win_rate = ai_wins / ITERATIONS
print("The AI won ", ai_wins, " times out of", ITERATIONS, "giving it a win rate of", win_rate, "%")

