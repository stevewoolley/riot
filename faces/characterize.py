#!/usr/bin/env python

import boto3
import json
import argparse

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="image file (png or jpg)", required=True)
    parser.add_argument("-b", "--bucket", help="s3 bucket", required=True)
    args = parser.parse_args()

    client = boto3.client('rekognition')
    response = client.detect_faces(Image={'S3Object': {'Bucket': args.bucket, 'Name': args.filename}},
                                   Attributes=['ALL'])

    print('Detected faces for ' + args.filename)
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))
