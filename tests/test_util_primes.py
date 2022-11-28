import pytest
from kit.utils.primes import *


def test_parse_factor_line():
    # parse_factor_line doesn't check for correctness
    assert parse_factor_line("6: 2 3") == (6, (2, 3))
    assert parse_factor_line("6: \t2 \t3") == (6, (2, 3))
    assert parse_factor_line("6: 3 2") == (6, (3, 2))  # order matters
    assert parse_factor_line("36: 2 2 3 3") == (36, (2, 2, 3, 3))

    with pytest.raises(ValueError):
        parse_factor_line("6 3 2")
        parse_factor_line("6.1: 3 2")
