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

from pytest import mark


NON_EXISTENT_STATION = "This Station Does Not Exist"


class TestMeansOfTransport:

    @mark.repeat(10)
    def test_list_contains_all_means_of_transport(self, query_service_client):
        resp = query_service_client.get_means_of_transport_list()
        assert resp.status_code == 200
        identifiers = {item["identifier"] for item in resp.json_data}
        assert "U-Bahn" in identifiers
        assert "S-Bahn" in identifiers
        assert "Tram" in identifiers
        assert "Bus" in identifiers


class TestStations:

    @mark.repeat(10)
    def test_list_contains_known_stations(self, query_service_client):
        resp = query_service_client.get_station_list()
        assert resp.status_code == 200
        names = {s["name"] for s in resp.json_data}
        assert "Karlsplatz" in names
        assert "Stephansplatz" in names
        assert "Westbahnhof" in names

    @mark.repeat(10)
    def test_filter_with_wildcard_returns_matching_stations_only(self, query_service_client):
        resp = query_service_client.get_station_list(filter="Karl*")
        assert resp.status_code == 200
        names = [s["name"] for s in resp.json_data]
        assert len(names) > 0
        assert all(name.startswith("Karl") for name in names)

    @mark.repeat(10)
    @mark.parametrize("station_name", ["Karlsplatz", "Stephansplatz", "Westbahnhof", "Praterstern", "Simmering"])
    def test_get_station_by_name(self, query_service_client, station_name) -> None:
        resp = query_service_client.get_station_details(station_name)
        assert resp.status_code == 200
        assert resp.json_data["name"] == station_name

    @mark.repeat(10)
    def test_get_unknown_station_returns_404(self, query_service_client):
        resp = query_service_client.get_station_details(NON_EXISTENT_STATION)
        assert resp.status_code == 404


class TestLines:

    @mark.repeat(10)
    def test_list_contains_all_lines(self, query_service_client):
        resp = query_service_client.get_line_list()
        assert resp.status_code == 200
        labels = {line["label"] for line in resp.json_data}
        assert "U1" in labels
        assert "U2" in labels
        assert "U3" in labels
        assert "U4" in labels
        assert "U6" in labels
        assert "S1" in labels
        assert "S45" in labels

    @mark.repeat(10)
    @mark.parametrize("means_of_transport", ["U-Bahn", "S-Bahn"])
    def test_filter_by_means_of_transport(self, query_service_client, means_of_transport):
        resp = query_service_client.get_line_list(means_of_transport=means_of_transport)
        assert resp.status_code == 200
        assert len(resp.json_data) > 0
        assert all(line["means_of_transport"] == means_of_transport for line in resp.json_data)

    @mark.repeat(10)
    @mark.parametrize("label,expected_means_of_transport", [("U1", "U-Bahn"), ("S45", "S-Bahn")])
    def test_get_line_by_label(self, query_service_client, label, expected_means_of_transport):
        resp = query_service_client.get_line_details(label)
        assert resp.status_code == 200
        assert resp.json_data["label"] == label
        assert resp.json_data["means_of_transport"] == expected_means_of_transport


class TestJourneyPlan:

    @mark.repeat(10)
    def test_direct_single_edge(self, query_service_client):
        # Karlsplatz → Stephansplatz: single edge on U1, 2 min
        resp = query_service_client.search_journey_plan("Karlsplatz", "Stephansplatz")
        assert resp.status_code == 200
        assert resp.json_data["start"] == "Karlsplatz"
        assert resp.json_data["destination"] == "Stephansplatz"
        assert resp.json_data["duration_minutes"] == 2

    @mark.repeat(10)
    def test_multi_stop_same_line(self, query_service_client):
        # Westbahnhof → Stephansplatz: 5 edges on U3, 7 min
        resp = query_service_client.search_journey_plan("Westbahnhof", "Stephansplatz")
        assert resp.status_code == 200
        assert resp.json_data["start"] == "Westbahnhof"
        assert resp.json_data["destination"] == "Stephansplatz"
        assert resp.json_data["duration_minutes"] == 7

    @mark.repeat(10)
    def test_unknown_start_returns_404(self, query_service_client):
        resp = query_service_client.search_journey_plan(NON_EXISTENT_STATION, "Karlsplatz")
        assert resp.status_code == 404

    @mark.repeat(10)
    def test_unknown_destination_returns_404(self, query_service_client):
        resp = query_service_client.search_journey_plan("Karlsplatz", NON_EXISTENT_STATION)
        assert resp.status_code == 404
