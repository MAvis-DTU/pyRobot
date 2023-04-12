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

import random
from search_algorithms.and_or_graph_search import and_or_graph_search
from utils import *


def broken_results(state, action):
    # Building the Results() function containing the indeterminism
    # If performing two of the same actions is possible from the state,
    # this result is added as a possible outcome..
    standard_case = state.result(action)
    if standard_case.is_applicable(action):
        broken_case = standard_case.result(action)
        return [standard_case, broken_case]
    else:
        return [standard_case]

CHANCE_OF_EXTRA_ACTION = 0.5

def non_deterministic_agent_type(level, initial_state, action_library, goal_description):
    # Create an action set for a single agent.
    action_set = [action_library]

    # Call AND-OR-GRAPH-SEARCH to compute a conditional plan
    worst_case_length, plan = and_or_graph_search(initial_state, action_set, goal_description, broken_results)

    if worst_case_length is None:
        print("Failed to find strong plan!", file=sys.stderr)
        return

    print("Found plan of worst-case length", worst_case_length, file=sys.stderr)

    current_state = initial_state

    while True:
        # If we have reached the goal, then we are done
        if goal_description.is_goal(current_state):
            break

        if current_state not in plan:
            # The agent reached a state not covered by the plan; AND-OR-GRAPH-SEARCH failed.
            print(f"Reached state not covered by plan!\n{current_state}", file=sys.stderr)
            break

        # Otherwise, read the correct action to execute
        joint_action = plan[current_state]

        # Send the joint action to the server (also print it for help)
        print(joint_action_to_string(joint_action), flush=True, file=sys.stderr)
        print(joint_action_to_string(joint_action), flush=True)
        _ = parse_response(read_line())
        current_state = current_state.result(joint_action)

        # Broken executor in-determinism: After performing action, roll dice to check whether
        # action will be executed twice (only if it is still applicable)
        is_broken = random.random() < CHANCE_OF_EXTRA_ACTION
        is_applicable = current_state.is_applicable(joint_action)
        if is_broken and is_applicable:
            print(f"Ups! Extra {joint_action_to_string(joint_action)}", flush=True, file=sys.stderr)
            print(joint_action_to_string(joint_action), flush=True)
            _ = parse_response(read_line())
            current_state = current_state.result(joint_action)
