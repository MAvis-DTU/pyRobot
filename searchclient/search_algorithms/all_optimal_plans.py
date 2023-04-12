# coding: utf-8
#
# Copyright 2021 The Technical University of Denmark
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import time
import memory
from collections import deque
try:
    import graphviz
except ImportError:
    pass


# A global variable used to generate unique node IDs
next_id = 0


# Always return a new unique number
def get_fresh():
    global next_id
    unique_id = next_id
    next_id += 1
    return unique_id


class MultiParentNode:
    """
    In order to represent the nodes of a solution graph, we need to track additional information beyond that contained
    in the HospitalState class. For this reason, we here provide a wrapper class you can use for your ALL_OPTIMAL_PATHS
    search. More precisely, it provides the following additional members:
    - parents: A list of parents such that we can support each node having multiple parents
    - actions: A list of all possible actions from this state.
    - optimal_actions_and_results: A map of actions into their resulting MultiParentNode.
        Note that these actions should be the subset of all possible actions, which occurs on some optimal plan.
    - consistent_goals: A set of GoalDescriptions which can contain the goal labelling.

    The implemented methods assume that the state only contains a single agent, but feel free to extend this to also
    support the multi-agent case if you so desire.
    """

    def __init__(self, state):
        self.state = state
        self.path_cost = state.path_cost
        self.parents = []
        self.actions = []
        self.optimal_actions_and_results = {}
        self.consistent_goals = set()
        self.id = get_fresh()  # Only used for visualization

    def get_applicable_actions(self, action_set):
        # Find all joint actions and then pick out the action of the first agent
        joint_actions = self.state.get_applicable_actions(action_set)
        actions = [joint_action[0] for joint_action in joint_actions]
        return actions

    def result(self, action):
        # Pack the action into a joint action
        joint_action = [action]
        return self.state.result(joint_action)

    def get_actions_and_results_consistent_with_goal(self, goal):
        # Returns a list of actions and their corresponding resulting states, which would be consistent with an
        # optimal plan to solve the specified goal.
        consistent_actions_and_results = []
        for (action, state) in self.optimal_actions_and_results.items():
            if goal in state.consistent_goals:
                consistent_actions_and_results.append((action, state))

        return consistent_actions_and_results

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.state == other.state
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.state)


def visualize_solution_graph(solution_graph):
    """
    The function allow you to visualize the found solution graph as a picture.

    Use of this function is completely optional, but some of you might find it helpful for debugging your code or
    to to gain a better understanding of the found solution.
    Given a solution graph it will create a file 'all_optimal_paths.svg' on your current path.
    Note:
        This function requires graphviz to be installed on your machine. You will need to install both the Graphviz
        engine (see https://graphviz.org/download/) and the graphviz python package (pip install graphviz).
    """

    graph = graphviz.Digraph()
    graph.format = "svg"

    visited = set()

    def visitor(subgraph):
        # Ensure we only visit each node a single time
        if subgraph in visited:
            return subgraph.id
        visited.add(subgraph)

        # Draw the node itself
        graph.node(f"{subgraph.id}", f"{subgraph.id} -> {subgraph.consistent_goals}")

        # Now recurse down into all the optimal children of the node and draw edges along the way
        for (action, resulting_state) in subgraph.optimal_actions_and_results.items():
            child_id = visitor(resulting_state)
            graph.edge(f"{subgraph.id}", f"{child_id}", label=f"{action}")
        return subgraph.id

    visitor(solution_graph)
    graph.render("all_optimal_paths", view=True)



def all_optimal_plans(initial_state, action_set, possible_goals, frontier):
    """
    An implementation of the ALL_OPTIMAL_PLANS algorithm as described in the MAvis3 assignment description.
    - initial_state: A instance of HospitalState representing the initial state of the level
    - action_set: A list of possible actions
    - possible_goals: A list of goal descriptions, one of which the agent is trying to complete
    - frontier: A frontier
    The function should return a pair (boolean, MultiParentNode) where:
    - if the search found a solution, the boolean should be True and the MultiParentNode should be the root of the
      solution graph
    - if the search did not find a solution, the boolean should be False and the MultiParentNode should be None
    """
    iterations = 0

    # Clear the parent pointer and path_cost in order make sure that the initial state is a root node
    initial_state.parent = None
    initial_state.path_cost = 0
    frontier.prepare(possible_goals)

    root = MultiParentNode(initial_state)

    frontier.add(root)
    generated_states = {}

    # Your implementation of ALL-OPTIMAL-PLANS goes here...
    raise NotImplementedError()


# A global variable used to keep track of the start time of the current search
start_time = 0


def print_search_status(generated, frontier):
    global start_time
    if len(generated) == 0:
        start_time = time.time()
    memory_usage_bytes = memory.get_usage()
    # Replacing the generated comma thousands separators with dots is neither pretty nor locale aware but none of
    # Pythons four different formatting facilities seems to handle this correctly!
    num_frontier = f"{frontier.size():8,d}".replace(',', '.')
    num_generated = f"{len(generated):8,d}".replace(',', '.')
    elapsed_time = f"{time.time() - start_time:3.3f}".replace('.',',')
    memory_usage_mb = f"{memory_usage_bytes / (1024*1024):3.2f}".replace('.',',')
    status_text = f"##Frontier: {num_frontier}, #Generated: {num_generated}," \
                  f" Time: {elapsed_time} s, Memory: {memory_usage_mb} MB\n"
    print(status_text, file=sys.stderr)
