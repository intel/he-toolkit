# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass


@dataclass(frozen=True)
class Natural:
    """Represent natural numbers including zero a.k.a positive integers."""

    number: int

    def __post_init__(self):
        if self.number < 0:
            raise ValueError(
                f"Number of entries must be a positive integer, not '{self.number}'"
            )
