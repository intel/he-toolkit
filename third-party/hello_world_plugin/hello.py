# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


def print_msg(args) -> None:
    """Executes new functionality"""
    msg = quote() if args.quote else "hello world"
    print(msg)


def quote() -> str:
    """Print some quote"""
    return "Look both ways before crossing the road"
