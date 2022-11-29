import os.path
from os import path


class Configurator:
    OPENFHE_DEVELOPMENT_BRANCH = "v0.9.2"
    OPENFHE_HEXL_BRANCH = "main"

    OPENFHE_DEVELOPMENT_REPO = "openfhe-development"
    OPENFHE_REPO = "openfhe-development"
    OPENFHE_HEXL = ""

    ROOT = os.getcwd()

    @classmethod
    def configure(args) -> None:
        print(args)
        if args.delete:
            try:
                shutil.rmtree(ROOT + "/openfhe_plugin/openfhe-staging")
                print("previous staging directory deleted.")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        else:
            self.abort("Unwilling to proceed - aborting.")
        if args.ofhe:
            OPENFHE_REPO = "openfhe-release"
        if args.hexl:
            OPENFHE_HEXL = "openfhe-hexl"

        if not OPENFHE_HEXL:
            if OPENFHE_REPO == OPENFHE_DEVELOPMENT_REPO:
                print("running stage-openfhe-development.sh")
                stage_openfhe_development()

            else:
                print("Unsupported build type.")
        else:
            print("running stage-openfhe-development-hexl.sh")

    @classmethod
    def stage_openfhe_development():
        # WIP
        # mkdir repos > /dev/null 2>&1
        repos = ROOT + "/repos"
        try:
            if not os.path.exists(repos):
                os.mkdir(repos)
        except OSError as e:
            self.abort("Unable to create repos directory.")
        os.chdir(repos)

        if not os.path.exists(repos + "/openfhe-development"):
            self.separator()
            print("Cloning openfhe-development repository.\n")
            os.mkdir(repos + "/openfhe-development")
            os.chdir(repos + "/openfhe-development")
            Repo.clone_from(
                "https://github.com/openfheorg/openfhe-development.git", repos
            )

        self.separator()
        print(
            "Switching to branch openfhe-development ",
            OPENFHE_DEVELOPMENT_BRANCH,
            ".\n",
        )
        if not os.path.exists(repos + "/openfhe-development"):
            os.chdir(repos + "/openfhe-development")
        else:
            self.abort("Clone of openfhe-development failed.")

    @classmethod
    def abort(self, MSG):
        print("\n")
        print("ERROR: $MSG")
        print()
        # WIP: variables
        # print("CC=$CC CXX=$CXX CMAKE_FLAGS=$CMAKE_FLAGS")
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
