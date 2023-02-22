import argparse
import time

class Puzzle:
    def __init__(self):
        self.elements = []
        self.goal_state = ['1', '2', '3', '4', '5', '6', '7', '8', '_']
        pass

    def print_state(self, state):
        if len(state) != 9:
            return
        for i in range(0, 9, 3):
            print(state[i] + " " + state[i + 1] + " " + state[i + 2])

    def get_possible_transitions(self, curr_state):
        poss_trans = []
        current_index = curr_state.index('_')

        if current_index > 2:
             poss_trans.append("D")
        if current_index != 2 and current_index != 5 and current_index != 8:
            poss_trans.append("L")
        if current_index != 0 and current_index != 3 and current_index != 6:
            poss_trans.append("R")
        if current_index < 6:
            poss_trans.append("U")

        return poss_trans

    def get_next_state_given_transition(self, curr_state, transition):
        if transition not in self.get_possible_transitions(curr_state):
            return

        current_index = curr_state.index('_')

        modified_state = curr_state.copy()
        del modified_state[current_index]

        move_index = -1
        move_char = ''

        if transition == "L":
            move_index = current_index + 1
            move_char = curr_state[move_index]
            modified_state.insert(move_index, '_')

        elif transition == "R":
            move_index = current_index - 1
            move_char = curr_state[move_index]
            modified_state.insert(move_index, '_')

        elif transition == "U":
            move_index = current_index + 3
            move_char = curr_state[move_index]
            modified_state.insert(move_index, '_')

        elif transition == "D":
            move_index = current_index - 3
            move_char = curr_state[move_index]
            modified_state.insert(move_index, '_')

        else:
            return []

        modified_state.remove(move_char)
        modified_state.insert(current_index, move_char)

        return modified_state

    def stringify_state(self, state):
        return "".join(map(str,state))

    def solvable(self, state):
        state_copied = state.copy()

        state_copied.remove('_')

        inversions = 0

        for idx, c in enumerate(state_copied):
            int1 = int(c)

            for idy in range(idx + 1, len(state_copied)):
                int2 = int(state_copied[idy])
                if int1 > int2:
                    inversions += 1

        print("Found " + str(inversions) + " inversions")
        if inversions % 2 == 0:
            return True
        else:
            return False


    def bfs(self):

        node = self.elements

        visited = []
        queue = []

        paths = {}

        visited.append(node)
        queue.append(node)
        m = None

        while m != self.goal_state:
            m = queue.pop(0)

            for trans in self.get_possible_transitions(m):

                next_state = self.get_next_state_given_transition(m, trans)

                if self.stringify_state(m) in paths:
                    paths[self.stringify_state(next_state)] = paths[self.stringify_state(m)] + trans
                else:
                    paths[self.stringify_state(next_state)] = trans

                # We know the parent is m, it took the trans path to get to the state next_state

                if next_state not in visited:
                    visited.append(next_state)
                    queue.append(next_state)

        print("Correct path: " + paths[self.stringify_state(self.goal_state)])
        print("Nodes generated: " + str(len(visited)))

    def iddfs(self, max_depth):

        total_visited = []

        for depth_limit in range(max_depth+1):
            stack = [(puz.elements, 0)]
            visited = []
            paths = {}

            while stack:
                node, depth = stack.pop()
                if node == puz.goal_state:
                    print("Correct path: " + paths[self.stringify_state(self.goal_state)])
                    print("Nodes generated: " + str(len(total_visited)))
                    return "Solution found!"
                if depth < depth_limit:
                    visited.append(node)
                    total_visited.append(node)
                    children = self.get_possible_transitions(node)
                    for transition in children:

                        next_state = self.get_next_state_given_transition(node, transition)

                        if self.stringify_state(node) in paths:
                            paths[self.stringify_state(next_state)] = paths[self.stringify_state(node)] + transition
                        else:
                            paths[self.stringify_state(next_state)] = transition

                        if next_state not in visited:
                            stack.append((next_state, depth+1))

        # If the goal state is not found, return failure
        return None

    def get_misplaced_tiles(self, current_state):
        misplaced_tiles = 0

        for i in range(len(current_state)):
            if current_state[i] != self.goal_state[i]:
                misplaced_tiles += 1

        return misplaced_tiles

    def a_star(self, heuristic):
        initial_state = puz.elements
        paths = {}
        # Create an open list to store the nodes to be expanded
        queue = []
        # Create a closed list to store the visited nodes
        visited = set()
        # Add the initial state to the open list
        queue.append((initial_state, 0, 0))
        # While the open list is not empty, continue searching
        while queue:
            # Sort the open list by the sum of the current depth and the heuristic
            queue.sort(key=lambda x: x[1]+x[2])
            # Pop the first node from the open list
            node, depth, misplaced_tiles = queue.pop(0)

            # If the current node is the goal state, return the solution path
            if node == self.goal_state:
                print("Correct path: " + paths[self.stringify_state(self.goal_state)])
                print("Nodes generated: " + str(len(visited)))
                return "Solution found!"

            # Add the current node to the closed list
            visited.add(self.stringify_state(node))
            # Get the child nodes of the current node
            possible_transitions = self.get_possible_transitions(node)

            # Add the child nodes to the open list if they have not been visited before
            for transition in possible_transitions:

                next_state = self.get_next_state_given_transition(node, transition)

                if self.stringify_state(next_state) not in visited:

                    if self.stringify_state(node) in paths:
                        paths[self.stringify_state(next_state)] = paths[self.stringify_state(node)] + transition
                    else:
                        paths[self.stringify_state(next_state)] = transition

                    # Calculate the depth and misplaced tiles heuristic of the child node
                    child_depth = depth + 1
                    heuristic_val = 0
                    if heuristic == "misplaced":
                        heuristic_val = self.get_misplaced_tiles(next_state, self.goal_state)
                    elif heuristic == "manhattan":
                        heuristic_val = self.calculate_manhattan_heuristic(next_state)
                    # Add the child node to the open list
                    queue.append((next_state, child_depth, heuristic_val))
        # If the goal state is not found, return failure
        return None

    def calculate_manhattan_heuristic(self, state):
        val = 0

        for state_char in state:
            x_current, y_current = self.get_char_location_in_state(state_char, state)
            x_goal, y_goal = self.get_char_location_in_state(state_char, self.goal_state)
            horizontal_distance = abs(x_current - x_goal)
            vertical_distance = abs(y_current - y_goal)
            val += horizontal_distance + vertical_distance

        return val

    def get_char_location_in_state(self, char, state):
        index = state.index(char)
        return index % 3, round(index / 3)


def read_file(name, puz):
    with open(name, "r") as f:
        for l in f:
            elements = l.split(" ")
            for element in elements:
                puz.elements.append(element.strip())



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'The 8-puzzle',
        description = 'Solves an 8-puzzle using various algorithms')

    parser.add_argument('--fPath')
    parser.add_argument('--alg')

    args = parser.parse_args()

    puz = Puzzle()

    read_file(args.fPath, puz)

    x, y = puz.get_char_location_in_state('5', puz.elements)
    print("X: " + str(x) + " Y: " + str(y))

    isSolvable = puz.solvable(puz.elements)

    if isSolvable:
        solveStart = time.time()

        if args.alg == "bfs":
            puz.bfs()
        elif args.alg == "IDS":
            result = None

            puz.iddfs(1000)
        elif args.alg == "h1":
            result = puz.a_star("misplaced")
            print(result)
        elif args.alg == "h2":
            result = puz.a_star("manhattan")

        solveEnd = time.time() - solveStart
        print("BFS Time: " + str(solveEnd))
    else:
        print("Puzzle isn't solvable")




