import json
import time
import boto3
from botocore.exceptions import ClientError
from app.common.log import init_logger
from app.common.date import utc_iso

logger = init_logger()


class AwsS3Handler:
    client = None
    # resource = None
    bucket = None
    cf_client = None
    distribution_id = None

    def __init__(self, bucket, distribution_id=None):
        self.bucket = bucket
        self.client = boto3.client('s3')
        self.cf_client = boto3.client(
            'cloudfront') if distribution_id else None
        self.distribution_id = distribution_id

    def __del__(self):
        pass

    def get_data(self, path, data_type='raw'):
        s3_data = self.client.get_object(Bucket=self.bucket, Key=path)
        raw_data = s3_data['Body'].read()
        if data_type == 'raw':
            return raw_data

        str_data = s3_data['Body'].read().decode('utf-8')
        if data_type == 'json':
            dict_data = json.loads(str_data)
            return dict_data

        return str_data

    def get_list_by_dir(self, dir_path):
        res = self.client.list_objects(Bucket=self.bucket, Prefix=dir_path)
        return res.get('Contents', [])

    def upload(self, blob, path, mimetype=None):
        res = self.client.put_object(
            Body=blob,
            # Body = file_strage.stream.read(),
            # Body = io.BufferedReader(file_strage).read(),
            Bucket=self.bucket,
            ContentType=mimetype,
            Key=path
        )
        self.create_invalidation([f'/{path}'])
        return res

    def update(self, blob, path, mimetype=None):
        return self.upload(blob, path, mimetype)

    def delete(self, path):
        res = self.client.delete_object(
            Bucket=self.bucket,
            Key=path
        )
        self.create_invalidation([f'/{path}'])
        return res

    def delete_by_dir(self, dir_path):
        objs = self.get_list_by_dir(dir_path)
        if len(objs) == 0:
            return None

        delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objs]}
        res = self.client.delete_objects(
            Bucket=self.bucket, Delete=delete_keys)
        if self.cf_client and self.distribution_id:
            paths = [f'/{obj["Key"]}' for obj in objs]
            self.create_invalidation(paths)
        return res

    def get_file_uploaded_at(self, path):
        try:
            # Get the object metadata
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=path
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return None
            else:
                raise e
        return utc_iso(False, True, response['LastModified'])

    def create_invalidation(self, paths):
        if not self.cf_client or not self.distribution_id:
            return None

        res = self.cf_client.create_invalidation(
            DistributionId=self.distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': str(time.time())  # ユニークな参照ID
            }
        )
        logger.info('create_invalidation: paths=%s', paths)
        logger.debug('create_invalidation: res=%s', res)
        return res
