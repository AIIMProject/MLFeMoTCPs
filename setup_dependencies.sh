#!/usr/bin/env bash
# Clone all Python dependencies into the dependencies/ folder and install them.
# Run this once after cloning the main repository.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPS_DIR="$SCRIPT_DIR/dependencies"
mkdir -p "$DEPS_DIR"

clone_or_pull() {
    local url="$1"
    local dest="$2"
    local branch="${3:-}"

    if [ -d "$dest/.git" ]; then
        echo "Updating $dest..."
        git -C "$dest" pull
    else
        echo "Cloning $url into $dest..."
        if [ -n "$branch" ]; then
            git clone --branch "$branch" "$url" "$dest"
        else
            git clone "$url" "$dest"
        fi
    fi
}

apply_patch() {
    local repo="$1"
    local patch="$2"
    echo "Applying patch to $(basename $repo)..."
    git -C "$repo" apply --check "$patch" 2>/dev/null \
        && git -C "$repo" apply "$patch" \
        || echo "Patch already applied or not needed, skipping."
}

# Optional dependecy:
# clone_or_pull "git@git.noc.ruhr-uni-bochum.de:fortimtb/bopdftprojections.git" "$DEPS_DIR/bopdftprojections"
clone_or_pull "git@github.com:AIIMProject/BopfoxFeaturizer.git"  "$DEPS_DIR/bopfoxfeaturizer" "bypassbofox"
clone_or_pull "https://github.com/AIIMProject/PyCEF.git"                       "$DEPS_DIR/PyCEF"  "packaging"

# python-ace: requires patching, then compilation via setup.py
clone_or_pull "https://github.com/ICAMS/python-ace.git"                        "$DEPS_DIR/python-ace"
apply_patch "$DEPS_DIR/python-ace" "$SCRIPT_DIR/dependencies/python-ace.patch"

echo "Installing build-time dependencies for python-ace..."
pip install "numpy<=1.26.4" "Cython<3" &> /dev/null

echo "Installing python-ace (compiling C++ extensions)..."
cd "$DEPS_DIR/python-ace"
pip install . &> /dev/null
python setup.py install &> /dev/null
cd "$SCRIPT_DIR"

# Optional: BopFox Fortran binary (requires manual compilation after cloning)
# clone_or_pull "git@git.noc.ruhr-uni-bochum.de:fortimtb/bopfox.git" "$DEPS_DIR/bopfox"
# cd "$DEPS_DIR/bopfox" && make && make install

echo ""
echo "Done. Installing dependencies"

pip install -r requirements.txt &> /dev/null

echo "Downloading raw data from Zenodo..."
bash Tools/download_from_zenodo.sh


echo "done, now running tests to verify installation. This may take a while..."

export NBMAKE_KERNEL=test_mlfemotcps
#export CALC_IMPORTANCES

pytest --nbmake -vv --durations=10 -s test/

#
#pytest  --nbmake -vv -s  --nbmake-kernel=test_mlfemotcps --nbmake-timeout=0  \
#  03_PrepareDataset.ipynb         \
#  04_ComputeACEFeatures.ipynb     \
#  04_ComputeACEFeatures.ipynb     \
#  04_ComputeLibraryFeatures.ipynb \
#  05_ComputeBOPFeatures.ipynb     
#
#echo ""
#echo ""
#echo ""
#echo ""
#echo "=============================="
#echo "Building models for Kernel Ridge"
#MODELNAME="Kernel Ridge" pytest  --nbmake -vv -s  --nbmake-kernel=test_mlfemotcps --nbmake-timeout=0  \
#  07_MachineLearn-ModelSelection.ipynb 
#
#echo ""
#echo ""
#echo ""
#echo ""
#echo "=============================="
#echo "Building models for MLP"
#MODELNAME="MLP" pytest  --nbmake -vv -s  --nbmake-kernel=test_mlfemotcps --nbmake-timeout=0  \
#  07_MachineLearn-ModelSelection.ipynb  \
#
#echo ""
#echo ""
#echo ""
#echo ""
#echo "=============================="
#echo "Building models for Random Forest"
#MODELNAME="Random Forest" pytest  --nbmake -vv -s --nbmake-kernel=test_mlfemotcps --nbmake-timeout=0  \
#  07_MachineLearn-ModelSelection.ipynb  \
#  07_MachineLearn.ipynb \
#  08_AnalysisModels.ipynb\
#  test
#
