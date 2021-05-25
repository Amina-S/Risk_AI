import math
import pygame
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

pygame.init()

display_width = 1200
display_height = 900

black = (0, 0, 0)
grey = (50, 50, 50)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (0, 0, 255)
brown = (139, 69, 19)
lavender = (230,230,250)

brighter_red = (220, 0, 0)
brighter_green = (0, 220, 0)
brightest_red = (255, 0, 0)
brightest_green = (0, 255, 0)

button_radius = 75

gameDisplay = pygame.display.set_mode(
    (display_width, display_height), pygame.RESIZABLE)
# gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("RISK")
clock = pygame.time.Clock()

gameIcon = pygame.image.load('Logo.png')
pygame.display.set_icon(gameIcon)

bgImg_unscaled = pygame.image.load("./Map.png").convert()
bgImg = pygame.transform.scale(bgImg_unscaled, (display_width, display_height))


dim = 140
bright = 200
brightest = 255
colors = {
    "RED": [(dim, 0, 0), (bright, 0, 0), (brightest, 0, 0)],
    "YELLOW": [(dim, dim, 0), (bright, bright, 0), (brightest, brightest, 0)],
    "GREEN": [(0, dim, 0), (0, bright, 0), (0, brightest, 0)],
    "CYAN": [(0, dim, 150), (0, bright, bright), (0, brightest, brightest)],
    "BLUE": [(0, 0, dim), (0, 0, bright), (0, 0, brightest)],
    "PURPLE": [(dim, 0, dim), (bright, 0, bright), (brightest, 0, brightest)],
}

def event_loop():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_quit()
        if event.type == pygame.VIDEORESIZE:
            rescale_locations(event.w, event.h)

def text_objects(text, font, color=black):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def load_img(path):
    img_unscaled = pygame.image.load(path)
    x, y = img_unscaled.get_rect().size
    img = pygame.transform.scale(
        img_unscaled, (int(x*display_width/1600), int(y*display_height/1200)))
    return img

tick_img = load_img("./Tick.png")
tick_active_img = load_img("./Tick_active.png")
message_img = load_img("./Message_table.png")
cardlist_img = load_img("./Cardlist.png")
cards_img = load_img("./Cards.png")
cards_active_img = load_img("./Cards_active.png")
button_generic_img = load_img("./Button_generic_large.png")
button_generic_active_img = load_img("./Button_generic_large_active.png")

def button_textless_rect(x, y, inactive_img, active_img, action=None):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    width, height = inactive_img.get_rect().size

    if x-width/2 < mouse[0] < x+width/2 and y-height/2 < mouse[1] < y+height/2:
        gameDisplay.blit(active_img, (x-width/2, y-height/2))
        if click[0] == 1:
            if action is not None:
                action() 
    else:
        gameDisplay.blit(inactive_img, (x-width/2, y-height/2))

def button_textless_circular(x, y, inactive_img, active_img, action=None):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    width, height = inactive_img.get_rect().size
    radius = width/2

    if distance(mouse, (x, y)) <= radius:
        gameDisplay.blit(active_img, (x-width/2,y-height/2))
        
        if click[0] == 1:
            if action is not None:
                action()
    else:
        width, height = inactive_img.get_rect().size
        gameDisplay.blit(inactive_img, (x-width/2,y-height/2))


def distance(pos1, pos2):
    return math.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)


def node_button_deploy(node, radius, width=0, font_color=white,
                       font_type='roboto', font_size=30, curr_player=None):
    global selected_node_deploy
    global deploy_in_progress

    # For some reason, when resizing, one needs to keep the old node locations
    # when placing nodes BUT new locations when calculating distances, which
    # is reflected in the variables (x, y) - "old", and (x_dist, y_dist) -
    # "new", resized.
    x, y = node.get_location()
    x_dist, y_dist = locations[node.get_name()]
    # Inactive color, active color, click color.
    ic, ac, cc = colors[node.get_owner().name]

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Node already selected.
    if selected_node_deploy == node:
        pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
        if not deploy_in_progress and click[0] and distance(mouse, (x_dist, y_dist)) > radius+width:
            selected_node_deploy = None
    elif selected_node_deploy is not None:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)

    # No node yet selected and this node is belongs to the player.
    if node.get_owner() == curr_player.get_color():
        # Mouse hovered over the node.
        if distance(mouse, (x_dist, y_dist)) <= radius+width:
            # Node selected.
            if click[0]:
                selected_node_deploy = node
                deploy_in_progress = True
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
        else:
            pygame.draw.circle(gameDisplay, ac, (x, y), radius, width)
    # This node can't be selected since it doesn't belong to the player.
    else:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)

    # Display troops.
    smallText = pygame.font.SysFont(font_type, font_size)
    textSurf, textRect = text_objects(
        str(node.get_troops()), smallText, font_color)
    textRect.center = (x, y)
    gameDisplay.blit(textSurf, textRect)

