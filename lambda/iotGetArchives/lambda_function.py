import boto3
import json
ARCHIVE = 'archive.snerted.com'


def parameter_parser(evt, key):
    if key in evt:
        return evt[key]
    elif 'pathParameters' in evt and key in evt['pathParameters']:
        return evt['pathParameters'][key]
    elif 'queryStringParameters' in evt and key in evt['queryStringParameters']:
        return evt['queryStringParameters'][key]
    return None


def response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
    }


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    prefix = parameter_parser(event, 'prefix')
    results = []
    for obj in s3.list_objects_v2(Bucket=ARCHIVE, Prefix=prefix)['Contents']:
        o = dict()
        o['name'] = obj['Key']
        o['url'] = s3.generate_presigned_url('get_object', Params={'Bucket': ARCHIVE, 'Key': obj['Key']})
        o['timestamp'] = date_handler(obj['LastModified'])
        o['size'] = obj['Size']
        results.append(o)
    return response(sorted(results, key=lambda k: k['timestamp'], reverse=True), 200)
