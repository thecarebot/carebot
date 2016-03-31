import boto3
import logging
import uuid

import app_config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Uploader:
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(app_config.S3_BUCKET)

    def upload(self, data, name=None):
        if not name:
            name = str(uuid.uuid4())

        key = 'graphics/' + name + '.png'

        obj = self.bucket.put_object(
            Key=key,
            Body=data,
            ACL='public-read',
            ContentType='image/gif'
        )

        client = self.s3.meta.client
        url = '{}/{}/{}'.format(client.meta.endpoint_url, app_config.S3_BUCKET, key)

        return url
