import boto3
import json
import logging

s3_client = boto3.client('s3')
SNAPSHOTS = 'snapshots.snerted.com'
COLLECTION = 'snerted'
CONFIDENCE = 75
from boto3.dynamodb.conditions import Key


def tagify(arr, field):
    o = []
    for i in arr:
        if field in i:
            o.append(i[field])
    return '+'.join(o)


def lambda_handler(event, context):
    print("Received event: {}".format(json.dumps(event)))
    if 'Records' in event:
        s3 = boto3.resource('s3')

        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            file_name = record['s3']['object']['key']
            client = boto3.client('rekognition')
            result = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': file_name}},
                                          MinConfidence=CONFIDENCE)
            response = client.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': file_name}})
            tags = {}
            if "Labels" in result:
                tags['recognize'] = tagify(result['Labels'], 'Name')
                # Identify faces
                if len(response['FaceDetails']) > 0:
                    try:
                        c = client.search_faces_by_image(
                            Image={"S3Object": {"Bucket": bucket, "Name": file_name, }},
                            CollectionId=COLLECTION)
                        table = boto3.resource('dynamodb').Table('faces')
                        hits = {}
                        for i in c['FaceMatches']:
                            record = table.query(KeyConditionExpression=Key('id').eq(i['Face']['FaceId']))['Items']
                            if len(record) > 0:
                                if record[0]['name'] in hits:
                                    hits[record[0]['name']] += 1
                                else:
                                    hits[record[0]['name']] = 1
                        if len(hits) > 0:
                            diff = len(response['FaceDetails']) - len(hits)
                            if diff > 0:
                                tags['identities'] = '+'.join(hits) + '+{} Unknowns'.format(diff)
                            else:
                                tags['identities'] = '+'.join(hits)
                    except Exception as e:
                        logging.warning("identify error: {}".format(e.message))
            existing_tags = s3.meta.client.get_object_tagging(Bucket=bucket, Key=file_name)['TagSet']
            if tags is not None:
                for k, v in tags.items():
                    existing_tags.append({'Key': k.strip(), 'Value': v.strip()})
                s3.meta.client.put_object_tagging(Bucket=bucket, Key=file_name, Tagging={'TagSet': existing_tags})