def node_button_attack_from(node, radius, width=0, font_color=white,
                            font_type='roboto', font_size=30, action=None, curr_player=None):
    global selected_node_attack_from

    troops = node.get_troops()
    # For some reason, when resizing, one needs to keep the old node locations
    # when placing nodes BUT new locations when calculating distances, which
    # is reflected in the variables (x, y) - "old", and (x_dist, y_dist) -
    # "new", resized.
    x, y = node.get_location()
    x_dist, y_dist = locations[node.get_name()]
    # Inactive color, active color, click color.
    ic, ac, cc = colors[node.get_owner().name]

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Node already selected.
    if selected_node_attack_from is not None:
        if selected_node_attack_from == node:
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
            return
        else:
            pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
            return

    # No node is currently selected.
    # Could potentially choose the node.
    if node.get_owner() == curr_player.get_color() and troops > 1:
        # Mouse hovered over a node that could potentially be selected.
        if distance(mouse, (x_dist, y_dist)) <= radius+width:
            # Node selected.
            if click[0]:
                selected_node_attack_from = node
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
        else:
            pygame.draw.circle(gameDisplay, ac, (x, y), radius, width)
    # Node doesn't belong to the player or has 1 troop.
    else:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)

    # Display troops.
    smallText = pygame.font.SysFont(font_type, font_size)
    textSurf, textRect = text_objects(str(troops), smallText, font_color)
    textRect.center = (x, y)
    gameDisplay.blit(textSurf, textRect)


def node_button_attack_to(node,  radius, width=0, font_color=white,
                          font_type='roboto', font_size=30, action=None, curr_player=None):
    global selected_node_attack_from
    global selected_node_attack_to
    global blitz_res

    # For some reason, when resizing, one needs to keep the old node locations
    # when placing nodes BUT new locations when calculating distances, which
    # is reflected in the variables (x, y) - "old", and (x_dist, y_dist) -
    # "new", resized.
    x, y = node.get_location()
    x_dist, y_dist = locations[node.get_name()]
    # Inactive color, active color, click color.
    ic, ac, cc = colors[node.get_owner().name]

    # Needs to choose a node to attack from again.
    if selected_node_attack_from is None:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
        return
    # Node to attack has already been picked.
    elif selected_node_attack_to is not None and selected_node_attack_to != node:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
        return

    selected_node_owner = selected_node_attack_from.get_owner()

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Current node is selected.
    if selected_node_attack_from == node:
        # Code below might be confusing but it's necessary for bug-free run.
        # If left-click is made AND it is not on the one of the possible options
        # reassign selected_node_attack_from and go back to selecting the node
        # to attack from. Otherwise, return before reassigning the global
        # variable and let the other nodes conduct the attack and record
        # changes.
        if click[0] and distance(mouse, (x_dist, y_dist)) > radius+width:
            for n in node.attack_options():
                x_dist_n, y_dist_n = locations[n.get_name()]
                if distance(mouse, (x_dist_n, y_dist_n)) <= radius+width:
                    return
            selected_node_attack_from = None
        # Still selected but no click.
        else:
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
    # Node could be attacked from a selected node.
    elif node in selected_node_attack_from.get_neighbors() and node.get_owner() != selected_node_owner:
        # Mouse is hovered above the node.
        if distance(mouse, (x_dist, y_dist)) <= radius+width:
            # Node is selected to be attacked.
            if click[0]:
                selected_node_attack_to = node
                blitz_res = blitz_attack(selected_node_attack_from, node)
                pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
            else:
                pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
        # Mouse is not above the node.
        else:
            pygame.draw.circle(gameDisplay, ac, (x, y), radius, width)
    # Node cannot be attacked from a selected node.
    else:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)

    # Display troops.
    smallText = pygame.font.SysFont(font_type, font_size)
    textSurf, textRect = text_objects(
        str(node.get_troops()), smallText, font_color)
    textRect.center = (x, y)
    gameDisplay.blit(textSurf, textRect)

def node_button_fortify_from(node, radius, width=0, font_color=white,
                            font_type='roboto', font_size=30, action=None, curr_player=None):
    global selected_node_fortify_from

    troops = node.get_troops()
    # For some reason, when resizing, one needs to keep the old node locations
    # when placing nodes BUT new locations when calculating distances, which
    # is reflected in the variables (x, y) - "old", and (x_dist, y_dist) -
    # "new", resized.
    x, y = node.get_location()
    x_dist, y_dist = locations[node.get_name()]
    # Inactive color, active color, click color.
    ic, ac, cc = colors[node.get_owner().name]

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Node already selected.
    if selected_node_fortify_from is not None:
        if selected_node_attack_from == node:
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
            return
        else:
            pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
            return

    # No node is currently selected.
    # Could potentially choose the node.
    if node.get_owner() == curr_player.get_color() and troops > 1:
        # Mouse hovered over a node that could potentially be selected.
        if distance(mouse, (x_dist, y_dist)) <= radius+width:
            # Node selected.
            if click[0]:
                selected_node_fortify_from = node
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
        else:
            pygame.draw.circle(gameDisplay, ac, (x, y), radius, width)
    # Node doesn't belong to the player or has 1 troop.
    else:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)

    # Display troops.
    smallText = pygame.font.SysFont(font_type, font_size)
    textSurf, textRect = text_objects(str(troops), smallText, font_color)
    textRect.center = (x, y)
    gameDisplay.blit(textSurf, textRect)


