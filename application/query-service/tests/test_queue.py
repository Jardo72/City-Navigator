#
# Copyright 2026 Jaroslav Chmurny
#
# This file is part of City Navigator.
#
# City Navigator is free software developed for educational and experimental
# purposes. It is licensed under the Apache License, Version 2.0 # (the
# "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

from helpers import FakeStation
from journey_plan_search.queue import RepriorizablePriorityQueue


def _station(name: str) -> FakeStation:
    return FakeStation(uuid=name, name=name)


class TestIsNotEmpty:

    def test_returns_false_for_empty_queue(self):
        q = RepriorizablePriorityQueue()
        assert not q.is_not_empty()

    def test_returns_true_after_single_enqueue(self):
        q = RepriorizablePriorityQueue()
        q.enqueue(_station("A"), 5)
        assert q.is_not_empty()

    def test_returns_false_after_single_enqueue_and_dequeue(self):
        q = RepriorizablePriorityQueue()
        q.enqueue(_station("A"), 5)
        q.dequeue()
        assert not q.is_not_empty()

    def test_returns_true_while_stations_remain(self):
        q = RepriorizablePriorityQueue()
        a, b = _station("A"), _station("B")
        q.enqueue(a, 3)
        q.enqueue(b, 7)
        q.dequeue()
        assert q.is_not_empty()


class TestDequeue:

    def test_raises_index_error_on_empty_queue(self):
        q = RepriorizablePriorityQueue()
        with pytest.raises(IndexError):
            q.dequeue()

    def test_returns_station_with_lowest_distance_first(self):
        q = RepriorizablePriorityQueue()
        a, b, c = _station("A"), _station("B"), _station("C")
        q.enqueue(a, 10)
        q.enqueue(b, 3)
        q.enqueue(c, 7)
        result = q.dequeue()
        assert result.station is b
        assert result.distance_from_start_min == 3

    def test_dequeues_in_ascending_distance_order(self):
        q = RepriorizablePriorityQueue()
        a, b, c = _station("A"), _station("B"), _station("C")
        q.enqueue(a, 10)
        q.enqueue(b, 3)
        q.enqueue(c, 7)
        first = q.dequeue()
        second = q.dequeue()
        third = q.dequeue()
        assert first.distance_from_start_min == 3
        assert second.distance_from_start_min == 7
        assert third.distance_from_start_min == 10

    def test_single_station_dequeued_correctly(self):
        q = RepriorizablePriorityQueue()
        a = _station("A")
        q.enqueue(a, 42)
        result = q.dequeue()
        assert result.station is a
        assert result.distance_from_start_min == 42


class TestReprioritization:

    def test_reprioritized_station_dequeued_with_lower_distance(self):
        q = RepriorizablePriorityQueue()
        a = _station("A")
        q.enqueue(a, 10)
        q.enqueue(a, 4)  # reprioritize with lower distance
        result = q.dequeue()
        assert result.station is a
        assert result.distance_from_start_min == 4

    def test_reprioritization_does_not_increase_queue_size(self):
        q = RepriorizablePriorityQueue()
        a = _station("A")
        q.enqueue(a, 10)
        q.enqueue(a, 4)
        q.dequeue()
        assert not q.is_not_empty()

    def test_reprioritized_station_dequeued_before_higher_distance_station(self):
        q = RepriorizablePriorityQueue()
        a, b = _station("A"), _station("B")
        q.enqueue(a, 10)
        q.enqueue(b, 7)
        q.enqueue(a, 3)  # reprioritize A below B
        first = q.dequeue()
        assert first.station is a
        assert first.distance_from_start_min == 3

    def test_two_stations_with_one_reprioritized_dequeue_order(self):
        q = RepriorizablePriorityQueue()
        a, b = _station("A"), _station("B")
        q.enqueue(a, 10)
        q.enqueue(b, 5)
        q.enqueue(a, 2)  # reprioritize A to beat B
        first = q.dequeue()
        second = q.dequeue()
        assert first.station is a
        assert first.distance_from_start_min == 2
        assert second.station is b
        assert second.distance_from_start_min == 5
