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
from journey_plan_search.search import find_shortest_path


def _station(name: str) -> FakeStation:
    return FakeStation(uuid=name, name=name)


def _edge(uid: str, start: FakeStation, end: FakeStation, distance: int) -> FakeEdge:
    edge = FakeEdge(uuid=uid, distance_min=distance, start_station=start, end_station=end)
    start.outbound_edges.append(edge)
    return edge


class TestFindShortestPath:

    def test_direct_single_edge_path(self):
        a, b = _station("A"), _station("B")
        ab = _edge("e1", a, b, 5)
        result = find_shortest_path(a, b)
        assert result.overall_distance_min == 5
        assert len(result.path) == 1
        assert result.path[0] is ab

    def test_two_hop_linear_path(self):
        a, b, c = _station("A"), _station("B"), _station("C")
        ab = _edge("e1", a, b, 5)
        bc = _edge("e2", b, c, 3)
        result = find_shortest_path(a, c)
        assert result.overall_distance_min == 8
        assert len(result.path) == 2
        assert result.path[0] is ab
        assert result.path[1] is bc

    def test_three_hop_linear_path(self):
        a, b, c, d = _station("A"), _station("B"), _station("C"), _station("D")
        ab = _edge("e1", a, b, 2)
        bc = _edge("e2", b, c, 3)
        cd = _edge("e3", c, d, 4)
        result = find_shortest_path(a, d)
        assert result.overall_distance_min == 9
        assert len(result.path) == 3

    def test_indirect_path_preferred_over_longer_direct_edge(self):
        # A -3-> B -4-> C  (total 7)
        # A -10-> C        (total 10)
        # Expected: via B with distance 7
        a, b, c = _station("A"), _station("B"), _station("C")
        _edge("e1", a, b, 3)
        _edge("e2", b, c, 4)
        _edge("e3", a, c, 10)
        result = find_shortest_path(a, c)
        assert result.overall_distance_min == 7

    def test_direct_edge_preferred_over_longer_indirect_path(self):
        # A -5-> C         (total 5)
        # A -7-> B -1-> C  (total 8)
        # Expected: direct with distance 5
        a, b, c = _station("A"), _station("B"), _station("C")
        _edge("e1", a, c, 5)
        _edge("e2", a, b, 7)
        _edge("e3", b, c, 1)
        result = find_shortest_path(a, c)
        assert result.overall_distance_min == 5

    def test_diamond_topology_shortest_path(self):
        # A -2-> B -6-> D  (total 8)
        # A -5-> C -1-> D  (total 6)
        # Expected: via C with distance 6
        a = _station("A")
        b = _station("B")
        c = _station("C")
        d = _station("D")
        _edge("e1", a, b, 2)
        _edge("e2", a, c, 5)
        _edge("e3", b, d, 6)
        _edge("e4", c, d, 1)
        result = find_shortest_path(a, d)
        assert result.overall_distance_min == 6

    def test_no_reachable_path_raises_value_error(self):
        a, b = _station("A"), _station("B")
        # No edges added — B is unreachable from A
        with pytest.raises(ValueError):
            find_shortest_path(a, b)

    def test_disconnected_graph_raises_value_error(self):
        # A -3-> B    C (isolated)
        a, b, c = _station("A"), _station("B"), _station("C")
        _edge("e1", a, b, 3)
        with pytest.raises(ValueError):
            find_shortest_path(a, c)

    def test_result_start_and_destination(self):
        a, b = _station("A"), _station("B")
        _edge("e1", a, b, 5)
        result = find_shortest_path(a, b)
        assert result.start is a
        assert result.destination is b

    def test_result_start_and_destination_multi_hop(self):
        a, b, c = _station("A"), _station("B"), _station("C")
        _edge("e1", a, b, 3)
        _edge("e2", b, c, 4)
        result = find_shortest_path(a, c)
        assert result.start is a
        assert result.destination is c
