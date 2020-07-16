from room import Room
from player import Player
from world import World

import random
from ast import literal_eval


class Graph:

    """Represent a graph as a dictionary of vertices mapping labels to edges."""

    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex_id):
        """
        Add a vertex to the graph.
        """
        self.vertices[vertex_id] = {}

    def add_edge(self, v1, v2, direction):
        """
        Add a directed edge to the graph.
        """
        if v1 in self.vertices and v2 in self.vertices:
            self.vertices[v1][direction] = v2

    def get_neighbors(self, vertex_id):
        """
        Get all neighbors (edges) of a vertex.
        """
        return self.vertices[vertex_id]


class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None

    def size(self):
        return len(self.queue)


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        if self.size() > 0:
            return self.stack.pop()
        else:
            return None

    def size(self):
        return len(self.stack)


# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']


# MY CODE
g = Graph()

# the graph will be populated by first traversing all available rooms


def populate_graph():
    s = Stack()
    s.push(world.starting_room)

    visited = set()

    while s.size() > 0:
        room = s.pop()
        room_id = room.id

        if room_id not in g.vertices:
            g.add_vertex(room_id)

        # find the exits available in a room
        exits = room.get_exits()
        for direction in exits:
            # find the next rooms and add them to the graph
            next_rooms = room.get_room_in_direction(direction)
            next_rooms_id = next_rooms.id

            if next_rooms_id not in g.vertices:
                g.add_vertex(next_rooms_id)

              # connect rooms as edges with direction
            g.add_edge(room_id, next_rooms_id, direction)

            # add the room to the stack if we haven't been there yet
            if next_rooms_id not in visited:
                s.push(next_rooms)

        visited.add(room_id)


def find_next_path(room_id, visited, g=g):
    v = set()
    v.add(room_id)

    q = Queue()
    q.enqueue({room_id: []})

    while q.size() > 0:
        room_info = q.dequeue()

        # Room is the current room, moves is how many moves it took to get here
        room = list(room_info.keys())[0]
        moves = room_info[room]

        # Grab neighbors of room
        neighbors = g.get_neighbors(room)

        neighbors_keys = list(neighbors.keys())

        # If we reach a dead end we traverse back

        if len(neighbors_keys) == 1 and neighbors[neighbors_keys[0]] not in visited:
            dead_end = list(moves) + [neighbors_keys[0]]

            return dead_end

        else:
            # We keep going until we hit a dead end
            for direction in neighbors:
                next_room = neighbors[direction]
                new_moves = moves + [direction]

                if next_room not in visited:
                    return new_moves

                if next_room not in v:
                    q.enqueue({next_room: new_moves})
                    v.add(next_room)


populate_graph()

traversal_path = []

visited = set()
visited.add(world.starting_room.id)

current_room_id = world.starting_room.id
total_rooms = len(g.vertices)

while len(visited) < total_rooms:
    moves = find_next_path(current_room_id, visited)
    # Traverse the returned list of moves
    for direction in moves:
        player.travel(direction)
        traversal_path.append(direction)
        visited.add(player.current_room.id)
    # update current room
    current_room_id = player.current_room.id

# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(
        f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")


#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
