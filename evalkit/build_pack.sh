#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e


VERSION="v0.3"
PUB_VERSION_HEXL="v1.0.0"
STARTTIME=$(date +"%m_%d_%Y-%I_%M_%p")

if [ -d "./projects" ]
then
    echo "Now deleting the directory ./projects to start fresh"
    read -p "Press enter to continue"
    rm -rf ./projects
fi

mkdir projects
pushd projects

echo -e "\nSTARTING CLONING REPO'S:"
if [ "$1" != "PUBLIC" ]
then
    git clone ssh://git@gitlab.devtools.intel.com:29418/DBIO/glade/intel-hexl.git
fi
git clone ssh://git@gitlab.devtools.intel.com:29418/DBIO/glade/intel-palisade-development.git
git clone ssh://git@gitlab.devtools.intel.com:29418/DBIO/glade/intel-seal.git
git clone ssh://git@gitlab.devtools.intel.com:29418/DBIO/glade/he-toolkit.git
echo -e "DONE CLONING REPOS\n"

# he-toolkit:
echo -e "\nSTARTING HE-TOOLKIT:"
pushd he-toolkit
git checkout $VERSION
rm CODEOWNERS
rm .pre-commit-config.yaml
rm .gitlab-ci.yml
rm README.md
rm -rf examples/secure-query/project
rm -rf .git
sed -i '/set(INTEL_HEXL_GIT_REPO_URL/c\set(INTEL_HEXL_GIT_REPO_URL LINK)' ./cmake/intel-hexl.cmake
sed -i '/set(INTEL_HEXL_GIT_LABEL/c\set(INTEL_HEXL_GIT_LABEL TAG)' ./cmake/intel-hexl.cmake
sed -i '/set(PALISADE_REPO_URL/c\  set(PALISADE_REPO_URL LINK)' ./cmake/palisade.cmake
sed -i '/set(PALISADE_GIT_TAG/c\  set(PALISADE_GIT_TAG TAG)' ./cmake/palisade.cmake
sed -i '/set(SEAL_REPO_URL/c\  set(SEAL_REPO_URL LINK)' ./cmake/seal.cmake
sed -i '/set(SEAL_GIT_TAG/c\  set(SEAL_GIT_TAG TAG)' ./cmake/seal.cmake
popd
echo -e "DONE HE-TOOLKIT\n"

