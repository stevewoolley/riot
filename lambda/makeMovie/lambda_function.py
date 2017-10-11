import boto3
import subprocess

WORKSPACE = 'workspace.snerted.com'


def lambda_handler(event, context):
    for f in event["Files"]:
        print f
    result = subprocess.call("./ffmpeg -r 20 -qscale 2  -i {} output.mp4".format(' '.join(event["Files"])), shell=True)
    return "ffmpeg: {}".format(result)

# results = []
# for obj in s3.list_objects_v2(Bucket=SNAPSHOTS, Prefix='pi', MaxKeys=10)['Contents']:
#   o = dict()
#   o['name'] = obj['Key']
#   o['url'] = s3.generate_presigned_url('get_object', Params={'Bucket': SNAPSHOTS, 'Key': obj['Key']})
#   results.append(o)
