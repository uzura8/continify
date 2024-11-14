from app.models.dynamodb.base import Base


class ShortenUrlDomain(Base):
    table_name = 'shorten-url-domain'
    public_attrs = [
        'domain',
        'createdAt',
        'updatedAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'serviceIdDomain',
        'serviceId',
        'createdBy',
    ]
    all_attrs = public_attrs + private_attrs

    @classmethod
    def check_not_exists_and_create_item(self, service_id, domain):
        # If new domain not saved, Add new domain to domains table
        service_id_domain = f'{service_id}#{domain}'
        # query_keys = {
        #     'p': {'key': 'serviceIdDomain', 'val': service_id_domain}}
        keys = {'serviceIdDomain': service_id_domain}
        domain_item = self.get_one_by_pkey_new(keys)
        if domain_item:
            return

        vals = {
            'serviceIdDomain': service_id_domain,
            'serviceId': service_id,
            'domain': domain,
        }
        return ShortenUrlDomain.create(vals)

    @classmethod
    def check_exists_and_delete_item(self, service_id, domain):
        # If old domain not exits in urls table, delete from domains table
        service_id_domain = f'{service_id}#{domain}'
        keys = {'serviceIdDomain': service_id_domain}
        url_item = self.get_one_by_pkey_new(keys)
        if url_item:
            return
        return ShortenUrlDomain.delete(keys)
