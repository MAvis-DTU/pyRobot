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
import sys


def pos_add(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] + y[0], x[1] + y[1]


def pos_sub(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] - y[0], x[1] - y[1]


# 2^31-1 is sufficiently large such that no feasible plan would ever be of this length,
# yet small enough to be efficiently stored in memory
APPROX_INFINITY = 2**31 - 1


def read_line() -> str:
    return sys.stdin.readline().rstrip()


def joint_action_to_string(joint_action) -> str:
    joint_action_names = map(lambda action: action.name, joint_action)
    return "|".join(joint_action_names)


def parse_response(response: str) -> list[bool]:
    return [part == "true" for part in response.split('|')]


class GenericNoOp:
    """A NoOP action which is independent of a specific domain and
    therefore can be used inside domain-agnostic agent types"""

    name = "NoOp"

    def __init__(self):
        pass

    def is_applicable(self, agent_index, state):
        # Optimization. NoOp can never change the state if we only have a single agent
        return len(state.agent_positions) > 1

    def result(self, agent_index, state):
        pass

    def conflicts(self, agent_index, state):
        current_agent_position, _ = state.agent_positions[agent_index]
        return [current_agent_position], []
