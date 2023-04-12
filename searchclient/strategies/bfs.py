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
from collections import deque

import domains.hospital.goal_description as h_goal_description
import domains.hospital.state as h_state

class FrontierBFS:

    def __init__(self):
        # We use both a deque and a set for the BFS implementation.
        # Using the deque as a queue allows us to keep track of the ordering while the set allows us to perform
        # efficient membership checks, e.g. whether some specific state is in the queue.
        self.queue = deque()
        self.set = set()

    def prepare(self, goal_description: h_goal_description.HospitalGoalDescription):
        # Prepare is called at the beginning of a search and since we will sometimes reuse frontiers for multiple
        # searches, prepares must ensure that state is cleared.
        self.queue.clear()
        self.set.clear()

    def add(self, state: h_state.HospitalState):
        # Append adds to the tail of the queue
        self.queue.append(state)
        self.set.add(state)

    def pop(self) -> h_state.HospitalState:
        # Popleft takes from the head of the queue
        state = self.queue.popleft()
        self.set.remove(state)
        return state

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def size(self) -> int:
        return len(self.queue)

    def contains(self, state: h_state.HospitalState) -> bool:
        return state in self.set
