# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module simple class representing the positive integers"""

from __future__ import annotations
from typing import Union


class Natural:
    """Represent natural numbers including zero a.k.a non-negative integers."""

    def __init__(self, number: Union[int, str]) -> None:
        self.number = int(number)
        if self.number < 0:
            raise ValueError(
                f"Number of entries must be a non-negative integer, not '{self.number}'"
            )

    def __int__(self) -> int:
        return self.number

    def __le__(self, other: Union[Natural, int]) -> bool:
        return self.number <= int(other)

    def __gt__(self, other: Union[Natural, int]) -> bool:
        return self.number > int(other)

    # mypy says arg for __eq__ should be type object
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Natural, int)):
            raise NotImplementedError
        return self.number == int(other)
