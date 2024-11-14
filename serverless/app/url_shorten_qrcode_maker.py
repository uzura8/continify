import os
import sys
from io import BytesIO
import qrcode
from app.aws_s3_handler import AwsS3Handler
from app.common.log import output_log
from app.models.dynamodb import ShortenUrl

MEDIA_S3_BUCKET_NAME = os.environ.get('MEDIA_S3_BUCKET_NAME')
URL_SHORTEN_BASE_URL = os.environ.get('URL_SHORTEN_BASE_URL')
DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'
QR_CODE_FILE_NAME_PREFIX = 'qr'

class UrlShortenQrcodeMaker:
    s3handler = None
    bucket_dir_path = ''
    debug_log_enabled = False
    url_shorten_base_url = ''


    def __init__(self):
        self.debug_log_enabled = DEBUG_LOG_ENABLED
        self.url_shorten_base_url = URL_SHORTEN_BASE_URL
        self.s3handler = AwsS3Handler(MEDIA_S3_BUCKET_NAME)


    def __del__(self):
        pass


    def create_qrcode(self, url_id, service_seq_num=None):
        item = ShortenUrl.get_one_by_pkey('urlId', url_id)
        if not item:
            raise InvalidValueError('urlId does not exist')

        file_name_items = [url_id]
        if QR_CODE_FILE_NAME_PREFIX:
            file_name_items.insert(0, QR_CODE_FILE_NAME_PREFIX)
        if service_seq_num:
            seq_num_str = str(service_seq_num).zfill(5)
            file_name_items.append(seq_num_str)
        file_name = '-'.join(file_name_items) + '.png'
        

        shorten_url = self.url_shorten_base_url + url_id
        upload_key = f'shorten-url/qrcodes/{file_name}'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(shorten_url)
        qr.make()
        img = qr.make_image()

        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)

        self.s3handler.upload(buffer, upload_key, 'image/png')
        output_log(['def url_shorten_qrcode_maker.create_qrcode', 'qrcode created', upload_key])


def get_event_data(target_dict, attr_name, data_type):
    try:
        res = target_dict[attr_name][data_type]
        return res
    except KeyError:
        return None


class InvalidValueError(Exception):
    pass


def handler(event=None, context=None):
    output_log('START: url_shorten_qrcode_maker.handler')
    output_log(['url_shorten_qrcode_maker.handler:event', event])

    qcm = UrlShortenQrcodeMaker()
    if event and 'Records' in event:
        err_cnt = 0
        for r in event['Records']:
            if r['eventName'] != 'INSERT':
                output_log(['def url_shorten_qrcode_maker.handler', 'Skip event for not INSERT'])
                continue

            try:
                url_id = get_event_data(r['dynamodb']['NewImage'], 'urlId', 'S')
                service_seq_num = get_event_data(r['dynamodb']['NewImage'], 'serviceSeqNumber', 'N')
                qcm.create_qrcode(url_id, service_seq_num)

            except Exception as e:
                tb = sys.exc_info()[2]
                msg = e.with_traceback(tb)
                output_log(msg, 'error')
                err_cnt += 1

        return 'Success' if not err_cnt else 'END: url_shorten_qrcode_maker.handler: Error'
