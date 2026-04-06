#!/usr/bin/env bash
# Clone all Python dependencies into the dependencies/ folder.
# Run this once after cloning the main repository.

set -e

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dependencies"
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

clone_or_pull "git@git.noc.ruhr-uni-bochum.de:fortimtb/bopfoxfeaturizer.git"  "$DEPS_DIR/bopfoxfeaturizer"
clone_or_pull "https://github.com/ICAMS/python-ace.git"                        "$DEPS_DIR/python-ace"
clone_or_pull "https://github.com/AIIMProject/PyCEF.git"                       "$DEPS_DIR/PyCEF"             "packaging"

# Optional: BopFox Fortran binary (requires manual compilation after cloning)
# Uncomment following lines if you have access to these packages.
#
# clone_or_pull "git@git.noc.ruhr-uni-bochum.de:fortimtb/bopdftprojections.git" "$DEPS_DIR/bopdftprojections"
# clone_or_pull "git@git.noc.ruhr-uni-bochum.de:fortimtb/bopfox.git" "$DEPS_DIR/bopfox"
# cd $DEPS_DIR/bopfox 
# make 
# make install /src/bopfox/api

echo ""
echo "Done. Now run:  pip install -r requirements.txt"
