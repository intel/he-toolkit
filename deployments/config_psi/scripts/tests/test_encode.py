# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import string
from functools import partial

import pytest
from encode import *


def test_inner_prod():
    v1 = [5, 0, 7, 1]
    v2 = [1, 20, 2, 5]
    assert inner_prod(v1, v2) == 24


def test_int_to_poly():
    num = 121
    p = 5
    d = 3
    powers_of_p = [p**i for i in reversed(range(d))]
    coeffs = int_to_poly(num, p, d)
    assert len(powers_of_p) == len(coeffs)
    assert coeffs == [4, 4, 1]  # 4 * 5^2 + 4 * 5 + 1 == 121
    assert inner_prod(coeffs, powers_of_p) == num


def test_base_from_alphabet():
    base_from_alphabet = BaseFromAlphabet(alphabet="XYZ", to_base=5, size=2)
    assert base_from_alphabet("ZYX") == [4, 1]


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
    assert list(composite_split(data, 1)) == ["1234"]
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
    # Remember that header line not counted
    assert how_many_entries_in_file(filepath.resolve()) == num_of_lines - 1


def test_parse_args_params_only(tmp_path):
    config_file = tmp_path / "some_config.file"
    config_file.open("w").write(
        """
        [params]
        p = 257
        m = 80

        [config]
        columns = 3
        segments = 2

        [columns.encoding]
        column1 = "alphanumeric"
        column2 = "alphabetical"
        column3 = "numeric"

        [columns.composite]
        column2 = 2
    """
    )
    cmdline_args = f"--config {config_file} some_data.file".split()
    args = parse_args(cmdline_args)
    expected_obj = {
        "config": Config(
            params=Params(m=80, p=257),
            columns=3,
            segments=2,
            encodings={
                "column1": "alphanumeric",
                "column2": "alphabetical",
                "column3": "numeric",
            },
            composites={"column2": 2},
        ),
        "datafile": "some_data.file",
        "server": False,
    }

    assert vars(args) == expected_obj


def test_encode_datum():
    # Translation table encoding
    assert encode_datum("ABB", {"A": 1, "B": 2}) == [1, 2, 2]

    # Encoding function
    def fn(s):
        cnt = 0
        for c in s:
            if c == "A":
                cnt += 10
            elif c == "B":
                cnt += 12
        return [cnt]

    assert encode_datum("ABB", fn) == [34]


def test_encode_for_client_translation_table(
    encode_obj_for_client_translation_table, test_vector_p41_m41_translation_table
):
    data_entries, expected_encoding, _ = test_vector_p41_m41_translation_table
    encode = encode_obj_for_client_translation_table
    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, expected in zip(ptxts, expected_encoding):
        assert ptxt.slots() == expected


def test_encode_for_client_full_packing(encode_obj_for_client, test_vector_p41_m41):
    data_entries, expected_encoding, _ = test_vector_p41_m41
    encode = encode_obj_for_client
    print(vars(encode), file=sys.stderr)
    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, expected in zip(ptxts, expected_encoding):
        assert ptxt.slots() == expected


def test_encode_for_server(
    encode_obj_for_server_translation_table, test_vector_p41_m41_translation_table
):
    data_entries, _, expected_encoding = test_vector_p41_m41_translation_table
    encode = encode_obj_for_server_translation_table
    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, expected in zip(ptxts, expected_encoding):
        assert ptxt.slots() == expected


def test_encode_for_server_full_packing(encode_obj_for_server, test_vector_p41_m41):
    data_entries, _, expected_encoding = test_vector_p41_m41
    encode = encode_obj_for_server
    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, expected in zip(ptxts, expected_encoding):
        assert ptxt.slots() == expected


def test_edge_case(edge_case_data):
    p, d, entry, expected_colA, expected_colB, expected_colC = edge_case_data
    assert (
        BaseFromAlphabet(p, d, alphabet=string.digits + string.ascii_uppercase)(
            entry["colA"]
        )
        == expected_colA
    )
    assert BaseFromAlphabet(p, d)(entry["colB"]) == expected_colB
    # won't fit with d coeffs
    with pytest.raises(ValueError):
        int_to_poly(int(entry["colC"]), p, d)
    # will fit with 2d coeffs
    assert int_to_poly(int(entry["colC"]), p, d * 2) == expected_colC
    assert int_to_poly(int(entry["colC"]) - 1, p, d * 2) != expected_colC
    assert int_to_poly(int(entry["colC"]) + 1, p, d * 2) != expected_colC


