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


class HospitalLevel:
    """
    The Level class stores all information loaded from the level file in a convenient format.
    - Walls are stored as a two-dimensional row-major array of booleans, i.e. walls[row][col] is True iff
      there is a wall at (row, col)
    - Colors is a map from characters into a color string. I.e. if box A is red then colors['A'] = "red".
      Note that this map stores the colors of both agents and boxes
    - agent_goals and box_goals are lists of goals in the format (position, char, is_positive).
      See goal_description.py for further detail
    - initial_agent_positions and initial_box_positions are lists of the initial positions of agents and boxes in
      the format (position, character).
    """

    def __init__(self, name, walls, colors, agent_goals, box_goals, initial_agent_positions, initial_box_positions):
        self.name = name
        self.walls = walls
        self.colors = colors
        self.agent_goals = agent_goals
        self.box_goals = box_goals
        self.initial_agent_positions = initial_agent_positions
        self.initial_box_positions = initial_box_positions

        # Some convenience length variables
        self.num_agents = len(self.initial_agent_positions)
        self.num_boxes = len(self.initial_box_positions)
        self.num_agent_goals = len(self.agent_goals)
        self.num_box_goals = len(self.box_goals)

    @staticmethod
    def parse_level_lines(level_lines):
        # Reverse the lines in the level file such that we can efficiently read the next line using 'pop'
        level_lines.reverse()

        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain
        level_lines.pop() # '#domain'
        level_lines.pop() # 'hospital'

        # Read level name
        level_lines.pop()  # '#levelname'
        level_name = level_lines.pop()  # <levelname>

        # Read colors
        level_lines.pop()  # '#colors'
        colors = {}

        line = level_lines.pop()
        while not line.startswith("#"):
            split = line.split(":")
            color = split[0].strip()
            objects = split[1].split(",")
            for obj in objects:
                char = obj.strip()[0]
                if '0' <= char <= '9':
                    colors[char] = color
                elif 'A' <= char <= 'Z':
                    colors[char] = color
            line = level_lines.pop()

        # Scan ahead to determine number of rows and columns in level file
        num_rows = 0
        num_cols = 0

        # Skip first line since that is just '#initial'
        for line in level_lines[1:]:
            if line.startswith("#"):
                # Found start of next section
                break
            num_rows += 1
            num_cols = max(num_cols, len(line))

        # Read initial state
        initial_agent_positions = [((0, 0), '')] * 10
        initial_box_positions = []
        walls = [[True for _ in range(num_cols)] for _ in range(num_rows)]

        num_agents = 0
        for row in range(num_rows):
            line = level_lines.pop()
            for col, char in enumerate(line):

                walls[row][col] = char == '+'
                if '0' <= char <= '9':
                    idx = ord(char) - ord('0')
                    initial_agent_positions[idx] = ((row, col), char)
                    num_agents += 1
                elif 'A' <= char <= 'Z':
                    initial_box_positions.append(((row, col), char))

        # Cut off agents not used in level
        initial_agent_positions = initial_agent_positions[:num_agents]

        # Read goal state
        agent_goals = []
        box_goals = []

        level_lines.pop()  # Skip line since that is just '#goal'

        for row in range(num_rows):
            line = level_lines.pop()
            for col, char in enumerate(line):

                if '0' <= char <= '9':
                    agent_goals.append(((row, col), char, True))
                if 'A' <= char <= 'Z':
                    box_goals.append(((row, col), char, True))

        return HospitalLevel(level_name, walls, colors, agent_goals, box_goals, initial_agent_positions, initial_box_positions)

    def wall_at(self, position):
        """Returns True if there is a wall at the requested position and False otherwise"""
        return self.walls[position[0]][position[1]]

    def agent_goal_at(self, position):
        """If there is an agent goal at the requested position, its letter is returned and None otherwise"""
        for (goal_position, goal_letter, _) in self.agent_goals:
            if goal_position == position:
                return goal_letter
        return None

    def box_goal_at(self, position):
        """If there is a box goal at the requested position, its letter is returned and None otherwise"""
        for (goal_position, goal_letter, _) in self.box_goals:
            if goal_position == position:
                return goal_letter
        return None

    def goal_at(self, position):
        """If there is a goal at the requested position, its letter is returned and None otherwise"""
        return self.agent_goal_at(position) or self.box_goal_at(position)
