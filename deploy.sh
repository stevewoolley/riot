#!/bin/bash

# Check if the AWS CLI is in the PATH
found=$(which aws)
if [ -z "$found" ]; then
  echo "Please install the AWS CLI under your PATH: http://aws.amazon.com/cli/"
  exit 1
fi
export AWS_DEFAULT_PROFILE=personal
export BUCKET=snerted.com
export MAX_AGE=10

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

echo "Sync html content..."
cd ../www
for f in $(ls -1 *.html); do
  aws s3 cp ./$f s3://$BUCKET --cache-control max-age="$MAX_AGE" --acl public-read
done
cd ..

# Updating www app.js
echo "Sync assets..."
cd www/assets
for f in $(ls -1 *.*); do
  aws s3 cp ./$f s3://$BUCKET/assets/ --cache-control max-age="$MAX_AGE" --acl public-read
done
cd ../..
