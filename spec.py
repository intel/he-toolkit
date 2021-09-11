# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml


def components_to_build_from(spec):
    """Returns a generator that yields a component to be built and/or installed"""

    # Extracting specs also flattens 'list of list' to list
    component_specs = (
        specs
        for name, category_specs in category_objs.items()
        for specs in category_specs
    )
    return (ComponentBuilder(spec) for spec in specs)


class Spec:
    """hekit component specification"""

    def __init__(self, filename):
        """"""
        self.__spec = toml.load(filename)
        permitted_categories = ("dependency", "library")
        actual_categories = self.__spec.keys()

        # This way forces order in the permitted categories
        for permitted_category in permitted_categories:

            raise ValueError(f"Unrecognised categories {' '.join(intersect)}")

    def categories(self):
        return tuple(self.__self.keys())