def test_segmentation_edge_case(edge_case_data):
    p, d, entry = edge_case_data[:3]
    colC = entry["colC"]
    split_entries = composite_split([colC], 2)
    expected_split = "9" * 11
    expected_ptxt = [219, 690, 342, 540]
    for s in split_entries:
        assert s == expected_split
        assert int_to_poly(int(s), p, d) == expected_ptxt

    colC = str(int(entry["colC"]) - 1)
    split_entries = list(composite_split([colC], 2))
    assert split_entries == [expected_split, "9" * 10 + "8"]
    split_entries = list(map(int, split_entries))
    assert split_entries[1] != expected_split  # Should be expected_split - 1
    assert int_to_poly(split_entries[0], p, d) == expected_ptxt
    assert int_to_poly(split_entries[1], p, d) != expected_ptxt
    expected_ptxt[-1] -= 1  # decr the last element
    assert int_to_poly(split_entries[1], p, d) == expected_ptxt


def test_client_segmentation(
    encode_obj_for_client_translation_table, test_vector_p41_m41_translation_table
):
    """Test when number of queries is smaller than the segmentation size."""
    data_entries, expected_encoding, _ = test_vector_p41_m41_translation_table
    encode = encode_obj_for_client_translation_table
    data_entries.pop(-1)  # Remove last entry so now 3 entries
    # Alter expected_encoding accordingly (remove every 4th entry)
    len_data_entries = len(data_entries) + 1
    for i, enc in enumerate(expected_encoding):
        expected_encoding[i] = [
            [] if (i + 1) % len_data_entries == 0 else e for i, e in enumerate(enc)
        ]

    ptxts = encode(data_entries)
    assert len(ptxts) == len(expected_encoding)
    for ptxt, expected in zip(ptxts, expected_encoding):
        assert ptxt.slots() == expected


def test_more_queries_than_capacity(
    encode_obj_for_client_translation_table, test_vector_p41_m41_translation_table
):
    """Test for when number of entries is larger than max capacity in ptxt"""
    data_entries, expected_encoding, _ = test_vector_p41_m41_translation_table
    encode = encode_obj_for_client_translation_table
    # Append extra entry
    data_entries.append({"colA": "IJ", "colB": "FR", "colC": "89"})
    with pytest.raises(ValueError):
        ptxts = encode(data_entries)


@pytest.fixture
def edge_case_data():
    p = 769
    d = 4
    entry = {"colA": "ZZZZ", "colB": "ZZ", "colC": "9" * 22}
    expected_colA = [0, 2, 646, 119]
    expected_colB = [0, 0, 0, 675]
    expected_colC = [62, 677, 49, 84, 254, 438, 535, 460]
    return p, d, entry, expected_colA, expected_colB, expected_colC


@pytest.fixture
def test_vector_p41_m41(test_vector_p41_m41_translation_table):
    (
        data_entries,
        expected_client_encoding,
        expected_server_encoding,
    ) = test_vector_p41_m41_translation_table

    def change_base(coeffs, len_alphabet):
        print(coeffs, file=sys.stderr, end=" ")
        number = inner_prod(
            coeffs, [len_alphabet**i for i in reversed(range(len(coeffs)))]
        )
        print(number, file=sys.stderr, end=" ")
        poly = int_to_poly(number, base=41, numof_coeffs=2)
        print(poly, file=sys.stderr)
        return poly

    expected_client_encoding[0] = [
        change_base(data, 36) for data in expected_client_encoding[0]
    ]
    expected_client_encoding[1] = [
        change_base(data, 26) for data in expected_client_encoding[1]
    ]

    expected_server_encoding[0] = [
        change_base(data, 36) for data in expected_server_encoding[0]
    ]
    expected_server_encoding[4] = [
        change_base(data, 36) for data in expected_server_encoding[4]
    ]
    expected_server_encoding[1] = [
        change_base(data, 26) for data in expected_server_encoding[1]
    ]
    expected_server_encoding[5] = [
        change_base(data, 26) for data in expected_server_encoding[5]
    ]

    return data_entries, expected_client_encoding, expected_server_encoding


