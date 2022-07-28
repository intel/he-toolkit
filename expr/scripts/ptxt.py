# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module for Ptxt helper object"""

from __future__ import annotations
import json
import math
from dataclasses import dataclass, field
from typing import List, Iterable


def phi(m: int) -> int:
    """Euler totient"""
    if m < 2:
        raise ValueError(f"m value '{m}' is not valid")
    return sum((1 for n in range(2, m) if math.gcd(n, m) == 1), start=1)


def order_of_p(p: int, m: int) -> int:
    """The order of p in Z^*_m"""
    d = 1
    while (p ** d) % m != 1:
        d += 1
    return d


@dataclass  # (frozen=True)
class Params:
    """Ptxt parameters"""

    m: int
    p: int
    d: int = field(init=False)
    nslots: int = field(init=False)

    def __post_init__(self):
        self.d = order_of_p(self.p, self.m)
        self.nslots = phi(self.m) // self.d


class Ptxt:
    """Represent a ptxt to make it easier to work with when (en/de)coding"""

    def __init__(self, params: Params) -> None:
        """A list is used to store the ptxt.
           Inputs are params and an encode function"""
        if not isinstance(params, Params):
            raise ValueError("params argument not type Params but type {type(params)}")
        self._params = params
        self._slots = None

    def _check_valid(self, slots: List = None, check_length: bool = True) -> None:
        """Util function to check validity of data struct holding a ptxt."""
        slots = self._slots if slots is None else slots
        params = self._params

        # Check correct number of slots
        if check_length and len(slots) != params.nslots:
            raise ValueError(
                f"Number of slots '{len(slots)}' does not equal the required number '{params.nslots}'"
            )

        # Check datatypes
        if not isinstance(slots, list):
            raise ValueError(
                f"Slots container is not a list, but of type '{type(slots)}'"
            )
        for slot_num, slot in enumerate(slots):
            if not isinstance(slot, list):
                raise ValueError(
                    f"Slot '{slot_num}' is not a list, but type '{type(slot)}'"
                )
            for coeff in slot:
                if not isinstance(coeff, (int, float)):
                    raise ValueError(
                        f"Slot '{slot_num}' does not contain correct types, but type '{type(coeff)}': '{slot}'"
                    )

        # Check slot sizes
        all_gen = (len(slot) <= params.d for slot in slots)
        for slot_num, (slot, cond) in enumerate(zip(slots, all_gen)):
            if cond is False:
                raise ValueError(
                    f"Slot '{slot_num}' with value '{slot}' is not of length '{params.d}' or less"
                )

    def slots(self):
        """Return the list of slots."""
        return self._slots

    def insert_data(self, iterable: Iterable) -> Ptxt:
        """Insert given data into ptxt"""
        encoded_data = list(iterable)
        nslots = self._params.nslots
        len_encoded_data = len(encoded_data)

        encoded_data.extend([] for _ in range(nslots - len_encoded_data))
        self._check_valid(encoded_data)
        # Once happy assign
        self._slots = encoded_data
        return self

    def insert_repeated_across_slots(self, data) -> Ptxt:
        """Insert the data in all slots."""
        slots = []
        rep_slots = self._params.nslots // len(data)
        for datum in data:
            slots.extend(datum for _ in range(rep_slots))

        # Sanity check
        self._check_valid(slots)
        # Once happy assign
        self._slots = slots
        return self

    def to_json(self) -> str:
        """stringify as valid HElib JSON ptxt"""
        encode_dict = {
            "HElibVersion": "2.2.0",
            "serializationVersion": "0.0.1",
            "type": "Ptxt",
            "content": {"scheme": "BGV", "slots": self._slots},
        }
        return json.dumps(encode_dict)

    def from_json(self, string: str) -> None:
        """Make Ptxt form JSON string"""
        jobj = json.loads(string)
        slots = jobj["content"]["slots"]
        # sanity
        if len(slots) == self._params.nslots:
            self._slots = slots
        else:
            raise ValueError(
                f"JSON '{len(slots)}' slots do not match parameter slots '{self._params}'"
            )
