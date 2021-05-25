from color import Color


class Node():

    def __init__(self, id, name, owner=Color.NONE, neighbors=[], numtroops=-1, location=(0, 0)):
        ''' Initiates a Node object with given [id] (int), [name] of the region
        (string), [owner] (Color object), [neighbors] (list of Node 
        objects.), and [numtroops] (int).'''
        self.id = id
        self.name = name
        self.owner = owner
        self.neighbors = neighbors
        self.numtroops = numtroops
        self.location = location

    def __repr__(self):
        return "Node" + str(self.id) + ": " + str(self.owner) + " " + \
            str(self.numtroops) + " troops"

    def __str__(self):
        return str(self.id) + ": " + self.name

    # Override comparison function for class.
    def __gt__(self, node):
        return self.id > node.id

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_owner(self):
        return self.owner

    def get_neighbors(self):
        return self.neighbors

    def get_troops(self):
        return self.numtroops

    def get_location(self):
        return self.location

    def get_colors(self):
        colors = {
            "RED": [(200, 0, 0), (220, 0, 0), (255, 0, 0)],
            "YELLOW": [(200, 200, 0), (220, 220, 0), (255, 255, 0)],
            "GREEN": [(0, 200, 0), (0, 220, 0), (0, 255, 0)],
            "CYAN": [(0, 200, 200), (0, 220, 220), (0, 255, 255)],
            "BLUE": [(0, 0, 200), (0, 0, 220), (0, 0, 255)],
            "PURPLE": [(200, 0, 200), (220, 0, 220), (255, 0, 255)],
        }
        return colors[self.owner.name]

    def set_owner(self, owner):
        self.owner = owner

    def set_troops(self, numtroops):
        self.numtroops = numtroops

    def set_location(self, location):
        self.location = location

    def add_troops(self, numtroops):
        self.numtroops += numtroops

    def subtract_troops(self, numtroops):
        self.numtroops -= numtroops

    def add_edge(self, node):
        self.neighbors = add_node(node, self.neighbors)
        node.neighbors = add_node(self, node.neighbors)

    def attack_options(self):
        '''Returns a list of nodes that could be attacked from the given node.'''
        res = []
        for node in self.neighbors:
            if node.owner != self.owner:
                res.append(node)
        return res


def find_node(id, node_lst):
    '''
    Uses binary search to look for a Node object with given [id] (int)
        in the [node_lst]
    Returns a Node object, or None if not found.

    Preconditions: [id] is a positive integer; [node_lst] is a list of Node 
    objects that are sorted by id in an increasing order. [node_lst] can be 
    empty.
    '''
    if len(node_lst) == 0:
        return None

    i = len(node_lst) // 2
    curr_node = node_lst[i]

    if curr_node.get_id() < id:
        return find_node(id, node_lst[i+1:])
    elif curr_node.get_id() > id:
        return find_node(id, node_lst[:i])
    return curr_node


def add_node(node, node_lst):
    '''
    Uses binary search to add a given Node object to the given list of Node
        objects.
    Returns a new list of Node objects. If [node_lst] already has the given 
    Node, returns [node_lst].

    Preconditions: [node] is a Node object; [node_lst] is a list of Node objects
        that are sorted by id in an increasing order. [node_lst] can be empty.
    '''
    if len(node_lst) == 0:
        return [node]

    i = len(node_lst) // 2

    if node_lst[i] < node:
        return node_lst[:i+1] + add_node(node, node_lst[i+1:])
    elif node_lst[i] > node:
        return add_node(node, node_lst[:i]) + node_lst[i:]
    return node_lst


def find_territory(territory, node_lst):
    '''
    Like above, finds node with a give [territory] (str) in a given [node_lst].

    Preconditions: 
    [node_lst] sorted in alphabetical order by territory name. No duplicates.
    '''
    if len(node_lst) == 0:
        return None

    i = len(node_lst) // 2

    if node_lst[i].get_name() < territory:
        return find_territory(territory, node_lst[i+1:])
    elif node_lst[i].get_name() > territory:
        return find_territory(territory, node_lst[:i])
    return node_lst[i]
