import re


class BuildError(Exception):
    """Exception for something wrong with the build."""

    def __init__(self, message, errors):
        super().__init__(message)


def chain_run(funcs):
    """"""
    for fn in funcs:
        success, return_code = fn()
        if success:
            print("success")
        else:
            print("failure", return_code)
            raise BuildError("")


def fill_self_ref_string_dict(d):
    """Returns a dict with str values.
    NB. Only works for flat str value dict."""

    def fill_str(s):
        if not isinstance(s, str):
            raise TypeError(
                f"fill_str expects type str, but got type '{type(s).__name__}'"
            )

        symbols = re.findall(r"(%(.*?)%)", s)

        if not symbols:
            return s

        new_s = s
        for symbol, k in symbols:
            new_s = new_s.replace(symbol, fill_str(d[k]))

        return new_s

    return {k: fill_str(v) for k, v in d.items()}


class ComponentBuilder:
    def __init__(self, spec):
        """"""
        if not isinstance(spec, dict):
            raise TypeError(
                f"A spec should be a of type dict, but got '{type(spec).__name__}'"
            )
        self.__spec = fill_self_ref_string_dict(spec)
        print(self.__spec)

    def pre_build(self):
        """"""
        print("pre-build")
        return "success", 0

    def build(self):
        """"""
        print("build")
        return "success", 0

    def post_build(self):
        """"""
        print("post-build")
        return "success", 0

    def install(self):
        """"""
        print("install")
        return "success", 0