@pytest.fixture
def test_vector_p41_m41_translation_table():
    data_entries = [
        {"colA": "AB", "colB": "NC", "colC": "56"},
        {"colA": "CD", "colB": "SU", "colC": "22"},
        {"colA": "EF", "colB": "KU", "colC": "32"},
        {"colA": "GH", "colB": "ED", "colC": "67"},
    ]
    expected_client_encoding = [
        [[0, 1], [2, 3], [4, 5], [6, 7], [0, 1], [2, 3], [4, 5], [6, 7]],
        [[13, 2], [18, 20], [10, 20], [4, 3], [13, 2], [18, 20], [10, 20], [4, 3]],
        [[0, 5], [0, 2], [0, 3], [0, 6], [0, 5], [0, 2], [0, 3], [0, 6]],
        [[0, 6], [0, 2], [0, 2], [0, 7], [0, 6], [0, 2], [0, 2], [0, 7]],
    ]
    expected_server_encoding = [
        [[0, 1], [0, 1], [0, 1], [0, 1], [2, 3], [2, 3], [2, 3], [2, 3]],
        [[13, 2], [13, 2], [13, 2], [13, 2], [18, 20], [18, 20], [18, 20], [18, 20]],
        [[0, 5], [0, 5], [0, 5], [0, 5], [0, 2], [0, 2], [0, 2], [0, 2]],
        [[0, 6], [0, 6], [0, 6], [0, 6], [0, 2], [0, 2], [0, 2], [0, 2]],
        [[4, 5], [4, 5], [4, 5], [4, 5], [6, 7], [6, 7], [6, 7], [6, 7]],
        [[10, 20], [10, 20], [10, 20], [10, 20], [4, 3], [4, 3], [4, 3], [4, 3]],
        [[0, 3], [0, 3], [0, 3], [0, 3], [0, 6], [0, 6], [0, 6], [0, 6]],
        [[0, 2], [0, 2], [0, 2], [0, 2], [0, 7], [0, 7], [0, 7], [0, 7]],
    ]
    return data_entries, expected_client_encoding, expected_server_encoding


@pytest.fixture
def config_and_policies_alpha_translation_tables():
    config = Config(
        params=Params(p=41, m=48),
        columns=3,
        segments=2,
        encodings={"colA": "alphanumeric", "colB": "alphabetical", "colC": "numeric"},
        composites={"colC": 2},
    )

    params = config.params
    policies = {
        "alphanumeric": {
            symbol: code
            for code, symbol in enumerate(string.ascii_uppercase + string.digits)
        },
        "alphabetical": {
            symbol: code for code, symbol in enumerate(string.ascii_uppercase)
        },
        "numeric": BaseFromAlphabet(params.p, params.d, alphabet=string.digits),
    }
    return config, policies


@pytest.fixture
def config_and_policies():
    config = Config(
        params=Params(p=41, m=48),
        columns=3,
        segments=2,
        encodings={"colA": "alphanumeric", "colB": "alphabetical", "colC": "numeric"},
        composites={"colC": 2},
    )

    params = config.params
    policies = {
        "alphanumeric": BaseFromAlphabet(
            params.p, params.d, alphabet=string.ascii_uppercase + string.digits
        ),
        "alphabetical": BaseFromAlphabet(params.p, params.d),
        "numeric": BaseFromAlphabet(params.p, params.d, alphabet=string.digits),
    }
    return config, policies


@pytest.fixture
def encode_obj_for_client_translation_table(
    config_and_policies_alpha_translation_tables,
):
    return ClientEncoder(*config_and_policies_alpha_translation_tables)


@pytest.fixture
def encode_obj_for_server_translation_table(
    config_and_policies_alpha_translation_tables,
):
    return ServerEncoder(*config_and_policies_alpha_translation_tables)


@pytest.fixture
def encode_obj_for_client(config_and_policies):
    return ClientEncoder(*config_and_policies)


@pytest.fixture
def encode_obj_for_server(config_and_policies):
    return ServerEncoder(*config_and_policies)
