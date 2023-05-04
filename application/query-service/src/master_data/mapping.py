#
# Copyright 2023 Jaroslav Chmurny
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

from db import MeansOfTransport, Station

from .dto import MeansOfTransportMaster, StationMaster


def as_means_of_transport(master_record: MeansOfTransportMaster) -> MeansOfTransport:
    return MeansOfTransport(
        uuid=master_record.uuid,
        identifier=master_record.identifier
    )


def as_station(master_record: StationMaster) -> Station:
    return Station(
        uuid=master_record.uuid,
        name=master_record.name
    )
