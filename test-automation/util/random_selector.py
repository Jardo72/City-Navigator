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

from enum import IntEnum
from enum import auto, unique
from random import randint
from typing import Tuple


@unique
class _SelectionMode(IntEnum):
    VALID = auto()
    INVALID = auto()


class RandomSelector:

    def __init__(self, values: Tuple[str], error_percentage: int = 0) -> None:
        self._values = values
        self._max_index = len(values) - 1
        self._error_period = 100 / error_percentage if error_percentage > 0 else None
        self._counter = 0

    def _get_current_selection_mode(self) -> _SelectionMode:
        self._counter += 1
        if self._error_period is None:
            return _SelectionMode.VALID
        if (self._counter % self._error_period) == 0:
            return _SelectionMode.INVALID
        return _SelectionMode.VALID

    def _random_value(self, selection_mode: _SelectionMode) -> str:
        if selection_mode is _SelectionMode.VALID:
            random_index = randint(0, self._max_index)
            return self._values[random_index]
        return "NoSuchValue"

    def random_value(self) -> str:
        selection_mode = self._get_current_selection_mode()
        return self._random_value(selection_mode)

    def random_pair(self) -> Tuple[str, str]:
        selection_mode = self._get_current_selection_mode()
        a = self._random_value(selection_mode)
        b = self._random_value(_SelectionMode.VALID)
        while a == b:
            b = self._random_value(_SelectionMode.VALID)
        return (a, b)
