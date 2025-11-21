#!/usr/bin/env bash

TARGET_COMMIT=$1
TOP_FILE=$2

REPO_DIR="$(git rev-parse --show-toplevel)"
TOP_PREFIX=$(basename "$REPO_DIR")

# Save current commit hash
ORIGINAL_COMMIT=$(git rev-parse HEAD)

# Make sure submodules point to the right commit for the target commit
git checkout "$TARGET_COMMIT"
git submodule update --init --recursive

# Archive the main repo at the desired commit
git archive --format=tar --output="$TOP_FILE" "$TARGET_COMMIT"

export TOP_PREFIX
export TOP_FILE
export TARGET_COMMIT

git submodule foreach --recursive '
  SUB_PREFIX="$displaypath/"
  SUB_FILE="$(basename $(git rev-parse --show-toplevel))-$TARGET_COMMIT.tar"
  git archive --format=tar --prefix="$SUB_PREFIX" --output="$SUB_FILE" HEAD
  tar --concatenate --file="../$TOP_FILE" "$SUB_FILE"
  rm "$SUB_FILE"
'

# Return to the original commit
git checkout "$ORIGINAL_COMMIT"
git submodule update --init --recursive
