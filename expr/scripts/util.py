from typing import List, Sequence


def int_to_pd_poly(num: int, base: int, no_coeffs: int) -> List[int]:
    """Return a list of coeffs of a polynomial encoded from an integer"""

    def coeffs(pd, num):
        for pth in pd:
            coeff, num = divmod(num, pth)
            yield coeff

    pd = (base ** i for i in reversed(range(no_coeffs)))
    poly = list(coeffs(pd, num))
    if poly[0] >= p:
        raise ValueError(f"Integer cannot fit in {d} slot coeffs: {poly}")
    return poly


def inner_prod(v1: Sequence[int], v2: Sequence[int]) -> int:
    """Computes the inner product of two vectors"""
    if len(v1) != len(v2):
        raise ValueError(f"v1 and v2 are not the same length '{len(v1)} != {len(v2)}'")
    return sum(a * b for a, b in zip(v1, v2))
