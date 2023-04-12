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

class HospitalGoalDescription:

    """
    A goal description is simple a list of goal literals where each literal is a triplet on
    the form (position, character, is_positive). Is_positive is used to denote how this goal is satisfied, with a
    positive goal being satisfied when an object with the matching character is at the goal position, while a
    negative goal is satisfied when such an object is *not* at the goal position.
    The 'goal' member contains all goals (both agent and box goals) while 'agent_goal' and 'box_goal' only
    contains one kind. This double representation allows for quick and convenient lookup of goals of a specific kind
    """

    def __init__(self, level, goals):
        self.level = level
        self.goals = goals
        self.agent_goals = []
        self.box_goals = []
        for goal in self.goals:
            if '0' <= goal[1] <= '9':
                self.agent_goals.append(goal)
            elif 'A' <= goal[1] <= 'Z':
                self.box_goals.append(goal)

    def is_goal(self, state):
        """Returns whether the given state satisfies all goals in the goal description"""
        for (goal_position, goal_char, is_positive_literal) in self.goals:
            char = state.object_at(goal_position)
            if is_positive_literal and goal_char != char:
                return False
            elif not is_positive_literal and goal_char == char:
                return False

        return True

    def color_filter(self, color):
        """Creates a copy of the goal descriptions where all entities of another color has been removed"""
        filtered_goals = []
        for goal in self.goals:
            if self.level.colors[goal[1]] == color:
                filtered_goals.append(goal)

        return HospitalGoalDescription(self.level, filtered_goals)

    def get_sub_goal(self, index):
        """
        This function allow each sub goal to be considered one at a time.
        Usage is as follows:
        for index in range(goal_description.num_sub_goals()):
            sub_goal = goal_description.get_sub_goal(index)

        where sub_goal will be a goal_description containing exactly one of the sub goals contained
        in the goal description.
        All box goals are visited prior to the agent goals.
        """
        num_box_goals = len(self.box_goals)
        if index < num_box_goals:
            return HospitalGoalDescription(self.level, [self.box_goals[index]])
        else:
            return HospitalGoalDescription(self.level, [self.agent_goals[index - num_box_goals]])

    def num_sub_goals(self):
        """
        This function returns the number of sub goals contained in the goal description.
        It is meant to be used together with get_sub_goal
        """
        return len(self.goals)

    def create_new_goal_description_of_same_type(self, goals):
        """
        This function just creates a new goal description, but is useful in domain-agnostic agent types where
        we wish to create new goal descriptions without referring to the domain.
        """
        return HospitalGoalDescription(self.level, goals)

    def __repr__(self):
        agent_goals_str = " and ".join(map(lambda goal: str(goal), self.agent_goals))
        box_goals_str = " and ".join(map(lambda goal: str(goal), self.box_goals))
        if len(agent_goals_str) > 0 and len(box_goals_str) > 0:
            return agent_goals_str + " and " + box_goals_str
        else:
            return agent_goals_str + box_goals_str

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.goals == other.goals
        else:
            return False

    def __hash__(self):
        return hash(tuple(self.goals))