def node_button_fortify_to(node,  radius, width=0, font_color=white,
                          font_type='roboto', font_size=30, action=None, curr_player=None):
    global selected_node_fortify_from
    global selected_node_fortify_to

    # For some reason, when resizing, one needs to keep the old node locations
    # when placing nodes BUT new locations when calculating distances, which
    # is reflected in the variables (x, y) - "old", and (x_dist, y_dist) -
    # "new", resized.
    x, y = node.get_location()
    x_dist, y_dist = locations[node.get_name()]
    # Inactive color, active color, click color.
    ic, ac, cc = colors[node.get_owner().name]

    # Needs to choose a node to fortify from again.
    if selected_node_fortify_from is None:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
        return
    # Node to fortify has already been picked.
    elif selected_node_fortify_to is not None and selected_node_fortify_to != node:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
        return


    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Current node is selected.
    if selected_node_fortify_from == node:
        # Code below might be confusing but it's necessary for bug-free run.
        # If left-click is made AND it is not on the one of the possible options
        # reassign selected_node_fortify_from and go back to selecting the node
        # to fortify from. Otherwise, return before reassigning the global
        # variable and let the other nodes conduct the fortify and record
        # changes.
        if click[0] and distance(mouse, (x_dist, y_dist)) > radius+width:
            for n in all_nodes:
                x_dist_n, y_dist_n = locations[n.get_name()]
                if distance(mouse, (x_dist_n, y_dist_n)) <= radius+width and node.get_owner() == curr_player.get_color() and path_exists(selected_node_fortify_from, n):
                    return
            selected_node_fortify_from = None
        # Still selected but no click.
        else:
            pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
    # Node could reached from a selected node.
    elif path_exists(selected_node_fortify_from, node) and node.get_owner() == selected_node_fortify_from.get_owner():
        # Mouse is hovered above the node.
        if distance(mouse, (x_dist, y_dist)) <= radius+width:
            # Node is selected to be attacked.
            if click[0]:
                selected_node_fortify_to = node
                pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)
            else:
                pygame.draw.circle(gameDisplay, cc, (x, y), radius, width)
        # Mouse is not above the node.
        else:
            pygame.draw.circle(gameDisplay, ac, (x, y), radius, width)
    # Node cannot be fortified from a selected node.
    else:
        pygame.draw.circle(gameDisplay, ic, (x, y), radius, width)

    # Display troops.
    smallText = pygame.font.SysFont(font_type, font_size)
    textSurf, textRect = text_objects(
        str(node.get_troops()), smallText, font_color)
    textRect.center = (x, y)
    gameDisplay.blit(textSurf, textRect)


def num_displayed_increase():
    '''Helper function for display_numbers().'''
    global num_displayed
    num_displayed += 1


def num_displayed_decrease():
    '''Helper function for display_numbers().'''
    global num_displayed
    num_displayed -= 1


def deselect_deploy_node():
    '''Helper function for display_numbers().'''
    global selected_node_deploy
    global deploy_in_progress
    selected_node_deploy = None
    deploy_in_progress = False


def place_troops_deploy():
    '''Helper function for display_numbers().'''
    global num_displayed
    global selected_node_deploy
    global deploy_in_progress

    assert selected_node_deploy is not None
    assert deploy_in_progress

    selected_node_deploy.add_troops(num_displayed)
    curr_player.subtract_troops(num_displayed)

    selected_node_deploy = None
    deploy_in_progress = False

def go_back_deploy():
    '''Helper function for display_numbers().'''
    global deploy_in_progress
    global selected_node_deploy

    deploy_in_progress = False
    selected_node_deploy = None

def occupy_territory():
    '''Helper function for display_numbers().'''
    global num_displayed
    global selected_node_attack_from
    global selected_node_attack_to
    global territory_occupied

    assert selected_node_attack_to is not None
    assert not territory_occupied

    total_troops = selected_node_attack_from.get_troops() + selected_node_attack_to.get_troops()

    selected_node_attack_to.set_troops(num_displayed)
    selected_node_attack_from.set_troops(total_troops-num_displayed)

    territory_occupied = True

def fortify_territory():
    '''Helper function for display_numbers().'''
    global num_displayed
    global selected_node_fortify_from
    global selected_node_fortify_to
    global fortify_in_progress
    global fortify_phase

    assert selected_node_fortify_to is not None
    assert not territory_occupied
    assert fortify_in_progress

    selected_node_fortify_to.add_troops(num_displayed)
    selected_node_fortify_from.subtract_troops(num_displayed)

    fortify_in_progress = False
    fortify_phase_over = True

def go_back_fortify():
    '''Helper function for display_numbers().'''
    global selected_node_fortify_from
    global selected_node_fortify_to
    global fortify_in_progress

    selected_node_fortify_from = None
    selected_node_fortify_to = None
    fortify_in_progress = False

def finish_attack_phase():
    global attack_phase_over
    assert not attack_phase_over
    attack_phase_over = True

def finish_fortify_phase():
    global fortify_phase_over
    assert not fortify_phase_over
    fortify_phase_over = True


