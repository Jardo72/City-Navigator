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

from helpers import FakeEdge, FakeStation
from journey_plan_search.distance_table import DistanceTable


def _station(name: str) -> FakeStation:
    return FakeStation(uuid=name, name=name)


def _edge(uid: str, start: FakeStation, end: FakeStation, distance: int) -> FakeEdge:
    return FakeEdge(uuid=uid, distance_min=distance, start_station=start, end_station=end)


class TestUpdate:

    def test_new_station_creates_entry_and_returns_true(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 5)
        assert table.update(ab, 5) is True

    def test_shorter_distance_updates_entry_and_returns_true(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab_long = _edge("e1", a, b, 10)
        ab_short = _edge("e2", a, b, 4)
        table.update(ab_long, 10)
        assert table.update(ab_short, 4) is True

    def test_longer_distance_does_not_update_and_returns_false(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab_short = _edge("e1", a, b, 4)
        ab_long = _edge("e2", a, b, 10)
        table.update(ab_short, 4)
        assert table.update(ab_long, 10) is False

    def test_equal_distance_does_not_update_and_returns_false(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 5)
        ab_same = _edge("e2", a, b, 5)
        table.update(ab, 5)
        assert table.update(ab_same, 5) is False

    def test_multiple_independent_stations_tracked_separately(self):
        a, b, c = _station("A"), _station("B"), _station("C")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 3)
        ac = _edge("e2", a, c, 7)
        assert table.update(ab, 3) is True
        assert table.update(ac, 7) is True


class TestBacktrackShortestPath:

    def test_raises_value_error_when_no_path_to_destination(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        with pytest.raises(ValueError):
            table.backtrack_shortest_path(b)

    def test_direct_single_edge_path(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 5)
        table.update(ab, 5)
        result = table.backtrack_shortest_path(b)
        assert len(result.path) == 1
        assert result.path[0] is ab

    def test_two_hop_path(self):
        a, b, c = _station("A"), _station("B"), _station("C")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 3)
        bc = _edge("e2", b, c, 4)
        table.update(ab, 3)
        table.update(bc, 7)
        result = table.backtrack_shortest_path(c)
        assert len(result.path) == 2
        assert result.path[0] is ab
        assert result.path[1] is bc

    def test_shortest_path_used_when_entry_updated(self):
        # Initially record long direct path A→C (10), then update with shorter A→B→C (7).
        # Backtrack should return A→B→C.
        a, b, c = _station("A"), _station("B"), _station("C")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 3)
        bc = _edge("e2", b, c, 4)
        ac_long = _edge("e3", a, c, 10)
        table.update(ac_long, 10)
        table.update(ab, 3)
        table.update(bc, 7)   # 7 < 10, so this updates the C entry
        result = table.backtrack_shortest_path(c)
        assert len(result.path) == 2
        assert result.path[0] is ab
        assert result.path[1] is bc

    def test_result_start_property(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 5)
        table.update(ab, 5)
        result = table.backtrack_shortest_path(b)
        assert result.start is a

    def test_result_destination_property(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 5)
        table.update(ab, 5)
        result = table.backtrack_shortest_path(b)
        assert result.destination is b

    def test_result_overall_distance_single_edge(self):
        a, b = _station("A"), _station("B")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 5)
        table.update(ab, 5)
        result = table.backtrack_shortest_path(b)
        assert result.overall_distance_min == 5

    def test_result_overall_distance_multi_hop(self):
        a, b, c = _station("A"), _station("B"), _station("C")
        table = DistanceTable(a)
        ab = _edge("e1", a, b, 3)
        bc = _edge("e2", b, c, 4)
        table.update(ab, 3)
        table.update(bc, 7)
        result = table.backtrack_shortest_path(c)
        assert result.overall_distance_min == 7
