import os
import shutil


class Configurator:
    OPENFHE_DEVELOPMENT_BRANCH = "v0.9.2"
    OPENFHE_HEXL_BRANCH = "main"

    OPENFHE_DEVELOPMENT_REPO = "openfhe-development"
    OPENFHE_REPO = "openfhe-development"
    OPENFHE_HEXL = ""

    ROOT = os.getcwd()

    @classmethod
    def configure(args) -> None:
        # if args.del:
        #     # remove ./openfhe-staging
        #     try:
        #         shutil.rmtree("./openfhe-staging")
        #     except OSError as e:
        #         print("Error: %s - %s." % (e.filename, e.strerror))
        #     print("previous staging directory deleted.")
        # else:
        #     print("Unwilling to proceed - aborting.")
        #     exit(1)
        # if (args.ofhe_build):
        #     OPENFHE_REPO = "openfhe-release"
        # if args.hexl:
        #     OPENFHE_HEXL = "openfhe-hexl"

        if not OPENFHE_HEXL:
            if OPENFHE_REPO == OPENFHE_DEVELOPMENT_REPO:
                # run a different method - stage-openfhe-development-hexl.sh
                print("running stage-openfhe-development.sh")
            else:
                print("Unsupported build type.")
        else:
            print("running stage-openfhe-development-hexl.sh")

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
