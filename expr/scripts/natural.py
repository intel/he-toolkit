# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module simple class representing the positive integers"""

from __future__ import annotations
from typing import Union


class Natural:
    """Represent natural numbers including zero a.k.a positive integers."""

    def __init__(self, number: Union[int, str]) -> None:
        self.number = int(number)
        if self.number < 0:
            raise ValueError(
                f"Number of entries must be a positive integer, not '{self.number}'"
            )

    def __int__(self) -> int:
        return self.number

    def __le__(self, other_number: Union[Natural, int]) -> bool:
        return self.number <= int(other_number)

    def __eq__(self, other_number: Union[Natural, int]) -> bool:
        return self.number == int(other_number)
