from app.models.dynamodb.base import Base


class Contact(Base):
    table_name = 'contact'
    public_attrs = [
        'serviceId',
        'code',
        'createdAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'status',
        'name',
        'email',
        'customFields',
        'emailInfo',
        'requestInfo',
        'content',
        'updatedAt',
        'serviceIdCode',
    ]
    all_attrs = public_attrs + private_attrs