def display_numbers(max_num, min_num=1, tick_action=None, cross_action=None, running_condition=None):
    ''' Displays a numerical window to choose the number of troops with the 
    two arrows. Numbers go from 1 to [max_num] and then, if increased, cycle 
    back to one; similarly, if user presses the "smaller" button when the
    number displayed is 1, the next number is [max_num].
    In case if the tick is clicked, does [tick_action]. In case if the cross 
    is clicked, does [cross_action]. At every frame, checks for 
    [running_condition] and returns  if it's False.

    Preconditions: [max_num] is int; [tick_action], [cross_action] are functions;
    [running_condition] is bool.'''
    global num_displayed


    number_bg_img = load_img("./Number_bg.png")
    right_img = load_img("./Right.png")
    right_active_img = load_img("./Right_active.png")
    left_img = load_img("./Left.png")
    left_active_img = load_img("./Left_active.png")
    cross_img = load_img("./Cross.png")
    cross_active_img = load_img("./Cross_active.png")

    # If player clicks outside of the table, one has to select a node again.
    button_textless_rect(0.125*display_width, display_height/9,
                    number_bg_img, number_bg_img)
    button_textless_rect(0.17*display_width, display_height/9,
                    right_img, right_active_img, action=num_displayed_increase)
    button_textless_rect(0.08*display_width, display_height/9,
                    left_img, left_active_img, action=num_displayed_decrease)
    button_textless_circular(0.22*display_width, display_height/9,
                    tick_img, tick_active_img, action=tick_action)
    button_textless_circular(0.03*display_width, display_height/9,
                    cross_img, cross_active_img, action=cross_action)
    
    if not running_condition:
        return

    # Check if the number went out of bounds.
    if num_displayed > max_num:
        num_displayed = min_num
    elif num_displayed < min_num:
        num_displayed = max_num
    # Display the number.
    numberText = pygame.font.SysFont("consolas", 30, bold=True)
    textSurf, textRect = text_objects(str(num_displayed), numberText, brown)
    textRect.center = (0.125*display_width, display_height/9)

    event_loop()

    gameDisplay.blit(textSurf, textRect)

    pygame.display.update()
    clock.tick(30)
    


def display_nodes_deploy(node_lst, curr_player):
    for node in node_lst:
        node_button_deploy(node, 20, width=5,
                           font_color=white, curr_player=curr_player)

def display_nodes_attack_from(node_lst, curr_player):
    for node in node_lst:
        node_button_attack_from(node, 20, width=5, font_color=white,
                                action=None, curr_player=curr_player)

def display_nodes_attack_to(node_lst, curr_player):
    for node in node_lst:
        node_button_attack_to(node, 20, width=5, font_color=white,
                              action=None, curr_player=curr_player)
                              
def display_nodes_fortify_from(node_lst, curr_player):
    for node in node_lst:
        node_button_fortify_from(node, 20, width=5, font_color=white,
                                action=None, curr_player=curr_player)


def display_nodes_fortify_to(node_lst, curr_player):
    for node in node_lst:
        node_button_fortify_to(node, 20, width=5, font_color=white,
                              action=None, curr_player=curr_player)


def print_console(text):
    consoleText = pygame.font.SysFont("consolas", 23, bold=True)
    textSurf, textRect = text_objects(text, consoleText, white)
    textRect.left = 10
    textRect.y = 865

    gameDisplay.blit(textSurf, textRect)


def print_phase(phase):
    phaseText = pygame.font.SysFont("trebuchet", 60, bold=False)
    textSurf, textRect = text_objects(phase, phaseText, white)
    textRect.center = ((0.5*display_width, display_height/36))

    gameDisplay.blit(textSurf, textRect)

def close_msg_display():
    global msg_displayed    
    assert msg_displayed
    msg_displayed = False

def game_quit():
    pygame.quit()
    quit()


locations = {
    "Afghanistan": (776, 370),
    "Alaska": (79, 210),
    "Alberta": (198, 255),
    "Argentina": (283, 725),
    "Brazil": (367, 609),
    "Central America": (215, 415),
    "China": (926, 420),
    "Congo": (591, 642),
    "East Africa": (673, 600),
    "Eastern Australia": (1011, 682),
    "Eastern United States": (290, 354),
    "Egypt": (603, 492),
    "Great Britain": (507, 303),
    "Greenland": (457, 176),
    "Iceland": (506, 217),
    "India": (822, 512),
    "Indonesia": (944, 602),
    "Irkutsk": (951, 286),
    "Japan": (1048, 364),
    "Kamchatka": (1115, 213),
    "Madagascar": (691, 723),
    "Middle East": (696, 500),
    "Mongolia": (980, 347),
    "New Guinea": (1074, 597),
    "North Africa": (521, 551),
    "Northern Europe": (593, 331),
    "Northwest Territory": (245, 210),
    "Ontario": (275, 260),
    "Peru": (249, 613),
    "Quebec": (370, 256),
    "Russia": (686, 282),
    "Scandinavia": (563, 234),
    "Siam": (912, 500),
    "Siberia": (880, 230),
    "South Africa": (582, 762),
    "Southern Europe": (589, 392),
    "Ural": (808, 268),
    "Venezuela": (251, 529),
    "Western Australia": (946, 706),
    "Western Europe": (505, 395),
    "Western United States": (200, 360),
    "Yakutsk": (993, 208)
}


def rescale_locations(w, h):
    '''Rescale for the current resolution (the original locations are for 1200X900).'''
    print(w, h)
    for loc in locations:
        coords = locations[loc]
        x = int(coords[0] * w/1200)
        y = int(coords[1] * h/900)
        locations[loc] = (x, y)


for node in all_nodes:
    node.set_location(locations[node.get_name()])


def darken_screen():
    dark = pygame.Surface(
        (bgImg.get_width(), bgImg.get_height()), flags=pygame.SRCALPHA)
    dark.fill((10, 10, 10, 0))
    for _ in range(3):
        bgImg.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


