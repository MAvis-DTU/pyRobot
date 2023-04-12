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

from search_algorithms.graph_search import graph_search
from utils import *


def classic_agent_type(level, initial_state, action_library, goal_description, frontier):

    # Create an action set where all agents can perform all actions
    action_set = [action_library] * level.num_agents

    planning_success, plan = graph_search(initial_state, action_set, goal_description, frontier)

    if not planning_success:
        print("Unable to solve level.", file=sys.stderr)
        return

    print(f"Found solution of length {len(plan)}", file=sys.stderr)

    for joint_action in plan:

        # Send the joint action to the server
        print(joint_action_to_string(joint_action), flush=True)
        # Uncomment the below line to print the executed actions to the command line for debugging purposes
        # print(joint_action_to_string(joint_action), file=sys.stderr, flush=True)

        # Read back whether the agents succeeded in performing the joint action
        execution_successes = parse_response(read_line())
        if False in execution_successes:
            print("Execution failed! Stopping...", file=sys.stderr)
            # One of the agents failed to execute their action.
            # This should not occur in classical planning and we therefore just abort immediately
            return
