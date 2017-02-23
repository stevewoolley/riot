#!/usr/bin/env python

import boto3
import pprint
import argparse
import sys
from os.path import basename
from boto3.dynamodb.conditions import Key


def search_known_faceid(f):
    ddb = boto3.resource('dynamodb', region_name=args.region)
    table = ddb.Table('faces')
    hits = {}
    for i in f['FaceMatches']:
        record = table.query(KeyConditionExpression=Key('id').eq(i['Face']['FaceId']))['Items']
        if len(record) > 0:
            if 'name' in record[0]:
                if record[0]['name'] in hits:
                    hits[record[0]['name']] += 1
                else:
                    hits[record[0]['name']] = 1
    return hits


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--image", help="image file (png or jpg)", required=True)
    parser.add_argument("-b", "--bucket", help="S3 rekognition bucket", required=True)
    parser.add_argument("-c", "--collection", help="rekognition collection id", default='snerted')
    parser.add_argument("-r", "--region", help="aws region", default='us-east-1')
    parser.add_argument("-n", "--name", help="name of person in picture", default=None)
    args = parser.parse_args()

    externalImageId = basename(args.image)

    s3 = boto3.client('s3')
    results = s3.list_objects(Bucket=args.bucket, Prefix=externalImageId)
    if 'Contents' in results:
        sys.exit("ERROR: {} already exists in bucket {}".format(externalImageId, args.bucket))
    else:
        # first copy image up to s3
        with open(args.image, 'rb') as data:
            s3.upload_fileobj(data, args.bucket, args.image)
        # recognize
        rekognition = boto3.client('rekognition', region_name=args.region)
        with open(args.image, 'rb') as image:
            response = rekognition.index_faces(CollectionId=args.collection,
                                               DetectionAttributes=["ALL"],
                                               Image={"S3Object": {
                                                   "Bucket": args.bucket,
                                                   "Name": externalImageId
                                               }},
                                               ExternalImageId=externalImageId)
            if len(response['FaceRecords']) == 0:
                print "No faces found"
            elif len(response['FaceRecords']) == 1 and args.name is not None:
                dynamodb = boto3.resource('dynamodb', region_name=args.region)
                table = dynamodb.Table('faces')
                for i in response['FaceRecords']:
                    resp = table.put_item(
                        Item={
                            'id': i['Face']['FaceId'],
                            'name': args.name
                        }
                    )
            else:
                print "Face(s) Found: {} ".format(len(response['FaceRecords']))
                if args.name is not None:
                    print("Too many faces in image, ignoring name argument")

                dynamodb = boto3.resource('dynamodb', region_name=args.region)
                table = dynamodb.Table('faces')
                for i in response['FaceRecords']:
                    r = rekognition.search_faces(
                        CollectionId=args.collection,
                        FaceId=i['Face']['FaceId']
                    )
                    hits = search_known_faceid(r)
                    if len(hits) == 1:
                        resp = table.put_item(
                            Item={
                                'id': i['Face']['FaceId'],
                                'name': hits.keys()[0]
                            }
                        )
                        print("================================================================")
                        print(
                            "Found: {} Hits: {} FaceId: {}".format(hits.keys()[0],
                                                                   hits.values()[0],
                                                                   i['Face']['FaceId'])
                        )
                    else:
                        resp = table.put_item(
                            Item={
                                'id': i['Face']['FaceId']
                            }
                        )
                        print("================================================================")
                        print("Unknown:")
                        pprint.pprint(i)