def lighten_screen():
    dark = pygame.Surface(
        (bgImg.get_width(), bgImg.get_height()), flags=pygame.SRCALPHA)
    dark.fill((10, 10, 10, 0))
    for _ in range(3):
        bgImg.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)



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

def blitz_attack(from_node, to_node):
    '''Conducts blitz attack between the two nodes and changes the results.
    Returns a boolean representing whether attack was successful or not.
    In case of a successful attack, moves all possible troops into a new
    territory; however, this is done purely for bookkeeping purposes when 
    letting the player choose how many troops to actually move in.

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
        from_node.set_troops(1)
        to_node.set_troops(blitz_res[0]-1)
        to_node.set_owner(from_node.get_owner())
        return True
    else:
        raise ValueError("Wrong results for blitz: (%i, %i)" % blitz_res)

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

def territories(color, continents):
    '''Returns a list of territories (Node list) owned by a player with a
    given color in the given continent list (can be empty).'''
    res = []
    for continent in continents:
        for node in continent.get_nodes():
            if node.get_owner() == color:
                res.append(node)
    return res

def calculate_territorial_bonus(curr_color, continents):
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
    return troops_gained, territories_owned, continents_owned
    
def calculate_troops_gained(curr_color, continents):
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
    return troops_gained, territories_owned, continents_owned

msg_displayed = False
def show_new_troops(curr_player):
    global msg_displayed

    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        print_phase("DEPLOY")
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        new_troops, num_terr, continents_owned = calculate_territorial_bonus(curr_player.get_color(), continents)

        msgText = pygame.font.SysFont("consolas", 30, bold=True)

        textSurf, textRect = text_objects("%s Player" % curr_player.get_color(), msgText, lavender)
        textRect.left = 0.27*display_width
        textRect.y = 0.275*display_height
        gameDisplay.blit(textSurf, textRect)

        # Display continental bonus.
        i = 0
        for continent in continents_owned:
            textSurf, textRect = text_objects("%i troops for %s," % (continent.get_bonus(), continent.get_name()), msgText, black)
            textRect.left = 0.27*display_width
            textRect.y = 0.35*display_height + i * 0.05*display_height
            gameDisplay.blit(textSurf, textRect)
            i += 1
        
        # Display bonus for number of territories owned.
        textSurf, textRect = text_objects("%i troops for %i territories." % (max(num_terr//3, 3), num_terr), msgText, black)
        textRect.left = 0.27*display_width
        textRect.y = 0.35*display_height + i * 0.05*display_height
        gameDisplay.blit(textSurf, textRect)

        i += 1    
        # Display total territorial bonus.
        textSurf, textRect = text_objects("Total %i troops." % new_troops, msgText, black)
        textRect.left = 0.27*display_width
        textRect.y = 0.35*display_height + i * 0.05*display_height
        gameDisplay.blit(textSurf, textRect)

        event_loop()

        button_textless_circular(0.72*display_width, 0.71*display_height,
                    tick_img, tick_active_img, action=close_msg_display)
        
        pygame.display.update()
        clock.tick(30)
        

def show_new_card(curr_player, card):
    global msg_displayed

    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        new_troops, num_terr, continents_owned = calculate_territorial_bonus(curr_player.get_color(), continents)

        msgText = pygame.font.SysFont("consolas", 30, bold=True)
        
        textSurf, textRect = text_objects("You got a card!", msgText, lavender)
        textRect.left = 0.27*display_width
        textRect.y = 0.275*display_height
        gameDisplay.blit(textSurf, textRect)

        # Display card.
        textSurf, textRect = text_objects(str(card), msgText, black)
        textRect.left = 0.27*display_width
        textRect.y = 0.35*display_height
        gameDisplay.blit(textSurf, textRect)

        event_loop()

        button_textless_circular(0.72*display_width, 0.71*display_height,
                    tick_img, tick_active_img, action=close_msg_display)
        
        pygame.display.update()
        clock.tick(30)

def use_cards():
    global best_hand
    assert best_hand is not None

    for card in best_hand:
        all_cards.insert(random.randint(0, len(all_cards)), card)
    curr_player.add_troops(curr_player.use_cards(best_hand))
    best_hand = None

def use_cards_forced():
    global best_hand
    global msg_displayed
    assert best_hand is not None
    assert msg_displayed

    for card in best_hand:
        all_cards.insert(random.randint(0, len(all_cards)), card)
    curr_player.add_troops(curr_player.use_cards(best_hand))
    best_hand = None
    msg_displayed = False

def display_cards():
    global msg_displayed
    global best_hand


    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        msgText = pygame.font.SysFont("consolas", 30, bold=True)

        textSurf, textRect = text_objects("%s Player: Your cards" % curr_player.get_color(), msgText, lavender)
        textRect.left = 0.27*display_width
        textRect.y = 0.275*display_height
        gameDisplay.blit(textSurf, textRect)

        i = 0
        for card in curr_player.get_cards():
            textSurf, textRect = text_objects(str(card), msgText, black)
            textRect.left = 0.27*display_width
            textRect.y = 0.35*display_height + i * 0.05*display_height
            gameDisplay.blit(textSurf, textRect)
            i += 1

        event_loop()

        button_textless_circular(0.72*display_width, 0.71*display_height,
                    tick_img, tick_active_img, action=close_msg_display)
        
        # If player can use cards, suggest:
        if len(curr_player.possible_combos()) > 0:
            best_hand = curr_player.decide()
            _, possible_bonus = curr_player.count_bonus(best_hand, False)
            button_textless_rect(0.50*display_width, 0.67*display_height, button_generic_img, button_generic_active_img, action=use_cards)

            buttonText = pygame.font.SysFont("consolas", 22, bold=True)
            textSurf1, textRect1 = text_objects("Use cards", buttonText, black)
            textSurf2, textRect2 = text_objects("Bonus: %i troops" % possible_bonus, buttonText, black)
            textRect1.center = (0.50*display_width, 0.65*display_height)
            textRect2.center = (0.50*display_width, 0.68*display_height)
            gameDisplay.blit(textSurf1, textRect1)
            gameDisplay.blit(textSurf2, textRect2)


        
        pygame.display.update()
        clock.tick(30)

def display_cards_no_use():
    '''Same as display_cards() except doesn't let player use them.'''
    global msg_displayed
    global best_hand


    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        msgText = pygame.font.SysFont("consolas", 30, bold=True)

        textSurf, textRect = text_objects("%s Player: Your cards" % curr_player.get_color(), msgText, lavender)
        textRect.left = 0.27*display_width
        textRect.y = 0.275*display_height
        gameDisplay.blit(textSurf, textRect)

        i = 0
        for card in curr_player.get_cards():
            textSurf, textRect = text_objects(str(card), msgText, black)
            textRect.left = 0.27*display_width
            textRect.y = 0.35*display_height + i * 0.05*display_height
            gameDisplay.blit(textSurf, textRect)
            i += 1

        event_loop()

        button_textless_circular(0.72*display_width, 0.71*display_height,
                    tick_img, tick_active_img, action=close_msg_display)


        
        pygame.display.update()
        clock.tick(30)

