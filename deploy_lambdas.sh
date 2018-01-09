#!/bin/bash

# Check if the AWS CLI is in the PATH
found=$(which aws)
if [ -z "$found" ]; then
  echo "Please install the AWS CLI under your PATH: http://aws.amazon.com/cli/"
  exit 1
fi

export AWS_DEFAULT_PROFILE=personal

# Updating Lambda functions
echo "Sync lambda content"
cd lambda
for f in $(ls -1); do
  echo "Updating function $f begin..."
  cd $f
  bin=""
  if [ -d "bin" ]; then
    cd bin
    for bf in $(ls -1); do
        bin+="--extra-file bin/$bf"
    done
    cd ..
  fi
  lambda-uploader $bin
  cd ..
done
