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
	cp ../config.json $f/
  cd $f
  zip -r $f.zip index.js config.json
  aws lambda update-function-code --function-name ${f} --zip-file fileb://${f}.zip --region $REGION
	rm config.json
	rm $f.zip
  cd ..
  echo "Updating function $f end"
done

# Updating www content
echo "Generate www content"
cd ../www
if [ -d "edit" ]; then
  rm edit/*
else
  mkdir edit
fi
for f in $(ls -1 *.*); do
  echo "    $f..."
  sed -e "s/<REGION>/$REGION/g" \
      -e "s/<IDENTITY_POOL_ID>/$IDENTITY_POOL_ID/g" \
      -e "s/<USER_POOL_ID>/$USER_POOL_ID/g" \
      -e "s/<CLIENT_ID>/$CLIENT_ID/g" \
      -e "s/<DEVELOPER_PROVIDER_NAME>/$DEVELOPER_PROVIDER_NAME/g" \
      $f > edit/$f
done
echo "Sync www content"
cd edit
aws s3 sync . s3://$BUCKET --cache-control max-age="$MAX_AGE" --acl public-read
cd ../..
# Updating www app.js
echo "Sync app.js"
cd www/assets
aws s3 cp ./app.js s3://$BUCKET/assets/ --cache-control max-age="$MAX_AGE" --acl public-read
cd ../..
