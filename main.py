import argparse
import os
import time
import threading
from os import path

class Puzzle:
    def __init__(self, name=None):
        self.elements = []
        self.goal_state = ['1', '2', '3', '4', '5', '6', '7', '8', '_']
        self.start_time = None
        self.paths = {}
        self.total_visited = []
        self.visited = []
        self.time_limit = 15 * 60

        if name is not None:
            self.read_file(name)

    def clear(self):
        self.start_time = None
        self.paths = {}
        self.total_visited = []
        self.visited = []

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

        #print("Found " + str(inversions) + " inversions")
        if inversions % 2 == 0:
            return True
        else:
            return False


    def bfs(self):

        node = self.elements

        queue = []

        self.visited.append(node)
        queue.append(node)
        m = None

        while m != self.goal_state and (time.time() - self.start_time) < self.time_limit:
            m = queue.pop(0)

            for trans in self.get_possible_transitions(m):

                next_state = self.get_next_state_given_transition(m, trans)

                if self.stringify_state(m) in self.paths:
                    self.paths[self.stringify_state(next_state)] = self.paths[self.stringify_state(m)] + trans
                else:
                    self.paths[self.stringify_state(next_state)] = trans

                # We know the parent is m, it took the trans path to get to the state next_state

                if next_state not in self.visited:
                    self.visited.append(next_state)
                    queue.append(next_state)

        if m == self.goal_state:
            return self.paths[self.stringify_state(self.goal_state)], len(self.visited)
        else:
            return None

    def iddfs(self):

        max_depth = 1

        while (time.time() - self.start_time) < self.time_limit:

            stack = [(self.elements, 0)]
            self.visited = []

            while stack and (time.time() - self.start_time) < self.time_limit:
                node, depth = stack.pop()
                if node == self.goal_state:
                    return self.paths[self.stringify_state(self.goal_state)], len(self.total_visited)
                if depth < max_depth:
                    self.visited.append(node)
                    self.total_visited.append(node)
                    children = self.get_possible_transitions(node)
                    for transition in children:

                        next_state = self.get_next_state_given_transition(node, transition)

                        if self.stringify_state(node) in self.paths:
                            self.paths[self.stringify_state(next_state)] = self.paths[self.stringify_state(node)] + transition
                        else:
                            self.paths[self.stringify_state(next_state)] = transition

                        if next_state not in self.visited:
                            stack.append((next_state, depth+1))

            max_depth += 1
            self.paths = {}

        # If the goal state is not found, return failure
        return None

    def get_misplaced_tiles(self, current_state):
        misplaced_tiles = 0

        for i in range(len(current_state)):
            if current_state[i] != self.goal_state[i]:
                misplaced_tiles += 1

        return misplaced_tiles

    def a_star(self, heuristic):
        initial_state = self.elements

        queue = []

        visited = set()

        queue.append((initial_state, 0, 0))

        while queue and (time.time() - self.start_time) < self.time_limit:

            queue.sort(key=lambda x: x[1]+x[2])
            node, depth, misplaced_tiles = queue.pop(0)

            if node == self.goal_state:
                return self.paths[self.stringify_state(self.goal_state)], len(visited)

            visited.add(self.stringify_state(node))

            possible_transitions = self.get_possible_transitions(node)

            for transition in possible_transitions:

                next_state = self.get_next_state_given_transition(node, transition)

                if self.stringify_state(next_state) not in visited:

                    if self.stringify_state(node) in self.paths:
                        self.paths[self.stringify_state(next_state)] = self.paths[self.stringify_state(node)] + transition
                    else:
                        self.paths[self.stringify_state(next_state)] = transition


                    child_depth = depth + 1
                    heuristic_val = 0
                    if heuristic == "misplaced":
                        heuristic_val = self.get_misplaced_tiles(next_state)
                    elif heuristic == "manhattan":
                        heuristic_val = self.calculate_manhattan_heuristic(next_state)

                    queue.append((next_state, child_depth, heuristic_val))
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

    def read_file(self, name):
        with open(name, "r") as f:
            for l in f:
                elements = l.split(" ")
                for element in elements:
                    self.elements.append(element.strip())

solution_dict = {}

def solve_puzzle(fname):
    puz = Puzzle(fname)

    isSolvable = puz.solvable(puz.elements)

    algs = []
    if args.alg != "all":
        algs.append(args.alg)
    else:
        algs = ["bfs", "ids", "h1", "h2"]

    if isSolvable:
        for alg in algs:
            puz.start_time = time.time()

            result = None

            if alg == "bfs":
                result = puz.bfs()
            elif alg == "ids":
                result = puz.iddfs()
            elif alg == "h1":
                result = puz.a_star("misplaced")
            elif alg == "h2":
                result = puz.a_star("manhattan")

            total_time = time.time() - puz.start_time
            if result is None:
                solution_dict[fname + "-" + alg] = {
                    "path": None,
                    "nodes_generated": None,
                    "time": total_time
                }
            else:
                solution_dict[fname + "-" + alg] = {
                    "path": result[0],
                    "nodes_generated": result[1],
                    "time": total_time
                }
            puz.clear()
    else:
        solution_dict[fname + "-" + args.alg] = {
            "path": "Unsolvable",
            "nodes_generated": None,
            "time": None
        }




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'The 8-puzzle',
        description = 'Solves an 8-puzzle using various algorithms')

    parser.add_argument('--fPath')
    parser.add_argument('--alg')

    args = parser.parse_args()

    files = []

    threads = []

    if path.isdir(args.fPath):
        for f in os.listdir(args.fPath):
            files.append(os.path.join(args.fPath, f))
    else:
        files.append(args.fPath)

    for puzzle_file in files:
        print("Solving puzzle: " + puzzle_file)
        puz_thread = threading.Thread(target=solve_puzzle, args=(puzzle_file, ))
        threads.append(puz_thread)

    for thr in threads:
        thr.start()

    for thr in threads:
        thr.join()

    print("Threads done")

    for key in solution_dict:
        solution = solution_dict[key]
        print("/---------------/")
        print("Puzzle: " + key)

        if solution["path"] is not None:
            print("Correct path: " + solution["path"])
        else:
            print("Puzzle ran out of time")

        if solution["nodes_generated"] is not None:
            print("Nodes generated: " + str(solution["nodes_generated"]))

        if solution["time"] is not None:
            print("Time: %.8f seconds" % solution["time"])




