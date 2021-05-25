from node import Node, find_node


def path_exists(node1, node2):
    '''Finds if there is a path between the two nodes that only includes 
    nodes that share the same owner. Uses Dijkstra's shortes path algorithm
    that terminates as soon as any path from [node1] to [node2] is found, since
    we are only interested in whether there is a path or not. All edges are 
    assumed to have a distance of 1.
    Returns a boolean.

    Precondition: [node1] and [node2] both belong to the same player.

    Credits to Prof. David Gries and his course CS 2110 at Cornell University.'''
    distances_settled = {}
    distances_frontier = {}
    # Initialize the loop.
    settled = []
    frontier = [node1]
    distances_frontier[node1] = 0

    while len(frontier) > 0:
        # Remove f from F with shortest distance to f and add it to S.
        min_distance = min(distances_frontier.values())
        for node in distances_frontier:
            if distances_frontier[node] == min_distance:
                min_node = node
                frontier.remove(node)
                settled.append(min_node)
                # Remove f from D_F and add it to D_S.
                distances_settled[node] = distances_frontier.pop(node)
                break

        for node in min_node.get_neighbors():
            # Check if the node belongs to the same player.
            if node.get_owner() != min_node.get_owner():
                continue
            # Check if the node we're looking for is found.
            if node == node2:
                return True
            if (node not in settled) and (node not in frontier):
                distances_frontier[node] = distances_settled[min_node] + 1
                frontier.append(node)
            elif node in settled:
                if distances_settled[min_node]+1 < distances_settled[node]:
                    distances_settled[node] = distances_settled[min_node] + 1
            else:
                if distances_settled[min_node]+1 < distances_frontier[node]:
                    distances_frontier[node] = distances_settled[min_node] + 1

    # The node needed wasn't found.
    return False
