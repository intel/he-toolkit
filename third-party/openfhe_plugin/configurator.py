import os.path
from os import path
import shutil
from git import Repo, GitError

# import subprocess


class Configurator:
    OPENFHE_DEVELOPMENT_BRANCH = "v0.9.2"
    OPENFHE_HEXL_BRANCH = "main"

    OPENFHE_DEVELOPMENT_REPO = "openfhe-development"
    OPENFHE_REPO = "openfhe-development"
    OPENFHE_HEXL = ""

    ROOT = os.getcwd()

    # Sets up the build of OpenFHE
    @classmethod
    def configure(self, args) -> None:
        # delete previous staging directory if it already exists
        if args.delete:
            if path.exists(self.ROOT + "/openfhe_plugin/openfhe-staging"):
                try:
                    shutil.rmtree(self.ROOT + "/openfhe_plugin/openfhe-staging")
                    print("previous staging directory deleted.")
                except OSError as e:
                    print("Error: %s - %s." % (e.filename, e.strerror))
        else:
            self.abort("Unwilling to proceed - aborting.")
        if args.ofhe:
            self.OPENFHE_REPO = "openfhe-release"
        if args.hexl:
            self.OPENFHE_HEXL = "openfhe-hexl"

        if not self.OPENFHE_HEXL:
            if self.OPENFHE_REPO == self.OPENFHE_DEVELOPMENT_REPO:
                self.stage_openfhe_development()
            else:
                print("Unsupported build type.")
        else:
            self.stage_openfhe_development()
            # WIP: add hexl script afterwards

    @classmethod
    def stage_openfhe_development(self):
        # WIP
        # mkdir repos > /dev/null 2>&1
        repos = self.ROOT + "/repos"
        print(repos)
        try:
            if not os.path.exists(repos):
                os.mkdir(repos)
                os.chdir(repos)
        except OSError as e:
            self.abort("Unable to create repos directory.")

        # CLONES INTO CURRENT FILES - change in future
        if not os.path.exists(repos + "/openfhe-development"):
            self.separator()
            print("Cloning openfhe-development repository.\n")
            os.mkdir(repos + "/openfhe-development")
            os.chdir(repos + "/openfhe-development")
            repo = Repo.clone_from(
                "https://github.com/openfheorg/openfhe-development.git", repos
            )
            # it's assumed that when repo is cloned, it will make a new folder within repos.

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

        # git checkout main || abort "Checkout of openfhe-hexl main failed."
        try:
            repo.git.checkout("main")
        except GitError as e:
            self.abort("Checkout of openfhe-hexl main failed.")

        # git pull || abort "Pull of the openfhe-development failed."
        try:
            repo.pull("origin", "main")
        except GitError as e:
            self.abort("Pull of the openfhe-development failed.")

        # git checkout $OPENFHE_DEVELOPMENT_BRANCH || abort "Checkout of openfhe-development branch $OPENFHE_DEVELOPMENT_BRANCH failed."
        try:
            repo.git.checkout(self.OPENFHE_DEVELOPMENT_BRANCH)
        except GitError as e:
            self.abort(
                "Checkout of openfhe-development branch ",
                self.OPENFHE_DEVELOPMENT_BRANCH,
                " failed.\n",
            )

        self.separator()
        print(
            "Status of branch openfhe-development ",
            self.OPENFHE_DEVELOPMENT_BRANCH,
            ".\n",
        )
        print(repo.git.status())
        self.separator()
        print("Staging [default] build.\n")

        os.chdir(ROOT)

        if path.exists(ROOT + "/openfhe-staging"):
            try:
                shutil.rmtree(ROOT + "/openfhe-staging")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

        try:
            os.mkdir(ROOT + "/openfhe-staging")
            os.chdir(ROOT + "/openfhe-staging")
        except OSError as e:
            self.abort("Unable to create openfhe staging directory.")

        # subprocess.run(["cp", "-r", "$ROOT/repos/openfhe-development/"])
        self.separator()
        print("Bulid [default] is staged.\n")
        print(
            "You may now run scripts/build-openfhe-development.sh to perform a default build.\n"
        )

    @classmethod
    def stage_openfhe_development_hexl(self):
        # CLONES INTO CURRENT FILES - change in future
        if not os.path.exists(self.ROOT + "/repos/openfhe-hexl"):
            try:
                if not os.path.exists(self.ROOT + "/repos"):
                    os.chdir(self.ROOT + "/repos")
            except OSError as e:
                self.abort("Unable to enter the repos directory.")
            try:
                repo = Repo.clone_from(
                    "https://github.com/openfheorg/openfhe-hexl.git",
                    self.ROOT + "/repos",
                )
            except GitError as e:
                self.abort("Unable to clone the openfhe-hexl repository.")
            # it's assumed that when repo is cloned, it will make a new folder within repos.

        self.separator()
        print("Switching to branch openfhe-hexl ", self.OPENFHE_HEXL_BRANCH, ".\n")
        if not os.path.exists(self.ROOT + "repos/openfhe-hexl"):
            os.chdir(self.ROOT + "repos/openfhe-hexl")
        else:
            self.abort("Clone of openfhe-hexl failed.")

        # git checkout main || abort "Checkout of openfhe-hexl main failed."
        try:
            repo.git.checkout("main")
        except GitError as e:
            self.abort("Checkout of openfhe-hexl main failed.")

        # git pull || abort "Pull of the openfhe-hexl failed."
        try:
            repo.pull("origin", "main")
        except GitError as e:
            self.abort("Pull of the openfhe-hexl failed.")

        # git checkout $OPENFHE_DEVELOPMENT_BRANCH || abort "Checkout of openfhe-development branch $OPENFHE_DEVELOPMENT_BRANCH failed."
        try:
            repo.git.checkout(self.OPENFHE_HEXL_BRANCH)
        except GitError as e:
            self.abort(
                "Checkout of openfhe-hexl branch ",
                self.OPENFHE_HEXL_BRANCH,
                " failed.\n",
            )

        self.separator()
        print("Status of branch openfhe-hexl ", self.OPENFHE_HEXL_BRANCH, ".\n")
        print(repo.git.status())
        self.separator()
        print("Build [hexl-enabled] is staged.\n")
        print(
            "You may now run scripts/build-openfhe-development-hexl.sh to perform a hexl-enabled build."
        )

    @classmethod
    def abort(self, MSG):
        print("\n")
        print("ERROR: ", MSG)
        print()
        # WIP: variables
        # print("CC=$CC CXX=$CXX CMAKE_FLAGS=$CMAKE_FLAGS")
        print()
        print("abort.")
        exit(1)

    @classmethod
    def separator(self):
        print("\n")
        print(
            "==============================================================================="
        )
        print()
