#!/bin/bash

# Check if the AWS CLI is in the PATH
found=$(which aws)
if [ -z "$found" ]; then
  echo "Please install the AWS CLI under your PATH: http://aws.amazon.com/cli/"
  exit 1
fi

# Check if jq is in the PATH
found=$(which jq)
if [ -z "$found" ]; then
  echo "Please install jq under your PATH: http://stedolan.github.io/jq/"
  exit 1
fi

# Read other configuration from config.json
REGION=$(jq -r '.REGION' config.json)
CLI_PROFILE=$(jq -r '.CLI_PROFILE // empty' config.json)
BUCKET=$(jq -r '.BUCKET' config.json)
MAX_AGE=$(jq -r '.MAX_AGE' config.json)
IDENTITY_POOL_ID=$(jq -r '.IDENTITY_POOL_ID' config.json)
USER_POOL_ID=$(jq -r '.USER_POOL_ID' config.json)
CLIENT_ID=$(jq -r '.CLIENT_ID' config.json)
DEVELOPER_PROVIDER_NAME=$(jq -r '.DEVELOPER_PROVIDER_NAME' config.json)

echo "Cache Control max age $MAX_AGE"

#if a CLI Profile name is provided... use it.
if [[ ! -z "$CLI_PROFILE" ]]; then
  echo "AWS Credentials Profile: $CLI_PROFILE"
  export AWS_DEFAULT_PROFILE=$CLI_PROFILE
fi

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
