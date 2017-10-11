import boto3

s3_client = boto3.client('s3')
SNAPSHOTS = 'snapshots.snerted.com'


def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        if '-snapshot.jpg' in key:
            copy_source = {
                'Bucket': bucket,
                'Key': key
            }
            s3_client.copy(copy_source, SNAPSHOTS, "{}.{}".format(key.split('-')[0], 'jpg'))
