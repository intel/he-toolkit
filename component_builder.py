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


class ComponentBuilder:
    def __init__(self, spec):
        """"""
        self.__spec = spec

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
