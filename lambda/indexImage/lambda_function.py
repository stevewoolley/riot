import urllib
import boto3
import json
from boto3.dynamodb.conditions import Key

REGION = 'us-east-1'
ITEMS = 'Items'
COLLECTION = 'snerted'
TABLE = 'faces'

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name=REGION)
ddb = boto3.resource('dynamodb', region_name=REGION)
table = ddb.Table(TABLE)


def search_known_faceid(f):
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


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = rekognition.index_faces(CollectionId=COLLECTION,
                                           DetectionAttributes=["ALL"],
                                           Image={"S3Object": {
                                               "Bucket": bucket,
                                               "Name": key
                                           }},
                                           ExternalImageId=key)
        if len(response['FaceRecords']) == 0:
            print "No faces found in {}".format(key)
        else:
            print "Face(s) Found: {} in {}".format(len(response['FaceRecords']), key)
            for i in response['FaceRecords']:
                r = rekognition.search_faces(
                    CollectionId=COLLECTION,
                    FaceId=i['Face']['FaceId']
                )
                hits = search_known_faceid(r)
                if len(hits) == 1:
                    # found a unique match
                    resp = table.put_item(
                        Item={
                            'id': i['Face']['FaceId'],
                            'name': hits.keys()[0]
                        }
                    )
                    print(
                        "Found: {} Hits: {} FaceId: {}".format(hits.keys()[0],
                                                               hits.values()[0],
                                                               i['Face']['FaceId'])
                    )
                else:
                    # no match
                    resp = table.put_item(
                        Item={
                            'id': i['Face']['FaceId'],
                            'details': json.dumps(i)
                        }
                    )
                    print(
                        "Not Found: {} in {}".format(i['Face']['FaceId'], key)
                    )
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e
