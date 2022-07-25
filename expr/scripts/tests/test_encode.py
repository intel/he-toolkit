# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from collections import namedtuple
from functools import partial
from encode import *


def test_inner_prod():
    v1 = [5, 0, 7, 1]
    v2 = [1, 20, 2, 5]
    assert inner_prod(v1, v2) == 24


def test_int_to_pd_poly():
    num = 121
    p = 5
    d = 3
    powers_of_p = [p ** i for i in reversed(range(d))]
    coeffs = int_to_pd_poly(num, p, d)
    assert len(powers_of_p) == len(coeffs)
    assert coeffs == [4, 4, 1]  # 4 * 5^2 + 4 * 5 + 1 == 121
    assert inner_prod(coeffs, powers_of_p) == num


def test_base_from_alphabet():
    base_from_alphabet = BaseFromAlphabet(alphabet="XYZ", to_base=5, size=2)
    assert base_from_alphabet("ZYX") == [4, 1]


def test_base():
    # Similar to int_to_poly. Internally uses base 10 to pivot between bases.
    numstr = "AZ"  # 10 * 36 + 35 = 395
    num_base10 = base(numstr, from_base=36, to_base=10, size=4)
    numstr_base10 = "".join(map(str, num_base10))
    assert numstr_base10 == "0395"
    assert base(numstr_base10, from_base=10, to_base=5, size=4) == [3, 0, 4, 0]


def test_transpose():
    matrix = [1, 2, 3, 4, 5, 6]  # column major
    expected_transposed = [1, 3, 5, 2, 4, 6]
    transposed = transpose(matrix, 2, 3)
    assert transposed == expected_transposed
    assert transpose(transposed, 3, 2) == matrix


def test_grouper():
    assert list(grouper("ABCDEFG", 3, "x")) == [
        ("A", "B", "C"),
        ("D", "E", "F"),
        ("G", "x", "x"),
    ]


def test_read_txt_worth():
    data = ["A", "B", "C", "D", "E"]
    nslots = 2

    ls = list(enumerate(read_txt_worth(data, nslots)))
    print(ls)
    no_datums = 0
    for i, chunk in ls:
        # check each chunk
        n = i * nslots
        data_slice = data[n : n + nslots]
        assert chunk == data_slice
        no_datums += len(data_slice)
    # check all data was read in
    assert no_datums == len(data)


def test_composite_split():
    data = ["1234"]
    assert list(composite_split(data, 1)) == data
    assert list(composite_split(data, 2)) == ["12", "34"]
    assert list(composite_split(data, 4)) == ["1", "2", "3", "4"]


def test_round_robin_encode():
    def fn(num):
        """simple function that doubles a num."""
        return 2 * num

    data = [i for i in range(10)]
    # composite cols == 1
    assert round_robin_encode(fn, data, composite_columns=1) == [
        [fn(datum) for datum in data]
    ]
    # composite cols > 1
    assert round_robin_encode(fn, data, composite_columns=3) == [
        [0, 6, 12, 18],
        [2, 8, 14],
        [4, 10, 16],
    ]


def test_extend_with_repetitions():
    ls_of_ls = [["A", "B", "C"], [1, 2, 3], [7.0, 8.0, 9.0]]
    copy_of = [["A", "B", "C"], [1, 2, 3], [7.0, 8.0, 9.0]]

    # A repeat 1 should not modify list
    extend_with_repetitions(ls_of_ls, repeat=1)
    assert ls_of_ls == copy_of

    # A repeat of greater than 1
    # i.e. each element ['A', 'B', 'C'] -> ['A', 'B', 'C', 'A', 'B', 'C', ... ]
    extend_with_repetitions(ls_of_ls, repeat=3)
    for ls, cp in zip(ls_of_ls, copy_of):
        assert ls == (cp * 3)


def test_how_many_entries_in_file(tmp_path):
    filepath = tmp_path / "several_lines.txt"
    num_of_lines = 100
    filepath.write_text("\n".join([str(n) for n in range(num_of_lines)]))
    assert how_many_entries_in_file(filepath.resolve()) == num_of_lines


def test_parse_args():
    cmdline_args = (
        "some_params.file some_data.file --composite 1 2 3 --segment 2".split()
    )
    args = parse_args(cmdline_args)

    expected_obj = {
        "params": "some_params.file",
        "datafile": "some_data.file",
        "composite": [1, 2, 3],
        "segment": 2,
        "server": False,
    }

    assert vars(args) == expected_obj


def test_encode_datum():
    # Translation table encoding
    assert encode_datum("ABB", {"A": 1, "B": 2}) == [1, 2, 2]

    # Func encoding
    def fn(s):
        cnt = 0
        for c in s:
            if c == "A":
                cnt += 10
            elif c == "B":
                cnt += 12
        return [cnt]

    assert encode_datum("ABB", fn) == [34]


def test_encode_for_client(encode_obj_for_client, test_vector):
    data_entries, expected_encoding, _ = test_vector
    encode = encode_obj_for_client
    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, enc in zip(ptxts, expected_encoding):
        assert ptxt.slots() == enc


def test_encode_for_server(encode_obj_for_server, test_vector):
    data_entries, _, expected_encoding = test_vector
    encode = encode_obj_for_server
    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, enc in zip(ptxts, expected_encoding):
        assert ptxt.slots() == enc


