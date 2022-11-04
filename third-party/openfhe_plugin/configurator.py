class Configurator:
    OPENFHE_DEVELOPMENT_BRANCH = "v0.9.2"
    OPENFHE_HEXL_BRANCH = "main"

    OPENFHE_DEVELOPMENT_REPO = "openfhe-development"
    OPENFHE_REPO = "openfhe-development"
    OPENFHE_HEXL = ""

    ROOT = ""

    @classmethod
    def configure(args) -> None:
        if args.exists in "Yy":
            # remove ./openfhe-staging
            print("previous staging directory deleted.")
        elif args.exists in "Nn":
            print("Unwilling to proceed - aborting.")
            exit(1)
        if (args.of_build) in "Yy":
            OPENFHE_REPO = "openfhe-release"
        if args.hexl_build in "Yy":
            OPENFHE_HEXL = "openfhe-hexl"

    @classmethod
    def abort():
        # MSG=$1
        # WIP: variables
        print("\n")
        print("ERROR: $MSG")
        print()
        print("CC=$CC CXX=$CXX CMAKE_FLAGS=$CMAKE_FLAGS")
        print()
        print("abort.")
        exit(1)

    @classmethod
    def separator():
        print("\n")
        print(
            "==============================================================================="
        )
        print()
