from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base


class ServiceContent(Base):
    table_name = 'service-content'

    public_attrs = [
        'serviceId',
        'contentId',
        'commentDefaultPublishStatus',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'createdAt',
        'updatedAt',
    ]
    all_attrs = public_attrs + private_attrs

    allowed_vals = {}
