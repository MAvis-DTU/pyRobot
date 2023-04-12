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
from __future__ import annotations

import copy
import itertools
import random
# Set fixed seed for random shuffle (ensures deterministic runs)
random.seed(a=0, version=2)

import domains.hospital.level as h_level
import domains.hospital.actions as actions


class HospitalState:
    """
    HospitalState stores all *dynamic* information regarding a state in the hospital state,
    that is, it only contains the agent positions and the box positions.
    Both agent and box positions are stored in the format (position, character).
    Note that the index of a particular agents and boxes is *not* necessarily fixed across states.
    The *static* information is instead stored in the HospitalLevel class in the level.py file.
    This separation greatly reduces the memory usage since we only store static information once.
    """

    level = None

    def __init__(
        self,
        level: h_level.HospitalLevel,
        agent_positions: list[tuple[tuple[int, int], str]],
        box_positions: list[tuple[tuple[int, int], str]],
        parent = None,
        action: actions.AnyAction = None
    ):
        self.level = level
        self.agent_positions = agent_positions
        self.box_positions = box_positions
        self.parent = parent
        self.action = action
        self.path_cost = 0 if parent is None else parent.path_cost + 1

    def agent_at(self, position: tuple[int, int]) -> tuple[int, str]:
        """
        Returns the index and character of the agent at the given position.
        If there is no agent at the position, -1,'' is returned instead.
        """
        for (idx, (agent_position, agent_char)) in enumerate(self.agent_positions):
            if agent_char == '':
                continue
            if agent_position == position:
                return idx, agent_char
        return -1, ''

    def box_at(self, position: tuple[int, int]) -> tuple[int, str]:
        """
        Returns the index and character of the box at the given position.
        If there is no box at the position, -1,'' is returned instead.
        """
        for (idx, (box_position, box_char)) in enumerate(self.box_positions):
            if box_char == '':
                continue
            if box_position == position:
                return idx, box_char
        return -1, ''

    def object_at(self, position: tuple[int, int]) -> str:
        """
        Returns the index and character of the object at the given position.
        It can be used for checks where we do not care whether it is an agent or a box, e.g. when checking
        for obstacles. If there is no object at the position, -1,'' is returned instead.
        """
        idx, agent_char = self.agent_at(position)
        if agent_char != '':
            return agent_char
        else:
            idx, box_char = self.box_at(position)
            return box_char

    def free_at(self, position: tuple[int, int]) -> bool:
        """Returns True iff there are no objects at the requested location"""
        return not self.level.wall_at(position) and \
               self.agent_at(position)[1] == '' and \
               self.box_at(position)[1] == ''

    def extract_plan(self) -> list[actions.AnyAction]:
        """Extracts a plan from the search tree by walking backwards through the search tree"""
        reverse_plan = []
        current_node = self
        while current_node.parent is not None:
            reverse_plan.append(current_node.action)
            current_node = current_node.parent
        reverse_plan.reverse()
        return reverse_plan

    def is_conflicting(self, joint_action: list[actions.AnyAction]) -> bool:
        """Returns true if any of the individual agent actions in the joint action results in a conflict"""
        # All previously free cells which either an agent or box will move into during the joint action
        destinations = set()
        # All cells currently containing a box which will be moved during the joint action
        active_boxes = set()

        for agent_index, action in enumerate(joint_action):
            # We ignore actions for filtered agents
            if self.agent_positions[agent_index][1] == '':
                continue
            # Compute destinations and moved boxes for action
            action_destinations, action_boxes = action.conflicts(agent_index, self)
            # Check for destination conflicts
            for dest in action_destinations:
                if dest in destinations:
                    return True
                destinations.add(dest)
            # Check for moved box conflicts
            for box in action_boxes:
                if box in active_boxes:
                    return True
                active_boxes.add(box)

        return False

    def result(self, joint_action: list[actions.AnyAction]):
        """Computes the state resulting from applying a joint action to this state"""
        new_state = HospitalState(self.level, copy.copy(self.agent_positions), copy.copy(self.box_positions),
                                  self, joint_action)

        for (agent_index, action) in enumerate(joint_action):
            action.result(agent_index, new_state)

        # Sorting the box positions ensures that the boxes are indistinguishable which significantly
        # reduces the search space size.
        new_state.box_positions.sort()

        return new_state

    def result_of_plan(self, plan: list[list[actions.AnyAction]]):
        """Computes the state resulting from applying a sequence of joint actions (a plan) to this state"""
        # If the plan is empty, just return a new copy of the current state
        if len(plan) == 0:
            return HospitalState(self.level, copy.copy(self.agent_positions), copy.copy(self.box_positions))
        # Otherwise, result each action in the plan
        new_state = self.result(plan[0])
        for joint_action in plan[1:]:
            new_state = new_state.result(joint_action)
        return new_state

    def is_applicable(self, joint_action: list[actions.AnyAction]) -> bool:
        """Returns whether all individual actions in the joint_action is applicable in this state"""
        for agent_index, action in enumerate(joint_action):
            if not action.is_applicable(agent_index, self):
                return False
        return True

    def get_applicable_actions(self, action_set: list[list[actions.AnyAction]]):
        """Returns a list of all applicable joint_action in this state"""
        num_agents = len(self.agent_positions)

        # Determine all applicable actions for each individual agent, i.e. without consideration of conflicts.
        applicable_actions = [[] for _ in range(num_agents)]

        for agent_index in range(num_agents):
            for action in action_set[agent_index]:
                if action.is_applicable(agent_index, self):
                    applicable_actions[agent_index].append(action)

        # Determine all applicable joint actions, but checking all combinations of the individual applicable actions
        # We can skip this step if there only is one agent
        applicable_joint_actions = []
        if num_agents == 1:
            for action in applicable_actions[0]:
                applicable_joint_actions.append([action])
        else:
            for joint_action in itertools.product(*applicable_actions):
                if not self.is_conflicting(joint_action):
                    applicable_joint_actions.append(joint_action)

        random.shuffle(applicable_joint_actions)
        return applicable_joint_actions

    def color_filter(self, color: str):
        """
        Returns a copy of the current state where all entities, of another color than the color passed as an argument,
        has been removed
        """

        filtered_agent_positions = []
        for (agent_position, agent_char) in self.agent_positions:
            if self.level.colors[agent_char] == color:
                filtered_agent_positions.append((agent_position, agent_char))

        filtered_box_positions = []
        for (box_position, box_char) in self.box_positions:
            if self.level.colors[box_char] == color:
                filtered_box_positions.append((box_position, box_char))

        return HospitalState(self.level, filtered_agent_positions, filtered_box_positions)

    def __repr__(self) -> str:
        lines = []
        lookup_table = {}
        for (position, agent_char) in self.agent_positions:
            lookup_table[position] = agent_char
        for (position, box_char) in self.box_positions:
            lookup_table[position] = box_char

        for row in range(len(self.level.walls)):
            line = []
            for col in range(len(self.level.walls[row])):
                position = (row, col)
                if position in lookup_table:
                    line.append(lookup_table[position])
                elif self.level.walls[row][col]:
                    line.append('+')
                else:
                    line.append(' ')
            lines.append(''.join(line))
        return '\n'.join(lines)

    def __eq__(self, other) -> bool:
        """
        Notice that we here only compare the agent positions and box positions, but ignore all other fields.
        That means that two states with identical positions but e.g. different parent will be seen as equal.
        """
        if isinstance(other, self.__class__):
            return self.agent_positions == other.agent_positions and self.box_positions == other.box_positions
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        """
        Allows the state to be stored in a hash table for efficient lookup.
        Notice that we here only hash the agent positions and box positions, but ignore all other fields.
        That means that two states with identical positions but e.g. different parent will map to the same hash value.
        """
        return hash((tuple(self.agent_positions), tuple(self.box_positions)))
