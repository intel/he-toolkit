from decode import *
import pytest
from types import SimpleNamespace


def test_sum_vectors():
    vectors = [[1, 2, 3], [2, 1, 0], [6, 6, 6]]
    assert sum_vectors(*vectors) == [9, 9, 9]


def test_sum_segments():
    no_segs = 4
    upto_10 = list([i] for i in range(10))
    nums = []
    for i in range(no_segs):
        nums.extend(upto_10 if i % 2 else reversed(upto_10))
    print(nums)
    for total in sum_segments(nums, no_segs):
        assert total == [18]


def test_parse_header_with_two_numbers():
    header_str = "2 3"
    assert (2, 3) == parse_header(header_str)


def test_parse_header_with_one_number():
    header_str = "3"
    assert (3, 1) == parse_header(header_str)


def test_parse_args():
    cmdline_args = "some_params.file some_data.file".split()
    args = parse_args(cmdline_args)
    expected_obj = {
        "params": "some_params.file",
        "datafile": "some_data.file",
        "segment": 1,
        "entries": 0,
    }
    assert vars(args) == expected_obj


def test_main(capfd, empty_obj, example_params_and_data_files):
    args = empty_obj
    args.params, args.datafile, indices = example_params_and_data_files(
        "test.params", "test.data"
    )
    args.segment = 1
    args.entries = 0
    main(args)
    captured = capfd.readouterr()
    expected_out = "\n".join([f"Match on line '{i+1}'" for i in indices]) + "\n"
    assert captured.out == expected_out


def test_ignore_padding(capfd, empty_obj, example_params_and_data_files):
    args = empty_obj
    args.params, args.datafile, indices = example_params_and_data_files(
        "test.params", "test.data"
    )
    args.segment = 1
    args.entries = 9  # Only count first 9 lines
    main(args)
    captured = capfd.readouterr()
    expected_out = "\n".join([f"Match on line '{i+1}'" for i in indices]) + "\n"
    assert captured.out == expected_out  # No difference because last match is entry 9

    args.entries = 7  # This should now ignore the match on line 9
    main(args)
    captured = capfd.readouterr()
    # Match on line 9 should be missing from captured.out
    assert captured.out != expected_out
    new_expected_out = (
        "\n".join([f"Match on line '{i+1}'" for i in indices if i <= args.entries])
        + "\n"
    )
    assert captured.out == new_expected_out


def test_invalid_entries_arg(empty_obj, example_params_and_data_files):
    args = empty_obj
    args.params, args.datafile, _ = example_params_and_data_files(
        "test.params", "test.data"
    )
    args.segment = 1
    args.entries = -1
    with pytest.raises(ValueError):
        main(args)


@pytest.fixture
def empty_obj():
    """Empty object. Useful for late binding attribs."""
    return SimpleNamespace()


@pytest.fixture
def example_params_and_data_files(tmp_path):
    """Create in a tmp dir an example params and data file."""

    def _create_func(params_filename: str, datafile_filename: str):
        # Create params file
        params_path = tmp_path / f"{params_filename}"
        params_path.write_text("m = 45\np = 19\n")

        # Create data file
        datafile_path = tmp_path / f"{datafile_filename}"
        params = read_params(params_path.resolve())
        ptxt = Ptxt(params)
        indices = [2, 5, 8]  # sorted unique nums
        ptxt.insert_data([1] if i in indices else [0] for i in range(params.nslots))
        out = f"1\n{ptxt.to_json()}\n"
        datafile_path.write_text(out)
        return params_path.resolve(), datafile_path.resolve(), indices

    return _create_func
