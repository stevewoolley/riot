#!/usr/bin/env python

import boto3
import pprint
import argparse


def detect_faces(f):
    with open(f, 'rb') as image:
        response = client.detect_faces(Image={'Bytes': image.read()})
        pprint.pprint(response)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--image", help="image file (png or jpg)", required=True)
    parser.add_argument("-c", "--collection", help="rekognition collection id", default='snerted')
    parser.add_argument("-r", "--region", help="aws region", default='us-east-1')
    args = parser.parse_args()

    client = boto3.client('rekognition', region_name=args.region)

    print(detect_faces(args.image))
