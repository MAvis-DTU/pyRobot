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
from search_algorithms.all_optimal_plans import all_optimal_plans
from search_algorithms.and_or_graph_search import and_or_graph_search
from utils import *


actor_AGENT = 0
HELPER_AGENT = 1


class DisjunctiveGoalDescription:
    """
    DisjunctiveGoalDescription is a wrapper class which allow for the representation of multiple possible
    goal descriptions. It has the same 'is_goal' method as a GoalDescription object and can therefore be
    used in the same places, but in contrast to the regular GoalDescription object, it returns True when
    one of its give goals are satisfied, thus allowing for a logical 'OR' to be expressed.
    """

    def __init__(self, possible_goal_descriptions):
        # possible_goal_descriptions should be a list of goals
        self.possible_goals = possible_goal_descriptions

    def is_goal(self, belief_node):
        for possible_goal in self.possible_goals:
            if possible_goal.is_goal(belief_node.state):
                return True
        return False


class GoalRecognitionNode:
    """
    GoalRecognitionNode is a wrapper class which can be used for implementing AND-OR based graph search.
    It allow a hospital state object and a solution graph object to be integrated into a single object, which
    the methods 'get_applicable_actions' and 'result' as required by the AND-OR graph search.
    Note that the usage of this class is completely optional and you are free to implement your goal recognition
    in a different manner, if you so desire.

    """

    def __init__(self, state, solution_graph):
        self.state = state
        self.solution_graph = solution_graph

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.state == other.state and self.solution_graph == other.solution_graph
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.state, self.solution_graph))

    def get_applicable_actions(self, action_set):
        # Here we are only interested in the actions of the helper, but state.get_applicable_actions will return a list
        # of joint actions, where the actor action is always GenericNoOp().
        applicable_joint_actions = self.state.get_applicable_actions(action_set)
        applicable_actions = [joint_action[HELPER_AGENT] for joint_action in applicable_joint_actions]
        return applicable_actions

    def result(self, joint_action):

        # The result method should return a new GoalRecognitionNode which contains the resulting state and the
        # solution graph obtained from executing the joint_action in the current state.
        raise NotImplementedError()


def solution_graph_results(recognition_node, helper_action):

    # This results method can be used as the 'results' function for the AND-OR graph-search.
    # It takes a GoalRecognitionNode (or something else if you choose to not use the GoalRecognitionNode class) and
    # the action taken by the helper, i.e., the chosen OR-branch.
    # This function should then return all of the possible outcomes, i.e., the possible AND-nodes.
    raise NotImplementedError()


def goal_recognition_agent_type(level, initial_state, action_library, goal_description, frontier):
    # You should implement your goal recognition agent type here. You can take inspiration on how to structure the code
    # from your previous helper and non deterministic agent types.
    # Note: Similarly to the non deterministic agent type, this is not a fast algorithm and you should therefore start
    # by testing on very small levels, such as those found in the assignment.
    raise NotImplementedError()



