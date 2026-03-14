#!/bin/bash
# NOTE: This script originally pushed built images to an internal Docker registry.
# Replace <YOUR_REGISTRY> with your own registry URL if you wish to publish images.
set -e

CURRENT_REPO=$(basename `git rev-parse --show-toplevel`)
CURRENT_BRANCH=`git rev-parse --abbrev-ref HEAD | sed 's/\//_/g'`
CURRENT_COMMIT_HASH=`git log --pretty=format:"%h" -1`

earthly ${@} --build-arg CURRENT_BRANCH=$CURRENT_BRANCH --build-arg CURRENT_COMMIT_HASH=$CURRENT_COMMIT_HASH --build-arg CURRENT_REPO=$CURRENT_REPO +tag-image

# Example output (replace <YOUR_REGISTRY> with your actual registry):
echo "<YOUR_REGISTRY>/$CURRENT_REPO:$CURRENT_BRANCH <YOUR_REGISTRY>/$CURRENT_REPO:$CURRENT_BRANCH-$CURRENT_COMMIT_HASH"
