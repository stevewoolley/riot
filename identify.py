#!/usr/bin/env python

import boto3
import argparse

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="image file (png or jpg)", required=True)
    parser.add_argument("-b", "--bucket", help="s3 bucket", required=True)
    parser.add_argument("-c", "--confidence", help="Network port", type=int, default=75)
    args = parser.parse_args()

    client = boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object': {'Bucket': args.bucket, 'Name': args.filename}},
                                    MinConfidence=args.confidence)

    print('Detected labels for ' + args.filename)
    for label in response['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))
