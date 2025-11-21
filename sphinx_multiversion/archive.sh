#!/usr/bin/env bash

TARGET_COMMIT=$1
TOP_FILE=$2

REPO_DIR="$(git rev-parse --show-toplevel)"
TOP_PREFIX=$(basename "$REPO_DIR")

# Archive the main repo at the desired commit
git archive --format=tar --output="$TOP_FILE" "$TARGET_COMMIT"

export TOP_PREFIX
export TOP_FILE
export TARGET_COMMIT

git config --file .gitmodules --get-regexp path | awk '{ print $2 }' | while read submodule_path; do
  # Get the submodule commit referenced by the parent repo at $TARGET_COMMIT
  SUB_COMMIT=$(git ls-tree $TARGET_COMMIT "$submodule_path" | awk '{print $3}')
  SUB_PREFIX="$submodule_path/"
  SUB_FILE="$(basename "$submodule_path")-$SUB_COMMIT.tar"
  echo "Archiving submodule $submodule_path to $SUB_FILE"
  git -C "$submodule_path" archive --format=tar --prefix="$SUB_PREFIX" --output="$SUB_FILE" "$SUB_COMMIT"
  tar --concatenate --file="$TOP_FILE" "external/$SUB_FILE"
  rm "external/$SUB_FILE"
done
