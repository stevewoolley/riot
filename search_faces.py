#!/usr/bin/env python

import boto3
import pprint
import argparse
from boto3.dynamodb.conditions import Key


def search_known_faceid(f):
    ddb = boto3.resource('dynamodb', region_name=args.region)
    table = ddb.Table('faces')
    hits = {}
    for i in f['FaceMatches']:
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
    parser.add_argument("-f", "--faceId", help="Face ID", required=True)
    parser.add_argument("-c", "--collection", help="rekognition collection id", default='snerted')
    parser.add_argument("-r", "--region", help="aws region", default='us-east-1')
    args = parser.parse_args()

    client = boto3.client('rekognition', region_name=args.region)

    response = client.search_faces(
        CollectionId=args.collection,
        FaceId=args.faceId
    )
    pprint.pprint(search_known_faceid(response))



