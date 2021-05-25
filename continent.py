from enum import Enum
import random

from node import Node, find_node


class Continent():

    def __init__(self, name, nodes=[], bonus=None, owner=None):
        self.name = name
        self.nodes = nodes
        self.bonus = bonus
        self.owner = owner

    def get_name(self):
        return self.name

    def get_nodes(self):
        return self.nodes

    def get_bonus(self):
        return self.bonus

    def get_owner(self):
        return self.owner

    def monopolize(self, owner):
        self.owner = owner

    def demonopolize(self):
        self.owner = None

    def find(self, nodeid):
        return find_node(nodeid, self.nodes)

    def change_owner(self, nodeid, new_owner):
        node = self.find(nodeid)
        node.set_owner(new_owner)


# Initialize continents.

# North America.
NA1 = Node(11, "Alaska")
NA2 = Node(12, "Northwest Territory")
NA3 = Node(13, "Greenland")
NA4 = Node(14, "Alberta")
NA5 = Node(15, "Ontario")
NA6 = Node(16, "Quebec")
NA7 = Node(17, "Western United States")
NA8 = Node(18, "Eastern United States")
NA9 = Node(19, "Central America")

NA1.add_edge(NA2)
NA1.add_edge(NA4)
NA2.add_edge(NA3)
NA2.add_edge(NA4)
NA2.add_edge(NA5)
NA3.add_edge(NA5)
NA3.add_edge(NA6)
NA4.add_edge(NA5)
NA4.add_edge(NA7)
NA5.add_edge(NA6)
NA5.add_edge(NA7)
NA5.add_edge(NA8)
NA6.add_edge(NA8)
NA7.add_edge(NA8)
NA7.add_edge(NA9)
NA8.add_edge(NA9)

North_America = Continent(
    "North America", [NA1, NA2, NA3, NA4, NA5, NA6, NA7, NA8, NA9], 5, None)

# Europe.
E1 = Node(21, "Iceland")
E2 = Node(22, "Great Britain")
E3 = Node(23, "Scandinavia")
E4 = Node(24, "Western Europe")
E5 = Node(25, "Northern Europe")
E6 = Node(26, "Russia")
E7 = Node(27, "Southern Europe")

E1.add_edge(E2)
E1.add_edge(E3)
E2.add_edge(E3)
E2.add_edge(E4)
E2.add_edge(E5)
E3.add_edge(E5)
E3.add_edge(E6)
E4.add_edge(E5)
E4.add_edge(E7)
E5.add_edge(E6)
E5.add_edge(E7)
E6.add_edge(E7)

Europe = Continent("Europe", [E1, E2, E3, E4, E5, E6, E7], 5, None)

# Africa.

AF1 = Node(31, "North Africa")
AF2 = Node(32, "Egypt")
AF3 = Node(33, "Congo")
AF4 = Node(34, "East Africa")
AF5 = Node(35, "South Africa")
AF6 = Node(36, "Madagascar")

AF1.add_edge(AF2)
AF1.add_edge(AF3)
AF1.add_edge(AF4)
AF2.add_edge(AF4)
AF3.add_edge(AF4)
AF3.add_edge(AF5)
AF4.add_edge(AF5)
AF4.add_edge(AF6)
AF5.add_edge(AF6)

Africa = Continent("Africa", [AF1, AF2, AF3, AF4, AF5, AF6], 3, None)

# South America.

SA1 = Node(41, "Venezuela")
SA2 = Node(42, "Peru")
SA3 = Node(43, "Brazil")
SA4 = Node(44, "Argentina")

SA1.add_edge(SA2)
SA1.add_edge(SA3)
SA2.add_edge(SA3)
SA2.add_edge(SA4)
SA3.add_edge(SA4)

South_America = Continent("South America", [SA1, SA2, SA3, SA4], 2, None)

# Australia.

AU1 = Node(51, "Indonesia")
AU2 = Node(52, "New Guinea")
AU3 = Node(53, "Western Australia")
AU4 = Node(54, "Eastern Australia")

AU1.add_edge(AU2)
AU1.add_edge(AU3)
AU2.add_edge(AU3)
AU2.add_edge(AU4)
AU3.add_edge(AU4)

Australia = Continent("Australia", [AU1, AU2, AU3, AU4], 2, None)

# Asia.

AS1 = Node(61, "Ural")
AS2 = Node(62, "Siberia")
AS3 = Node(63, "Yakutsk")
AS4 = Node(64, "Kamchatka")
AS5 = Node(65, "Irkutsk")
AS6 = Node(66, "Mongolia")
AS7 = Node(67, "Japan")
AS8 = Node(68, "Afghanistan")
AS9 = Node(69, "China")
AS10 = Node(70, "Middle East")
AS11 = Node(71, "India")
AS12 = Node(72, "Siam")

AS1.add_edge(AS2)
AS1.add_edge(AS8)
AS1.add_edge(AS9)
AS2.add_edge(AS3)
AS2.add_edge(AS5)
AS2.add_edge(AS6)
AS2.add_edge(AS9)
AS3.add_edge(AS4)
AS3.add_edge(AS5)
AS4.add_edge(AS5)
AS4.add_edge(AS6)
AS4.add_edge(AS7)
AS5.add_edge(AS6)
AS6.add_edge(AS7)
AS6.add_edge(AS9)
AS8.add_edge(AS9)
AS8.add_edge(AS10)
AS8.add_edge(AS11)
AS9.add_edge(AS11)
AS9.add_edge(AS12)
AS10.add_edge(AS11)
AS11.add_edge(AS12)

# Inter-continental connections.
NA1.add_edge(AS4)
NA3.add_edge(E1)
NA9.add_edge(SA1)
E4.add_edge(AF1)
E6.add_edge(AS1)
E6.add_edge(AS8)
E6.add_edge(AS10)
E7.add_edge(AF1)
E7.add_edge(AF2)
E7.add_edge(AS10)
AF1.add_edge(SA3)
AF2.add_edge(AS10)
AF4.add_edge(AS10)
AU1.add_edge(AS12)


Asia = Continent(
    "Asia", [AS1, AS2, AS3, AS4, AS5, AS6, AS7, AS8, AS9, AS10, AS11, AS12], 7,
    None)

# Put all in a single list.
continents = [North_America, Europe, Africa, South_America, Australia,
              Asia]

all_nodes = []
for continent in continents:
    for node in continent.get_nodes():
        all_nodes.append(node)
all_nodes_sorted = all_nodes.copy()
random.shuffle(all_nodes)
