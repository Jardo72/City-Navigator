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

NON_EXISTENT_UUID = "00000000-0000-0000-0000-000000000000"


class TestStationCrud:

    def test_lifecycle(self, master_data_client):
        resp = master_data_client.create_station("Test Station")
        assert resp.status_code == 201
        uuid = resp.json_data["uuid"]
        try:
            assert resp.json_data["name"] == "Test Station"

            resp = master_data_client.get_station(uuid)
            assert resp.status_code == 200
            assert resp.json_data["name"] == "Test Station"

            resp = master_data_client.update_station(uuid, "Updated Station")
            assert resp.status_code == 200
            assert resp.json_data["name"] == "Updated Station"

            resp = master_data_client.get_station(uuid)
            assert resp.status_code == 200
            assert resp.json_data["name"] == "Updated Station"

            resp = master_data_client.delete_station(uuid)
            assert resp.status_code == 204

            resp = master_data_client.get_station(uuid)
            assert resp.status_code == 404
        except Exception:
            master_data_client.delete_station(uuid)
            raise

    def test_get_nonexistent_returns_404(self, master_data_client):
        resp = master_data_client.get_station(NON_EXISTENT_UUID)
        assert resp.status_code == 404


class TestMeansOfTransportCrud:

    def test_lifecycle(self, master_data_client):
        resp = master_data_client.create_means_of_transport("TestMoT")
        assert resp.status_code == 201
        uuid = resp.json_data["uuid"]
        try:
            assert resp.json_data["identifier"] == "TestMoT"

            resp = master_data_client.get_means_of_transport(uuid)
            assert resp.status_code == 200
            assert resp.json_data["identifier"] == "TestMoT"

            resp = master_data_client.update_means_of_transport(uuid, "TestMoTUpdated")
            assert resp.status_code == 200
            assert resp.json_data["identifier"] == "TestMoTUpdated"

            resp = master_data_client.get_means_of_transport(uuid)
            assert resp.status_code == 200
            assert resp.json_data["identifier"] == "TestMoTUpdated"

            resp = master_data_client.delete_means_of_transport(uuid)
            assert resp.status_code == 204

            resp = master_data_client.get_means_of_transport(uuid)
            assert resp.status_code == 404
        except Exception:
            master_data_client.delete_means_of_transport(uuid)
            raise

    def test_get_nonexistent_returns_404(self, master_data_client):
        resp = master_data_client.get_means_of_transport(NON_EXISTENT_UUID)
        assert resp.status_code == 404


class TestLineCrud:

    def test_lifecycle(self, master_data_client):
        mot_uuid = stop_a_uuid = stop_b_uuid = stop_c_uuid = line_uuid = None
        try:
            mot = master_data_client.create_means_of_transport("TestBus")
            assert mot.status_code == 201
            mot_uuid = mot.json_data["uuid"]

            stop_a = master_data_client.create_station("Test Stop Alpha")
            assert stop_a.status_code == 201
            stop_a_uuid = stop_a.json_data["uuid"]

            stop_b = master_data_client.create_station("Test Stop Beta")
            assert stop_b.status_code == 201
            stop_b_uuid = stop_b.json_data["uuid"]

            stop_c = master_data_client.create_station("Test Stop Gamma")
            assert stop_c.status_code == 201
            stop_c_uuid = stop_c.json_data["uuid"]

            resp = master_data_client.create_line(
                label="TX",
                means_of_transport_uuid=mot_uuid,
                terminal_stop_one_uuid=stop_a_uuid,
                terminal_stop_two_uuid=stop_c_uuid,
                direction_one_itinerary=[
                    {"station_uuid": stop_a_uuid, "point_in_time_minutes": 0},
                    {"station_uuid": stop_b_uuid, "point_in_time_minutes": 5},
                    {"station_uuid": stop_c_uuid, "point_in_time_minutes": 10},
                ],
                direction_two_itinerary=[
                    {"station_uuid": stop_c_uuid, "point_in_time_minutes": 0},
                    {"station_uuid": stop_b_uuid, "point_in_time_minutes": 5},
                    {"station_uuid": stop_a_uuid, "point_in_time_minutes": 10},
                ],
            )
            assert resp.status_code == 201
            line_uuid = resp.json_data["uuid"]
            assert resp.json_data["label"] == "TX"

            resp = master_data_client.get_line(line_uuid)
            assert resp.status_code == 200
            assert resp.json_data["label"] == "TX"

            resp = master_data_client.delete_line(line_uuid)
            assert resp.status_code == 204
            deleted_line_uuid = line_uuid
            line_uuid = None

            resp = master_data_client.get_line(deleted_line_uuid)
            assert resp.status_code == 404
        finally:
            if line_uuid:
                master_data_client.delete_line(line_uuid)
            if stop_a_uuid:
                master_data_client.delete_station(stop_a_uuid)
            if stop_b_uuid:
                master_data_client.delete_station(stop_b_uuid)
            if stop_c_uuid:
                master_data_client.delete_station(stop_c_uuid)
            if mot_uuid:
                master_data_client.delete_means_of_transport(mot_uuid)

    def test_get_nonexistent_returns_404(self, master_data_client):
        resp = master_data_client.get_line(NON_EXISTENT_UUID)
        assert resp.status_code == 404
