#!/bin/bash
set -e

CURRENT_REPO=$(basename `git rev-parse --show-toplevel`)
CURRENT_BRANCH=`git rev-parse --abbrev-ref HEAD | sed 's/\//_/g'`
CURRENT_COMMIT_HASH=`git log --pretty=format:"%h" -1`

earthly ${@} --build-arg CURRENT_BRANCH=$CURRENT_BRANCH --build-arg CURRENT_COMMIT_HASH=$CURRENT_COMMIT_HASH --build-arg CURRENT_REPO=$CURRENT_REPO +tag-image

echo "<internal_registry>:500/$CURRENT_REPO:$CURRENT_BRANCH <internal_registry>:500/$CURRENT_REPO:$CURRENT_BRANCH-$CURRENT_COMMIT_HASH"