# intel-palisade-development:
echo -e "\nSTARTING PALISADE:"
pushd intel-palisade-development
git checkout intel-$VERSION
rm CMakeLists.User.txt
rm .gitlab-ci.yml
rm .pre-commit-config.yaml
rm .gitmodules
rm -rf .git
git init .
rm -r third-party/cereal third-party/google-benchmark third-party/google-test third-party/gperftools
git submodule add https://github.com/JerryRyan/cereal.git third-party/cereal
git submodule add https://github.com/google/benchmark.git third-party/google-benchmark
git submodule add https://github.com/google/googletest.git third-party/google-test
git submodule add https://github.com/gperftools/gperftools.git third-party/gperftools
pushd third-party
cd cereal
git checkout a384b101e4437b5a83b91c9f4e4fd2eae1d5c9e8
cd ../
git add cereal
cd google-benchmark
git checkout d3ad0b9d11c190cb58de5fb17c3555def61fdc96
cd ../
git add google-benchmark
cd google-test
git checkout 8b4817e3df3746a20502a84580f661ac448821be
cd ../
git add google-test
cd gperftools
git checkout c1d546d7b22cc503f37e9a6efa1d249be60243a3
cd ../
git add gperftools
popd
pwd
rm third-party/cereal/* -rf
rm third-party/google-benchmark/* -rf
rm third-party/google-test/* -rf
rm third-party/gperftools/* -rf
set +e
rm third-party/cereal/.* -rf
rm third-party/google-benchmark/.* -rf
rm third-party/google-test/.* -rf
rm third-party/gperftools/.* -rf
set -e
sed -i '/set(INTEL_HEXL_GIT_REPO_URL/c\    set(INTEL_HEXL_GIT_REPO_URL LINK)' ./third-party/intel-hexl/intel-hexl.cmake
sed -i '/set(INTEL_HEXL_GIT_LABEL/c\    set(INTEL_HEXL_GIT_LABEL TAG)' ./third-party/intel-hexl/intel-hexl.cmake
popd
echo -e "DONE PALISADE\n"

# intel-seal:
echo -e "\nSTARTING SEAL:"
pushd intel-seal
git checkout intel-$VERSION
rm CODEOWNERS
rm .gitlab-ci.yml
rm .pre-commit-config.yaml
rm -rf .git
sed -i '/GIT_REPOSITORY/c\    GIT_REPOSITORY LINK' ./cmake/ExternalIntelHEXL.cmake
sed -i '/GIT_TAG/c\    GIT_TAG TAG' ./cmake/ExternalIntelHEXL.cmake
popd
echo -e "DONE SEAL\n"

echo -e "\nSTARTNG HEXL:"
if [ "$1" == "PUBLIC" ]
then
    awk -v vers=$PUB_VERSION_HEXL 'NR==66{print "# Build / Test Intel HEXL\necho -e \"\\nBUILDING & TESTING INTEL HEXL:\"\ngit clone https://github.com/intel/hexl.git intel-hexl\npushd intel-hexl\ngit checkout " vers "\nmkdir build && cd build\ncmake .. -DCMAKE_INSTALL_PREFIX=../ \\\n         -DHEXL_SHARED_LIB=OFF \\\n         -DHEXL_EXPORT=ON \\\n         -DCMAKE_CXX_COMPILER=clang++-10 \\\n         -DCMAKE_C_COMPILER=clang-10 \\\n         -DCMAKE_BUILD_TYPE=Release\nmake -j\n./test/unit-test\nmake install\necho -e \"DONE TESTING INTEL HEXL\\n\"\npopd\n"}1' he-toolkit/evalkit/scripts/background/setup.sh > filler.txt
    cat filler.txt > he-toolkit/evalkit/scripts/background/setup.sh
    rm filler.txt
    HEXL_OPT="hexl-public"
else
    pushd intel-hexl
    git checkout $VERSION
    if [ "$1" == "SOURCE" ]
    then
        rm .clang-format
        rm .gitignore
        rm .gitlab-ci.yml
        rm .pre-commit-config.yaml
        rm CPPLINT.cfg
        rm CODEOWNERS
        rm -rf .git
        awk 'NR==66{print "# Build / Test Intel HEXL\necho -e \"\\nBUILDING & TESTING INTEL HEXL:\"\npushd intel-hexl\nmkdir build && cd build\ncmake .. -DCMAKE_INSTALL_PREFIX=../ \\\n         -DHEXL_SHARED_LIB=OFF \\\n         -DHEXL_EXPORT=ON \\\n         -DCMAKE_CXX_COMPILER=clang++-10 \\\n         -DCMAKE_C_COMPILER=clang-10 \\\n         -DCMAKE_BUILD_TYPE=Release\nmake -j\n./test/unit-test\nmake install\necho -e \"DONE TESTING INTEL HEXL\\n\"\npopd\n"}1' ../he-toolkit/evalkit/scripts/background/setup.sh > filler.txt
        cat filler.txt > ../he-toolkit/evalkit/scripts/background/setup.sh
        rm filler.txt
        HEXL_OPT="hexl-source"
    else
        mkdir build && cd build
        cmake .. -DCMAKE_INSTALL_PREFIX=../ -DHEXL_SHARED_LIB=OFF -DHEXL_EXPORT=ON -DCMAKE_CXX_COMPILER=clang++-10 -DCMAKE_C_COMPILER=clang-10 -DCMAKE_BUILD_TYPE=Release
        make -j
        ./test/unit-test # test correctness
        make install
        mkdir ../../intel-hexl-pack
        mv ../intel-hexl/include ../../intel-hexl-pack/
        mv ../lib ../../intel-hexl-pack/
        cd ../../
        rm -rf intel-hexl
        mv intel-hexl-pack intel-hexl
        sed -i '/INTERFACE_INCLUDE_DIRECTORIES/c\  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include/"' ./intel-hexl/lib/cmake/IntelHEXLTargets.cmake
        HEXL_OPT="hexl-binary"
    fi
    popd
fi
echo -e "DONE HEXL\n"


popd


# Build Evalkit (toolkit)
mkdir INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT
cp -rf projects/he-toolkit/evalkit/* INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT/
rm -rf projects/he-toolkit/evalkit
rm INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT/build_pack.sh
pushd projects
mv intel-seal seal
mv intel-palisade-development palisade
mv he-toolkit he-samples
pushd he-samples
sed -i 's/he-toolkit/he-samples/g' ./examples/secure-query/CMakeLists.txt
popd
popd
tar -czvf projects.tar.gz projects
rm -rf projects
mv projects.tar.gz INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT/
mv INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT/scripts .
sed -i 's/intel-seal/seal/g' scripts/background/setup.sh
sed -i 's/intel-palisade-development/palisade/g' scripts/background/setup.sh
sed -i 's/he-toolkit/he-samples/g' scripts/background/setup.sh
sed -i 's/HE-TOOLKIT/HE-SAMPLES/g' scripts/background/setup.sh
sed -i 's/he-toolkit/he-samples/g' scripts/runner/*
tar -czvf scripts.tar.gz scripts
rm -rf scripts
mv scripts.tar.gz INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT/
tar -czvf INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT_$HEXL_OPT\_$VERSION\_$STARTTIME.tar.gz INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT
rm -rf INTEL_HOMOMORPHIC_ENCRYPTION_TOOLKIT