def display_cards_force_use():
    global msg_displayed
    global best_hand


    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        msgText = pygame.font.SysFont("consolas", 30, bold=True)

        textSurf, textRect = text_objects("%s Player: Your cards" % curr_player.get_color(), msgText, lavender)
        textRect.left = 0.27*display_width
        textRect.y = 0.275*display_height
        gameDisplay.blit(textSurf, textRect)

        i = 0
        for card in curr_player.get_cards():
            # Display up to 6 cards.
            if i < 6:
                textSurf, textRect = text_objects(str(card), msgText, black)
                textRect.left = 0.27*display_width
                textRect.y = 0.35*display_height + i * 0.05*display_height
                gameDisplay.blit(textSurf, textRect)
            elif i == 6:
                textSurf, textRect = text_objects("...", msgText, black)
                textRect.left = 0.27*display_width
                textRect.y = 0.35*display_height + i * 0.05*display_height
                gameDisplay.blit(textSurf, textRect)
            i += 1

        event_loop()
        
        # If player can use cards, suggest:
        if len(curr_player.possible_combos()) > 0:
            best_hand = curr_player.decide()
            _, possible_bonus = curr_player.count_bonus(best_hand, False)
            button_textless_circular(0.50*display_width, 0.67*display_height, button_generic_img, button_generic_active_img, action=use_cards_forced)

            buttonText = pygame.font.SysFont("consolas", 22, bold=True)
            textSurf1, textRect1 = text_objects("Use cards", buttonText, black)
            textSurf2, textRect2 = text_objects("Bonus: %i troops" % possible_bonus, buttonText, black)
            textRect1.center = (0.50*display_width, 0.65*display_height)
            textRect2.center = (0.50*display_width, 0.68*display_height)
            gameDisplay.blit(textSurf1, textRect1)
            gameDisplay.blit(textSurf2, textRect2)


        
        pygame.display.update()
        clock.tick(30)

def display_message(msg):
    global msg_displayed

    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        msgText = pygame.font.SysFont("consolas", 27, bold=True)

        textSurf, textRect = text_objects(msg, msgText, black)
        textRect.left = 0.27*display_width
        textRect.y = 0.35*display_height
        gameDisplay.blit(textSurf, textRect)

        event_loop()

        button_textless_circular(0.72*display_width, 0.71*display_height,
                    tick_img, tick_active_img, action=close_msg_display)
        
        pygame.display.update()
        clock.tick(30)

def display_message_2(msg):
    '''Same as display_message(), except the tick button is slightly displaced
    so that player can read it after having seen a previous message. Meant 
    to be used right after/right before display_message().'''
    global msg_displayed

    msg_displayed = True
    while msg_displayed:
        gameDisplay.blit(bgImg, (0,0))
        
        boxRect = message_img.get_rect()
        boxRect.center = (0.5*display_width, 0.5*display_height)
        gameDisplay.blit(message_img, boxRect)

        msgText = pygame.font.SysFont("consolas", 27, bold=True)

        textSurf, textRect = text_objects(msg, msgText, black)
        textRect.left = 0.27*display_width
        textRect.y = 0.35*display_height
        gameDisplay.blit(textSurf, textRect)

        event_loop()

        button_textless_circular(0.28*display_width, 0.71*display_height,
                    tick_img, tick_active_img, action=close_msg_display)
        
        pygame.display.update()
        clock.tick(30)


def find_defeated(player_lst):
    '''Returns a list of players that have been defeated.

    Preconditions: no duplicates in [player_lst].'''
    res = []
    for i in range(len(player_lst)):
        player = player_lst[i]
        if len(territories(player.get_color(), continents)) == 0:
            res.append(player)
    return res
       

