#!/usr/bin/env python

import boto3
import argparse
from boto3.dynamodb.conditions import Key


def search_in(f):
    with open(f, 'rb') as image:
        response = client.search_faces_by_image(Image={'Bytes': image.read()}, CollectionId=args.collection)
        return response


def search_known_in(f):
    ddb = boto3.resource('dynamodb', region_name=args.region)
    table = ddb.Table('faces')
    result = search_in(f)
    hits = {}
    for i in result['FaceMatches']:
        record = table.query(KeyConditionExpression=Key('id').eq(i['Face']['FaceId']))['Items']
        if len(record) > 0:
            if record[0]['name'] in hits:
                hits[record[0]['name']] += 1
            else:
                hits[record[0]['name']] = 1
    return hits


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--image", help="image file (png or jpg)", required=True)
    parser.add_argument("-c", "--collection", help="rekognition collection id", default='snerted')
    parser.add_argument("-r", "--region", help="aws region", default='us-east-1')
    args = parser.parse_args()

    client = boto3.client('rekognition', region_name=args.region)

    print(search_known_in(args.image))