num_displayed = None
selected_node_deploy = None
# Represents if player is currently choosing the number of troops to be deployed.
deploy_in_progress = False
best_hand = None


def deploy_phase(curr_player):
    global selected_node_deploy
    global deploy_in_progress
    global num_displayed

    deploy_in_progress = False

    curr_color = curr_player.get_color()
    troops_gained, _, _ = calculate_troops_gained(curr_color, continents)
    curr_player.add_troops(troops_gained)

    while len(curr_player.get_cards()) >= 5:
        display_cards_force_use()

    while curr_player.get_troops() > 0:

        # Selecting node to put troops to.
        while selected_node_deploy is None:

            gameDisplay.blit(bgImg, (0, 0))
            print_phase("DEPLOY")

            # Cards button.
            button_textless_circular(0.95*display_width, 0.92*display_height, cards_img, cards_active_img, action=display_cards)

            event_loop()

            if curr_player.get_troops() == 1:
                print_console(
                    "%s Player: Choose where to deploy troops. You have %i more troop." % (curr_color, curr_player.get_troops()))
            else:
                print_console(
                    "%s Player: Choose where to deploy troops. You have %i more troops." % (curr_color, curr_player.get_troops()))
            display_nodes_deploy(all_nodes, curr_player)

            pygame.display.update()
            clock.tick(30)

        # Selecting the number of troops to put.
        darken_screen()
        num_displayed = curr_player.get_troops()
        while deploy_in_progress:

            gameDisplay.blit(bgImg, (0, 0))
            print_console("%s Player: Choose how many troops to deploy in %s." % (
                curr_color, selected_node_deploy.get_name()))
            print_phase("DEPLOY")



            event_loop()

            display_nodes_deploy(all_nodes, curr_player)
            display_numbers(max_num=curr_player.get_troops(), min_num=1, tick_action=place_troops_deploy, cross_action=go_back_deploy, running_condition=deploy_in_progress)

            pygame.display.update()
            pygame.event.get()
            clock.tick(30)
        lighten_screen()


blitz_res = None
selected_node_attack_from = None
selected_node_attack_to = None
territory_occupied = None
attack_phase_over = None


def attack_phase(curr_player):
    global blitz_res
    global selected_node_attack_from
    global selected_node_attack_to
    global territory_occupied
    global attack_phase_over
    global num_displayed

    blitz_res = None
    selected_node_attack_from = None
    selected_node_attack_to = None
    territory_occupied = False
    attack_phase_over = False
    received_card = False

    curr_color = curr_player.get_color()
    skip_img = load_img("./Skip.png")
    skip_active_img = load_img("./Skip_active.png")

    while not attack_phase_over:


        # Selecting node to attack from.
        while selected_node_attack_from is None:
            
            gameDisplay.blit(bgImg, (0, 0))
            print_phase("ATTACK")
            
            # Finish phase.
            button_textless_rect(0.825*display_width, display_height/10, skip_img, skip_active_img, action=finish_attack_phase)
            if attack_phase_over:
                break

            # Cards button.
            button_textless_circular(0.95*display_width, 0.92*display_height, cards_img, cards_active_img, action=display_cards_no_use)

            event_loop()

            print_console("%s Player: pick a territory to attack from. The territory should have at least 1 troop." %
                          curr_color)
            display_nodes_attack_from(all_nodes, curr_player)

            pygame.display.update()
            clock.tick(30)

        # Selecting a node to attack.
        while selected_node_attack_to is None:
            # Node to attack from was unselected. Return to the first while-loop.
            if selected_node_attack_from is None:
                break

            gameDisplay.blit(bgImg, (0, 0))
            print_phase("ATTACK")
            display_nodes_attack_to(all_nodes, curr_player)
            print_console("%s Player: Choose an enemy territory to attack." % curr_color)

            # Finish phase.
            button_textless_rect(0.825*display_width, display_height/10, skip_img, skip_active_img, action=finish_attack_phase)
            if attack_phase_over:
                break

            # Cards button.
            button_textless_circular(0.95*display_width, 0.92*display_height, cards_img, cards_active_img, action=display_cards_no_use)

            event_loop()

            # Attack successful. Let player choose how many troops to move.
            if blitz_res and selected_node_attack_to.get_troops() > 3:
                # Set num_displayed to 1 to show the max possible number.
                num_displayed = 1
                darken_screen()
                while not territory_occupied:

                    gameDisplay.blit(bgImg, (0, 0))
                    print_phase("ATTACK")
                    display_nodes_attack_to(all_nodes, curr_player)

                    event_loop()
                    
                    from_node = selected_node_attack_from
                    to_node = selected_node_attack_to
                    
                    print_console("%s Player: Attack successful! Move up to %i troops in %s." % (curr_color, to_node.get_troops(), to_node.get_name()))
                    # Currently: 1 troop in [from_node] and the remaining troops in [to_node]. Thus, can move up to [to_node.get_troops()] troops
                    # into [to_node].
                    display_numbers(max_num=to_node.get_troops(), min_num=3, tick_action=occupy_territory, cross_action=None, running_condition=not territory_occupied)

                    pygame.display.update()
                    clock.tick(30)
                lighten_screen()

            # Give a card.
            if blitz_res:
                received_card = True

                # Check if any player has been defeated.
                defeated = find_defeated(order)
                for defeated_player in defeated:
                    defeated_cards = defeated_player.get_cards()
                    display_message("%s Player has been defeated!" % defeated_player.get_color())
                    display_message_2("You got %i cards from %s Player!" % (len(defeated_cards), defeated_player.get_color()))
                    # Give the defeated player's cards to the conqueror.
                    for card in defeated_player.get_cards():
                        curr_player.give_card(card)
                    order.remove(defeated_player)   
                
                # Check for victory.
                if len(defeated) > 0:
                    if len(order) == 1:
                        display_message("%s Player won! CONGRATULATIONS!" % order[0].get_color())
                        game_quit()

            # Reset global variables to let player conduct another attack.
            if blitz_res is not None:
                assert selected_node_attack_from is not None
                assert selected_node_attack_to is not None
                blitz_res = None
                selected_node_attack_from = None
                selected_node_attack_to = None
                territory_occupied = False

            pygame.display.update()
            clock.tick(30)
    
    # If player conquered anything, one receives a card.
    if received_card:
        card = all_cards.pop(0)
        curr_player.give_card(card)
        show_new_card(curr_player, card)


selected_node_fortify_from = None
selected_node_fortify_to = None
fortify_in_progress = None
fortify_phase_over = None


def fortify_phase(curr_player):
    global selected_node_fortify_from
    global selected_node_fortify_to
    global fortify_in_progress
    global fortify_phase_over
    global num_displayed

    selected_node_fortify_from = None
    selected_node_fortify_to = None
    fortify_in_progress = False
    fortify_phase_over = False

    curr_color = curr_player.get_color()
    skip_img = load_img("./Skip.png")
    skip_active_img = load_img("./Skip_active.png")

    while not fortify_phase_over:

        # Selecting node to attack from.
        while selected_node_fortify_from is None:
            
            gameDisplay.blit(bgImg, (0, 0))
            print_phase("FORTIFY")
            
            # Finish phase button.
            button_textless_circular(0.925*display_width, display_height/10, skip_img, skip_active_img, action=finish_fortify_phase)
            if fortify_phase_over:
                break

            # Cards button.
            button_textless_circular(0.95*display_width, 0.92*display_height, cards_img, cards_active_img, action=display_cards_no_use)

            event_loop()

            print_console("%s Player: pick a territory with at least 1 troop to take troops from." % curr_color)
            display_nodes_fortify_from(all_nodes, curr_player)

            pygame.display.update()
            clock.tick(30)

        # Selecting a node to attack.
        while selected_node_fortify_to is None:

            gameDisplay.blit(bgImg, (0, 0))
            print_phase("FORTIFY")
            display_nodes_fortify_to(all_nodes, curr_player)
            # Node to fortify from was unselected. Return to the first while-loop.
            if selected_node_fortify_from is None:
                break
            print_console("%s Player: Choose a territory connected to %s to fortify." % (curr_color, selected_node_fortify_from.get_name()))

            # Finish phase.
            button_textless_rect(0.925*display_width, display_height/10, skip_img, skip_active_img, action=finish_fortify_phase)
            if fortify_phase_over:
                break

            # Cards button.
            button_textless_circular(0.95*display_width, 0.92*display_height, cards_img, cards_active_img, action=display_cards_no_use)

            event_loop()


            # Let player choose how many troops to move.
            if selected_node_fortify_from is not None and selected_node_fortify_to is not None:
                fortify_in_progress = True
                # Display the max number that could be changed.
                num_displayed = selected_node_fortify_from.get_troops()-1
                darken_screen()
                while fortify_in_progress:

                    gameDisplay.blit(bgImg, (0, 0))
                    print_phase("FORTIFY")
                    display_nodes_fortify_to(all_nodes, curr_player)

                    event_loop()
                    
                    from_node = selected_node_fortify_from
                    to_node = selected_node_fortify_to
                    
                    print_console("%s Player: Move up to %i troops from %s to %s." % (curr_color, from_node.get_troops()-1, from_node.get_name(), to_node.get_name()))
                    display_numbers(max_num=from_node.get_troops()-1, min_num=1, tick_action=fortify_territory, cross_action=go_back_fortify, running_condition=fortify_in_progress)

                    pygame.display.update()
                    clock.tick(30)
                lighten_screen()

            pygame.display.update()
            clock.tick(30)
        
        if selected_node_fortify_to is not None:
            assert selected_node_fortify_from is not None

            # Reset global variables.
            selected_node_fortify_from = None
            selected_node_fortify_to = None
            fortify_in_progress = False

            # Finish Fortify phase.
            fortify_phase_over = True


claim_territories(order, all_nodes.copy())
initialize_troops(order, all_nodes.copy())

# Ensure there are no unowned nodes.
for continent in continents:
    for node in continent.get_nodes():
        if node.get_owner() == Color.NONE:
            raise ValueError('Unowned node!' + str(node))

while True:
    # Pick the next player.
    curr_player = order.pop(0)
    order.append(curr_player)
    # Check continent ownership.
    set_continent_owners(continents)
    # Give new troops.
    show_new_troops(curr_player)
    # Deploy - Attack - Fortify.
    deploy_phase(curr_player)
    attack_phase(curr_player)
    fortify_phase(curr_player)

